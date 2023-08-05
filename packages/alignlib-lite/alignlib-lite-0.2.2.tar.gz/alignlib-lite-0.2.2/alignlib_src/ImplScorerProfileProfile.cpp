/*
  alignlib - a library for aligning protein sequences

  $Id: Iterator2D.cpp,v 1.2 2004/01/07 14:35:32 aheger Exp $

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
#include "AlignlibException.h"
#include "AlignlibDebug.h"
#include "Alignandum.h"
#include "Encoder.h"
#include "Toolkit.h"
#include "ImplProfile.h"
#include "ImplScorerProfileProfile.h"

using namespace std;

namespace alignlib
{

  // factory function for creating iterator over full matrix
  Scorer * makeScorerProfileProfile(
		  const HProfile & row,
		  const HProfile & col )
  {
    return new ImplScorerProfileProfile( row, col );
  }

  //--------------------------------------------------------------------------------------
  ImplScorerProfileProfile::ImplScorerProfileProfile() :
	  ImplScorer(), mRowProfile(NULL), mColProfile(NULL)
	  {}

  //--------------------------------------------------------------------------------------
  ImplScorerProfileProfile::ImplScorerProfileProfile(
		  const HProfile & row,
		  const HProfile & col ) :
    ImplScorer( row, col )
  {
	debug_func_cerr( 5 );

    const HImplProfile s1 = boost::dynamic_pointer_cast<ImplProfile, Profile>(row);
    const HImplProfile s2 = boost::dynamic_pointer_cast<ImplProfile, Profile>(col);

    if (!s1)
      throw AlignlibException( "ImplScoreProfileProfile.cpp: row not a profile.");

    if (!s2)
      throw AlignlibException( "ImplScoreProfileProfile.cpp: col not a profile.");

    mRowProfile     = s1->exportScoreMatrix();
    mRowFrequencies = s1->exportFrequencyMatrix();

    mColProfile     = s2->exportScoreMatrix();
    mColFrequencies = s2->exportFrequencyMatrix();

    if ( s1->getToolkit()->getEncoder()->getAlphabetSize() !=
    	s2->getToolkit()->getEncoder()->getAlphabetSize() )
    	throw AlignlibException( "ImplScorerProfileProfile.cpp: alphabet size different in row and col");

    mProfileWidth = s1->getToolkit()->getEncoder()->getAlphabetSize();
  }

  //--------------------------------------------------------------------------------------
  ImplScorerProfileProfile::~ImplScorerProfileProfile ()
  {
  }

  //--------------------------------------------------------------------------------------
  ImplScorerProfileProfile::ImplScorerProfileProfile(const ImplScorerProfileProfile & src) :
    ImplScorer(src),
    mRowProfile( src.mRowProfile ), mRowFrequencies( src.mRowFrequencies ),
    mColProfile( src.mColProfile ), mColFrequencies( src.mColFrequencies ),
    mProfileWidth( src.mProfileWidth )
  {
  }

  IMPLEMENT_CLONE( HScorer, ImplScorerProfileProfile );

  /** return a new instance of this object initialized with row and col
   */
  HScorer ImplScorerProfileProfile::getNew(
		  const HAlignandum & row,
		  const HAlignandum & col) const
  {
	  debug_func_cerr( 5 );
	  const HProfile s1 = boost::dynamic_pointer_cast<Profile, Alignandum>(row);
	  const HProfile s2 = boost::dynamic_pointer_cast<Profile, Alignandum>(col);

	  assert( s1 );
	  assert( s2 );

	  return HScorer( new ImplScorerProfileProfile( s1, s2 ) );
  }

  /** return score of matching row to col
   */
  Score ImplScorerProfileProfile::getScore(
		  const Position & row,
		  const Position & col ) const
  {
	  Score score = 0;
	  const Score * profile_row = mRowProfile->getRow( row );
	  const Score * profile_col = mColProfile->getRow( col );
	  const Frequency * frequency_row = mRowFrequencies->getRow( row );
	  const Frequency * frequency_col = mColFrequencies->getRow( col );

	  for (int i = 0; i < mProfileWidth; i++ )
		  score +=	profile_row[i] * frequency_col[i] +
      		profile_col[i] * frequency_row[i];

	  return score;
  }

}


