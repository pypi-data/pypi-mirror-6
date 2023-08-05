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

#ifndef FRAGMENTOR_H
#define FRAGMENTOR_H 1

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

/**
   @short Protocoll class for alignment generators.

   Fragmentors repeatedly apply an @ref Alignator to @ref Alignandum objects.
   In contrast to @ref Alignator objects, these objects will return a list of
   @ref Alignment objects, and not a single @ref Alignment.

   @author Andreas Heger
   @version $Id: Fragmentor.h,v 1.3 2004/03/19 18:23:40 aheger Exp $
*/

class Fragmentor : public virtual AlignlibBase
{
  /* class member functions-------------------------------------------------------------- */
 public:
    /* constructors and desctructors------------------------------------------------------- */
    /** empty constructor */
    Fragmentor();

    /** destructor */
    virtual ~Fragmentor ();

    /** copy constructor */
    Fragmentor( const Fragmentor & src);

    DEFINE_ABSTRACT_CLONE( HFragmentor )

    /** method for aligning two arbitrary objects
     * @param dest 	@ref Alignment object in which to store data.
     * @param row	@ref Alignandum object to use.
     * @param col	@ref Alignandum object to use.*/
    virtual HFragmentVector fragment(
    		HAlignment & dest,
    		const HAlignandum & row,
    		const HAlignandum & col ) = 0;

};

}

#endif /* FRAGMENTOR_H */


