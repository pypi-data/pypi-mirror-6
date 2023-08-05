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

#ifndef IMPL_MULTIPLEALIGNATOR_H
#define IMPL_MULTIPLEALIGNATOR_H 1

#include "alignlib_fwd.h"
#include "MultipleAlignator.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{
  /**
     @short base implementation class for MultipleAlignator objects.

     This class implements some common behaviour of MultipleAlignator
     objects.

     @author Andreas Heger
     @version $Id$
  */

  class ImplMultipleAlignator : public MultipleAlignator, public ImplAlignlibBase
    {
      /* class member functions-------------------------------------------------------------- */
    public:
      /* constructors and desctructors------------------------------------------------------- */
      /** constructor */
      ImplMultipleAlignator();

      /** destructor */
      virtual ~ImplMultipleAlignator();

      /** copy constructor */
      ImplMultipleAlignator( const ImplMultipleAlignator & src);

      /** align @ref Alignandum objects and store result in @ref Alignment
       *
       * @param dest	@ref MultAligment object to store the alignment result.
       * @param sequences	@ref Alignandum object to align.
      */
      virtual void align(
    		  HMultAlignment & dest,
    		  const HAlignandumVector & sequences ) const;

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
    		  const HStringVector & sequences ) const;
    };

}

#endif /* IMPL_MULTIPLEALIGNATOR_H */
