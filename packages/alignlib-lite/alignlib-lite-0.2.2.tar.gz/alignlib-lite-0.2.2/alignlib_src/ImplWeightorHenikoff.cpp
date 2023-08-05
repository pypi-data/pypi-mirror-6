/*
  alignlib - a library for aligning protein sequences

  $Id: ImplWeightorHenikoff.cpp,v 1.2 2004/01/07 14:35:36 aheger Exp $

  Copyright (C) 2004 Andreas Heger

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

#include <iostream>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "alignlib_fwd.h"
#include "AlignlibDebug.h"

#include "Weightor.h"
#include "ImplWeightorHenikoff.h"
#include "MultipleAlignment.h"
#include "HelpersEncoder.h"
#include "Encoder.h"

using namespace std;

namespace alignlib
{

/** factory functions */
HWeightor makeWeightorHenikoff( const bool rescale )
{
	return HWeightor(new ImplWeightorHenikoff( rescale));
}

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplWeightorHenikoff::ImplWeightorHenikoff ( const bool rescale )
: ImplWeightor(), mRescale( rescale )
{
}

ImplWeightorHenikoff::~ImplWeightorHenikoff ()
{
}

ImplWeightorHenikoff::ImplWeightorHenikoff (const ImplWeightorHenikoff & src ) :
	ImplWeightor(src), mRescale(src.mRescale)
{
}

// implement cloning and creation
IMPLEMENT_CLONE( HWeightor, ImplWeightorHenikoff );

//--------------------------------------------------------------------------------------------------------------------------------
HSequenceWeights ImplWeightorHenikoff::calculateWeights(
			const HMultipleAlignment & src,
			const HEncoder & translator ) const
{
	debug_func_cerr(5);

	//!! TODO: Right now I have to translate twice. This could be improved by making a temporary
	// copy (at the expense of memory, though)

	int width = translator->getAlphabetSize();

	int nsequences = src->getNumSequences();
	Position length = src->getLength();

	Position column;
	int i, j;

	//-----------------> calculate counts for each column and amino acid<----------------------
	WeightedCount * counts = new WeightedCount[length * width];

	for (j = 0; j < length; j++)
	{
		WeightedCount * ccolumn = &counts[j * width];
		for ( i = 0; i < width; i++)
			ccolumn[i] = 0;
	}
	Residue residue;

	for (i = 0; i < nsequences; i++)
	{
		const std::string & sequence = (*src)[i];
		for (column = 0; column < length; column++)
			if ((residue = translator->encode(sequence[column])) < width)
				counts[column * width + residue]++;
	}

	//-----------------> calculate types per column <------------------------------------------
	int * ntypes = new int[length];

	for (column = 0; column < length; column++)
	{
		WeightedCount * ccolumn = &counts[j * width];
		ntypes[column] = 0;
		for (i = 0; i < width; i++)
			if (ccolumn[i] > 0)
				ntypes[column]++;
	}
	//---------------> calculate sequence weights <------------------------------------------
	HSequenceWeights weights( new SequenceWeights(nsequences) );
	SequenceWeights & w = *weights;
	for (i = 0; i < nsequences; i++)
	{
		w[i] = 0;
		for (column = 0; column < length; column++)
		{
			const std::string & sequence = (*src)[i];			// sum up, but skip gaps and masked characters
			if ( (residue = translator->encode(sequence[column])) < width)
				w[i] += (SequenceWeight)(1.0 /
						((double)counts[column * width + residue] * (double)ntypes[column]));
		}
	}

	//---------------> clean up------------------------------------------------------------
	delete [] counts;
	delete [] ntypes;

	//---------------> rescale weights, so that they sum to 1 <---------------------------
	if (mRescale)
		rescaleWeights( weights, nsequences, nsequences);
	else
		rescaleWeights( weights, nsequences, 1.0);

	return HSequenceWeights( weights );
}
} // namespace alignlib

