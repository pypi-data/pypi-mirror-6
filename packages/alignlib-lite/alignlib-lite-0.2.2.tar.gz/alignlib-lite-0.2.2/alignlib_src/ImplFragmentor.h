/*
  alignlib - a library for aligning protein sequences

  $Id: ImplFragmentor.h,v 1.3 2004/03/19 18:23:41 aheger Exp $

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

#ifndef IMPL_FRAGMENTOR_H
#define IMPL_FRAGMENTOR_H 1

#include "alignlib_fwd.h"
#include "Fragmentor.h"
#include "Alignment.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{


/**
   @short Basic implementation class for Fragmentor objects.

   Fragmentors repeatedly apply an @ref Alignator to @ref Alignandum objects and
   return a list of fragments.

   @author Andreas Heger
   @version $Id: ImplFragmentor.h,v 1.3 2004/03/19 18:23:41 aheger Exp $
*/
class ImplFragmentor : public Fragmentor, public ImplAlignlibBase
{
  /* class member functions-------------------------------------------------------------- */
 public:
    /* constructors and desctructors------------------------------------------------------- */
    /** constructor */
    ImplFragmentor();

    /** destructor */
    virtual ~ImplFragmentor ();

    /** copy constructor */
    ImplFragmentor( const ImplFragmentor & src);

    virtual HFragmentVector fragment(
    		HAlignment & dest,
    		const HAlignandum & row,
    		const HAlignandum & col );

 protected:
    /** get length of row object */
    Position getRowLength();

    /** get length of col */
    Position getColLength();

    /** perform initialisation before alignment. Overload, but call this function in subclasses! */
    virtual void startUp( HAlignment & dest,
    					const HAlignandum & row,
    					const HAlignandum & col );

    /** perform cleanup after alignment */
    virtual void cleanUp( HAlignment & dest, const HAlignandum & row, const HAlignandum & col );

    /* perform the actual alignment */
    virtual void performFragmentation(
    		const HAlignment & dest,
    		const HAlignandum & row,
    		const HAlignandum & col ) = 0;

    /** length of object in row */
    Position mRowLength;
    /** length of object in col */
    Position mColLength;

    /** result */
    HFragmentVector mFragments;
};

}

#endif /* FRAGMENTOR_H */



