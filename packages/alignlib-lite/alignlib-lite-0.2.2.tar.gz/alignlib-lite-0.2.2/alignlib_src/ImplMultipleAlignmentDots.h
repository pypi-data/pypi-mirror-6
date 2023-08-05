/*
  alignlib - a library for aligning protein sequences

  $Id: ImplMultipleAlignmentDots.h,v 1.2 2004/01/27 12:14:49 aheger Exp $

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

#ifndef IMPL_MULTIPLE_ALIGNMENT_DOTS_H
#define IMPL_MULTIPLE_ALIGNMENT_DOTS_H 1

#include <iosfwd>
#include <string>
#include <list>

#include "alignlib_fwd.h" 
#include "ImplMultipleAlignment.h"

namespace alignlib 
{

/** 
    Multiple alignments are collection of aligned sequences (more specifically: objects of type
    @ref Alignment). A multiple alignment
    receives submitted aligned objects, or unaligned objects together with a multiple
    alignment, etc. Ownership belongs to the multiple alignment.

    The multiple alignment is a sort of container. Output-formatting, etc. is done
    by the @ref Alignment-objects.
    
    The interface for this class is quite fat, because multiple alignments are used
    in a variety of contexts.

    In this implementation the rows are stored as pairs of sequences and alignments.
    Adding alignments is quick.
    
    @author Andreas Heger
    @version $Id: ImplMultipleAlignmentDots.h,v 1.2 2004/01/27 12:14:49 aheger Exp $
    @short an implementation for multiple alignments
*/

/** Lazily maps input to output via alignment. 
 */

class ImplMultipleAlignmentDots : public ImplMultipleAlignment 
{

	struct MaliRow 
	{
		MaliRow( const HAlignatum & input, 
				const HAlignment & map_alignatum2mali ); 
	  
		MaliRow( MaliRow & src );
	  
		~MaliRow();
	  
		/** the raw input */
		HAlignatum mAlignatumInput; 
		/** the dots */
		HAlignment mMapMali2Alignatum;
	};

	typedef boost::shared_ptr< MaliRow > HMaliRow;

	typedef std::vector< HMaliRow > RowVector;
	
  // class member functions
 public:

    // constructors and desctructors
    /** empty constructor 
     */
    ImplMultipleAlignmentDots(
    		const bool compress_unaligned_columns = true,
    		const int max_insertion_length = -1);

    /** copy constructor */
    ImplMultipleAlignmentDots  (const ImplMultipleAlignmentDots &);

    /** destructor */
    virtual ~ImplMultipleAlignmentDots ();

    //---------------------------------------------------------------------------------------
    /*------- accessors --------------------------------------------------------------------*/
    
    /** erases an entry form the multiple alignment */
    virtual void eraseRow( int row );
    
    /* ------------------ mutators ----------------------------------------------------------- */

    /*------------------- functions for adding new members to the multiple alignment---------*/

    /** add an aligned object to the multiple alignment. Ownership of this object is transferred to
	the multiple alignment. 
	@param src	       pointer to the aligned object to be added.
	@param alignment pointer to the alignment used for combining these two objects. If it is
		       not supplied, then it is assumed, that it is the identity alignment. In
		       that case src has to have the same length the multiple alignment. Note, the
		       multiple alignment is in col, the src is in row of the multiple alignment, so
		       when calling the member-function Alignment::Map() with a residue from
		       src, you get the correct position in the multiple alignment.
	@param skip_gaps false, if gaps in existing multiple alignment shall be introduced
    */
    virtual void add( const HAlignatum & src,
		      const HAlignment & alignment,
		      bool mali_is_in_row = true,
		      bool insert_gaps_mali = true,
		      bool insert_gaps_alignatum= true,
		      bool use_end_mali = false,
		      bool use_end_alignatum = false);

    /** add a aligned sequence of the same length to this multiple alignment.
     */
    virtual void add( const HAlignatum & src );
    
    /** add the contents of a multiple alignment to the multiple alignment by mapping it through an alignment
	@param src	       pointer to the unaligned object to be added.
	@param alignment pointer to the alignment used for combining these two objects. If it is
		       not supplied, then it is assumed, that it is the identity alignment. In
		       that case src has to have the same length the multiple alignment. Note, the
		       multiple alignment is in col, the src is in row of the multiple alignment, so
		       when calling the member-function Alignment::Map() with a residue from
		       src, you get the correct position in the multiple alignment.
          @param skip_gaps false, if gaps in existing multiple alignment shall be introduced
			   
     */
    virtual void add( const HMultipleAlignment & src,
		      const HAlignment & alignment,
		      bool mali_is_in_row = true,
		      bool insert_gaps_mali = true,
		      bool insert_gaps_alignatum= true,
		      bool use_end_mali = false,
		      bool use_end_alignatum = false);

    /** add a aligned sequence of the same length to this multiple alignment.
     */
    virtual void add( const HMultipleAlignment & src );
    
    /** returns a clone of this object */
    virtual HMultipleAlignment getClone() const;
    
    /** returns an empty version of this object */
    virtual HMultipleAlignment getNew() const;
    
 protected:
    /** render the multiple alignment */
    virtual void update() const;
    
    /** free all memory. Tell all stored objects to destruct themselves */
    virtual void freeMemory();

 private:
    /** I store an array of vectors. The pointers can not be const, because sequences are told to rescale. */
    mutable RowVector mRowData;             

    /** whether or not to compress unaligned columns */
    bool mCompressUnalignedColumns;

    /** maximal length of an insertion */
    int mMaxInsertionLength;
    
    /** flag for object status */
    mutable bool mIsDirty;
    
};

typedef boost::shared_ptr< ImplMultipleAlignmentDots > HImplMultipleAlignmentDots;

}

#endif /* IMPL_MULTIPLE_ALIGNMENT_DOTS_H */

