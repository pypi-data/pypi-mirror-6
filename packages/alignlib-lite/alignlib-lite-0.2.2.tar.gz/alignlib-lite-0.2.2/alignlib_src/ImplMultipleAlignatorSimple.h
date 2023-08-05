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

#ifndef IMPL_MULTIPLEALIGNATOR_SIMPLE_H
#define IMPL_MULTIPLEALIGNATOR_SIMPLE_H 1

#include "alignlib_fwd.h"
#include "ImplMultipleAlignator.h"

namespace alignlib
{
  /**
     @short base implementation class for MultipleAlignator objects.

	 This object aligns the first sequence against all other sequences
	 and stacks the alignments on top of each other.

     @author Andreas Heger
     @version $Id$
  */

  class ImplMultipleAlignatorSimple : public ImplMultipleAlignator
    {
      /* class member functions-------------------------------------------------------------- */
    public:
      /* constructors and desctructors------------------------------------------------------- */

    	/** constructor */
    	ImplMultipleAlignatorSimple();

    	/** constructor */
    	ImplMultipleAlignatorSimple( const HAlignator & alignator );

      /** destructor */
      virtual ~ImplMultipleAlignatorSimple ();

      /** copy constructor */
      ImplMultipleAlignatorSimple( const ImplMultipleAlignatorSimple & src);

      DEFINE_CLONE( HMultipleAlignator );

      /** align sequences in src
       *
       * The strings are converted to @ref Alignandum object using
       * makeSequence() and the default @ref Encoder.
       *
       * @param dest	@ref MultAligment object to store the alignment result.
       * @param col		@ref Alignandum objects to align.
      */
      virtual void align(
    		  HMultAlignment & dest,
    		  const HAlignandumVector & src ) const ;

    private:
    	// object used to build a tree
		const HAlignator mAlignator;

    };


}

#endif /* IMPL_MULTIPLEALIGNATOR_PROGRESSIVE_H */
