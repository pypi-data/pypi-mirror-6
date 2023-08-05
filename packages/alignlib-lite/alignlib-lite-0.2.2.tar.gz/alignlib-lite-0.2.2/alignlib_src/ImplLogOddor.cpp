/*
  alignlib - a library for aligning protein sequences

  $Id: ImplLogOddor.cpp,v 1.2 2004/01/07 14:35:35 aheger Exp $

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
#include "alignlib_fwd.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"

#include "Matrix.h"
#include "ImplLogOddor.h"
#include "HelpersLogOddor.h"

using namespace std;

namespace alignlib
{

//---------------------------------------------------------< factory functions >--------------------------------------
HLogOddor makeLogOddor( const Score & scale, const Score & mask_value )
{
	return HLogOddor( new ImplLogOddor( scale, mask_value ) );
}

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplLogOddor::ImplLogOddor ( const Score & scale_factor, const Score & mask_value) :
	mScaleFactor( scale_factor ), mMaskValue( mask_value )
	{
		debug_func_cerr( 5 );
	}

ImplLogOddor::~ImplLogOddor ()
{
	debug_func_cerr( 5 );
}

ImplLogOddor::ImplLogOddor (const ImplLogOddor & src ) :
	mScaleFactor (src.mScaleFactor ), mMaskValue( src.mMaskValue )
	{
	}

IMPLEMENT_CLONE( HLogOddor, ImplLogOddor );

//--------------------------------------------------------------------------------------------------------------------------------
void ImplLogOddor::fillProfile(
		ScoreMatrix & profile ,
		const FrequencyMatrix & frequencies,
		const HEncoder & encoder) const
{
	debug_func_cerr(5);

	assert( profile.getNumRows() == frequencies.getNumRows() );
	assert( profile.getNumCols() == frequencies.getNumCols() );

	// simply take the frequencies and use them as scores.
	// For frequencies of 0, mMaskValue is used.

	Position length = frequencies.getNumRows();
	Residue width  = frequencies.getNumCols();

	for (Position column = 0; column < length; column++)
	{
		const Frequency * fcolumn = frequencies.getRow(column);
		Score * pcolumn = profile.getRow(column);

		for (Residue i = 0; i < width; ++i)
		{
			Frequency f;
			if ((f = fcolumn[i]) > 0)
				pcolumn[i] = f;
			else
				pcolumn[i] = mMaskValue;
		}
	}
}

} // namespace alignlib








