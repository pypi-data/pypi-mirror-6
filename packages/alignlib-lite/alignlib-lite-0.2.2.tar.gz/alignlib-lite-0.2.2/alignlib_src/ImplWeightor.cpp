/*
  alignlib - a library for aligning protein sequences

  $Id: ImplWeightor.cpp,v 1.2 2004/01/07 14:35:36 aheger Exp $

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
#include "AlignlibException.h"
#include "AlignlibDebug.h"
#include "ImplWeightor.h"

using namespace std;

namespace alignlib
{

/** factory functions */
HWeightor makeWeightor()
{
	return HWeightor(new ImplWeightor());
}

#define MIN_WEIGHT 0.0001

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplWeightor::ImplWeightor() :
	Weightor()
{
}

ImplWeightor::ImplWeightor (const ImplWeightor & src ) :
	Weightor(src)
	{
}

ImplWeightor::~ImplWeightor ()
{
  debug_func_cerr(5);

}

//--------------------------------------------------------------------------------------------------------------------------------
IMPLEMENT_CLONE( HWeightor, ImplWeightor );

//--------------------------------------------------------------------------------------------------------------------------------
void ImplWeightor::rescaleWeights(
		HSequenceWeights & weights,
		int nsequences,
		SequenceWeight value) const
{
  debug_func_cerr(5);


    if (value == 0)
      value = nsequences;

    //--------------> rescale weights
    double total = 0;
    int i;
    SequenceWeights & w = *weights;

    for ( i = 0; i < nsequences; i++)
    {
    	if (w[i] < MIN_WEIGHT)
    		w[i] = MIN_WEIGHT;               //!! to do: some warnings, exception handling, ...
    	total += w[i];
    }

    SequenceWeight factor = value / total;

    for ( i = 0; i < nsequences; i++) w[i] *= factor;
}

//--------------------------------------------------------------------------------------------------------------------------------
void ImplWeightor::fillCounts(
		WeightedCountMatrix & dest,
		const HMultipleAlignment & src,
		const HEncoder & translator) const
{
	debug_func_cerr(5);

	if (translator->getAlphabetSize() != dest.getNumCols())
		throw AlignlibException( "count matrix and alphabet have different size.");
	if (src->getLength() != dest.getNumRows())
		throw AlignlibException( "count matrix and multiple alignment have different size.");

	int nsequences = src->getNumSequences();

	HSequenceWeights weights( calculateWeights( src, translator) );

	debug_cerr_start( 5, "computed the following weights:");

#ifdef DEBUG
	for (int i = 0; i < src->getNumSequences(); i++)
		debug_cerr_add ( 5, " " << i << "=" << (*weights)[i] )
	debug_cerr_add( 5, std::endl );
#endif

	Position mali_length = src->getLength();
	int mali_width = src->getNumSequences();

	// calculate counts
	Residue width = translator->getAlphabetSize();

	for (int nsequence = 0; nsequence < mali_width; nsequence++)
	{
		SequenceWeight weight = (*weights)[nsequence];
		const std::string & seq = (*src)[nsequence];
		for (int x = 0; x < mali_length; ++x)
		{
			Residue code = translator->encode( seq[x] );
			// continue for out-of-range characters (gaps)
			if (code >= width) continue;

			debug_cerr(5, "width=" << (int)width << " char=" << seq[x] << " code=" << (int)code << " weight=" << weight );
			dest.setValue( x, code, dest.getValue( x, code) + weight );
		}
	}
}

HSequenceWeights ImplWeightor::calculateWeights(
		const HMultipleAlignment & src,
		const HEncoder & translator ) const
{
	int nsequences = src->getNumSequences();

	HSequenceWeights weights(new SequenceWeights(nsequences));

	 for (int i = 0; i < nsequences; i++)
		 (*weights)[i] = 1;

	return weights;
}

} // namespace alignlib
