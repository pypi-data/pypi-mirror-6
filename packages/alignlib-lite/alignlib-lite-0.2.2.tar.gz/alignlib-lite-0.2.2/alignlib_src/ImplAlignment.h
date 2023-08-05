/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignment.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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

#ifndef IMPL_ALIGNATA_H
#define IMPL_ALIGNATA_H 1

#include <iosfwd>
#include "alignlib_fwd.h"
#include "Alignment.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{

  /** basic implementation for aligned objects.

	  This class keeps track of alignment coordinates. These are always ensured
	  to be correct after every operation, even if the length of the alignment has
	  not been evaluated.

      @author Andreas Heger
      @version $Id: ImplAlignment.h,v 1.3 2004/03/19 18:23:40 aheger Exp $
      @short basic implementation class for aligned objects
  */

class ImplAlignment : public Alignment, public ImplAlignlibBase
{

 public:
    //------------------> constructors / destructors <---------------------------------------------------------
    /** empty constructor */
    ImplAlignment();

    /** copy constructor */
    ImplAlignment( const ImplAlignment &src );

    /** destructor */
    virtual ~ImplAlignment();

    //----------------> accessors <------------------------------------------------------------------------------
    /** returns the alignment score
     */
    virtual Score getScore() const;

    /** returns the length of the alignment including gaps in both row and col.
     */
    virtual Position getLength() const;

    /** returns the number of gaps in the alignment
     */
    virtual Position getNumGaps() const;

    /** returns the number of aligned positions
      * */
     virtual Position getNumAligned() const;

    /** set the alignment score
     */
    virtual void setScore( Score score );

    /** return true if the alignment is empty
     */
    bool isEmpty() const;

    /** switch row and column
     */
    virtual void switchRowCol();

    /** move aligned position by offsets in row and/or column
     */
    virtual void moveAlignment( Position row_offset, Position col_offset);

    /** maps a residue from row to column. returns 0, if not found. This default, but working implementation is
	very time-inefficient, especially, if you want to map the whole thing. Other implementations in derived
	classes can be much faster */
    virtual Position mapRowToCol( Position pos, SearchType search = NO_SEARCH ) const;

	/** maps a residue from row to column.
	 *
	 * This operator is synonymous to mapRowToCol( pos ).
	 *
	 * @param pos 		Position to map.
	 * @param search 	If pos does not map to a residue directly, search
	 * 					in direction given by search.
	 *
	 * returns NO_POS if mapping failed.
	 * */
    virtual Position operator[]( const Position & pos ) const;

    /** maps a residue from column to row. returns 0, if not found. This default, but working implementation is
	very time-inefficient, especially, if you want to map the whole thing. Other implementations in derived
	classes can be much faster*/
    virtual Position mapColToRow( Position pos, SearchType search = NO_SEARCH ) const;

    virtual void removeRowRegion( Position from, Position to );

    virtual void removeColRegion( Position from, Position to);

	/** insert position in row. Aligned residues are shifted downwards
	 *
	 * @param position	position at which to insert residues. If this position
	 *              was aligned, it will now be unaligned
	 * @param residues  number of residues to insert.
	 */
	virtual void insertRow(
			const Position & from,
			const Position & residues = 1);

	/** insert residues in col. Aligned residues are shifted downwards
	 *
	 * @param from	position at which to add residues. If this position
	 *              was aligned, it will now be unaligned
	 * @param distance shift residues by by distance
	 * */
	virtual void insertCol(
			const Position & from,
			const Position & residues = 1);

    virtual void clear() ;

	/** returns the first residue aligned in row */
	virtual Position getRowFrom() const;

	/** returns the last residue aligned in row */
	virtual Position	getRowTo() const;

	/** returns the first residue aligned in col */
	virtual Position	getColFrom() const;

	/** returns the last residue aligned in col */
	virtual Position	getColTo()   const;

    /** @brief adds a pair of residues to the alignment
	(have to add this here, otherwise it won't compile!. It seems that overloaded
	functions can not be separately implemented) */
    virtual void addPair( const ResiduePair & new_pair );

    /** adds a pair of residues to the alignment */
    virtual void addPair( Position row, Position col, Score score = 0);

	/** adds a diagonal to the alignment.
	 *
	 * @param row_from	  	row start
	 * @param row_to	  	row end
	 * @param col_offset	column offset.
	*/
	virtual void addDiagonal(
			Position row_from,
			Position row_to,
			Position col_offset = 0);

    /** removes a pair */
    virtual void removePair( const ResiduePair & pair );

	/** merge this alignment with another.
	 *
	 * @param other @ref Alignment to merge with
	 * @param invert if true, switch row and col in the other alignment before merging
	 * */
	virtual void merge(
			const HAlignment & other,
			bool invert = false );

    /** apply a map to the alignment.
     *
     * This method maps all rows/columns with a map
     * in another alignment.
     *
     * @param other @ref Alignment to map with
     * @param mode Combination mode.
     *
     * */
    virtual void map(
    		const HAlignment & other,
    		const CombinationMode & mode );


    /*-----------------> I/O <------------------------------------------------------------------------------ */
    virtual void write(std::ostream & output ) const;


 protected:
    /** the length has changed of the alignment */
    virtual void setChangedLength();

    /** set length of the alignment */
    virtual void setLength( Position length ) const;

    /** set length of the alignment */
    virtual void setNumGaps( Position num_gaps ) const;

    /** calculate alignment length */
    virtual void calculateLength() const;

    /** called update boundaries if alignment has changed
     * This function can not be generic, because it can not use
     * the iterator interface. In some child classes, the iterators
     * rely on the boundaries to be known.
     * */
    virtual void updateBoundaries() const = 0;

    /** flag, whether alignment length has changed. Protected, because some childs need to query and
     set this flag.
    */
    mutable bool mChangedLength;

    /** the alignment coordinates */
    mutable Position mRowFrom;
    mutable Position mRowTo;
    mutable Position mColFrom;
    mutable Position mColTo;

 private:

    /** length of alignemnt, has to be mutable, since length evaluation is lazy */
    mutable Position mLength;

    /** total score of alignment */
    Score mScore;

    /** number of gaps in alignment */
    mutable Position mNumGaps;


};


}

#endif /* IMPL_ALIGNATA_H */

