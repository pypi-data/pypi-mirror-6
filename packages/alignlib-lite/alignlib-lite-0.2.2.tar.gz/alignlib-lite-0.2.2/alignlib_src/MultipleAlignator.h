/*
  alignlib - a library for aligning protein sequences

  $Id$

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

#ifndef MULTIPLEALIGNATOR_H
#define MULTIPLEALIGNATOR_H 1

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

  /**
       @short Protocol class for objects that perform multiple alignment.

	   MultipleAlignator objects align multiple @ref Alignandum objects. The default way to use it

       @code
 	   HAlignandumVector sequences();
	   sequences->push_back( makeSomeAlignandumObject(...));
	   sequences->push_back( makeSomeAlignandumObject(...));
	   sequences->push_back( makeSomeAlignandumObject(...));
       HAlignator a( makeSomeAlignator(...) );
       HMultipleAlignment r( makeSomeMultipleAlignment(...) );

       a->align( r, sequences );
	   @endcode

       This class is a protocol class and as such defines only the interface.

       @author Andreas Heger
       @version $Id$
       @see Alignandum
       @see Alignment
  */
  class MultipleAlignator : public virtual AlignlibBase
    {
      /* class member functions-------------------------------------------------------------- */

    public:
      /* constructors and desctructors------------------------------------------------------- */

      /** empty constructor */
      MultipleAlignator();

      /** destructor */
      virtual ~MultipleAlignator ();

      /** copy constructor */
      MultipleAlignator( const MultipleAlignator & src);

      DEFINE_ABSTRACT_CLONE( HMultipleAlignator )

      /** align @ref Alignandum objects and store result in @ref Alignment
       *
       * @param dest	@ref MultAligment object to store the alignment result.
       * @param sequences	@ref Alignandum object to align.
      */
      virtual void align(
    		  HMultAlignment & dest,
    		  const HAlignandumVector & sequences ) const = 0;

      /** align @ref strings and store result in @ref Alignment
       *
       * The strings are converted to @ref Alignandum object using
       * makeSequence() and the default @ref Encoder.
       *
       * @param dest	@ref MultAligment object to store the alignment result.
       * @param sequences strings to align.
      */
      virtual void align(
    		  HMultAlignment & dest,
    		  const HStringVector & sequences ) const = 0;

      /* accessors */

    };
}

#endif /* ALIGNATOR_H */
