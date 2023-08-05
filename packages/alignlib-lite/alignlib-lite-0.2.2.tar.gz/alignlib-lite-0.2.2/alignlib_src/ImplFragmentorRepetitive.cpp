/*
  alignlib - a library for aligning protein sequences

  $Id: ImplFragmentorRepetitive.cpp,v 1.2 2004/01/07 14:35:35 aheger Exp $

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
#include "AlignlibDebug.h"

#include "Fragmentor.h"

#include "Alignment.h"
#include "HelpersAlignment.h"

#include "AlignmentIterator.h"

#include "Alignandum.h"
#include "AlignlibException.h"

#include "HelpersSubstitutionMatrix.h"

#include "Alignator.h"
#include "HelpersAlignator.h"

#include "HelpersToolkit.h"

#include "ImplFragmentorRepetitive.h"

using namespace std;

namespace alignlib
{

/*---------------------factory functions ---------------------------------- */

  /** make an alignator object, which does a dot-alignment. The default version can be given an AlignmentMatrix-
      object */
HFragmentor makeFragmentorRepetitive( const HAlignator & alignator, Score min_score )
{
  return HFragmentor( new ImplFragmentorRepetitive( alignator, min_score ) );
}


//----------------------------------------------------------------------------------------------------

ImplFragmentorRepetitive::ImplFragmentorRepetitive() :
	ImplFragmentor(),
	  mAlignator( getToolkit()->getAlignator() ),
	  mMinScore(0)
	  {}


ImplFragmentorRepetitive::ImplFragmentorRepetitive(
		const HAlignator & alignator,
		Score min_score ):
  ImplFragmentor(),
  mAlignator( alignator ),
  mMinScore( min_score)
  {
}


ImplFragmentorRepetitive::~ImplFragmentorRepetitive()
{
  debug_func_cerr(5);

}

IMPLEMENT_CLONE( HFragmentor, ImplFragmentorRepetitive);

ImplFragmentorRepetitive::ImplFragmentorRepetitive( const ImplFragmentorRepetitive & src ) :
    ImplFragmentor(src),
    mAlignator(src.mAlignator),
    mMinScore( src.mMinScore ) {
}

//------------------------------------------------------------------------------------------------
void ImplFragmentorRepetitive::performFragmentation(
		const HAlignment & sample,
		const HAlignandum & row,
		const HAlignandum & col )
{

  /* since src1 and src2 are const, I have to create two work-copies,
     so that the boundaries can be changed. */

  HAlignandum copy_row(row->getClone());
  HAlignandum copy_col(col->getClone());

  while ( 1 ) {

    HAlignment result = sample->getNew();
    mAlignator->align( result, copy_row, copy_col );

    if (result->getScore() >= mMinScore)
    {
      mFragments->push_back( result );
      copy_row->mask( result->getRowFrom(), result->getRowTo() );
      copy_col->mask( result->getColFrom(), result->getColTo() );

    } else
    {
      break;
    }
  }
}


} // namespace alignlib




