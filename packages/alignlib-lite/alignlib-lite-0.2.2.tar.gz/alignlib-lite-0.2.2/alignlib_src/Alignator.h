/*
  alignlib - a library for aligning protein sequences

  $Id: Alignator.h,v 1.3 2004/03/19 18:23:39 aheger Exp $

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

#ifndef ALIGNATOR_H
#define ALIGNATOR_H 1

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

  /**
       @short Protocol class for objects that align.

       Alignator objects align two objects. The default way to use it

       @code
       HAlignandum row( makeSomeAlignandumObject(...));
       HAlignandum col( makeSomeAlignandumObject(...));
       HAlignator a( makeSomeAlignator(...) );
       HAlignment r( makeSomeAlignment(...) );

       a->align( r, row, col);
	   @endcode

       The two objects to be aligned to each other are called row and col. This
       is inspired by the dynamic programming matrix where you have one sequence
       along the rows and the other along the columns of the matrix. Alignator objects
       need not necessarily perform dynamic programming.

	   The range of the sequences to be aligned is given by the
	   @ref Iterator2D object and the @ref Alignandum objects. The @Iterator2D
	   object determines the shape of the "alignment space", while the
	   @ref Alignandum objects determine the size of the "alignment space".
	   (In terms of dynamic programming, the "alignment space" is the size and
	   shape of the dynamic programming matrix.)

	   The @ref Scorer object takes care of computing alignment scores between
	   the positions in the two @ref Alignandum objects. The scorer object is
	   instantiated from a template with the two @ref Alignandum objects as paramters.
	   Based on the type of these objects the @ref Scorer object configures itself.
	   As a side effect, the default @ref SubstitutionMatrix will be used for sequence-
	   sequence alignment.

       This class is a protocol class and as such defines only the interface.

       @author Andreas Heger
       @version $Id: Alignator.h,v 1.3 2004/03/19 18:23:39 aheger Exp $
       @see Iterator2D
       @see Alignandum
       @see Alignment
  */
  class Alignator : public virtual AlignlibBase
    {
      /* class member functions-------------------------------------------------------------- */

    public:
      /* constructors and desctructors------------------------------------------------------- */

      /** empty constructor */
      Alignator();

      /** destructor */
      virtual ~Alignator ();

      /** copy constructor */
      Alignator( const Alignator & src);

      DEFINE_ABSTRACT_CLONE( HAlignator )

      /** align two @ref Alignandum objects and store result in @ref Alignment
       *
       * @param dest	@ref Aligment object to store the alignment result.
       * @param row		@ref Alignandum object to align.
       * @param col		@ref Alignandum object to align.
      */
      virtual void align(HAlignment & dest,
    		  const HAlignandum & row,
    		  const HAlignandum & col) = 0;

      /* accessors */

    };
}

#endif /* ALIGNATOR_H */
