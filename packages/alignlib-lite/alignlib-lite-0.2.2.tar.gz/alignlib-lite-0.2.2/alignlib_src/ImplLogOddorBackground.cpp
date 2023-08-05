/*
  alignlib - a library for aligning protein sequences

  $Id: ImplLogOddorBackground.cpp,v 1.2 2004/01/07 14:35:35 aheger Exp $

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
#include <iterator>
#include <math.h>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibException.h"
#include "AlignlibDebug.h"
#include "ImplLogOddorBackground.h"
#include "HelpersLogOddor.h"
#include "HelpersEncoder.h"
#include "Matrix.h"

using namespace std;

namespace alignlib
{

//---------------------------------------------------------< factory functions >--------------------------------------
HLogOddor makeLogOddorBackground(
		const HFrequencyVector & frequencies,
		const std::string & alphabet,
		const Score & scale,
		const Score & mask_value )
{
	return HLogOddor(new ImplLogOddorBackground( frequencies, alphabet,
			scale, mask_value ));
}

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplLogOddorBackground::ImplLogOddorBackground (
		const HFrequencyVector & frequencies,
		const std::string & alphabet,
		const Score & scale_factor,
		const Score & mask_value ) :
	ImplLogOddor( scale_factor, mask_value ),
	mBackgroundFrequencies( frequencies ),
	mAlphabet( alphabet )
{
	debug_func_cerr(5);

#ifdef DEBUG
	debug_cerr( 5, "background frequencies for alphabet " << mAlphabet );
	if (AlignlibDebug::mVerbosity >= 5)
	{
		std::copy( mBackgroundFrequencies->begin(),
				mBackgroundFrequencies->end(),
				std::ostream_iterator<Score>(std::cerr, ",") );
		std::cerr << std::endl;
	}
#endif

	if (mAlphabet.size() != mBackgroundFrequencies->size())
		throw AlignlibException("ImplLogOddorBackground.cpp: alphabet and frequency vector have different sizes.");
}

ImplLogOddorBackground::ImplLogOddorBackground (
		const Score & scale_factor,
		const Score & mask_value ) :
			ImplLogOddor( scale_factor, mask_value )
{
	mAlphabet = getToolkit()->getEncoder()->getAlphabet();
	mBackgroundFrequencies = HFrequencyVector( new FrequencyVector( mAlphabet.size(), 1.0 / mAlphabet.size()));
}

ImplLogOddorBackground::~ImplLogOddorBackground ()
{
}

ImplLogOddorBackground::ImplLogOddorBackground (const ImplLogOddorBackground & src ) :
	ImplLogOddor( src ),
	mBackgroundFrequencies( src.mBackgroundFrequencies ),
	mAlphabet( src.mAlphabet )
	{
	}

IMPLEMENT_CLONE( HLogOddor, ImplLogOddorBackground );

//--------------------------------------------------------------------------------------------------------------------------------
void ImplLogOddorBackground::fillProfile(
		ScoreMatrix & profile ,
		const FrequencyMatrix & frequencies,
		const HEncoder & encoder ) const
		{
	debug_func_cerr(5);

	// simply take the frequencies and divide by background-frequencies and take log.
	// For frequencies of 0, MASK_VALUE is used.
	Position length = frequencies.getNumRows();
	Residue width   = frequencies.getNumCols();

	FrequencyVector & bg = *mBackgroundFrequencies;

	// build map of residues to positions
	HResidueVector map_alphabet2code = encoder->getMap( mAlphabet );

	// check if alphabet and background are congruent
	assert( map_alphabet2code->size() == bg.size() );

	Residue gap_code = encoder->getGapCode();
#ifdef DEBUG
	if (AlignlibDebug::mVerbosity >= 5)
	{
		debug_cerr( 5, "background frequencies");
		std::copy( bg.begin(), bg.end(), std::ostream_iterator<Score>(std::cerr, ",") );
		std::cerr << std::endl;
	}
#endif

	for (Position column = 0; column < length; column++)
	{
		const Frequency * fcolumn = frequencies.getRow(column);
		Score * pcolumn = profile.getRow(column);

		// mask all undefined chars and with 0 frequency
		for (Residue x = 0; x < width; ++x)
			pcolumn[x] = mMaskValue;

		for (Residue i = 0; i < bg.size(); ++i)
		{
			Residue x = (*map_alphabet2code)[i];
			if (x == gap_code)
				continue;
			Frequency f = fcolumn[x];
			if (f > 0)
				pcolumn[x] = log(f / bg[i]) / mScaleFactor;
		}
	}
		}

} // namespace alignlib








