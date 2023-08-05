/*
  alignlib - a library for aligning protein sequences

  $Id: ImplMultAlignment.h,v 1.5 2004/03/19 18:23:41 aheger Exp $

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

#ifndef IMPL_MULT_ALIGNMENT_H
#define IMPL_MULT_ALIGNMENT_H 1

#include <iosfwd>
#include <string>
#include <list>

#include "alignlib_fwd.h"
#include "MultAlignment.h"
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
    @version $Id$
*/
class ImplMultAlignment : public MultAlignment, public ImplAlignlibBase
{

  // class member functions
 public:

    // constructors and desctructors
    /** empty constructor
     */
    ImplMultAlignment  ();

    /** copy constructor */
    ImplMultAlignment  (const ImplMultAlignment &);

    /** destructor */
    virtual ~ImplMultAlignment ();

    DEFINE_CLONE( HMultAlignment );

    /** return a modified copy of this alignment
    *
    * @param modification of the multiple alignment.
    *
    *     Full: unaligned residues are added to the multiple alignment.
    *           They are not stacked on each other, but for each unaligned
    *           residue a new multiple aligment position is created.
    * 	  Compressed: space is created within the multiple alignment
    *           in order to accommodate unaligned residues
    *
    * @return a new @ref MultAlignment instance.
    */

	virtual HMultAlignment getCopy(
				const ExpansionType & expansion_type ) const;

    //---------------------------------------------------------------------------------------
    /*------- accessors --------------------------------------------------------------------*/

    /** returns the length (number of columns) of the multiple alignment.
     *
     * @return the length (aligned positions) of the multiple alignment. */
    virtual Position getLength() const;

    /** returns the first aligned column of the multiple alignment.
     *
     * @return the first aligned column of the multiple alignment. */
    virtual Position getFrom() const;

    /** returns the last aligned column +1 of the multiple alignment.
     *
     * Note: this is synonymous to getLength()
     *
     * @return the last aligned column + 1 of the multiple alignment. */
    virtual Position getTo() const;

    /** returns the number of sequences in this multiple alignment.
     *
     * @return number of sequences in alignment.
     */
    virtual int getNumSequences() const;

    /** returns a row of the multiple alignment.
     *
     * @param row row of multiple alignment.
     * return multiple alignment
    */
    virtual const HAlignment operator[]( int row ) const ;

    /** returns a row of the multiple alignment.
     *
     * @param row row of multiple alignment.
     * return a @ref Alignatum object
    */
    virtual const HAlignment getRow( int row ) const;

    /** erases an row from the multiple alignment
     *
     * @param row row to erase.
     * */
    virtual void eraseRow( int row );

    /** return true, if a column is aligned.
     *
     * Unaligned columns result from adding
     * new sequences to the multiple alignment.
     *
     * @return true, if column @col is aligned.
     * */
    virtual bool isAligned( const Position & col );

    /** expand multiple alignment
     *
     * This will add columns into the multiple alignment for unaligned positions
     * in the rows.
     *
     * @param sequences  	a list of sequences. If this array is not null,
     * 						sequence lengths from this array will be used to expand
     * 						the multiple alignment before the first and after the last
     * 						column.
     * */
    virtual void expand(
    		const HAlignandumVector & sequences );

    /** shrink multiple alignment
     *
     * All columns that contain only one alignment positions will be removed.
     * */
    virtual void shrink();

    /** merges another multiple alignment with this multiple alignment
      *
      * Both multiple alignments need to have the same number of
      * sequences.
      *
      * @param other the other multiple alignment.
      * */
     virtual void merge( const HMultAlignment & other );

    /** move the multiple alignment
      *
      * shifts multiple alignment columns by @param position. A negative
      * position will shift to lower values.
      * @param position number of positions to shift
      * */
     virtual void move( const Position & position );

     /** trims the multiple alignment
       *
       * removes all unaligned columns to the left of the multiple
       * alignment.
       * */
      virtual void trim();

	/** apply a map to the multiple alignment.
	 *
	 * This method maps multiple alignment columns to new positions.
	 *
	 * The alignment mode denotes whether row or col are mapped.
	 * Only alignment modes CR and RC are applicable.
	 *
	 * RC: multiple alignment column is replaced with corresponding R->C from other
	 * CR: multiple alignment column is replaced with corresponding C->R from other.
	 * @param other @ref Alignment to map with
	 * @param mode Combination mode.
	 *
	 * */
	virtual void map(
			const HAlignment & other,
			const CombinationMode & mode );

    /* ------------------ mutators ----------------------------------------------------------- */

    /** add an @ref Alignment object to the multiple alignment.
     *
     * The alignment object maps the sequence to multiple alignment columns.
     *
	@param src	 @ref Alignment object to add.
	@param alignment @ref Alignment that maps src to mali.
    */
    virtual void add(
    		const HAlignment & map_mali2sequence );

    /** add a @ref MultipleAlignment object to the multiple alignment.
     *
     * The alignment object maps the sequence to multiple alignment columns.
     * Note that some alignment information can be potentially lost. If two
     * sequence positions are aligned in @param src, but that column is not
     * in map_mali2sequence, then the alignment of these two residues is lost.
     *
	@param other	 @ref MultipleAlignment object to add.
	@param map_src2this @ref Alignment that maps src to this.
    */
    virtual void add(
    		const HMultipleAlignment & src,
    		const HAlignment & map_src2this );


    /** add a @ref MultAlignment object to the multiple alignment.
     *
     * The alignment object maps the sequence to multiple alignment columns.
     * Note that some alignment information can be potentially lost. If two
     * sequence positions are aligned in @param src, but that column is not
     * in map_mali2sequence, then the alignment of these two residues is lost.
     *
	@param other	 @ref MultAlignment object to add.
	@param map_this2other @ref Alignment that maps this mali to the other.
    */
    virtual void add(
    		const HMultAlignment & other,
    		const HAlignment & map_this2other );

    /** add a @ref MultAlignment object to the multiple alignment.
     *
     * The alignment object maps the sequence to multiple alignment columns.
     * Note that some alignment information can be potentially lost. If two
     * sequence positions are aligned in @param src, but that column is not
     * in map_mali2sequence, then the alignment of these two residues is lost.
     *
	@param other	 @ref MultAlignment object to add.
	@param map_this2new @ref Alignment that maps this mali to the new.
	@param map_other2new @ref Alignment that maps this mali to the new.
    */
    virtual void add(
    		const HMultAlignment & other,
    		const HAlignment & map_this2new,
			const HAlignment & map_other2new);


    /** returns true, if the alignment is empty.
     *
     * @return true, if the alignment is emtpy.
     * */
    virtual bool isEmpty() const;

    /** clears the multiple alignment
    */
    virtual void clear();

    /** write the multiple alignment to a stream
     *
     * @param output output stream.
    */
    virtual void write( std::ostream & output ) const ;

    /** return multiple alignment as a matrix.
         *
         *  The default orientation is row/col, i.e. matrix[0][10] refers
         *  to the tenth column in the first sequence.
         *
         *  Unaligned positions are set to NO_POS.
         *
         * @param transpose if set to true, the transposed matrix is returned
         * @return a position matrix.
         */
     virtual HPositionMatrix getPositionMatrix( const bool & transpose = false ) const;

     /** return column counts.
      *
      *  Return a vector with the number of aligned residues per column
      *
      * @return a vector of counts.
      */
     virtual HCountVector getColumnCounts() const;

     /** return row counts.
      *
      *  Return a vector with the number of aligned residues per row
      *
      * @return a vector of counts.
      */
     virtual HCountVector getRowCounts() const;

     /** return the number of unaligned residues before a column.
      *
      *  Return a vector of length l+1 with the number of unaligned residues
      *  per column.
      *
      * @param sequences  	a list of sequences. If this array is not null,
      *						sequence lengths from this array will be used to expand
      *						the multiple alignment before the first and after the last
      *						column.
      * @param aggregate_type determines how counts are aggregated.
      * @return a vector of counts.
      */

     virtual HCountVector getGapCounts(
    		 const HAlignandumVector & sequences,
    		 AggregateType aggregate_type = AggSum) const;


 protected:
    /** free all memory. Tell all stored objects to destruct themselves */
    virtual void freeMemory();

    /** I store an array of handles to alignatum objects. */
    mutable std::vector<HAlignment> mRows;

    /** flag for recording aligned columns */
    mutable std::vector<bool> mIsAligned;

    /** the length of the multiple alignment */
    mutable int mLength;

    /** the first aligned column of the multiple alignment */
    mutable int mFrom;


 private:

	 /** update the aligned flag mapping onto new */
	 virtual void updateAligned(
			 const HAlignment & map_mali2sequence );

	 /** re-build the aligned flag*/
	 virtual void buildAligned();

	 /** update the length of the multiple alignment */
	 virtual void updateLength();

};


}

#endif /* IMPL_MULTIPLE_ALIGNMENT_H */

