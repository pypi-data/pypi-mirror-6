/*
 alignlib - a library for aligning protein sequences

 $Id: ImplAlignatorDotsDiagonal.cpp,v 1.2 2004/01/07 14:35:34 aheger Exp $

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
#include <iomanip>
#include <math.h>

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "ImplAlignatorDotsDiagonal.h"
#include "Alignandum.h"
#include "ImplAlignmentMatrixRow.h"

#include "HelpersSubstitutionMatrix.h"

#include "Alignment.h"
#include "HelpersAlignment.h"

#include "HelpersAlignator.h"

using namespace std;

namespace alignlib
{

/*---------------------factory functions ---------------------------------- */

/** make an alignator object, which does a dot-alignment. The default version can be given an
 * AlignmentMatrix-object */
HAlignator makeAlignatorDotsDiagonal(const HAlignator & alignator, Score gop,
		Score gep, Score diagonal_gop, Score diagonal_gep)
{
	return HAlignator(new ImplAlignatorDotsDiagonal(alignator, gop, gep,
			diagonal_gop, diagonal_gep));
}

//----------------------------------------------------------------------------------------------------------------------------------------
/** constructors and destructors */
ImplAlignatorDotsDiagonal::ImplAlignatorDotsDiagonal() :
	ImplAlignatorDots()
{}

ImplAlignatorDotsDiagonal::ImplAlignatorDotsDiagonal(const HAlignator & dots,
		Score row_gop, Score row_gep, Score col_gop, Score col_gep) :
			ImplAlignatorDots(dots, row_gop, row_gep, col_gop, col_gep)
{
}

//----------------------------------------------------------------------------------------------------------------------------------------
ImplAlignatorDotsDiagonal::ImplAlignatorDotsDiagonal(
		const ImplAlignatorDotsDiagonal & src) :
	ImplAlignatorDots(src)
{
	debug_func_cerr(5);

}

//----------------------------------------------------------------------------------------------------------------------------------------
ImplAlignatorDotsDiagonal::~ImplAlignatorDotsDiagonal()
{
	debug_func_cerr(5);

}

IMPLEMENT_CLONE( HAlignator, ImplAlignatorDotsDiagonal )
;

//----------------------------------------------------------------------------------------------------------------------------------------

Score ImplAlignatorDotsDiagonal::getGapCost(Dot x1, Dot x2) const
{

	const ResiduePair & p1 = (*mPairs)[x1];
	const ResiduePair & p2 = (*mPairs)[x2];

	Diagonal diagonal_difference = (p2.mRow - p2.mCol) - (p1.mRow - p1.mCol);

	if (diagonal_difference == 0)
		return mRowGop + (p2.mRow - p1.mRow) * mRowGep;
	else
		return mColGop + mColGep * abs(diagonal_difference);

}

} // namespace alignlib
