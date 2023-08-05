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
#include <algorithm>
#include <set>
#include <limits>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "ImplAlignmentVector.h"
#include "AlignmentIterator.h"

using namespace std;

namespace alignlib
{

/** by how much the vector grows */
#define GROWTH_FACTOR 2

//------------------------------factory functions -----------------------------
HAlignment makeAlignmentVector()
{
	return HAlignment( new ImplAlignmentVector() );
}

//------------------------------------< constructors and destructors >-----
ImplAlignmentVector::ImplAlignmentVector() :
	ImplAlignment()
{
}

ImplAlignmentVector::ImplAlignmentVector( const ImplAlignmentVector& src) :
	ImplAlignment( src )
{
	debug_func_cerr(5);
	mPairs.clear();
	std::copy(
			src.mPairs.begin(),
			src.mPairs.end(),
			std::back_inserter(mPairs) );
}

ImplAlignmentVector::~ImplAlignmentVector( )
{
	debug_func_cerr(5);

	clear();
}

//------------------------------------------------------------------------------------------------------------
HAlignment ImplAlignmentVector::getNew() const
{
	return HAlignment( new ImplAlignmentVector() );
}

HAlignment ImplAlignmentVector::getClone() const
{
	return HAlignment( new ImplAlignmentVector( *this ) );
}

//-----------------------------------------------------------------------------------------------------------
AlignmentIterator ImplAlignmentVector::begin() const
{
	return AlignmentIterator( new ImplAlignmentVector_Iterator( mPairs, mRowFrom, mRowFrom, mRowTo ));
}

AlignmentIterator ImplAlignmentVector::end() const
{
	return AlignmentIterator( new ImplAlignmentVector_Iterator(mPairs, NO_POS, mRowFrom, mRowTo));
}

//----------------> accessors <------------------------------------------------------------------------------

ResiduePair ImplAlignmentVector::front() const { return mPairs[mRowFrom]; }
ResiduePair ImplAlignmentVector::back()  const { return mPairs[mRowTo-1]; }

//----------------------------------------------------------------------------------------------------------------------
void ImplAlignmentVector::addPair( const ResiduePair & new_pair )
{
	debug_func_cerr( 5 );
	assert( new_pair.mRow >= 0);
	assert( new_pair.mCol >= 0);

    debug_cerr( 5, "adding pair " <<  new_pair << " to container of size "
    		<< mPairs.size() << " coords=" << mRowFrom << "-" << mRowTo << ":" << mColFrom << "-" << mColTo );

	ImplAlignment::addPair( new_pair );

	Position new_row = new_pair.mRow;

	size_t needed_size = std::max( mPairs.size(), (size_t)new_row + 1);

	if (mPairs.size() < needed_size)
		mPairs.resize( needed_size * GROWTH_FACTOR, ResiduePair() );

	mPairs[new_row] = new_pair;
}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignmentVector::moveAlignment( Position row_offset, Position col_offset)
{
	debug_func_cerr(5);

	if (isEmpty()) return;

	if (row_offset + mRowFrom < 0 )
		throw AlignlibException( "moving alignment out of bounds in row");
	if (col_offset + mColFrom < 0 )
		throw AlignlibException( "moving alignment out of bounds in col");

	// create copy of mPairs (= copy of pointers)
	PAIRVECTOR copy(mPairs);

	PairIterator it(copy.begin()), it_end(copy.end());

	size_t needed_size = std::max( mPairs.size(), (size_t)mRowTo + row_offset );

	// delete old alignment and allocate needed size
	mPairs.clear();
	mPairs.resize( needed_size, ResiduePair() );

	// copy pointers from copy into mPairs
	for (; it != it_end; ++it)
	{
		ResiduePair & p(*it);
		if (p.mRow != NO_POS)
		{
			p.mRow += row_offset;
			p.mCol += col_offset;
			mPairs[p.mRow] = p;
		}
	}
	// set new alignment coordinates
	mRowFrom += row_offset;
	mRowTo   += row_offset;
	mColFrom += col_offset;
	mColTo += col_offset;
}


//----------------------------------------------------------------------------------------------------------
/** retrieves a pair of residues from the alignment */
ResiduePair ImplAlignmentVector::getPair( const ResiduePair & p) const
{
	if (p.mRow != NO_POS)
		return mPairs[p.mRow];
	else
		return ResiduePair();
}

//----------------------------------------------------------------------------------------------------------
void ImplAlignmentVector::removePair( const ResiduePair & old_pair )
{
	// no resizing is done, just a range check
	if (old_pair.mRow >= mRowFrom && old_pair.mRow < mRowTo )
		mPairs[old_pair.mRow] = ResiduePair();
	ImplAlignment::removePair( old_pair );
}

//----------------------------------------------------------------------------------------------------------------
void ImplAlignmentVector::clearContainer()
{
	debug_func_cerr( 5 );
	mPairs.clear();
}

//----------------------------------------------------------------------------------------------------------------
void ImplAlignmentVector::clear()
{
	debug_func_cerr( 5 );
	ImplAlignment::clear();
	clearContainer();
}

//--------------> mapping functions <----------------------------------------------------------------------------
Position ImplAlignmentVector::mapRowToCol( Position pos, SearchType search ) const
{
  if (mRowFrom == NO_POS) return NO_POS;

  if ( search == LEFT && pos >= mRowTo)
    return mPairs[mRowTo - 1].mCol;

  if ( search == RIGHT && pos < mRowFrom )
    return mPairs[mRowFrom].mCol;

  if (pos < mRowFrom || pos >= mRowTo) return NO_POS;

  if (mPairs[pos].mRow != NO_POS)
    return mPairs[pos].mCol;
  
  if (search == NO_SEARCH)
    {
      return NO_POS;
    }
  else if (search == LEFT)
    {
      while (pos >= mRowFrom && mPairs[pos].mRow == NO_POS )
	--pos;
      if (pos < mRowFrom)
	return NO_POS;
    }
  else if (search == RIGHT)
    {
      while (pos < mRowTo && mPairs[pos].mRow == NO_POS )
	++pos;
      if (pos >= mRowTo)
	return NO_POS;
    }
  
  return mPairs[pos].mCol;
}


//-----------------------------------------------------------------------------------------------------------
void ImplAlignmentVector::updateBoundaries() const
{
	debug_func_cerr( 5 );

	debug_cerr( 5, "old alignment coordinates: row=" << mRowFrom << "-" << mRowTo << " col=" << mColFrom << "-" << mColTo );

	mRowFrom = mRowTo = mColFrom = mColTo = NO_POS;

	// ignore empty alignments
	// container is empty
	if (mPairs.size() == 0)
	  return;

	// no residues in container
	PAIRVECTOR::const_iterator it(mPairs.begin()), it_end(mPairs.end());
	while (it != it_end && it->mRow == NO_POS) ++it;
	if (it == it_end)
		return;

	mRowFrom = std::numeric_limits<Position>::max();
	mColFrom = std::numeric_limits<Position>::max();
	mRowTo = std::numeric_limits<Position>::min();
	mColTo = std::numeric_limits<Position>::min();


	for (; it != it_end; ++it )
	{
		// vector can contain empty entries
		if (it->mRow == NO_POS)
			continue;

    	const Position row = it->mRow;
    	const Position col = it->mCol;

		// get maximum boundaries
    	if (row < mRowFrom) mRowFrom = row;
    	if (col < mColFrom) mColFrom = col;
    	if (row > mRowTo)   mRowTo = row;
    	if (col > mColTo)   mColTo = col;
	}
	++mRowTo;
	++mColTo;

	debug_cerr( 5, "new alignment coordinates: row=" << mRowFrom << "-" << mRowTo << " col=" << mColFrom << "-" << mColTo );

}

//-----------------------------------------------------------------------------------------------------------
void ImplAlignmentVector::removeRowRegion( Position from, Position to)
{
	debug_func_cerr(5);

	Position pos;
	if (from == NO_POS || from < mRowFrom)
		from = mRowFrom;

	if (to == NO_POS || to > mRowTo)
		to = mRowTo;

	debug_cerr( 5, "deleting in row from " << from << " to " << to );

	// delete aligned positions
	for ( Position pos = from; pos < to; ++pos)
		mPairs[pos] = ResiduePair();

	updateBoundaries();

	setChangedLength();

	return;
}

//-----------------------------------------------------------------------------------------------------------
/* It is necessary to iterate from mFrowFrom to mRowTo, since the alignment need not be linear
 */
void ImplAlignmentVector::removeColRegion( Position from, Position to)
{
	debug_func_cerr(5);

	Position pos;

	if (mRowFrom == NO_POS) return;

	for (pos = mRowFrom; pos < mRowTo; pos++)
		if (mPairs[pos].mRow != NO_POS && mPairs[pos].mCol >= from && mPairs[pos].mCol < to)
			mPairs[pos] = ResiduePair();

	updateBoundaries();
	setChangedLength();
	return;
}

//-----------------------------------------------------------------------------------------------------------
void ImplAlignmentVector::insertRow(
		const Position & from,
		const Position & residues )
{
	if (from >= mRowTo) return;
	Position p = std::max( from, mRowFrom);

	for (Position x = p; x < mRowTo; ++x)
		if (mPairs[x].mRow != NO_POS)
			mPairs[x].mRow += residues;

	mPairs.insert( mPairs.begin() + p, residues, ResiduePair() );

	updateBoundaries();
	setChangedLength();
	return;
}

//-----------------------------------------------------------------------------------------------------------
void ImplAlignmentVector::insertCol(
		const Position & from,
		const Position & residues )
{
	debug_func_cerr( 5 );
	if (from >= mColTo) return;
	Position p = std::max( from, mColFrom);

	for (Position x = mRowFrom; x < mRowTo; ++x)
	{
		if (mPairs[x].mCol >= from)
			mPairs[x].mCol += residues;
	}

	updateBoundaries();
	setChangedLength();
	return;
}

//-----------------------------------------------------------------------------------------------------------
void ImplAlignmentVector::map(
		const HAlignment & other,
		const CombinationMode & mode )
{
	debug_func_cerr(5);

	// mapping is efficient for mode C{R,C}, for all others
	// revert to the default mapping mode.
	if (mode == RR || mode == RC)
		return ImplAlignment::map( other, mode );

	if (mode == CR)
	{
		for (Position x = 0; x < mPairs.size(); ++x)
			if (mPairs[x].mRow != NO_POS)
			{
				Position p = mapRowToCol(mPairs[x].mCol);
				if (p != NO_POS)
					mPairs[x].mCol = p;
				else
				{
					mPairs[x].mRow = mPairs[x].mCol = NO_POS;
					mPairs[x].mScore = 0;
				}

			}
	}
	else if (mode == CC )
	{
		for (Position x = 0; x < mPairs.size(); ++x)
			if (mPairs[x].mRow != NO_POS)
			{
				Position p = mapColToRow(mPairs[x].mCol);
				if (p != NO_POS)
					mPairs[x].mCol = p;
				else
				{
					mPairs[x].mRow = mPairs[x].mCol = NO_POS;
					mPairs[x].mScore = 0;
				}
			}
	}

	updateBoundaries();
	setChangedLength();
	return;
}

} // namespace alignlib

