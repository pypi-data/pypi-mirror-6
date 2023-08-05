/*
  alignlib - a library for aligning protein sequences

  $Id: ImplLogOddorGribskov.cpp,v 1.2 2004/01/07 14:35:35 aheger Exp $

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
#include "AlignlibException.h"
#include "ImplLogOddorGribskov.h"
#include "HelpersLogOddor.h"
#include "HelpersSubstitutionMatrix.h"
#include "Matrix.h"

namespace alignlib
{
//---------------------------------------------------------< factory functions >--------------------------------------
HLogOddor makeLogOddorGribskov(
		const HSubstitutionMatrix & matrix,
		const Score & scale,
		const Score & mask_value )
{
	return HLogOddor( new ImplLogOddorGribskov( matrix, scale, mask_value ) );
}

HLogOddor makeLogOddorGribskov(
		const Score & scale,
		const Score & mask_value )
{
	return HLogOddor( new ImplLogOddorGribskov( scale, mask_value ) );
}

//---------------------------------------------------------< constructors and destructors >--------------------------------------

ImplLogOddorGribskov::ImplLogOddorGribskov (
		const HSubstitutionMatrix & matrix,
		const Score & scale_factor,
		const Score & mask_value ) :
	ImplLogOddor( scale_factor, mask_value ),
	mSubstitutionMatrix( matrix )
	{
	}

ImplLogOddorGribskov::ImplLogOddorGribskov (
		const Score & scale_factor,
		const Score & mask_value ) :
			ImplLogOddor( scale_factor, mask_value )
{
		mSubstitutionMatrix = getToolkit()->getSubstitutionMatrix();
}

ImplLogOddorGribskov::~ImplLogOddorGribskov ()
{
}

ImplLogOddorGribskov::ImplLogOddorGribskov (const ImplLogOddorGribskov & src ) :
	ImplLogOddor( src ), mSubstitutionMatrix( src.mSubstitutionMatrix )
	{
	}

IMPLEMENT_CLONE( HLogOddor, ImplLogOddorGribskov );

//--------------------------------------------------------------------------------------------------------------------------------
void ImplLogOddorGribskov::fillProfile(
		ScoreMatrix & profile ,
		const FrequencyMatrix & frequencies,
		const HEncoder & encoder) const
{
	debug_func_cerr(5);

	// simply take the frequencies and divide by Gribskov-frequencies and take log.
	// For frequencies of 0, MASK_VALUE is used.
	Position length = frequencies.getNumRows();
	Residue width  = frequencies.getNumCols();

	if (mSubstitutionMatrix->getNumRows() != width )
		throw AlignlibException( "ImplLogOddorGribskov.cpp: frequencies and substitution matrix use different alphabet.");

	for (Position column = 0; column < length; ++column)
	{
		const Frequency * fcolumn = frequencies.getRow(column);
		Score * pcolumn = profile.getRow(column);
		for (Residue a = 0; a < width; ++a)
		{
			Score w = 0;
			Frequency t = 0;
			for (Residue b = 0; b < width; ++b)
			{
				w += fcolumn[b] * mSubstitutionMatrix->getValue(a,b);
				t += fcolumn[b];
			}
			if (t > 0)
				pcolumn[a] = w / mScaleFactor;
			else
				pcolumn[a] = mMaskValue;
		}
	}
}




} // namespace alignlib
