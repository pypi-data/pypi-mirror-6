/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignatorDP.h,v 1.1 2005/02/24 11:08:24 aheger Exp $

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

#ifndef IMPL_ALIGNATOR_DP_H
#define IMPL_ALIGNATOR_DP_H 1

#include "alignlib_fwd.h"
#include "alignlib_fwd.h"
#include "ImplAlignator.h"

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
    @version $Id: ImplAlignatorDP.h,v 1.1 2005/02/24 11:08:24 aheger Exp $
*/
class ImplAlignatorDP : public ImplAlignator
{

 public:

    /* Constructors and destructors */

	 /** empty constructor */
	ImplAlignatorDP();

    /** set affine gap penalties and substitution matrix
     @param subst_matrix	pointer to substitution matrix
     @param row_gop		gap opening penalty in row
     @param row_gep		gap elongation penalty in row
     @param col_gop		gap opening penalty in column, default = row
     @param col_gep		gap elongation penalty in row, default = col

    */
    ImplAlignatorDP( AlignmentType alignment_type,
		     Score row_gop, Score row_gep,
		     Score col_gop = 0, Score col_gep = 0,
		     bool penalize_row_left = false, bool penalize_row_right = false,
		     bool penalize_col_left = false, bool penzlize_col_right = false);

    /** copy constructor */
    ImplAlignatorDP( const ImplAlignatorDP & );

    /** destructor */
    virtual ~ImplAlignatorDP();

    /* operators------------------------------------------------------------------------------ */
    /** method for aligning two arbitrary objects */
    virtual void align( HAlignment & , const HAlignandum & , const HAlignandum &);

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
	    /** perform initialization before alignment */
	    virtual void startUp(HAlignment & dest, const HAlignandum & row, const HAlignandum & col );

	    /** clean up temporary memory after alignment step */
	    virtual void cleanUp(HAlignment & dest, const HAlignandum & row, const HAlignandum & col );

	    /** perform the alignment */
	    virtual void performAlignment(HAlignment & dest,
	    							const HAlignandum & row,
	    							const HAlignandum & col ) = 0;

    /* member data --------------------------------------------------------------------------- */
 protected:

    /** maximum score in matrix */
    Score mScore;

    /** internal helper array for the calculation of affine gap penalties */
    Score *mCC;

    /** internal helper array for the calculation of affine gap penalties */
    Score *mDD;

    // pointers to memory location of encoded sequences/profiles/...

    /** alignment type */
    AlignmentType mAlignmentType;

    bool mPenalizeRowLeft;
    bool mPenalizeRowRight;
    bool mPenalizeColLeft;
    bool mPenalizeColRight;

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

#endif /* _ALIGNATOR_MATRIX_H */

