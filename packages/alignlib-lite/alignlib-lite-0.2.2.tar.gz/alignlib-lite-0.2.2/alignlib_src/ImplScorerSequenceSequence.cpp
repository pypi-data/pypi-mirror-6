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
#include <cassert>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "Alignandum.h"
#include "Encoder.h"
#include "Matrix.h"
#include "ImplScorerSequenceSequence.h"
#include "ImplSequence.h"
#include "HelpersSubstitutionMatrix.h"

using namespace std;

namespace alignlib
{

  // factory function for creating iterator over full matrix
  HScorer makeScorerSequenceSequence(
		  const HSequence & row,
		  const HSequence & col,
		  const HSubstitutionMatrix & matrix )
  {
    return HScorer( new ImplScorerSequenceSequence( row, col, matrix ) );
  }

  //--------------------------------------------------------------------------------------
  ImplScorerSequenceSequence::ImplScorerSequenceSequence(
		  const HSequence & row,
		  const HSequence & col,
		  const HSubstitutionMatrix & matrix) :
    ImplScorer( row, col )
  {

	const HImplSequence s1(boost::dynamic_pointer_cast< ImplSequence, Sequence>(row));
	const HImplSequence s2(boost::dynamic_pointer_cast< ImplSequence, Sequence>(col));

    mRowSequence = s1->getSequence();
    mColSequence = s2->getSequence();

    mSubstitutionMatrix = matrix;

    if ( mSubstitutionMatrix->getNumRows() < row->getToolkit()->getEncoder()->getAlphabetSize() )
    	throw AlignlibException( "ImplScorerSequenceSequence.cpp: alphabet size in substitution matrix too small for row");

    if ( mSubstitutionMatrix->getNumCols() < col->getToolkit()->getEncoder()->getAlphabetSize() )
    	throw AlignlibException( "ImplScorerSequenceSequence.cpp: alphabet size in substitution matrix too small for col");

  }


	ImplScorerSequenceSequence::ImplScorerSequenceSequence() :
		ImplScorer()
		{
			mSubstitutionMatrix = getToolkit()->getSubstitutionMatrix();
		}


  //--------------------------------------------------------------------------------------
  ImplScorerSequenceSequence::~ImplScorerSequenceSequence ()
  {
  }

  //--------------------------------------------------------------------------------------
  ImplScorerSequenceSequence::ImplScorerSequenceSequence(const ImplScorerSequenceSequence & src) :
    ImplScorer(src ),
    mRowSequence( src.mRowSequence ), mColSequence( src.mColSequence ),
    mSubstitutionMatrix( src.mSubstitutionMatrix )
  {
  }

  IMPLEMENT_CLONE( HScorer, ImplScorerSequenceSequence );

  /** return a new instance of this object initialized with row and col
   */
  HScorer ImplScorerSequenceSequence::getNew(
		  const HAlignandum & row,
		  const HAlignandum & col) const
  {
	  debug_func_cerr( 5 );

	  const HSequence s1(boost::dynamic_pointer_cast< Sequence, Alignandum>(row));
	  const HSequence s2(boost::dynamic_pointer_cast< Sequence, Alignandum>(col));

	  assert( s1 );
	  assert( s2 );

	  return HScorer( new ImplScorerSequenceSequence( s1, s2, mSubstitutionMatrix ) );
  }

  /** return score of matching row to col
   */
  Score ImplScorerSequenceSequence::getScore(
		  const Position & row,
		  const Position & col ) const
  {
    assert( row >= 0);
    assert( col >= 0);
    return mSubstitutionMatrix->getValue((*mRowSequence)[row],(*mColSequence)[col]);
  }

}


