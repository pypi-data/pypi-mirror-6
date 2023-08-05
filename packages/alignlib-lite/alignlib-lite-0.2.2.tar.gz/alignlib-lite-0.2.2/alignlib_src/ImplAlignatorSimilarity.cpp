/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignatorSimilarity.cpp,v 1.2 2004/01/07 14:35:34 aheger Exp $

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
#include "Alignandum.h"
#include "Alignment.h"
#include "Matrix.h"
#include "ImplAlignatorSimilarity.h"

#include "Iterator2D.h"
#include "Scorer.h"
#include "HelpersIterator2D.h"

using namespace std;

namespace alignlib
{

  HAlignator makeAlignatorSimilarity()
  {
    return HAlignator( new ImplAlignatorSimilarity() );
  }

  //---------------------------------------------------------< constructors and destructors >--------------------------------------
  ImplAlignatorSimilarity::ImplAlignatorSimilarity () : ImplAlignator()
  {
  }

  ImplAlignatorSimilarity::~ImplAlignatorSimilarity ()
  {
  }

  ImplAlignatorSimilarity::ImplAlignatorSimilarity (const ImplAlignatorSimilarity & src ) :
	  ImplAlignator(src)
  {
  }

  IMPLEMENT_CLONE( HAlignator, ImplAlignatorSimilarity );

  void ImplAlignatorSimilarity::align(
		  HAlignment & result,
		  const HAlignandum & row,
		  const HAlignandum & col)
  {

    startUp(result, row, col );

    Score score, total_score = 0;

    HIterator2D it2d(mIterator->getNew( row, col ));

    Iterator2D::const_iterator rit(it2d->row_begin()), rend(it2d->row_end());

    for (; rit != rend; ++rit)
      {
	Position r = *rit;

	Iterator2D::const_iterator cit(it2d->col_begin(r)), cend(it2d->col_end(r));
	for (; cit != cend; ++cit)
	  {
	    Position c = *cit;
	    if ( (score = mScorer->getScore( r, c ) > 0) )
	      {
		result->addPair( ResiduePair( r, c, score ));
		total_score += score;
	      }
	  }
      }

    result->setScore( total_score );

    cleanUp(result, row, col );
  }


} // namespace alignlib
