/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignator.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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

#ifndef IMPL_ALIGNATOR_H
#define IMPL_ALIGNATOR_H 1

#include "alignlib_fwd.h"
#include "Alignator.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{
  /**
     @short base implementation class for Alignator objects.

     This class implements some common behaviour of Alignator
     objects.

     @author Andreas Heger
     @version $Id: ImplAlignator.h,v 1.3 2004/03/19 18:23:40 aheger Exp $
  */

  class ImplAlignator : public Alignator, public ImplAlignlibBase
    {
      /* class member functions-------------------------------------------------------------- */
    public:
      /* constructors and desctructors------------------------------------------------------- */
      /** constructor */
      ImplAlignator();

      /** destructor */
      virtual ~ImplAlignator ();

      /** copy constructor */
      ImplAlignator( const ImplAlignator & src);

    protected:

        /** perform initialisation before alignment. Overload, but call this function in subclasses! */
        virtual void startUp( HAlignment & ali,
      		  const HAlignandum & row, const HAlignandum & col);

        /** perform cleanup after alignment */
        virtual void cleanUp( HAlignment & ali,
      		  const HAlignandum & row, const HAlignandum & col );

    protected:
      /** object for iteration over sequences */
      HIterator2D mIterator;

      /** object for scoring sequence/profile positions */
      HScorer mScorer;

      /** length of row */
      int mRowLength;

    };

}

#endif /* ALIGNATOR_H */
