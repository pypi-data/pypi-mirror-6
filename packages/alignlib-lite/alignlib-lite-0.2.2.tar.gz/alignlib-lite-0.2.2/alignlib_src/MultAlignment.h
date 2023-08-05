/*
  alignlib - a library for aligning protein sequences

  $Id: MultAlignment.h,v 1.6 2004/09/16 16:02:38 aheger Exp $

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

#ifndef MULTALIGNMENT_H
#define MULTALIGNMENT_H 1

#include <iosfwd>
#include <string>

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

/**
    @short Protocoll class for multiple alignments.

    Multiple alignments are collections of aligned sequences (objects of type
    @ref Alignatum).

    This class is a protocol class and as such defines only the general interface

    About the parameter skip_gaps: When skip_gaps is set to true, then the current
    multiple alignment is regarded as a master multiple alignment and no gaps are
    inserted into this alignment. When it is not set, gaps are added in the middle
    and the ends.

    @author Andreas Heger
    @version $Id: MultAlignment.h,v 1.6 2004/09/16 16:02:38 aheger Exp $
*/
class MultAlignment : public virtual AlignlibBase
{

    friend std::ostream & operator<<( std::ostream &, const MultAlignment &);

    // class member functions
 public:

    // constructors and desctructors
    /** empty constructor */
    MultAlignment  ();

    /** copy constructor */
    MultAlignment  (const MultAlignment &);

    /** destructor */
    virtual ~MultAlignment ();

    DEFINE_ABSTRACT_CLONE( HMultAlignment )

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
				const ExpansionType & expansion_type ) const = 0;

    //---------------------------------------------------------------------------------------
    /*------- accessors --------------------------------------------------------------------*/
    /** returns the length (number of columns) of the multiple alignment.
     *
     * All objects in a multiple alignment have the same length.
     *
     * @return the length (aligned positions) of the multiple alignment. */
    virtual Position getLength() const = 0;

    /** returns the first aligned column of the multiple alignment.
     *
     * @return the first aligned column of the multiple alignment. */
    virtual Position getFrom() const = 0;

    /** returns the last aligned column +1 of the multiple alignment.
     *
     * Note: this is synonymous to getLength()
     *
     * @return the last aligned column + 1 of the multiple alignment. */
    virtual Position getTo() const = 0;

    /** returns the number of sequences in this multiple alignment.
     *
     * @return number of sequences in alignment.
     */
    virtual int getNumSequences() const = 0;

    /** returns a row of the multiple alignment.
     *
     * @param row row of multiple alignment.
     * return multiple alignment
    */
    virtual const HAlignment operator[]( int row ) const = 0;

    /** returns a row of the multiple alignment.
     *
     * @param row row of multiple alignment.
     * return a @ref Alignatum object
    */
    virtual const HAlignment getRow( int row ) const = 0;

    /** erases an row from the multiple alignment
     *
     * @param row row to erase.
     * */
    virtual void eraseRow( int row ) = 0;

    /** return true, if a column is aligned.
     *
     * Unaligned columns result from adding
     * new sequences to the multiple alignment.
     *
     * @return true, if column @col is aligned.
     * */
    virtual bool isAligned( const Position & col ) = 0;


    /* ------------------ mutators ----------------------------------------------------------- */

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
    		const HAlignandumVector & sequences ) = 0;

    /** shrink multiple alignment
     *
     * All columns that contain only one alignment positions will be removed.
     * */
    virtual void shrink() = 0;

    /** merges another multiple alignment with this multiple alignment
      *
      * Both multiple alignments need to have the same number of
      * sequences.
      *
      * @param other the other multiple alignment.
      * */
     virtual void merge( const HMultAlignment & other ) = 0;

    /** move the multiple alignment
      *
      * shifts multiple alignment columns by @param position. A negative
      * position will shift to lower values.
      * @param position number of positions to shift
      * */
     virtual void move( const Position & position ) = 0;

     /** trims the multiple alignment
       *
       * removes all unaligned columns to the left of the multiple
       * alignment.
       * */
      virtual void trim() = 0;

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
			const CombinationMode & mode ) = 0;

    /*------------------- functions for adding new members to the multiple alignment---------*/


    /** add an @ref Alignment object to the multiple alignment.
     *
     * The alignment object maps the sequence to multiple alignment columns.
     *
	@param src	 @ref Alignment object to add.
	@param alignment @ref Alignment that maps src to mali.
    */
    virtual void add(
    		const HAlignment & map_mali2sequence ) = 0;

    /** add a @ref MultAlignment object to the multiple alignment.
     *
     * The alignment object maps the sequence to multiple alignment columns.
     * Note that some alignment information can be potentially lost. If two
     * sequence positions are aligned in @param src, but that column is not
     * in map_src2this, then the alignment of these two residues is lost.
     *
	@param src	 @ref MultipleAlignment object to add.
	@param alignment @ref Alignment that maps src to this mali.
    */
    virtual void add(
    		const HMultipleAlignment & src,
    		const HAlignment & map_src2this ) = 0;

    /** add a @ref MultAlignment object to the multiple alignment.
     *
     * The alignment object maps the sequence to multiple alignment columns.
     * Note that some alignment information can be potentially lost. If two
     * sequence positions are aligned in @param src, but that column is not
     * in map_mali2sequnce, then the alignment of these two residues is lost.
     *
	@param src	 @ref Alignment object to add.
	@param alignment @ref Alignment that maps src to mali.
    */
    virtual void add(
    		const HMultAlignment & src,
    		const HAlignment & map_mali2sequence ) = 0;

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
			const HAlignment & map_other2new) = 0;

    /** returns true, if the alignment is empty.
     *
     * @return true, if the alignment is emtpy.
     * */
    virtual bool isEmpty() const = 0;

    /** clears the multiple alignment
    */
    virtual void clear() = 0;

    /** write the multiple alignment to a stream
     *
     * @param output output stream.
    */
    virtual void write( std::ostream & output ) const = 0;

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
    virtual HPositionMatrix getPositionMatrix( const bool & transpose = false) const = 0;

    /** return column counts.
     *
     *  Return a vector with the number of aligned residues per column
     *
     * @return a vector of counts.
     */
    virtual HCountVector getColumnCounts() const = 0;

    /** return row counts.
     *
     *  Return a vector with the number of aligned residues per row
     *
     * @return a vector of counts.
     */
    virtual HCountVector getRowCounts() const = 0;

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
   		 AggregateType aggregate_type = AggSum) const = 0;

};

}

#endif /* MULTIPLE_ALIGNMENT_H */

