/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignatorDots.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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

#ifndef IMPL_ALIGNATOR_DOTS_H
#define IMPL_ALIGNATOR_DOTS_H 1

#include "alignlib_fwd.h"

#include "ImplAlignator.h"
#include "ImplAlignmentMatrix.h"
#include "Macros.h"

namespace alignlib
{


/** @short dotplot alignment using full lookup of dots.

    @author Andreas Heger
    @version $Id: ImplAlignatorDots.h,v 1.3 2004/03/19 18:23:40 aheger Exp $
*/
class ImplAlignatorDots : public ImplAlignator
{
 public:

    /* constructors and destructors */

	 /** constructor
	  */
	 ImplAlignatorDots();

    /** constructor
     * @param dottor	@ref Alignator object to build dot plot.
     	@param row_gop		gap opening penalty in row.
     	@param row_gep		gap elongation penalty in row.
     	@param col_gop		gap opening penalty in column, default is same as row.
     	@param col_gep		gap elongation penalty in column, default is same as row.

    */
    ImplAlignatorDots(
    		const HAlignator & dottor,
    		Score row_gop,
    		Score row_gep,
    		Score col_gop = 0,
    		Score col_gep = 0 );

    /** copy constructor */
    ImplAlignatorDots( const ImplAlignatorDots & );

    /** destructor */
    virtual ~ImplAlignatorDots();

    /** method for aligning two arbitrary objects
     */
    virtual void align(
    		HAlignment & dest,
    		const HAlignandum & row,
    		const HAlignandum & col);


    DEFINE_CLONE( HAlignator );

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
	    virtual void performAlignment(
	    		HAlignment & dest,
	    		const HAlignandum & row,
	    		const HAlignandum & col );

    /** get GAP cost for a gap */
    virtual Score getGapCost( Dot x1, Dot x2 ) const;

    /** perform initialisation before alignment. Overload, but call this function in subclasses! */
    virtual void startUp(
    		HAlignment & ali,
  		  	const HAlignandum & row,
  		  	const HAlignandum & col);

    /** perform cleanup after alignment */
    virtual void cleanUp(
    		HAlignment & ali,
  		  	const HAlignandum & row,
  		  	const HAlignandum & col );

    /** return index for a row/col pair */
    virtual Position getPairIndex( Position r, Position c ) const;

    /** perform traceback */
    virtual void traceBack(
    		HAlignment & ali,
  		  	const HAlignandum & row,
  		  	const HAlignandum & col );


    /** The dotter object that supplies the dots */
    HAlignator mDottor;

    /* diverse helper variables */
    Position mNDots;

    /** pointer to dots for fast access */
    const ImplAlignmentMatrix::PAIRVECTOR * mPairs;

    /** pointer to first dot in row for fast access */
    const Dot * mRowIndices;

    /* help variables for backtracing */
    /** last dot */
    int	mLastDot;

    /** trace of dots that are part of the alignment */
    int	*mTrace;

    /** the score of the alignment */
    Score mScore;

    /** pointer to the matrix of Dots (= alignment ) */
    HAlignment mMatrix;

    /** flag, whether dots were created during alignment */
    bool mIsOwnDots;

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

#endif /* _ALIGNATOR_DOTS_H */

