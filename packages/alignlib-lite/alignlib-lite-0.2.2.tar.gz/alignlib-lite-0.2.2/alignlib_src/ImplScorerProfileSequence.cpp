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
#include "ImplSequence.h"
#include "ImplProfile.h"
#include "ImplScorerProfileSequence.h"

using namespace std;

namespace alignlib
{

  // factory function for creating iterator over full matrix
  HScorer makeScorerProfileSequence(
		  const HProfile & row,
		  const HSequence & col )
  {
    return HScorer( new ImplScorerProfileSequence( row, col ) );
  }

  //--------------------------------------------------------------------------------------
  ImplScorerProfileSequence::ImplScorerProfileSequence() :
	  ImplScorer(), mRowProfile(NULL), mColSequence(NULL)
  {
  }
  //--------------------------------------------------------------------------------------
  ImplScorerProfileSequence::ImplScorerProfileSequence(
		  const HProfile & row,
		  const HSequence & col ) :
    ImplScorer( row, col )
  {
    const HImplProfile s1 = boost::dynamic_pointer_cast<ImplProfile, Profile>(row);
    const HImplSequence s2 = boost::dynamic_pointer_cast<ImplSequence, Sequence>(col);

    mRowProfile  = s1->exportScoreMatrix();
    mColSequence = s2->getSequence();

    mProfileWidth = s1->getToolkit()->getEncoder()->getAlphabetSize();

    if ( mProfileWidth != s2->getToolkit()->getEncoder()->getAlphabetSize() )
    	throw AlignlibException( "ImplScorerProfileSequence.cpp: alphabet size different in row and col");

  }

  //--------------------------------------------------------------------------------------
  ImplScorerProfileSequence::~ImplScorerProfileSequence ()
  {
  }

  //--------------------------------------------------------------------------------------
  ImplScorerProfileSequence::ImplScorerProfileSequence(const ImplScorerProfileSequence & src) :
    ImplScorer(src),
    mRowProfile( src.mRowProfile ),
    mColSequence( src.mColSequence ),
    mProfileWidth( src.mProfileWidth )
  {
  }

  IMPLEMENT_CLONE( HScorer, ImplScorerProfileSequence );

  /** return a new instance of this object initialized with row and col
   */
  HScorer ImplScorerProfileSequence::getNew(
		  const HAlignandum & row,
		  const HAlignandum & col) const
  {
	  const HProfile s1 = boost::dynamic_pointer_cast<Profile, Alignandum>(row);
	  const HSequence s2 = boost::dynamic_pointer_cast<Sequence, Alignandum>(col);

	  assert( s1 );
	  assert( s2 );

	  return HScorer( new ImplScorerProfileSequence( s1, s2 ) ) ;
  }

  /** return score of matching row to col
   */
  Score ImplScorerProfileSequence::getScore(
		  const Position & row,
		  const Position & col ) const
  {
	  return mRowProfile->getValue( row, (*mColSequence)[col] );
  }

}


