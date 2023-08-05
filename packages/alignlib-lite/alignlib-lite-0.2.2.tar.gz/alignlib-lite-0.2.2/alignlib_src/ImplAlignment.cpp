/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignment.cpp,v 1.4 2004/06/02 12:11:37 aheger Exp $

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
#include <string>
#include <stdio.h>
#include "ImplAlignment.h"
#include "Alignandum.h"
#include "Alignatum.h"
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignmentIterator.h"
#include "Alignment.h"
#include "AlignlibException.h"

using namespace std;

namespace alignlib
{

//--------------------------------------------------------------------------------------------------------------
// constructors and desctructors
//--------------------------------------------------------------------------------------------------------------
ImplAlignment::ImplAlignment() : mChangedLength(true), mLength(0), mScore(0), mNumGaps( 0 ),
mRowFrom(NO_POS),
mRowTo(NO_POS),
mColFrom( NO_POS),
mColTo(NO_POS)
{
}

ImplAlignment::ImplAlignment( const ImplAlignment & src ) :
	mChangedLength(src.mChangedLength),
	mLength( src.mLength),
	mScore (src.mScore),
	mNumGaps (src.mNumGaps),
	mRowFrom( src.mRowFrom ),
	mRowTo( src.mRowTo ),
	mColFrom( src.mColFrom ),
	mColTo( src.mColTo )
	{
	debug_func_cerr(5);

	}

ImplAlignment::~ImplAlignment()
{
	debug_func_cerr(5);

}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignment::setChangedLength()
{
	mChangedLength = true;
}
//--------------------------------------------------------------------------------------------------------------
void ImplAlignment::setScore( Score score )
{
	mScore = score;
}

//--------------------------------------------------------------------------------------------------------------
Position ImplAlignment::getRowFrom() const { return mRowFrom; }
Position ImplAlignment::getRowTo() const { return mRowTo; }
Position ImplAlignment::getColFrom() const { return mColFrom; }
Position ImplAlignment::getColTo() const { return mColTo; }

//--------------------------------------------------------------------------------------------------------------
Score ImplAlignment::getScore() const
{
	return mScore;
}

//--------------------------------------------------------------------------------------------------------------
Position ImplAlignment::getLength() const
{
	if (mChangedLength)
		calculateLength();
	return mLength;
}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignment::clear()
{
	debug_func_cerr(5);

	mRowFrom = mRowTo = mColFrom = mColTo = NO_POS;
	mChangedLength = false;
	mLength = 0;
	mScore = 0;
	mNumGaps = 0;
}

Position ImplAlignment::getNumAligned() const
{
	if (mChangedLength)
		calculateLength();
	return mLength - mNumGaps;
}

//--------------------------------------------------------------------------------------------------------------
Position ImplAlignment::getNumGaps() const
{
	if (mChangedLength)
		calculateLength();
	return mNumGaps;
}
//--------------------------------------------------------------------------------------------------------------
bool ImplAlignment::isEmpty() const
{
	return (getLength() == 0);
}

//-----------------------------------------------------------------------------------------------------------
void ImplAlignment::write( std::ostream& output ) const
{
	debug_func_cerr(5);

	output << "Length: " << getLength() << "\tScore: " << getScore() << "\tGaps: " << getNumGaps() << endl;
	output << "Row\tColumn\tScore\t" << endl;

	AlignmentIterator it(begin());
	AlignmentIterator it_end(end());

	for (; it != it_end; ++it)
		output << *it << endl;

}

//--------------------------------------------------------------------------------------------------------------
// This implementation copies the alignment.
//
void ImplAlignment::moveAlignment( Position row_offset, Position col_offset)
{
	debug_func_cerr(5);

	if (isEmpty()) return;

	if (row_offset + mRowFrom < 0 )
		throw AlignlibException( "moving alignment out of bounds in row");
	if (col_offset + mColFrom < 0 )
		throw AlignlibException( "moving alignment out of bounds in col");

	HAlignment copy( this->getClone() );

	clear();

	AlignmentIterator it     = copy->begin();
	AlignmentIterator it_end = copy->end();

	for (;it != it_end; ++it)
	{
		addPair( it->mRow + row_offset,
				 it->mCol + col_offset,
				 it->mScore );
	}
}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignment::setLength( Position length ) const
{
	mLength = length;
}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignment::setNumGaps( Position num_gaps ) const
{
	mNumGaps = num_gaps;
}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignment::addPair( const ResiduePair & pair )
{
	assert( pair.mRow >= 0);
	assert( pair.mCol >= 0);

	Position row = pair.mRow;
	Position col = pair.mCol;


	if (mRowFrom == NO_POS)
	{
		mRowFrom = row;
		mColFrom = col;
		mRowTo = row + 1;
		mColTo = col + 1;
	}
	else
	{
		if (row < mRowFrom)
			mRowFrom = row;
		else if ( ++row > mRowTo )
			mRowTo = row;

		if (col < mColFrom)
			mColFrom = col;
		else if (++col > mColTo)
			mColTo = col;
	}
	setChangedLength();
}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignment::addDiagonal(
		Position row_from,
		Position row_to,
		Position col_offset)
{
	debug_func_cerr( 5 );
	assert( row_from >= 0);
	Position i;
	for (i = row_from; i < row_to; i++)
		addPair( ResiduePair( i, i + col_offset, 0));

}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignment::removePair( const ResiduePair & pair )
{
	debug_func_cerr( 5 );
	if (pair.mRow == mRowFrom || pair.mRow == mRowTo || pair.mCol == mColFrom || pair.mCol == mColTo )
		updateBoundaries();
	setChangedLength();
}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignment::addPair( Position row, Position col, Score score )
{
	debug_func_cerr(5);
	addPair(ResiduePair( row,col,score) );
}

//--------------------------------------------------------------------------------------------------------------
void ImplAlignment::calculateLength() const
{
	debug_func_cerr(5);

	AlignmentIterator it(begin());
	AlignmentIterator it_end(end());

	mLength = 0;
	mNumGaps = 0;
	if (it == it_end)
	{
		mRowFrom = mRowTo = mColFrom = mColTo = NO_POS;
		return;
	}

	mRowFrom = it->mRow;
	mColFrom = it->mCol;
	mRowTo = it->mRow;
	mColTo = it->mCol;

	++it;
	Position row_last = mRowFrom;
	Position col_last = mColFrom;
	Position d;
	++mLength;

	for (; it != it_end; ++it)
	{
		Position row = it->mRow;
		Position col = it->mCol;

		// get maximum boundaries
		if (row < mRowFrom) mRowFrom = row;
		if (col < mColFrom) mColFrom = col;
		if (row > mRowTo)   mRowTo = row;
		if (col > mColTo)   mColTo = col;

		++mLength;
		if ( (d = row - row_last - 1) > 0 )
		{
			mLength += d; mNumGaps += d;
		}

		if ( (d = col - col_last - 1) > 0 )
		{
			mLength += d; mNumGaps += d;
		}

		row_last = row;
		col_last = col;
	}

	++mRowTo;
	++mColTo;
	mChangedLength = false;
}

//-----------------------------------------------------------------------------------------------------------
/** switch row and column in the alignment. Use more efficient implementations in derived classes.
 */
void ImplAlignment::switchRowCol()
{

	debug_func_cerr(5);

	HAlignment copy = getClone();

	AlignmentIterator it     = copy->begin();
	AlignmentIterator it_end = copy->end();

	clear();

	// copy over residue pairs from copy reversing row and column
	for (;it != it_end; ++it)
		addPair( ResiduePair( it->mCol, it->mRow, it->mScore ) );

	setScore( copy->getScore() );
	calculateLength();
	return;
}

//-----------------------------------------------------------------------------------------------------------
//--------------> mapping functions <----------------------------------------------------------------------------
/** default implementation for mapping
 *
 * This function iterates through the alignment and is
 * very time inefficient and ignores the search option.
 */
Position ImplAlignment::mapRowToCol( Position pos, SearchType search ) const
{
	debug_func_cerr(5);

	if (getLength() == 0)
		return NO_POS;

	AlignmentIterator it = begin();
	AlignmentIterator it_end = end();

	for (; it != it_end; ++it)
	{
		if ((*it).mRow == pos)
			return (*it).mCol;
	}

	return NO_POS;
}

Position ImplAlignment::operator [](const Position & pos) const
{
	return mapRowToCol( pos );
}

//-----------------------------------------------------------------------------------------------------------
/** default implementation for mapping
 *
 * This function iterates through the alignment and is
 * very time inefficient and ignores the search option.
 */
Position ImplAlignment::mapColToRow( Position pos, SearchType search ) const
{

	if (getLength() == 0)
		return NO_POS;

	AlignmentIterator it(begin());
	AlignmentIterator it_end(end());

	while (it != it_end)
	{
		if ((*it).mCol == pos)
			return (*it).mRow;
		++it;
	}

	return NO_POS;
}

//-----------------------------------------------------------------------------------------------------------
/** This is a generic routine. It creates a new alignment by making a copy of the old one.
 */
void ImplAlignment::removeRowRegion( Position from, Position to)
{

	const HAlignment copy = getClone();

	AlignmentIterator it     = copy->begin();
	AlignmentIterator it_end = copy->end();

	clear();

	mScore = copy->getScore();

	for (; it != it_end; ++it)
	{
		if ( (*it).mRow < from || (*it).mRow >= to)
			addPair( ResiduePair(*it) );
	}

	updateBoundaries();
	setChangedLength();
	return;
}

//-----------------------------------------------------------------------------------------------------------
/** This is a generic routine. It creates a new alignment by making a copy of the old one.
 */
void ImplAlignment::removeColRegion( Position from, Position to)
{

	const HAlignment copy = getClone();

	AlignmentIterator it     = copy->begin();
	AlignmentIterator it_end = copy->end();

	clear();

	mScore = copy->getScore();

	for (; it != it_end; ++it)
	{
		const ResiduePair & p = (*it);
		if (p.mCol < from || p.mCol >= to)
			addPair( ResiduePair(p) );
	}

	updateBoundaries();
	setChangedLength();
	return;
}


//-----------------------------------------------------------------------------------------------------------
/** This is a generic routine. It creates a new alignment by making a copy of the old one.
 */
void ImplAlignment::insertRow(
		const Position & from,
		const Position & residues )
{
	if (from >= getRowTo()) return;
	Position p = std::max( from, getRowFrom());

	const HAlignment copy = getClone();

	AlignmentIterator it     = copy->begin();
	AlignmentIterator it_end = copy->end();

	clear();

	mScore = copy->getScore();

	for (; it != it_end && (*it).mRow < p; ++it)
		addPair( ResiduePair(*it) );

	for (; it != it_end; ++it)
	{
		addPair( ResiduePair(it->mRow+residues, it->mCol, it->mScore) );
	}

	updateBoundaries();
	setChangedLength();
	return;
}

//-----------------------------------------------------------------------------------------------------------
/** This is a generic routine. It creates a new alignment by making a copy of the old one.
 */
void ImplAlignment::insertCol(
		const Position & from,
		const Position & residues )
{
	debug_func_cerr( 5 );
	if (from >= getColTo()) return;
	Position p = std::max( from, getColFrom());

	const HAlignment copy = getClone();

	AlignmentIterator it     = copy->begin();
	AlignmentIterator it_end = copy->end();

	clear();

	mScore = copy->getScore();

	for (; it != it_end && (*it).mCol < p; ++it)
		addPair( ResiduePair(*it) );

	for (; it != it_end; ++it)
	{
		addPair( ResiduePair(it->mRow, it->mCol+residues, it->mScore) );
	}

	updateBoundaries();
	setChangedLength();
	return;
}

//-----------------------------------------------------------------------------------------------------------
/** This is a generic routine. It creates a new alignment by making a copy of the old one.
 */
void ImplAlignment::merge(
		const HAlignment & other,
		bool invert )
{
	debug_func_cerr(5);

	AlignmentIterator it(other->begin());
	AlignmentIterator end(other->end());

	if (invert)
	{
		for( ; it != end; ++it )
			addPair( it->mCol, it->mRow, it->mScore );
	}
	else
		for( ; it != end; ++it ) addPair( *it );

}

//-----------------------------------------------------------------------------------------------------------
/** This is a generic routine. It creates a new alignment by making a copy of the old one.
 */
void ImplAlignment::map(
		const HAlignment & other,
		const CombinationMode & mode )
{
	debug_func_cerr(5);

	const HAlignment copy = getClone();

	clear();

	AlignmentIterator it1(copy->begin());
	AlignmentIterator it1_end(copy->end());
	AlignmentIterator it2(other->begin());
	AlignmentIterator it2_end(other->end());

	while ( it1 != it1_end && it2 != it2_end )
	{

		const ResiduePair & x_pair = *it1;
		const ResiduePair & y_pair = *it2;

		Position map1 = NO_POS;
		Position value1 = NO_POS;

		Position map2 = NO_POS;
		Position value2 = NO_POS;

		switch (mode)
		{

		case RR:
			map1 = x_pair.mRow; value2 = x_pair.mCol;
			map2 = y_pair.mRow; value1 = y_pair.mCol;
			break;

		case CR:
			map1 = x_pair.mCol; value1 = x_pair.mRow;
			map2 = y_pair.mRow; value2 = y_pair.mCol;
			break;

		case RC:
			map1 = x_pair.mRow; value2 = x_pair.mCol;
			map2 = y_pair.mCol; value1 = y_pair.mRow;
			break;

		case CC:
			map1 = x_pair.mCol; value1 = x_pair.mRow;
			map2 = y_pair.mCol; value2 = y_pair.mRow;
			break;
		}

		assert( value1 != NO_POS);
		assert( value2 != NO_POS);

		debug_cerr( 5, "map1:" << map1 << " value1:" << value1 << " map2:" << map2 << " value2:" << value2 );

		if (map1 == map2)
		{
			addPair( ResiduePair(value1, value2, 0));
			++it1;
			++it2;
		}
		else
		{
			if (map1 < map2)
				++it1;
			else
				++it2;
		}

	}

	return;
}

//--------------------------------------------------------------------------------------------------------------



} // namespace alignlib
