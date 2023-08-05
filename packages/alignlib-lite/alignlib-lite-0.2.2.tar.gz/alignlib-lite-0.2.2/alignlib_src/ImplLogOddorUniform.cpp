/*
  alignlib - a library for aligning protein sequences

  $Id: ImplLogOddorUniform.cpp,v 1.2 2004/01/07 14:35:35 aheger Exp $

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

// Actually this is a bit misleading, there is no new class here, just the data
// and the implementation of a factory function.

#include <math.h>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "alignlib_fwd.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "ImplLogOddorUniform.h"
#include "Matrix.h"

namespace alignlib
{

//---------------------------------------------------------< factory functions >--------------------------------------
HLogOddor makeLogOddorUniform( const Score & scale, const Score & mask_value )
{
	return HLogOddor( new ImplLogOddorUniform( scale, mask_value ) );
}

IMPLEMENT_CLONE( HLogOddor, ImplLogOddorUniform );
//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplLogOddorUniform::ImplLogOddorUniform ( const Score & scale_factor, const Score & mask_value ) :
	ImplLogOddor( scale_factor, mask_value )
	{
	}

ImplLogOddorUniform::~ImplLogOddorUniform ()
{
}

ImplLogOddorUniform::ImplLogOddorUniform (const ImplLogOddorUniform & src ) :
	ImplLogOddor( src )
	{
	}

//--------------------------------------------------------------------------------------------------------------------------------
void ImplLogOddorUniform::fillProfile(
		ScoreMatrix & profile ,
		const FrequencyMatrix & frequencies,
		const HEncoder & encoder) const
{
	debug_func_cerr(5);

	// simply take the frequencies and divide by Uniform-frequencies and take log.
	// For frequencies of 0, MASK_VALUE is used.
	Position length = frequencies.getNumRows();
	Residue width  = frequencies.getNumCols();

	double background = 1.0 / double(width);

	for (Position column = 0; column < length; column++)
	{
		const Frequency * fcolumn = frequencies.getRow(column);
		Score * pcolumn = profile.getRow(column);
		for (Residue i = 0; i < width; ++i)
		{
			Frequency f = 0;
			if ((f = fcolumn[i]) > 0)
				pcolumn[i] = log(f / background) / mScaleFactor;
			else
				pcolumn[i] = mMaskValue;
		}
	}
}



} // namespace alignlib
