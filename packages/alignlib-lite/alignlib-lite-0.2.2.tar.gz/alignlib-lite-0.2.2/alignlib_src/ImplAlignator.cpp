/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignator.cpp,v 1.3 2005/02/24 11:07:25 aheger Exp $

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

#include "Alignator.h"

#include "Alignment.h"
#include "HelpersAlignment.h"

#include "Alignandum.h"
#include "AlignlibException.h"

#include "Iterator2D.h"
#include "HelpersIterator2D.h"

#include "Scorer.h"
#include "HelpersScorer.h"

#include "ImplAlignator.h"

#include <math.h>

using namespace std;

namespace alignlib
{

  //----------------------------------------------------------------------------------------
  ImplAlignator::ImplAlignator() : Alignator()
    {
	  debug_func_cerr( 5 );
    }

  ImplAlignator::~ImplAlignator()

    {
      debug_func_cerr(5);
    }

  ImplAlignator::ImplAlignator( const ImplAlignator & src ) : Alignator(src),
  mIterator(src.mIterator)
  {
  }

  //-------------------------------------------------------------------------------------------------------------------------------
  void ImplAlignator::startUp( HAlignment & ali,
		  const HAlignandum & row, const HAlignandum & col )

    {
      debug_func_cerr(5);

      row->prepare();
      col->prepare();

      debug_cerr( 5, "starting alignment for row=" << row->getFrom() << "-" << row->getTo()
          << " col=" << col->getFrom() << "-" << col->getTo() );

      mRowLength = row->getLength();

      mIterator = getToolkit()->getIterator2D()->getNew( row, col );

      debug_cerr( 5, "setting iterator to ranges: row="
          << *mIterator->row_begin() << "-" <<  *mIterator->row_end() << ":" << mIterator->row_size() << " col="
          << *mIterator->col_begin() << "-" <<  *mIterator->col_end() << ":" << mIterator->col_size() );

      mScorer = getToolkit()->getScorer()->getNew( row, col );

      ali->clear();
    }

  void ImplAlignator::cleanUp( HAlignment & ali,
		  const HAlignandum & row, const HAlignandum & col )
    {
      debug_func_cerr(5);

      /* round score to integer. This will get rid
       of ???
       */
      ali->setScore( round(ali->getScore()) );

    }

} // namespace alignlib
