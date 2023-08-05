/*
  alignlib - a library for aligning protein sequences

  $Id: ImplRegularizor.cpp,v 1.2 2004/01/07 14:35:35 aheger Exp $

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

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "alignlib_fwd.h"
#include "AlignlibDebug.h"
#include "Regularizor.h"
#include "ImplRegularizor.h"
#include "HelpersRegularizor.h"
#include "Matrix.h"

namespace alignlib
{

/** factory functions */
HRegularizor makeRegularizor()
{
	return HRegularizor(new ImplRegularizor());
}

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplRegularizor::ImplRegularizor()
			{
	debug_func_cerr(5);
			}

//--------------------------------------------------------------------------------------------------------------------------------
ImplRegularizor::~ImplRegularizor ()
{
	debug_func_cerr(5);
}

//-------------------------------------------------------------------------------------------------------------------------------
ImplRegularizor::ImplRegularizor (const ImplRegularizor & src )
{
}

IMPLEMENT_CLONE( HRegularizor, ImplRegularizor );

//-------------------------------------------------------------------------------------------------------
double ImplRegularizor::calculateDiversity( const WeightedCountMatrix & counts ) const
{
	// diversity is the average number of different characters per column
	Position width = counts.getNumCols();
	Position length = counts.getNumRows();

	double total = 0;
	for (Position p = 0; p < length; ++p)
	{
		Residue n = 0;
		WeightedCount * count_column = counts.getRow( p );
		for (Residue r = 0; r < width; ++r)
			if (count_column[r] > 0)
				++n;
		total += (double)n;
	}
	return total / length;
}

//-------------------------------------------------------------------------------------------------------
/** fill frequencies from counts without regularization.
 *  */
void ImplRegularizor::fillFrequencies(
		FrequencyMatrix & frequencies,
		const WeightedCountMatrix & counts,
		const HEncoder & encoder) const
		{
	debug_func_cerr(5);

	assert( frequencies.getNumRows() == counts.getNumRows() );
	assert( frequencies.getNumCols() == counts.getNumCols() );

	// simply calculate frequencies

	Position column;
	WeightedCount ntotal;
	int i;

	Position width = frequencies.getNumCols();
	Position length = frequencies.getNumRows();

	for (column = 0; column < length; ++column)
	{
		ntotal = 0;

		const WeightedCount * counts_column = counts.getRow(column);
		Frequency * frequency_column = frequencies.getRow(column);

		for (i = 0; i < width; i ++)
			ntotal += counts_column[i];

		if (ntotal == 0)
			ntotal = 1;

		for (i = 0; i < width; i++)
		{
			Frequency f = (Frequency)((Frequency)counts_column[i] / (Frequency)ntotal);
			frequency_column[i] = f;
		}
	}
		}

} // namespace alignlib
