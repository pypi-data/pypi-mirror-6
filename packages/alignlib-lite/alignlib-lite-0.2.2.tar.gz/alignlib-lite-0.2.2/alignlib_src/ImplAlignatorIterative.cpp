/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignatorIterative.cpp,v 1.2 2004/01/07 14:35:34 aheger Exp $

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
#include "Alignandum.h"

#include "Alignator.h"

#include "Alignment.h"
#include "HelpersAlignment.h"
#include "HelpersToolkit.h"

#include "ImplAlignatorIterative.h"

using namespace std;

namespace alignlib
{

  HAlignator makeAlignatorIterative(
		  const HAlignator & alignator,
		  Score min_score )
  {
    return HAlignator(new ImplAlignatorIterative( alignator, min_score ));
  }

  //---------------------------------------------------------< constructors and destructors >--------------------------------------
  ImplAlignatorIterative::ImplAlignatorIterative () :
	  ImplAlignator(), mMinScore( 0 ), mAlignator(getToolkit()->getAlignator())
  {
  }

  ImplAlignatorIterative::ImplAlignatorIterative ( const HAlignator & alignator, Score min_score) :
	  ImplAlignator(), mMinScore( min_score ),
  	  mAlignator ( alignator->getClone() )
  {
  }

  ImplAlignatorIterative::~ImplAlignatorIterative ()
  {
  }

  ImplAlignatorIterative::ImplAlignatorIterative (const ImplAlignatorIterative & src ) :
    ImplAlignator(src), mMinScore( src.mMinScore), mAlignator(src.mAlignator->getClone())
  {
  }

  IMPLEMENT_CLONE( HAlignator, ImplAlignatorIterative )

  void ImplAlignatorIterative::align(
		  HAlignment & result,
		  const HAlignandum & row,
		  const HAlignandum & col )
  {
      debug_func_cerr(5);

      startUp(result, row, col );

     /* since src1 and src2 are const, I have to create two work-copies,
        so that the boundaries can be changed. */

      HAlignandum copy_row(row->getClone());
      HAlignandum copy_col(col->getClone());

      // start aligning by calling recursively performIterativeAlignmentStep
      alignIteratively( result, copy_row, copy_col );

      cleanUp( result, row, col );
  }

  void ImplAlignatorIterative::alignIteratively(
		  	HAlignment & dest,
  			const HAlignandum & row,
  			const HAlignandum & col )
  {
    debug_func_cerr(5);

    // do alignment with current boundaries of the objects, but remember them
    Position from_1 = row->getFrom();
    Position from_2 = col->getFrom();

    Position to_1 = row->getTo();
    Position to_2 = col->getTo();

    debug_cerr(5, "aligning in regions (" << from_1 << "-" << to_1 <<") -> (" << from_2 << "-" << to_2 << ")" );

    if (from_1 > to_1 || from_2 > to_2)
      return;

    HAlignment result(dest->getNew());

    mAlignator->align( result, row, col );

    if (result->getScore() > mMinScore)
    {

        addAlignment2Alignment( dest, result );

        debug_cerr( 5, "new alignment\n" << *result )
        debug_cerr( 5, "new alignment coordinates: row=" << result->getRowFrom() << " " << result->getRowTo()
      		  	<< " col=" << result->getColFrom() << " " << result->getColTo() );
        debug_cerr( 5, "current alignment\n" << *result )

        Position from_1_result = result->getRowFrom();
        Position from_2_result = result->getColFrom();
        Position to_1_result   = result->getRowTo();
        Position to_2_result   = result->getColTo();

        // align in region before current alignment
        row->useSegment( from_1, from_1_result);
        col->useSegment( from_2, from_2_result);
        alignIteratively( dest, row, col );

        // align in region after current alignment
        row->useSegment( to_1_result, to_1);
        col->useSegment( to_2_result, to_2);

        alignIteratively( dest, row, col );

    }
  }



} // namespace alignlib
