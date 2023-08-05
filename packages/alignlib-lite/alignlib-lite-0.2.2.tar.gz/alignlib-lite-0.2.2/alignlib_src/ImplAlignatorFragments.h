/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignatorFragments.h,v 1.3 2004/03/19 18:23:41 aheger Exp $

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

#ifndef IMPL_ALIGNATOR_FRAGMENTS_H
#define IMPL_ALIGNATOR_FRAGMENTS_H 1

#include "alignlib_fwd.h"
#include "alignlib_fwd.h"
#include "ImplAlignator.h"
#include "Fragmentor.h"

namespace alignlib
{
#define STACKEMPTY     0

    class Alignandum;
    class Alignment;
    class Fragmentor;


/**
    @short aligns two @ref Alignandum objects using a supplied list of fragments.

    The difference to @ref ImplAlignatorDots is that a fragment is longer than a
    dot.

    @author Andreas Heger
    @version $Id: ImplAlignatorFragments.h,v 1.3 2004/03/19 18:23:41 aheger Exp $
*/
class ImplAlignatorFragments : public ImplAlignator
{
 public:

	    /* constructors and destructors */

	 /** empty constructors */
	ImplAlignatorFragments();

    /** set affine gap penalties
     @param row_gop		gap opening penalty in row
     @param row_gep		gap elongation penalty in row
     @param col_gop		gap opening penalty in column, default = row
     @param col_gep		gap elongation penalty in row, default = col

    */
	 ImplAlignatorFragments(
    		const HFragmentor & fragmentor,
    		Score row_gop,
    		Score row_gep,
    		Score col_gop = 0,
    		Score col_gep = 0 );

    /** copy constructor */
    ImplAlignatorFragments( const ImplAlignatorFragments & );

    /** destructor */
    virtual ~ImplAlignatorFragments();

    DEFINE_CLONE( HAlignator );

    /* operators------------------------------------------------------------------------------ */
    /** method for aligning two arbitrary objects */
    virtual void align( HAlignment & dest,
    		const HAlignandum & row,
    		const HAlignandum & col );

    /* member access functions--------------------------------------------------------------- */
    /** set gap opening penalty for row */
    virtual void setRowGop( Score gop );

    /** set gap extension penalty for row */
    virtual void setRowGep( Score gep );

    /** set gap opening penalty for col */
    virtual void setColGop( Score gop );

    /** set gap extension penalty for col */
    virtual void setColGep( Score gep );

    /** get gap opening penalty for row */
    Score getRowGop();

    /** get gap extension penalty for row */
    Score getRowGep();

    /** get gap opening penalty for col */
    Score getColGop();

    /** get gap extension penalty for col */
    Score getColGep();

 protected:

    /** perform the alignment */
    virtual void performAlignment( HAlignment & dest,
    		const HAlignandum & row,
    		const HAlignandum & col );

    /** get cost for a gap */
    virtual Score getGapCost( Dot x1, Dot x2 ) const;

    /** perform initialisation before alignment. Overload, but call this function in subclasses! */
    virtual void startUp(
    		HAlignment & dest,
    		const HAlignandum & row,
    		const HAlignandum & col );

    /** perform cleanup after alignment */
    virtual void cleanUp(
    		HAlignment & dest,
    		const HAlignandum & row,
    		const HAlignandum & col );

    /** traces back through dot-trace and put it in the alignment in Alignment-object */
    virtual void traceBack(
    		HAlignment & result,
    		const HAlignandum & row,
    		const HAlignandum & col );

 protected:

    /** The dotter object that supplies the fragments */
    HFragmentor mFragmentor;

    /* number of fragments */
    Position	mNFragments;

    /** pointer to fragments */
    HFragmentVector mFragments;

    /* help variables for backtracing */
    /** last dot */
    int	mLastFragment;

    /** trace of fragments that are part of the alignment */
    int	*mTrace;

    /** the score of the alignment */
    Score mScore;

    /** gap opening penalty for row-object */
    Score mRowGop;
    /** gap elongation penalty for col-object */
    Score mRowGep;
    /** gap opening penalty for row-object */
    Score mColGop;
    /** gap elongation penalty for col-object */
    Score mColGep;

    /** maximum length of a row */
    Position mRowLength;

    /** maximum length of a column */
    Position mColLength;

};


}

#endif /* _ALIGNATOR_FRAGMENTS_H */

