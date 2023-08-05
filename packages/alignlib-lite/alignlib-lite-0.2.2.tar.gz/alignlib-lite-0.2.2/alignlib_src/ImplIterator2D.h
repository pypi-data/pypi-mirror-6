/*
  alignlib - a library for aligning protein sequences

  $Id: Fragmentor.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef IMPLITERATOR2D_H
#define IMPLITERATOR2D_H 1

#include "alignlib_fwd.h"

#include "Iterator2D.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{

  class ImplIterator2D : public Iterator2D, public ImplAlignlibBase
    {
    public:

      /** empty constructor */
      ImplIterator2D();
      ImplIterator2D( const HAlignandum & row, const HAlignandum & col);

      /** destructor */
      virtual ~ImplIterator2D ();

      /** copy constructor */
      ImplIterator2D( const ImplIterator2D & src);

      /** reset ranges of iterator for new row and col objects
       */
      virtual void resetRanges( const HAlignandum & row, const HAlignandum & col );

      /** return iterators for rows/columns */
      virtual const_iterator row_begin ( Position col = NO_POS) const;
      virtual const_iterator row_end   ( Position col = NO_POS) const;
      virtual const_iterator col_begin ( Position row = NO_POS) const;
      virtual const_iterator col_end   ( Position row = NO_POS) const;

      /** return first/last residues in rows/columns */
      virtual Position row_front ( Position col = NO_POS) const = 0;
      virtual Position row_back  ( Position col = NO_POS) const = 0;
      virtual Position col_front ( Position row = NO_POS) const = 0;
      virtual Position col_back  ( Position row = NO_POS) const = 0;

      /** return extreme coordinates. If no row/col is given, return maximum extension */
      virtual Position row_size( Position col = NO_POS) const;
      virtual Position col_size( Position row = NO_POS) const;

    protected:
      Position mRowFrom;
      Position mRowTo;
      Position mColFrom;
      Position mColTo;
    };
}

#endif /* ITERATOR2D_H */
