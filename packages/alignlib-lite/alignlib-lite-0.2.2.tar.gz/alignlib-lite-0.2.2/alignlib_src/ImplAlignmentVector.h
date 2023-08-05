/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignmentVector.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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

#ifndef IMPL_ALIGNATA_VECTOR_H
#define IMPL_ALIGNATA_VECTOR_H 1

#include <iosfwd>
#include <vector>
#include <cassert>
#include "alignlib_fwd.h"
#include "ImplAlignment.h"

namespace alignlib {

class Alignandum;

/** alignment, where residues are kept in a vector.

    Residues are kept in a vector.

    It is not assumed that the alignment is linear, meaning that
    for all i < j : col[i] < col[j]

    The advantages:
    @li mapping is much faster

    The disadvantages:
    @li uses more memory for all the pairs, that are not part of the alignment
    @li iterating over all pairs is slower, since gaps have to be skipped explicitely.

    Implementation details:

    If the alignment is empty, mRowFrom is larger than mRowTo. This property is needed
    at some checks (for example in ImplAlignmentVector_iterator)

    @author Andreas Heger
    @version $Id: ImplAlignmentVector.h,v 1.3 2004/03/19 18:23:40 aheger Exp $
    @short protocol class for aligned objects
 */
class ImplAlignmentVector : public ImplAlignment
{

	typedef std::vector<ResiduePair> PAIRVECTOR;
	typedef PAIRVECTOR::iterator PairIterator;
	typedef PAIRVECTOR::const_iterator PairConstIterator;

	friend class ConstIterator;

public:

	//------------------> constructors / destructors <---------------------------------------------------------
	/** constructor */
	ImplAlignmentVector();

	/** copy constructor */
	ImplAlignmentVector( const ImplAlignmentVector &src );

	/** destructor */
	virtual ~ImplAlignmentVector();

	//------------------------------------------------------------------------------------------------------------
	virtual HAlignment getNew() const;

	/** return an identical copy */
	virtual HAlignment getClone() const;

	//------------------------------------------------------------------------------------------------------------
	/**
       @short Iterator over an alignment.
	 */
	class ImplAlignmentVector_Iterator : public Alignment::Iterator
	{
	public:
		ImplAlignmentVector_Iterator(const PAIRVECTOR & container,
				Position current,
				Position from,
				Position to) :
					mContainer( container ),
					mCurrentRow( current ),
					mFirstRow( from),
					mLastRow( to )
					{
			if (mCurrentRow >= mLastRow || to == NO_POS || mContainer.size() == 0)
				mCurrentRow = NO_POS;
		};

		ImplAlignmentVector_Iterator( const ImplAlignmentVector_Iterator & src ) :
			mContainer( src.mContainer),
			mCurrentRow( src.mCurrentRow),
			mFirstRow( src.mFirstRow),
			mLastRow( src.mLastRow) {};

			virtual ~ImplAlignmentVector_Iterator() {};

			virtual Iterator * getClone() const {return new ImplAlignmentVector_Iterator( *this );}

			/** dereference operator: runtime error, if out of bounds? */
			virtual const ResiduePair & getReference() const
			{
				assert( mCurrentRow >= 0 );
				return mContainer[mCurrentRow];
			}

			/** for indirection */
			virtual const ResiduePair * getPointer() const
			{
				if (mCurrentRow != NO_POS)
					return &mContainer[mCurrentRow];
				else
					return NULL;
			}

			/** advance one position, until you find an aligned pair */
			virtual void next()
			{
				mCurrentRow++;
				while (mCurrentRow < mLastRow && mContainer[mCurrentRow].mRow == NO_POS )
					mCurrentRow++;
				if (mCurrentRow >= mLastRow)
					mCurrentRow = NO_POS;
			}

			/** step back one position, until you find an aligned pair */
			virtual void previous()
			{
				mCurrentRow--;
				while (mCurrentRow >= mFirstRow && mContainer[mCurrentRow].mRow == NO_POS)
					mCurrentRow--;
				if (mCurrentRow < mFirstRow)
					mCurrentRow = NO_POS;
			}

	private:
		const PAIRVECTOR & mContainer;
		Position mCurrentRow;
		Position mFirstRow;
		Position mLastRow;
	};

	/** return const iterator */
	virtual AlignmentIterator begin() const;

	/** return const iterator */
	virtual AlignmentIterator end() const;

	//----------------> accessors <------------------------------------------------------------------------------

	/** returns the first aligned pair. Have to create a copy not a reference, because not all alignments will have
	a list of pairs ready */
	virtual ResiduePair front() const;

	/** returns the last aligned pair */
	virtual ResiduePair back() const;

	/** adds a pair of residue to the alignment */
	virtual void addPair( const ResiduePair & pair );

	/** removes a pair of residues from the alignment */
	virtual void removePair( const ResiduePair & old_pair );

	/** retrieves a pair of residues from the alignment */
	virtual ResiduePair getPair( const ResiduePair & p) const;

	/** maps a residue from row to column. returns 0, if not found. This is quick, since there is
	only one lookup in the array needed.*/
	virtual Position mapRowToCol( Position pos, SearchType search = NO_SEARCH ) const;

	/** move alignment */
	virtual void moveAlignment( Position row_offset, Position col_offset);

	/** removes a row-region in an alignment */
	virtual void removeRowRegion( Position from, Position to );

	/** removes a column-region in an alignment */
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

	/** clear the current alignemnt */
	void clear();
	protected:

		/** reset boundaries mRowFrom and mRowTo after the deletion of pairs */
		void resetBoundaries();

		/** update boundaries in case alignment length has changed */
		virtual void updateBoundaries() const;

	private:

		/** clear container */
		void clearContainer();

		/** Vector of residue pairs */
		PAIRVECTOR mPairs;

};



}

#endif /* _ALIGNATA_H */

