/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignmentblocks.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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

#ifndef IMPL_ALIGNATA_BLOCKS_H
#define IMPL_ALIGNATA_BLOCKS_H 1

#include <iosfwd>
#include <vector>
#include <cassert>
#include "alignlib_fwd.h"
#include "ImplAlignment.h"

namespace alignlib 
{

struct Block 
{
	friend std::ostream & operator<< (std::ostream &, const Block &);
	
	Block( const Position row_start = NO_POS,
			const Position col_start = NO_POS,
			const Position size = 0) :
				mRowStart( row_start),
				mColStart( col_start),
				mSize( size ) {}

	inline Position getDiagonal() const
	{
		return mColStart - mRowStart; 
	}

	/** shorten block on the left side.
	 * 
	 * @param n number of positions to shorten block by.
	*/
	inline void shortenLeft( const Position & n)
	{
		mRowStart += n;
		mColStart += n;
		mSize -= n;
	}
	/** shorten block on the right side.
	 * 
	 * @param n number of positions to shorten block by.
	*/
	inline void shortenRight( const Position & n)
	{
		mSize -= n;
	}
	
	
	/** assignment operator. 
	 */
	Block & operator=( const Block & src) 
	{ 
		mRowStart = src.mRowStart; 
		mColStart = src.mColStart; 
		mSize = src.mSize; 
		return *this;
	}
	Position mRowStart;
	Position mColStart;
	Position mSize;
	
	
};

typedef std::vector<Block>Blocks;
typedef Blocks::iterator BlockIterator;
typedef Blocks::const_iterator BlockConstIterator;

/** blocked alignment. Aligned residues are stored in diagonals (blocks)

	Assumptions:
	The mapping is n:1, i.e., it is unique for each row.

    The advantages:
    @li the alignment uses little memory.

    The disadvantages:
    @li not as fast as a direct map
    @li iterating over all pairs is slower, since gaps have to be skipped explicitely.

    Implementation details:

	The object cashes the last position looked up in row. Thus, lookup on row via
	incremental searches is quick.

	Initially blocks a kept in an unsorted order and are not compressed while the
	alignment is in the construction phase. Thus, residue pairs are added as blocks of 
	size 1. To ensure low memory usage during construction, use addDiagonal for 
	adding larger blocks. Only when the alignment is queried are the blocks merged.
	This implementation is a compromise between fast and random order construction
	and quick queries. 

	This implementation will throw an exception if there are conflicting entries
	for the same row.

    @author Andreas Heger
    @version $Id: ImplAlignmentVector.h,v 1.3 2004/03/19 18:23:40 aheger Exp $
    @short protocol class for aligned objects
 */
class ImplAlignmentBlocks : public ImplAlignment 
{
public:

	//------------------------------------------------------------------------------------------------------------
	//------------------------------------------------------------------------------------------------------------
	/**
       @short Non-Const iterator over an alignment.
	 */
	class ImplAlignmentBlocksIterator : public Alignment::Iterator 
	{
	public:
		ImplAlignmentBlocksIterator( BlockIterator it, BlockIterator it_end) 
		: 
			Iterator(), mIterator( it ), mEnd( it_end ) 
			{
			if (it != it_end)
			{
				mPair.mRow = it->mRowStart;
				mPair.mCol = it->mColStart;
			}
			};

			ImplAlignmentBlocksIterator( const ImplAlignmentBlocksIterator & src ) 
			: 
				Iterator(src), mIterator( src.mIterator), mEnd( src.mEnd ), mPair(src.mPair)
				{};

				virtual ~ImplAlignmentBlocksIterator() 
				{};

				virtual ImplAlignmentBlocksIterator * getClone() const
				{
					return new ImplAlignmentBlocksIterator( mIterator, mEnd );
				}

				/** dereference operator
				 * 
				 * Const-ness is cast away. Do not mess with mRow or mCol with
				 * the returned pair. However, it might be used to set the score.
				 */
				virtual const ResiduePair & getReference() const 
				{ 
					return mPair;
				}

				/** for indirection
				 * 
				 * Const-ness is cast away. Do not mess with mRow or mCol with
				 * the returned pair. However, it might be used to set the score.
				 *  	    
				 */
				virtual const ResiduePair * getPointer() const 
				{ 
					if (mIterator == mEnd)
						return NULL;
					return &mPair; 
				}	

				/** advance one position */
				virtual void next() 
				{ 
					if (mIterator == mEnd) return;

					++mPair.mRow;
					++mPair.mCol;

					// switch to next block
					if (mIterator->mRowStart + mIterator->mSize <= mPair.mRow )
					{
						++mIterator;
						if (mIterator != mEnd)
						{
							mPair.mRow = mIterator->mRowStart;
							mPair.mCol = mIterator->mColStart; 
						}
					}
				}

				/** step back one position */
				virtual void previous() 
				{ 
					if (mIterator == mEnd) return;

					--mPair.mRow;
					--mPair.mCol;

					if (mIterator->mRowStart >= mPair.mRow )
					{
						--mIterator;
						if (mIterator != mEnd)
						{
							mPair.mRow = mIterator->mRowStart + mIterator->mSize - 1;
							mPair.mCol = mIterator->mColStart + mIterator->mSize - 1; 
						}
					}
				}

	private:
		BlockIterator mIterator;
		BlockIterator mEnd;
		ResiduePair mPair;
	};

	//------------------> constructors / destructors <---------------------------------------------------------
	/** constructor */
	ImplAlignmentBlocks();

	/** copy constructor */
	ImplAlignmentBlocks( const ImplAlignmentBlocks &src );

	/** destructor */
	virtual ~ImplAlignmentBlocks();

	//------------------------------------------------------------------------------------------------------------
	virtual HAlignment getNew() const;

	/** return an identical copy */
	virtual HAlignment getClone() const;

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
	// virtual void removeRowRegion( Position from, Position to );

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

	/** clear the current alignemnt */
	void clear();

	protected:

		/** reset boundaries mRowFrom and mRowTo after the deletion of pairs */
		void resetBoundaries();

		/** update boundaries in case alignment length has changed */
		virtual void updateBoundaries() const;

		/** find block containing residue
		 * @param pos residue to look up
		 * @param previous if set, return the previous block if the residue is not
		 *        found in any block. Otherwise, end() is returned.  
		 * @return the block containing the residue. 
		 */
		BlockIterator find( const Position & pos, const bool & previous = false) const;
	
	    /** calculate alignment length */
	    virtual void calculateLength() const;
		
	private:

		/** clear container */
		void clearContainer();

		/** Starting positions of blocks and their sizes. This structure has to be
		 * mutable because it is cleaned up in updateBoundaries. */
		mutable std::vector<Block> mBlocks;

		/** the position of the found block in lookup */
		mutable BlockIterator mLastLookupBlock;
		
};



}

#endif /* _ALIGNATA_H */

