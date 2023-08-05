/*
  alignlib - a library for aligning protein sequences

  $Id: MultipleAlignment.h,v 1.6 2004/09/16 16:02:38 aheger Exp $

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

#ifndef MULTIPLEALIGNMENT_H
#define MULTIPLEALIGNMENT_H 1

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
    @version $Id: MultipleAlignment.h,v 1.6 2004/09/16 16:02:38 aheger Exp $
*/
class MultipleAlignment : public virtual AlignlibBase
{

    friend std::ostream & operator<<( std::ostream &, const MultipleAlignment &);

    // class member functions
 public:

    // constructors and desctructors
    /** empty constructor */
    MultipleAlignment  ();

    /** copy constructor */
    MultipleAlignment  (const MultipleAlignment &);

    /** destructor */
    virtual ~MultipleAlignment ();

    //---------------------------------------------------------------------------------------
    /*------- accessors --------------------------------------------------------------------*/
    /** returns the length (number of columns) of the multiple alignment.
     *
     * All objects in a multiple alignment have the same length.
     *
     * @return the length of the multiple alignment. */
    virtual Position getLength() const = 0;

    /** sets the length of the multiple alignment.
     *
     * @exception AlignlibException raised if alignment is not empty.
	*/
    virtual void setLength( Position length) = 0;

    /** returns the number of sequences in this multiple alignment.
     *
     * @return number of sequences in alignment.
     */
    virtual int getNumSequences() const = 0;

    /** returns a row in the multiple alignment.
     *
     * This allows treating the multiple alignment as a two-dimensional matrix.
     * Since string does define operator[] as well, you can access the symbol in column
     * c and row r by calling symbol =  multiple_alignment[r][c]
     *
     * @param row row of multiple alignment.
     * return string of aligned sequence.
    */
    virtual const std::string & operator[]( int row ) const = 0;

    /** returns a row in the multiple alignment.
     *
     * @param row row of multiple alignment.
     * return a @ref Alignatum object
    */
    virtual HAlignatum getRow( int row ) const = 0;

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

    /*------------------- functions for adding new members to the multiple alignment---------*/


    /** add an @ref Alignatum object to the multiple alignment.
     *
     *
	@param src	 @ref Alignatum object to add.
	@param alignment @ref Alignment that maps src to mali.
    @param mali_is_in_row			true, if the multiple alignment is in the row of the alignment.
	@param insert_gaps_mali			true, if gaps shall be inserted into the multiple alignment.
	@param insert_gaps_alignatum	analogous to insert_gaps_alignatum.
	@param use_end_mali				true, if not-aligned residues at the ends of the multiple alignment
									shall be kept.
	@param use_end_alignatum		analogous to use_end_mali.
    */
    virtual void add( const HAlignatum & src,
    		const HAlignment & alignment,
    		bool mali_is_in_row = true,
    		bool insert_gaps_mali = true,
    		bool insert_gaps_alignatum= true,
    		bool use_end_mali = false,
    		bool use_end_alignatum = false) = 0;

    /** add an @ref Alignatum object to mali.
     *
     * The @ref Alignatum object has to have the same length as the
     * mutliple alignment.
     * @param src @ref Alignatum object to add.
     */
    virtual void add( const HAlignatum & src ) = 0;

    /** add a @ref MultipleAlignment object to the multiple alignment.
     *
     *
	@param src	 @ref MultipleAlignment object to add.
	@param alignment @ref Alignment that maps src to mali.
    @param mali_is_in_row			true, if the multiple alignment is in the row of the alignment.
	@param insert_gaps_mali			true, if gaps shall be inserted into the multiple alignment.
	@param insert_gaps_alignatum	analogous to insert_gaps_alignatum.
	@param use_end_mali				true, if not-aligned residues at the ends of the multiple alignment
									shall be kept.
	@param use_end_alignatum		analogous to use_end_mali.
    */
    virtual void add(
    		const HMultipleAlignment & src,
    		const HAlignment & alignment,
    		bool mali_is_in_row = true,
    		bool insert_gaps_mali = true,
    		bool insert_gaps_alignatum= true,
    		bool use_end_mali = false,
		    bool use_end_alignatum = false) = 0;

    /** add a multiple alignment.
     *
     * Both multiple alignments have to have the same length.
     *
     * @param src @ref MultipleAlignment to add.
     */
    virtual void add( const HMultipleAlignment & src ) = 0;

    /** returns true, if the alignment is empty.
     *
     * @return true, if the alignment is emtpy.
     * */
    virtual bool isEmpty() const = 0;

    /** clears the multiple alignment
    */
    virtual void clear() = 0;

    DEFINE_ABSTRACT_CLONE( HMultipleAlignment )

    /** write the multiple alignment to a stream
     *
     * @param output output stream.
    */
    virtual void write( std::ostream & output ) const = 0;
};

}

#endif /* MULTIPLE_ALIGNMENT_H */

