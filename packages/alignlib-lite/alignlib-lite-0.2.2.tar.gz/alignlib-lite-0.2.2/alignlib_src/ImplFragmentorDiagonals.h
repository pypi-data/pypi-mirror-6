/*
  alignlib - a library for aligning protein sequences

  $Id: ImplFragmentorDiagonals.h,v 1.3 2004/03/19 18:23:41 aheger Exp $

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

#ifndef IMPL_FRAGMENTOR_DIAGONALS_H
#define IMPL_FRAGMENTOR_DIAGONALS_H 1

#include "alignlib_fwd.h"
#include "ImplFragmentor.h"
#include "Alignment.h"

namespace alignlib
{

/**
   @short align fragments using a gap penalty based on diagonal changes.

   @author Andreas Heger
   @version $Id: ImplFragmentorDiagonals.h,v 1.3 2004/03/19 18:23:41 aheger Exp $

*/
class ImplFragmentorDiagonals : public ImplFragmentor
{
  /* class member functions-------------------------------------------------------------- */
 public:
    /* constructors and desctructors------------------------------------------------------- */

	 /** constructor */
	ImplFragmentorDiagonals();

	/** constructor */
    ImplFragmentorDiagonals(
    		const HAlignator & dottor,
    		Score row_gop,
    		Score row_gep,
    		Score col_gop = 0 ,
    		Score col_gep = 0 );

    /** destructor */
    virtual ~ImplFragmentorDiagonals ();

    /** copy constructor */
    ImplFragmentorDiagonals( const ImplFragmentorDiagonals & src);

    DEFINE_CLONE( HFragmentor );

 protected:
    /** gap opening penalty for row-object */
    Score mRowGop;
    /** gap elongation penalty for col-object */
    Score mRowGep;
    /** gap opening penalty for row-object */
    Score mColGop;
    /** gap elongation penalty for col-object */
    Score mColGep;

    /** the alignator used to create dot-plots */
    HAlignator mDottor;

    virtual Score getGapCost( const ResiduePair & p1, const ResiduePair & p2 ) const ;

    /** perform the actual alignment */
    virtual void performFragmentation(
    		const HAlignment & sample,
    		const HAlignandum & row,
    		const HAlignandum & col );

    /** perform cleanup after alignment */
    virtual void cleanUp( HAlignment & sample, const HAlignandum & row, const HAlignandum & col );

};

}

#endif /* FRAGMENTOR_H */
