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

#ifndef IMPL_ALIGNATOR_GROUPIES_H
#define IMPL_ALIGNATOR_GROUPIES_H 1

#include "alignlib_fwd.h"
#include "ImplAlignator.h"

namespace alignlib
{
  /**
     @short Implementation of groupie alignments.

     Groupie alignments are alignments between sequences of high
     similarity (>90%).

     This @ref Alignator proceeds in the following way:

     1. Build dots for both sequence, typically using a k-tuple dottor
     (@ref ImplAlignatorTuples).

     2. Find the maximum diagonal and remove all dots that are far further
     than mTubeSize away from this diagonal.

     3. Align the dots within the tube.

     4. Fill alignment gaps using the @ref Alignator given in
     mAlignatorGaps.

     @author Andreas Heger
     @version $Id$
  */

  class ImplAlignatorGroupies : public ImplAlignator
    {
      /* class member functions-------------------------------------------------------------- */
    public:
      /* constructors and desctructors------------------------------------------------------- */

        /** constructor */
      ImplAlignatorGroupies();

      /** constructor
       *
       * @param tube_size 		size of the tube in which alignment is performed
       * @param alignator_dots	@ref Alignator to build dots.
       * @param alignator_gaps	@ref Alignator to use to fill in gaps.
       * */
      ImplAlignatorGroupies(
    		  const Position tube_size,
    		  const Position tuple_size,
    		  const HAlignator & alignator_dots,
    		  const HAlignator & alignator_gaps,
    		  const Score & gop,
    		  const Score & gep
    		  );

      /** destructor */
      virtual ~ImplAlignatorGroupies ();

      /** copy constructor */
      ImplAlignatorGroupies( const ImplAlignatorGroupies & src);

      DEFINE_CLONE( HAlignator );

    protected:
      /** perform the alignment.
      */
      virtual void align( HAlignment & ali,
    		  const HAlignandum & row,
    		  const HAlignandum & col );

    private:

    	/** tube size to use.
    	 *
    	 * This should correspond to the longest gap
    	 * expected between the two sequences.
    	 */
    	Position mTubeSize;

    	/** Alignator to use to fill in gaps */
    	HAlignator mAlignatorGaps;

    	/** Alignator to use to build dots */
    	HAlignator mAlignatorDots;

    	/** gap opening penalty */
    	Score mGop;

    	/** gap extension penalty
    	 */
    	Score mGep;

    	/** the tuple size
    	 */
    	Position mTupleSize;
    };

}

#endif /* ALIGNATOR_H */
