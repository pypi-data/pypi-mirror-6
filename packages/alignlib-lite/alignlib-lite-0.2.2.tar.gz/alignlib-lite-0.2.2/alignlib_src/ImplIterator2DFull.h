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

#ifndef ITERATOR2DFULL_H
#define ITERATOR2DFULL_H 1

#include "alignlib_fwd.h"
#include "ImplIterator2D.h"
namespace alignlib
{

  class Alignandum;

  class ImplIterator2DFull : public ImplIterator2D
    {
    public:

      /** empty constructor */
        ImplIterator2DFull();

        ImplIterator2DFull( const HAlignandum & row, const HAlignandum & col);

      /** destructor */
      virtual ~ImplIterator2DFull ();

      /** copy constructor */
      ImplIterator2DFull( const ImplIterator2DFull & src);

      DEFINE_CLONE( HIterator2D );

      /** return a new iterator of same type initializes with for row and col
       */
      virtual HIterator2D getNew(
    		  const HAlignandum & row,
    		  const HAlignandum & col ) const;

      /** reset ranges of iterator for new row and col objects
       */
      virtual void resetRanges(
    		  const HAlignandum & row,
    		  const HAlignandum & col );

      /** return iterators for rows/columns */
      virtual const_iterator row_begin ( Position col = 0 ) const;
      virtual const_iterator row_end   ( Position col = 0 ) const;
      virtual const_iterator col_begin ( Position row = 0 ) const;
      virtual const_iterator col_end   ( Position row = 0 ) const;

      /** return first/last residues in rows/columns */
      virtual Position row_front ( Position col = 0) const;
      virtual Position row_back  ( Position col = 0) const;
      virtual Position col_front ( Position row = 0) const;
      virtual Position col_back  ( Position row = 0) const;

      /** return extreme coordinates. If no row/col is given, return maximum extension */
      virtual Position row_size( Position col = 0) const;
      virtual Position col_size( Position row = 0) const;
    };
}

#endif /* ITERATOR2D_H */
