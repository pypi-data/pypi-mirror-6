/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignatorDPFull.h,v 1.1 2005/02/24 11:08:24 aheger Exp $

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

#ifndef IMPL_ALIGNATOR_DP_FULL_H
#define IMPL_ALIGNATOR_DP_FULL_H 1

#include "alignlib_fwd.h"
#include "ImplAlignatorDP.h"
#include "Iterator2D.h"
#include <cassert>

namespace alignlib
{

    /* re: Global functions and pointers for the fast determination of match score.

      I don't know how to use member functions as function pointers. After all, this is what
      inheritence is for. A possibility would be to automatically subclass an alignator-object.
      However, I do not like this idea, since this assumes that the parent has information
      about the child. On the other hand, via the inlining mechanism a function call could be saved.
      The problem is when you want to change the algorithm by overloading align. Then the parent
      functions () do not know, what the child is. Therefore I use the static
      functions. Maybe it is possible to separate the algorithm and the type-decision into different
      classes that interact.

      It should be possible, it is just a syntax problem?

      The danger of static functions is that the global pointers are unsafe, i.e. there exist just
      one copy for all alignator-objects, and my guess is that this code will never ever be threadsafe.
    */

/**
    @brief local, full dynamic programming alignment

    This objects aligns two @ref Alignandum objects using a full dynamic programming algorithm with
    affine gap penalties. The objects to be aligned are always assumed to be starting at residue 1.
    The object @ref Alignandum are responsible for mapping windows back and forth.

    This class implements the back-tracking algorithm used by several of its children.

    @author Andreas Heger
    @version $Id: ImplAlignatorDPFull.h,v 1.1 2005/02/24 11:08:24 aheger Exp $
*/
class ImplAlignatorDPFull : public ImplAlignatorDP
  {

    typedef unsigned char TraceEntry;
    typedef long TraceIndex;

    /** codes in trace-back matrix */
    enum TraceBackType
      {
    	TB_NOMATCH, TB_MATCH,
    	TB_INSERTION, TB_DELETION,
    	TB_INSERTION_OPEN, TB_INSERTION_EXTEND,
    	TB_DELETION_OPEN, TB_DELETION_EXTEND,
    	TB_STOP, TB_WRAP
      };

      enum TraceBackLevel
      {
    	  TBL_MATCH, TBL_INSERTION, TBL_DELETION
      };

  public:
    /* Constructors and destructors */

	  /** constructor */
	ImplAlignatorDPFull();

    /** set affine gap penalties and substitution matrix
	@param subst_matrix	pointer to substitution matrix
	@param row_gop		gap opening penalty in row
	@param row_gep		gap elongation penalty in row
	@param col_gop		gap opening penalty in column, default = row
	@param col_gep		gap elongation penalty in row, default = col

    */
    ImplAlignatorDPFull( AlignmentType alignment_type,
			 Score row_gop, Score row_gep,
			 Score col_gop = 0, Score col_gep = 0,
			 bool penalize_row_left = false, bool penalize_row_right = false,
			 bool penalize_col_left = false, bool penzlize_col_right = false);

    /** copy constructor */
    ImplAlignatorDPFull( const ImplAlignatorDPFull & );

    /** destructor */
    virtual ~ImplAlignatorDPFull();

    DEFINE_CLONE( HAlignator );

    /* operators------------------------------------------------------------------------------ */

    /* member access functions--------------------------------------------------------------- */

  protected:

	    /** perform initialization before alignment */
	    virtual void startUp(HAlignment & dest, const HAlignandum & row, const HAlignandum & col );

	    /** clean up temporary memory after alignment step */
	    virtual void cleanUp(HAlignment & dest, const HAlignandum & row, const HAlignandum & col );

	    /** perform the alignment */
	    virtual void performAlignment(HAlignment & dest,
	    							const HAlignandum & row,
	    							const HAlignandum & col );

	    /** perform local alignment */
	    virtual void performAlignmentLocal(HAlignment & dest,
	    							const HAlignandum & row,
	    							const HAlignandum & col );

	    /** perform global alignment */
	    virtual void performAlignmentGlobal(HAlignment & dest,
	    							const HAlignandum & row,
	    							const HAlignandum & col );

	    /** perform wrapped alignment
	     *
	     * wrap around col several times.
	     *
	     * The alignment is local for row and for col.
	     * */
	    virtual void performAlignmentWrapped(HAlignment & dest,
									const HAlignandum & row,
	    							const HAlignandum & col );



    /** traces back through trace matrix and put in the alignment in Alignment-object */
    virtual void traceBack( HAlignment & dest,
    		const HAlignandum & row, const HAlignandum & col );

    /** return index for given row and length.
     * */
    inline int getTraceIndex( TraceBackLevel level, Position row, Position col ) const
      {
    	assert( row >= mRowFrom - 1);
    	assert( row < mRowTo );
    	// col can be before element 0 in wrap-around alignments
    	assert( col >= mIterator->col_front(row) - 1);
    	assert( col <= mIterator->col_back(row) );
    	// the first element in each column is the carry over value from the previous
    	// column, thus the +1 modifier.
    	int index = mTraceRowStarts[row-mRowFrom] + col - mIterator->col_front(row) + 1;
#ifdef DEBUG
    	if (index < 0 || index >= mMatrixSize )
    		std::cout << "mRowFrom=" << mRowFrom << " row=" << row << " col=" << col << std::endl;
#endif
    	assert( index >= 0);
    	assert( index < mMatrixSize );
    	// shift matrix according to level
    	switch (level)
    	{
    	case TBL_DELETION:
    		index += mMatrixSize;
    	case TBL_INSERTION:
    		index += mMatrixSize;
    	case TBL_MATCH:
    		;
    	}

    	return index;
      };

    /* member data --------------------------------------------------------------------------- */
  protected:
    /** pointer to the trace matrix

    The trace is stored row-wise. This is used in the alignment that assumes
    the trace entries for a row to be continuous in memory.
    */
    TraceEntry * mTraceMatrix;

    /** size of a matrix */
    size_t mMatrixSize;

    /** list of start position of trace for a given row */
    TraceIndex * mTraceRowStarts;

    /** first row */
    Position mRowFrom;

    /** last row + 1*/
    Position mRowTo;

    /** row, where trace ended */
    Position mRowLast;

    /** column, where trace ended */
    Position mColLast;

    /** level on which trace ended */
    TraceBackLevel mLevelLast;

    /** print traceback matrix (for debugging purposes)
     */
	void printTraceMatrix( TraceBackLevel level ) const;


};


}

#endif /* IMPL_ALIGNATOR_DP_FULL_H */

