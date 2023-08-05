/*
  alignlib - a library for aligning protein sequences

  $Id: ImplMultipleAlignment.h,v 1.5 2004/03/19 18:23:41 aheger Exp $

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

#ifndef IMPL_MULTIPLE_ALIGNMENT_H
#define IMPL_MULTIPLE_ALIGNMENT_H 1

#include <iosfwd>
#include <string>
#include <list>

#include "alignlib_fwd.h"
#include "MultipleAlignment.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{
/**
    @short Implementation class for multiple alignments.

    This class keeps a vector of Alignatum objects. If a new
    @ref Alignatum object is added, gaps have to be added to all previously added
    @ref Alignatum objects, so this can be a costly operation. However, this class
    is efficient for pile-up alignments, with an ungapped query sequence at the
    top.

    @author Andreas Heger
    @version $Id: ImplMultipleAlignment.h,v 1.5 2004/03/19 18:23:41 aheger Exp $
*/
class ImplMultipleAlignment : public MultipleAlignment, public ImplAlignlibBase
{

  // class member functions
 public:

    // constructors and desctructors
    /** empty constructor
     */
    ImplMultipleAlignment  ();

    /** copy constructor */
    ImplMultipleAlignment  (const ImplMultipleAlignment &);

    /** destructor */
    virtual ~ImplMultipleAlignment ();

    //---------------------------------------------------------------------------------------
    /*------- accessors --------------------------------------------------------------------*/
    /** returns the length of the multiple alignment. All objects in a multiple alignment have
	the same length */
    virtual Position getLength() const;

    /** sets the length of the multiple alignment. Raises an exception, if the mali is not empty
	*/
    virtual void setLength( Position length);

    /** returns the width of the multiple alignment, i.e., the number of objects in this multiple
	alignment */
    virtual int getNumSequences() const;

    /** returns a const reference to the object at row in the multiple alignment. This allows treating
	the multiple alignment as a two-dimensional matrix. Since string does define operator[] as well, you
	can access the symbol in column c and row r by calling
	symbol =  multiple_alignment[r][c]
    */
    virtual const std::string & operator[]( int row ) const;

    /** returns a pointer to the object at row from the multiple alignment. The pointer is not const,
	so you are free to do all sort of ugly stuff.*/
    virtual HAlignatum getRow( int row ) const;

    /** erases an entry form the multiple alignment */
    virtual void eraseRow( int row );

    /** return true, if a column is aligned.
     *
     * Unaligned columns result from adding
     * new sequences to the multiple alignment.
     *
     * @return true, if column @col is aligned.
     * */
    virtual bool isAligned( const Position & col );

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

    /** returns true, if there are no aligned objects in this alignment */
    virtual bool isEmpty() const;

    /** clears the multiple alignment */
    virtual void clear();

    /** returns a clone of this object */
    virtual HMultipleAlignment getClone() const;

    /** returns an empty version of this object
    */
    virtual HMultipleAlignment getNew() const;

    /** write the multiple alignment to a stream.
     */
    virtual void write( std::ostream & output ) const;

 protected:
    /** free all memory. Tell all stored objects to destruct themselves */
    virtual void freeMemory();

    /** update */
    virtual void update() const;

    /** I store an array of handles to alignatum objects. */
    mutable std::vector<HAlignatum> mRows;

    /** flag for recording aligned columns */
    mutable std::vector<bool> mIsAligned;

    /** the length of the multiple alignment */
    mutable int mLength;

 private:

	 /** update the aligned flag mapping onto new */
	 virtual void updateAligned(
			 const HAlignment & map_this2new,
			 const HAlignment & map_other2new);

};


}

#endif /* IMPL_MULTIPLE_ALIGNMENT_H */

