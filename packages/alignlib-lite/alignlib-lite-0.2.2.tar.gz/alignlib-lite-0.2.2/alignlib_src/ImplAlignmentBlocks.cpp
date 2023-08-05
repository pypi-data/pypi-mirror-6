/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignmentVector.cpp,v 1.4 2004/06/02 12:11:37 aheger Exp $

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


#include <iostream>
#include <iterator>
#include <iomanip>
#include <algorithm>
#include <set>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "ImplAlignmentBlocks.h"
#include "AlignmentIterator.h"
#include "AlignlibException.h"

using namespace std;

namespace alignlib
{

//------------------------------factory functions -----------------------------
HAlignment makeAlignmentBlocks()
{
	return HAlignment( new ImplAlignmentBlocks() );
}

struct ComparatorBlock
{
  bool operator()( const Block & x, const Block & y) const
  {
    return x.mRowStart < y.mRowStart;
  }
};

bool operator==( const Block & x, const Block & y)
{
	return (x.mRowStart == y.mRowStart) &&
		(x.mColStart == y.mColStart) &&
		(x.mSize == y.mSize);
}
bool operator!=( const Block & x, const Block & y)
{
	return !(x == y);
}

std::ostream & operator<< (std::ostream & output, const Block & src)
{
  output << src.mRowStart << "\t" << std::setw(5) << src.mColStart << "\t" << std::setprecision(4) << src.mSize;
  return output;
}
//------------------------------------< constructors and destructors >-----
ImplAlignmentBlocks::ImplAlignmentBlocks() :
	ImplAlignment(), mLastLookupBlock(mBlocks.end())
{
}

ImplAlignmentBlocks::ImplAlignmentBlocks( const ImplAlignmentBlocks& src) :
	ImplAlignment( src )
{
	debug_func_cerr(5);
	mBlocks.clear();
	std::copy(
			src.mBlocks.begin(),
			src.mBlocks.end(),
			std::back_inserter(mBlocks) );
	mLastLookupBlock = mBlocks.end();
}

ImplAlignmentBlocks::~ImplAlignmentBlocks( )
{
	debug_func_cerr(5);
	clear();
}

//------------------------------------------------------------------------------------------------------------
HAlignment ImplAlignmentBlocks::getNew() const
{
	return HAlignment( new ImplAlignmentBlocks() );
}

HAlignment ImplAlignmentBlocks::getClone() const
{
	return HAlignment( new ImplAlignmentBlocks( *this ) );
}

//-----------------------------------------------------------------------------------------------------------
AlignmentIterator ImplAlignmentBlocks::begin() const
{
	if (mChangedLength) calculateLength();
	return AlignmentIterator( new ImplAlignmentBlocksIterator( mBlocks.begin(), mBlocks.end() ));
}

AlignmentIterator ImplAlignmentBlocks::end() const
{
	if (mChangedLength) calculateLength();
	return AlignmentIterator( new ImplAlignmentBlocksIterator( mBlocks.end(), mBlocks.end() ));
}

//----------------> accessors <------------------------------------------------------------------------------

ResiduePair ImplAlignmentBlocks::front() const { return ResiduePair( mRowFrom, mColFrom) ; }
ResiduePair ImplAlignmentBlocks::back()  const { return ResiduePair( mRowTo, mColTo) ; }

//----------------------------------------------------------------------------------------------------------------------
void ImplAlignmentBlocks::addPair( const ResiduePair & pair )
{
	debug_func_cerr( 5 );

    debug_cerr( 5, "adding pair " <<  pair << " to container of size "
    		<< mBlocks.size() << " coords=" << mRowFrom << "-" << mRowTo << ":" << mColFrom << "-" << mColTo );

	ImplAlignment::addPair( pair );

	mBlocks.push_back( Block( pair.mRow, pair.mCol, 1));
}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignmentBlocks::addDiagonal(
		Position row_from,
		Position row_to,
		Position col_offset)
{
	if (row_from == NO_POS || row_to == NO_POS)
		return;

	Position col_from = row_from + col_offset;
	Position col_to   = row_to + col_offset;

	if (mRowFrom == NO_POS)
	{
		mRowFrom = row_from;
		mColFrom = col_from;
		mRowTo = row_to;
		mColTo = col_to;
	}
	else
	{
		if (row_from < mRowFrom)
			mRowFrom = row_from;
		if (row_to > mRowTo )
			mRowTo = row_to;
		if (col_from < mColFrom)
			mColFrom = col_from;
		if (col_to > mColTo)
			mColTo = col_to;
	}

	mBlocks.push_back( Block( row_from, col_from, row_to - row_from ) );
	setChangedLength();
}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignmentBlocks::moveAlignment( Position row_offset, Position col_offset)
{
	debug_func_cerr(5);

	if (isEmpty()) return;

	if (row_offset + mRowFrom < 0 )
		throw AlignlibException( "moving alignment out of bounds in row");
	if (col_offset + mColFrom < 0 )
		throw AlignlibException( "moving alignment out of bounds in col");

	BlockIterator it(mBlocks.begin()), it_end(mBlocks.end());

	// copy pointers from copy into mPairs
	for (; it != it_end; ++it)
	{
		it->mRowStart += row_offset;
		it->mColStart += col_offset;
	}

	// set new alignment coordinates
	mRowFrom += row_offset;
	mRowTo   += row_offset;
	mColFrom += col_offset;
	mColTo += col_offset;
}


//----------------------------------------------------------------------------------------------------------
/** retrieves a pair of residues from the alignment */
ResiduePair ImplAlignmentBlocks::getPair( const ResiduePair & p) const
{
	if (mChangedLength) calculateLength();
	if (p.mRow != NO_POS)
	{
		Position col = mapRowToCol( p.mRow );
		return ResiduePair( p.mRow, col );
	}
	else
	{
		return ResiduePair();
	}
}

//----------------------------------------------------------------------------------------------------------
BlockIterator ImplAlignmentBlocks::find( const Position & pos, const bool & previous) const
{
	debug_func_cerr(5);

	// out of range
	if (pos <= mRowFrom && pos > mRowTo)
		return mBlocks.end();

	// do quick lookup first - is pos in the last block previously found?
	// if not, check adjacent block. If not found there, do a full binary search.
	// The lookup is messy, as the binary_search returns the block after
	// pos, unless pos coincides directly with mRowStart of the block.
	// The cached lookup has to have the same behaviour.
	BlockIterator it(mLastLookupBlock);

	size_t n = mBlocks.size();

	if (n == 0)
	{
		// empty alignment
		return mBlocks.end();
	}
	else if (n == 1)
	{
		// only one block
		it = mBlocks.begin();
	}
	else if (!mChangedLength && it != mBlocks.end())
	{
		// update from a previous search
		// coordinate is before current block
		if (pos < it->mRowStart)
		{
			// check previous block
			--it;
			// can't reach end, as otherwise mRowFrom > pos
			// but check
			assert( it != mBlocks.end());

			// if not within this block, do binary search
			if (pos < it->mRowStart)
			{
				// do binary seach
				it = std::lower_bound( mBlocks.begin(), it,
										Block( pos, 0, 0),
										ComparatorBlock() );
				assert( it != mBlocks.end() );
				if (it->mRowStart != pos)
					--it;
			}

		}
		// coordinate is after current block
		else if (pos >= it->mRowStart + it->mSize)
		{
			// check next block
			++it;
			assert( it != mBlocks.end());
			if (pos < it->mRowStart)
			{
				// pos is within gap to next block
				--it;
			}
			else
			{
				// if not within next block, do a binary search
				if (pos >= it->mRowStart + it->mSize )
				{
					it = std::lower_bound( it, mBlocks.end(),
							Block( pos, 0, 0),
							ComparatorBlock() );
					if (it == mBlocks.end())
						--it;
					else if (it->mRowStart != pos)
						--it;
				}
			}
		}
	}
	else
	{
		// find new coordinate
		// this fails if there is only a single block and pos > mRowFrom
		// std::copy( mBlocks.begin(), mBlocks.end(), std::ostream_iterator<Block>(std::cerr, ",") );
		// std::cerr << pos << std::endl;
		it = std::lower_bound(
				mBlocks.begin(), mBlocks.end(),
				Block( pos, 0, 0),
				ComparatorBlock() );

		if (it == mBlocks.end())
			--it;
		else if (it->mRowStart != pos)
			--it;
	}

	debug_cerr( 5, "looking for " << pos << " found=" << *it );
	mLastLookupBlock = it;

	if (it == mBlocks.end()) return it;

	if (pos > it->mRowStart + it->mSize)
		return (previous ? it : mBlocks.end());
	else
		return it;
}

//----------------------------------------------------------------------------------------------------------
void ImplAlignmentBlocks::removePair( const ResiduePair & old_pair )
{
	if (mChangedLength) calculateLength();

	debug_func_cerr( 5 );
	Position pos = old_pair.mRow;

	BlockIterator it = find( pos );

	// residue not within block
	if (it == mBlocks.end())
		return;

	debug_cerr( 5, "query=" << pos<< " block=" << *it);

	if (it->mSize == 1)
		mBlocks.erase( it );
	else if (it->mRowStart == pos)
		it->shortenLeft( 1 );
	else if( it->mRowStart + it->mSize - 1 == pos)
		it->shortenRight( 1 );
	else
	{
		Position old_size = it->mSize;
		Position new_size = pos - it->mRowStart;
		Position new_row_start = it->mRowStart + new_size + 1;
		Position new_col_start = it->mColStart + new_size + 1;
		it->shortenRight( old_size - new_size + 1);
		++it;
		mBlocks.insert( it, Block( new_row_start, new_col_start, old_size - new_size));
	}

	ImplAlignment::removePair( old_pair );
}

//----------------------------------------------------------------------------------------------------------------
void ImplAlignmentBlocks::clearContainer()
{
	debug_func_cerr( 5 );
	mBlocks.clear();
}

//----------------------------------------------------------------------------------------------------------------
void ImplAlignmentBlocks::clear()
{
	debug_func_cerr( 5 );
	ImplAlignment::clear();
	clearContainer();
}

//--------------> mapping functions <----------------------------------------------------------------------------
Position ImplAlignmentBlocks::mapRowToCol( Position pos, SearchType search ) const
{
	if (mChangedLength) calculateLength();

	debug_func_cerr( 5 );
  if (mRowFrom == NO_POS) return NO_POS;
  if (isEmpty()) return NO_POS;

  if ( search == LEFT && pos >= mRowTo)
	  return mColTo;

  if ( search == RIGHT && pos < mRowFrom )
    return mColFrom;

  if (pos < mRowFrom || pos >= mRowTo) return NO_POS;

  BlockIterator it = find( pos, true );

  debug_cerr( 5, "query=" << pos<< " block=" << *it);

  // residue within block
  if (it->mRowStart + it->mSize > pos)
	  return pos + (it->getDiagonal());

  // residue after block
  if (search == LEFT)
  {
	  return it->mColStart + it->mSize - 1;
  }
  else if (search == RIGHT)
  {
	  ++it;
	  return it->mColStart;
  }
  else
  {
	  return NO_POS;
  }
}

//-----------------------------------------------------------------------------------------------------------
void ImplAlignmentBlocks::calculateLength() const
{
	updateBoundaries();
	mChangedLength = false;
}

//-----------------------------------------------------------------------------------------------------------
void ImplAlignmentBlocks::updateBoundaries() const
{
	debug_func_cerr( 5 );

	// ignore empty alignments
	// container is empty
	if (mBlocks.size() == 0)
	{
		mRowFrom = mRowTo = mColFrom = mColTo = NO_POS;
		setLength(0);
		setNumGaps(0);
		return;
	}
	// blocks are non-overlapping - simply sort, iterate and
	// extend. This is done in-place as the number of new
	// blocks is guaranteed to be smaller.
	std::sort( mBlocks.begin(), mBlocks.end(), ComparatorBlock() );

	BlockIterator it(mBlocks.begin()), it_end(mBlocks.end());

	// extent of current block
	Position row_last = it->mRowStart + it->mSize;
	Position col_last = it->mColStart + it->mSize;
	mColFrom = it->mColStart;
	mColTo = col_last;

	BlockIterator current_block (it);
	debug_cerr( 5, "block=" << *it);
	++it;
	Position naligned=0;
	Position ngaps=0;

	for (; it != it_end; ++it )
	{
		debug_cerr( 5, "block=" << *it);
		if (it->mSize <= 0) continue;
    	const Position row_from = it->mRowStart;
    	const Position col_from = it->mColStart;
    	const Position row_to = row_from + it->mSize;
    	const Position col_to = col_from + it->mSize;
    	Position d = 0;
    	if ((d = row_from - row_last) < 0)
    		throw AlignlibException( "__FILE__:__LINE__ overlapping blocks in row");

    	// check for extension
    	if ( d == 0 && (col_from - col_last) == 0)
    	{
    		debug_cerr( 5, "extension" );

    		row_last = row_to;
    		col_last = col_to;
    	}
    	else
    	{
    		current_block->mSize = row_last - current_block->mRowStart;
    		naligned += current_block->mSize;
    		ngaps += row_from-row_last+col_from-col_last;
    		row_last = row_from + it->mSize;
    		col_last = col_from + it->mSize;
    		++current_block;
    		current_block->mRowStart = row_from;
    		current_block->mColStart = col_from;
    	}

    	// get maximum boundaries
    	if (col_from < mColFrom) mColFrom = col_from;
    	if (col_to   > mColTo)   mColTo = col_to;
	}

	current_block->mSize = row_last - current_block->mRowStart;
	naligned += current_block->mSize;
	++current_block;
	mBlocks.erase( current_block, mBlocks.end());

	mRowFrom = mBlocks.front().mRowStart;
	mRowTo   = mBlocks.back().mRowStart + mBlocks.back().mSize;

	mLastLookupBlock = mBlocks.end();

	setLength( naligned + ngaps );
	setNumGaps( ngaps );
	debug_cerr( 5, "last block: row=" << mBlocks.back() );
	debug_cerr( 5, "new alignment coordinates: row=" << mRowFrom << "-" << mRowTo
			<< " col=" << mColFrom << "-" << mColTo
			<< " naligned=" << naligned << " gaps=" << ngaps);
}

/*
//-----------------------------------------------------------------------------------------------------------
void ImplAlignmentBlocks::removeRowRegion( Position from, Position to)
{
	debug_func_cerr(5);

	Position pos;

	if (from < mRowFrom)
		from = mRowFrom;

	if (to > mRowTo)
		to = mRowTo;

	debug_cerr( 5, "deleting in row from " << from << " to " << to );
	//TODO
	updateBoundaries();

	setChangedLength();

	return;
}
*/
} // namespace alignlib

