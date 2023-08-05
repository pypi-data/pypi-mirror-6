/*
  alignlib - a library for aligning protein sequences

  $Id: Alignment.h,v 1.3 2004/03/19 18:23:39 aheger Exp $

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

#ifndef ALIGNATA_H
#define ALIGNATA_H 1

#include <iosfwd>
#include <string>
#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

	/**
   	@short A residuepair containing row, column, and a score.

   	This encapsulates the most basic information for an aligned residue pair.

   	Use an @ref ResidueDecorator object to attach more information to
   	a residue pair.
	 */

struct ResiduePair
{
	/** Base class for residue aligned residues.
	 */

	friend std::ostream & operator<< (std::ostream &, const ResiduePair &);

	/** empty constructor.
	 *
	 * An empty residue pair has NO_POS as row and column and a score of 0.
	 */
	ResiduePair() : mRow(NO_POS), mCol(NO_POS), mScore(0) {}

	ResiduePair( Position a, Position b, Score c = 0) : mRow(a), mCol(b), mScore(c) {}

	/** copy constructor.
	 */
	ResiduePair( const ResiduePair & src) :
		mRow(src.mRow), mCol(src.mCol), mScore(src.mScore) {}

	/** assignment operator.
	*/
	ResiduePair& operator=( const ResiduePair & src)
	{
		mRow = src.mRow;
		mCol = src.mCol;
		mScore = src.mScore;
		return *this;
	}

	/** return the diagonal of this residue pair.
	 */
	Position getDiagonal() const
	{
		return mCol - mRow;
	}

	/** the row coordinate of this residue pair
	 */
	Position mRow;

	/** the col coordinates of this residue pair
	 */
	Position mCol;

	/** the score of this residue pair
	 */
	Score mScore;
};

bool operator==( const ResiduePair & x, const ResiduePair & y);
bool operator!=( const ResiduePair & x, const ResiduePair & y);

/**
    @short Protocol class for pairwise alignments.

    Tthe purpose of this class to provide a mapping between
    two objects. In true dynamic programming spirit, the
    two objects are called "row" and "col".

    Different implementations of this interface store residues
    in different order and implement different efficiences in
    mapping residues.

    Each alignment provides iterators. However,
    since the implementation differs between the different
    container types, I went for passive iterators, unlike
    the STL iterators, which are active. A passive iterator
    relies on the collection to manage its advancement and
    therefore has to cooperate closely with its container.

    This class is a protocol class and as such defines only
    the general interface.

 */

class Alignment : public virtual AlignlibBase
{
	friend std::ostream & operator<<(std::ostream &output, const Alignment &);

public:

	//------------------> constructors / destructors <---------------------------------------------------------
	/** empty constructor */
	Alignment();

	/** copy constructor */
	Alignment( const Alignment &src );

	/** destructor */
	virtual ~Alignment();

	DEFINE_ABSTRACT_CLONE( HAlignment )

	//------------------------------------------------------------------------------------------------------------
	/**
       @short Iterator over an alignment.

       Only const iterators are provide. Changing mRow or mCol would
       leave the container in an undefined state.

       If you need to modify the score of a @ref ResiduePair returned
       by an iterator, cast away the const-ness.
	 */
	class Iterator
	{
	public:
		Iterator() {};

		Iterator( const Iterator & src ) {};

		virtual ~Iterator() {};

		virtual Iterator * getClone() const = 0;

		/** dereference operator */
		virtual const ResiduePair & getReference() const = 0;

		/** for indirection */
		virtual const ResiduePair * getPointer() const = 0;

		/** advance one position */
		virtual void next() = 0;

		/** step back one position */
		virtual void previous() = 0;
	};

	/** returns an iterator pointing to the first element in the container
	 */
	virtual AlignmentIterator begin() const = 0;

	/** returns an iterator pointing one past the last element in the container.
	 */
	virtual AlignmentIterator end() const = 0;

	//----------------> accessors <------------------------------------------------------------------------------

	/** get the score of the alignment
	 */
	virtual Score getScore() const = 0;

	/** get the length of an alignment

     The length of an alignment is the number of aligned residue pairs plus
     the number gaps.
	 */
	virtual Position getLength() const = 0 ;

	/** get the number of gaps in the alignment
	 *
	 * Gaps are counted in either sequence.
	 * */
	virtual Position getNumGaps() const = 0;

    /** get the number of aligned positions in the alignment.
     * */
    virtual Position getNumAligned() const = 0;

	/** set the alignment score.
	 *
	 * @param score score to set.
	 * */
	virtual void setScore( Score score ) = 0;

	/** returns true, if alignment is empty */
	virtual bool isEmpty() const = 0;

	/** returns the first residue aligned in row
	 * */
	virtual Position getRowFrom() const = 0;

	/** returns one past the last residue aligned in row
	 * */
	virtual Position getRowTo() const = 0;

	/** returns the first residue aligned in col
	 * */
	virtual Position getColFrom() const = 0;

	/** returns one past the last residue aligned in col
	 * */
	virtual Position getColTo() const = 0;

	/** returns a copy of the first aligned pair.
	 * */
	virtual ResiduePair front() const = 0;

	/** returns a copy of the last aligned pair
	 * */
	virtual ResiduePair back() const = 0;

	/** adds a pair of residues to the alignment
	 *
	 * @param pair The residue pair to be added.
	 * */
	virtual void addPair( const ResiduePair & pair ) = 0;

	/** adds a pair of residues to the alignment */
	virtual void addPair( Position row, Position col, Score score = 0) = 0;

	/** adds a diagonal to the alignment.
	 *
	 * @param row_from	  	row start
	 * @param row_to	  	row end
	 * @param col_offset	column offset.
	*/
	virtual void addDiagonal(
			Position row_from,
			Position row_to,
			Position col_offset = 0) = 0;

	/** removes a residue pair from the alignment
	 *
	 * @param pair @ref ResiduePair to be removed.
	*/
	virtual void removePair( const ResiduePair & pair ) = 0;

	/** retrieves a copy of a residue pair.
	 *
	 * Different containers will match residue pairs differently
	 * (by row, col, or diagonal).
	 *
	 * @param row row of residue pair
	 * */
	virtual ResiduePair getPair( const ResiduePair & p) const = 0;

	/** move alignment
	 *
	 * @param row_offset	add row_offset to row coordinates.
	 * @param col_offset	add col_offset to col coordinates.
	 * */
	virtual void moveAlignment( Position row_offset, Position col_offset) = 0;

	/** maps a residue from row to column.
	 *
	 * @param pos 		Position to map.
	 * @param search 	If pos does not map to a residue directly, search
	 * 					in direction given by search.
	 *
	 * returns NO_POS if mapping failed.
	 * */
	virtual Position mapRowToCol( Position pos, SearchType search = NO_SEARCH ) const = 0;

	/** maps a residue from row to column.
	 *
	 * This operator is synonymous to mapRowToCol( pos ).
	 *
	 * @param pos 		Position to map.
	 * returns NO_POS if mapping failed.
	 * */
    virtual Position operator[]( const Position & pos ) const = 0;

	/** maps a residue from row to column.
	 *
	 * @param pos 		Position to map.
	 * @param search 	If pos does not map to a residue directly, search
	 * 					in direction given by search.
	 *
	 * returns NO_POS if mapping failed.
	 */
	virtual Position mapColToRow( Position pos, SearchType search = NO_SEARCH ) const = 0;

	/** removes a row-region in an alignment
	 *
	 * @param from	start of region in row to remove
	 * @param to 	end of region in row to remove
	 */

	virtual void removeRowRegion( Position from, Position to ) = 0;

	/** removes a col-region in an alignment
	 *
	 * @param from	start of region in col to remove
	 * @param to 	end of region in col to remove
	 * */
	virtual void removeColRegion( Position from, Position to) = 0;

	/** insert position in row. Aligned residues are shifted downwards
	 *
	 * @param position	position at which to insert residues. If this position
	 *              was aligned, it will now be unaligned
	 * @param residues  number of residues to insert.
	 */
	virtual void insertRow(
			const Position & from,
			const Position & residues = 1) = 0;

	/** insert residues in col. Aligned residues are shifted downwards
	 *
	 * @param from	position at which to add residues. If this position
	 *              was aligned, it will now be unaligned
	 * @param distance shift residues by by distance
	 * */
	virtual void insertCol(
			const Position & from,
			const Position & residues = 1) = 0;


	/** switch row and column in the alignment
	 * */
	virtual void switchRowCol() = 0;

	/** clear the current alignemnt
	*/
	virtual void clear() = 0;

	/** merge this alignment with another.
	 *
	 * @param other @ref Alignment to merge with
	 * @param invert if true, switch row and col in the other alignment before merging
	 * */
	virtual void merge(
			const HAlignment & other,
			bool invert = false ) = 0;

	/** apply a map to the alignment.
	 *
	 * This method maps all rows/columns with a map
	 * in another alignment.
	 *
	 * The alignment mode denotes whether row or col are mapped.
	 * The first letter denotes whether row or col are mapped.
	 * The second letter denotes whether row or col in other are
	 *   matched up to the value that is replaced.
	 *
	 * RR: row is replaced with corresponding R->C from other
	 * RC: row is replaced with corresponding C->R from other
	 * CC: col is replaced with corresponding R->R from other
	 * CR: col is replaced with corresponding R->C from other.
	 * @param other @ref Alignment to map with
	 * @param mode Combination mode.
	 *
	 * */
	virtual void map(
			const HAlignment & other,
			const CombinationMode & mode ) = 0;

	/*-----------------> I/O <------------------------------------------------------------------------------ */
	/** write human readable representation of alignment to stream
	 *
	 * @param output stream to output the alignment.
	 *
	 * see @ref AlignmentFormat for formatted output of alignments.
	 */
	virtual void write(std::ostream & output ) const = 0;

};

}
#endif /* _ALIGNATA_H */

