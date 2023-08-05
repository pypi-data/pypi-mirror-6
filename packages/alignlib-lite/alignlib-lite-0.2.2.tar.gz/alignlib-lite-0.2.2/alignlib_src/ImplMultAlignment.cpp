/*
 alignlib - a library for aligning protein sequences

 $Id: ImplMultAlignment.cpp,v 1.6 2004/03/19 18:23:41 aheger Exp $

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
#include <fstream>
#include <iomanip>
#include <vector>
#include <cassert>
#include <limits>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"

#include "HelpersAlignandum.h"
#include "ImplMultAlignment.h"
#include "HelpersMultAlignment.h"
#include "HelpersEncoder.h"
#include "AlignlibException.h"
#include "Alignatum.h"
#include "Alignandum.h"
#include "Alignment.h"
#include "HelpersAlignment.h"
#include "AlignmentIterator.h"
#include "AlignlibException.h"
#include "HelpersAlignment.h"
#include "HelpersToolkit.h"
#include "AlignmentFormat.h"

using namespace std;

namespace alignlib
{

/* factory functions */

/** create an empty multiple alignment */
HMultAlignment makeMultAlignment()
{
	return HMultAlignment(new ImplMultAlignment());
}

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplMultAlignment::ImplMultAlignment() :
	mLength(0)
{
}

//--------------------------------------------------------------------------------------------------------------
ImplMultAlignment::~ImplMultAlignment()
{
	freeMemory();
}

//--------------------------------------------------------------------------------------------------------------
ImplMultAlignment::ImplMultAlignment(const ImplMultAlignment & src) :
	mLength(src.mLength)
{

	// clear old entries
	freeMemory();

	// add clones of the new entries
	for (unsigned int row = 0; row < src.mRows.size(); row++)
		add(src.mRows[row]->getClone());

	mIsAligned.clear();
	std::copy(src.mIsAligned.begin(), src.mIsAligned.end(), std::back_inserter(
			mIsAligned));
}

//--------------------------------------------------------------------------------------------------------------
IMPLEMENT_CLONE(HMultAlignment, ImplMultAlignment)
;

//---------------------------------------------------------------------------------------
HMultAlignment ImplMultAlignment::getCopy(
		const ExpansionType & expansion_type ) const
{
	debug_func_cerr(5);

	HMultAlignment result( makeMultAlignment() );

	if (isEmpty()) return result;
	if (expansion_type == UnalignedIgnore )
		return getClone();

	// save old length of mali
	Position mali_length = mLength;

	debug_cerr( 5, "length=" << mali_length );

	AggregateType t = AggSum;

	if (expansion_type == UnalignedSeparate)
	{
		t = AggSum;
	}
	else if (expansion_type == UnalignedStacked)
	{
		t = AggMax;
	}

	// get number of gaps between columns in the multiple alignment
	HCountVector ggaps(getGapCounts( HAlignandumVector(),t));

	CountVector & gaps = *ggaps;

#ifdef DEBUG
	for (unsigned int x = 0; x < gaps.size(); ++x)
		debug_cerr( 5, "col=" << x << " gaps=" << gaps[x]);
#endif

	// build map of aligned columns to output columns in mali
	// record gaps before each position
	HAlignment map_mali_old2new = makeAlignmentVector();
	{
		Position y = 0;
		for (Position x = 0; x < mali_length; ++x)
		{
			y += gaps[x];
			map_mali_old2new->addPair(x, y++, 0);
		}
	}

	debug_cerr( 5, "map_mali_old2new\n" << *map_mali_old2new );

	// remap each row to the new mali
	std::vector<int>used_gaps(mali_length + 1, 0);

	for (unsigned int x = 0; x < mRows.size(); ++x)
	{
		HAlignment old_map_mali2row = mRows[x];
		HAlignment new_map_mali2row = old_map_mali2row->getNew();

		// build new alignment by mapping the existing aligned columns
		combineAlignment(new_map_mali2row, map_mali_old2new, old_map_mali2row,
				RR);

		debug_cerr( 5, "map_mali2row after mapping aligned columns=\n" << *new_map_mali2row );

		if (expansion_type == UnalignedSeparate)
		{
			// insert gaps between aligned positions
			Position last_col = old_map_mali2row->getColFrom();
			for (Position row = old_map_mali2row->getRowFrom() + 1;
					row < old_map_mali2row->getRowTo();
					++row)
			{
				Position col = old_map_mali2row->mapRowToCol(row);

				if (col != NO_POS)
				{
					unsigned int u = map_mali_old2new->mapRowToCol(row) - gaps[row]
					                                                           + used_gaps[row];
					unsigned int d = col - last_col - 1;
					while (col - last_col - 1 > 0)
					{
						new_map_mali2row->addPair(u++, ++last_col, 0);
					}

					used_gaps[row] += d;
					last_col = col;
				}
			}
		}
		debug_cerr( 3, "map_mali2row after mapping unaligned columns=\n" << *new_map_mali2row );

		result->add( new_map_mali2row );
	}

	assert(getNumSequences() == result->getNumSequences());

	return result;
}


//--------------------------------------------------------------------------------------------------------------
void ImplMultAlignment::freeMemory()
{
	debug_func_cerr(5);
	mRows.clear();
	mIsAligned.clear();
}

//--------------------------------------------------------------------------------------------------------------
Position ImplMultAlignment::getLength() const
{
	return mLength;
}

//--------------------------------------------------------------------------------------------------------------
int ImplMultAlignment::getNumSequences() const
{
	return mRows.size();
}

//-----------------------------------------------------------------------------------------------------------
const HAlignment ImplMultAlignment::operator[](int row) const
{
	if (isEmpty())
		throw AlignlibException("In ImplMultAlignment.cpp: alignment is empty");

	if (row < 0 || row >= mRows.size())
		throw AlignlibException("In ImplMultAlignment.cpp: out-of-range access");

	return mRows[row];
}

//-----------------------------------------------------------------------------------------------------------
Position ImplMultAlignment::getFrom() const
{
	if (isEmpty())
		throw AlignlibException("In ImplMultAlignment.cpp: alignment is empty");
	return mFrom;
}

//-----------------------------------------------------------------------------------------------------------
Position ImplMultAlignment::getTo() const
{
	if (isEmpty())
		throw AlignlibException("In ImplMultAlignment.cpp: alignment is empty");
	return mLength;
}

//-----------------------------------------------------------------------------------------------------------
const HAlignment ImplMultAlignment::getRow(int row) const
{
	debug_func_cerr(5);
	if (isEmpty())
		throw AlignlibException("In ImplMultAlignment.cpp: alignment is empty");
	if (row < 0 || row >= mRows.size())
		throw AlignlibException("In ImplMultAlignment.cpp: out-of-range access");

	return mRows[row];
}

//-----------------------------------------------------------------------------------------------------------
void ImplMultAlignment::clear()
{
	debug_func_cerr(5);
	freeMemory();
	mLength = 0;
}

//-----------------------------------------------------------------------------------------------------------
void ImplMultAlignment::eraseRow(int row)
{
	debug_func_cerr(5);
	if (isEmpty())
		throw AlignlibException("In ImplMultAlignment.cpp: alignment is empty");
	if (row < 0 || row >= mRows.size())
		throw AlignlibException("In ImplMultAlignment.cpp: out-of-range access");

	mRows.erase(mRows.begin() + row);
	if (mRows.size() == 0)
		mLength = 0;
	updateLength();
}

//-----------------------------------------------------------------------------------------------------------
bool ImplMultAlignment::isAligned(const Position & col)
{
	debug_func_cerr(5);
	if (col < 0 || col >= getLength())
		throw AlignlibException("In ImplMultAlignment.cpp: out-of-range access");
	return mIsAligned[col];
}

//-----------------------------------------------------------------------------------------------------------
void ImplMultAlignment::updateAligned(const HAlignment & map_mali2sequence)
{
	debug_func_cerr(5);
	mIsAligned.resize(mLength, false);
	AlignmentIterator it(map_mali2sequence->begin()), end(
			map_mali2sequence->end());
	for (; it != end; ++it)
		mIsAligned[it->mRow] = true;
	return;
}

//-----------------------------------------------------------------------------------------------------------
void ImplMultAlignment::buildAligned()
{
	debug_func_cerr(5);
	mIsAligned.clear();
	mIsAligned.resize(mLength, false);
	for (int x = 0; x < mRows.size(); ++x)
	{
		AlignmentIterator it(mRows[x]->begin()), end(mRows[x]->end());
		for (; it != end; ++it)
			mIsAligned[it->mRow] = true;
	}
	return;
}

//------------------------------------------------------------------------------------
/** Add a full multiple alignment to the another alignment.
 */
void ImplMultAlignment::add(
		const HMultipleAlignment & src,
		const HAlignment & map_src2this )
{
	debug_func_cerr(5);

	// do not add empty mali
	if (src->isEmpty())
		return;

	debug_cerr( 5, "adding " << src->getNumSequences() << " sequences to " << mRows.size() << " rows");

	for (int x = 0; x < src->getNumSequences(); ++x)
	{
		HAlignatum other_row = src->getRow(x);
		HAlignment map_mali2sequence(makeAlignmentVector());

		const std::string s( other_row->getString() );
		Position seqpos = 0;
		char gapchar = getDefaultEncoder()->getGapChar();
		for (int x = 0; x < s.size(); ++x)
		{
			if (s[x] == gapchar) continue;
			Position malipos = map_src2this->mapRowToCol( x );
			if (malipos >= 0)
				map_mali2sequence->addPair( malipos, seqpos, 0 );
			seqpos += 1;
		}
		mRows.push_back(map_mali2sequence);
	}

	debug_cerr( 5, "after adding: " << mRows.size() << " rows");

	mFrom = std::min(mFrom, map_src2this->getColFrom());
	mLength = std::max(mLength, map_src2this->getColTo());
	buildAligned();
}

//------------------------------------------------------------------------------------
/** Add a full multiple alignment to the another alignment.
 */
void ImplMultAlignment::add(
		const HMultAlignment & other,
		const HAlignment & map_this2other)
{
	debug_func_cerr(5);

	// do not add empty mali
	if (other->isEmpty())
		return;

	for (int x = 0; x < other->getNumSequences(); ++x)
	{
		HAlignment new_map_mali2sequence(other->getRow(x)->getNew());

		combineAlignment(new_map_mali2sequence, map_this2other,
				other->getRow(x), CR);

		mRows.push_back(new_map_mali2sequence);
	}

	mFrom = std::min(mFrom, map_this2other->getRowFrom());
	mLength = std::max(mLength, map_this2other->getRowTo());
	buildAligned();
}

//------------------------------------------------------------------------------------
/** Add a full multiple alignment to the another alignment.
 */
void ImplMultAlignment::add(const HMultAlignment & other,
		const HAlignment & map_this2new, const HAlignment & map_other2new)
{
	debug_func_cerr(5);

	// do not add empty mali
	if (other->isEmpty())
		return;

	// map this alignment
	for (int x = 0; x < getNumSequences(); ++x)
	{
		mRows[x]->map(map_this2new, RR);
	}

	for (int x = 0; x < other->getNumSequences(); ++x)
	{
		HAlignment new_map_mali2sequence(other->getRow(x)->getClone());
		new_map_mali2sequence->map(map_other2new, RR);
		mRows.push_back(new_map_mali2sequence);
	}

	mFrom = std::min( map_this2new->getColFrom(), map_other2new->getColFrom());
	mLength = std::max(map_this2new->getColTo(), map_other2new->getColTo());
	buildAligned();
}

//------------------------------------------------------------------------------------
/* add single entry to *this multiple alignment given an alignment.
 */
void ImplMultAlignment::add(const HAlignment & map_mali2sequence)
{
	debug_func_cerr(5);
	mRows.push_back(map_mali2sequence->getClone());
	mFrom = std::min(mFrom, map_mali2sequence->getRowFrom());
	mLength = std::max(mLength, map_mali2sequence->getRowTo());
	updateAligned(map_mali2sequence);
}

//---------------------------------------------------------------------------------------
bool ImplMultAlignment::isEmpty() const
{
	return mRows.empty();
}

//---------------------------------------------------------------------------------------
void ImplMultAlignment::expand(const HAlignandumVector & sequences)
{
	debug_func_cerr(5);

	if (isEmpty()) return;

	bool insert_termini = false;
	if (sequences->size() != 0)
	{
		if (sequences->size() != getNumSequences())
			throw AlignlibException(
					"ImplMultAlignment.cpp: number of sequences given does not match number of sequences in MultAlignment");
		insert_termini = true;
	}

	// save old length of mali
	Position mali_length = mLength;

	debug_cerr( 5, "length=" << mali_length << " insert_termini=" << insert_termini);

	// special case: if all rows are empty and sequences are given, simple
	// concatenate all sequences. Without sequences, do nothing.
	if (mali_length == 0)
	{
		if (insert_termini)
		{
			Position start = 0;
			for (int x = 0; x < sequences->size(); ++x)
			{
				Position l = (*sequences)[x]->getLength();
				if (l > 0)
					mRows[x]->addDiagonal( start, start + l, -start );
				start += l;
			}
			mLength = start;
			mIsAligned.clear();
			mIsAligned.resize(mLength, true);
		}
		return;
	}

	HCountVector ggaps(getGapCounts(sequences,AggSum));

	CountVector & gaps = *ggaps;

#ifdef DEBUG
	for (unsigned int x = 0; x < gaps.size(); ++x)
		debug_cerr( 5, "col=" << x << " gaps=" << gaps[x]);
#endif

	// build map of aligned columns to output columns in mali
	// record gaps before each position
	HAlignment map_mali_old2new = makeAlignmentVector();
	{
		Position y = 0;
		for (Position x = 0; x < mali_length; ++x)
		{
			y += gaps[x];
			map_mali_old2new->addPair(x, y++, 0);
		}
	}

	debug_cerr( 5, "map_mali_old2new\n" << *map_mali_old2new );

	// remap each row to the new mali
	std::vector<int> used_gaps(mali_length + 1, 0);

	for (unsigned int x = 0; x < mRows.size(); ++x)
	{
		HAlignment old_map_mali2row = mRows[x];
		HAlignment new_map_mali2row = old_map_mali2row->getNew();

		// build new alignment by mapping the existing aligned columns
		combineAlignment(new_map_mali2row, map_mali_old2new, old_map_mali2row,
				RR);

		debug_cerr( 5, "map_mali2row after mapping aligned columns=\n" << *new_map_mali2row );

		// add residues for unaligned positions
		// insert before start
		if (insert_termini)
		{
			if ((*sequences)[x]->getLength() > 0)
			{
				unsigned int u = used_gaps[0];
				Position col = old_map_mali2row->getColFrom();
				Position s = (*sequences)[x]->getFrom();
				while (s < col)
				{
					assert( new_map_mali2row->mapRowToCol(u) == NO_POS);
					new_map_mali2row->addPair(u++, s++, 0);
				}
				used_gaps[0] = u;
			}
		}

		// insert gaps between aligned positions
		Position last_col = old_map_mali2row->getColFrom();
		for (Position row = old_map_mali2row->getRowFrom() + 1; row
				< old_map_mali2row->getRowTo(); ++row)
		{
			Position col = old_map_mali2row->mapRowToCol(row);

			if (col != NO_POS)
			{
				unsigned int u = map_mali_old2new->mapRowToCol(row) - gaps[row]
						+ used_gaps[row];
				unsigned int d = col - last_col - 1;
				while (col - last_col - 1 > 0)
				{
					new_map_mali2row->addPair(u++, ++last_col, 0);
				}
				used_gaps[row] += d;
				last_col = col;
			}
		}

		if (insert_termini)
		{
			Position l = (*sequences)[x]->getTo();
			Position t = old_map_mali2row->getColTo();

			if (t > l)
			{
				debug_cerr(2, "Alignment out of range t=" << t << " l=" << l );
				throw AlignlibException( "ImplMultAlignment.cpp: alignment longer than sequence" );
			}

			// use getLength to exclude empty sequences
			if ( (*sequences)[x]->getLength() > 0)
			{
				Position end = map_mali_old2new->getColTo();
				Position residues = l - t;
				// insert the full sequence if no alignment
				if (t == NO_POS) { t = (*sequences)[x]->getFrom(); residues = (*sequences)[x]->getLength(); }
				Position start = end + used_gaps[mali_length];
				debug_cerr( 3, "adding " << residues << " terminal residues for x=" << x
						<< " t=" << t
						<< " l=" << l
						<< " '" << (*sequences)[x]->asString()
						<< "' end=" << end
						<< " start=" << start
						<< " to=" << start + residues
						<< " diag=" << old_map_mali2row->getColTo() - start);
				new_map_mali2row->addDiagonal(start, start + residues,
						t - start);
				used_gaps[mali_length] += residues;
			}
		}

		debug_cerr( 3, "map_mali2row after mapping unaligned columns=\n" << *new_map_mali2row );

		mRows[x] = new_map_mali2row;
	}

	updateLength();

	// by definition all columns will be aligned
	mIsAligned.clear();
	mIsAligned.resize(mLength, true);
}

//---------------------------------------------------------------------------------------
void ImplMultAlignment::merge( const HMultAlignment & other)
{
	debug_func_cerr( 5 );
	if (getNumSequences() != other->getNumSequences() )
		throw AlignlibException( "multiple alignment to be merged contains no the same number of sequences");

	for (int x = 0; x < mRows.size(); ++x)
		mRows[x]->merge( other->getRow( x ) );

	mFrom = std::min( mFrom, other->getFrom() );
	mLength = std::max( mLength, other->getLength());
	buildAligned();
}

//---------------------------------------------------------------------------------------
void ImplMultAlignment::move( const Position & offset )
{
	debug_func_cerr( 5 );
	if (offset > 0)
	{
		for (int x = 0; x < mRows.size(); ++x)
			mRows[x]->moveAlignment( offset, 0);
	}
	else if (offset < 0)
		for (int x = 0; x < mRows.size(); ++x)
		{
			if (mRows[x]->getRowFrom() < -offset )
				throw AlignlibException( "moving alignment out of bounds" );
			mRows[x]->moveAlignment( offset, 0);
		}
	mLength += offset;
	mFrom += offset;
	buildAligned();
}

//---------------------------------------------------------------------------------------
void ImplMultAlignment::trim()
{
	debug_func_cerr( 5 );
	Position offset = std::numeric_limits<Position>::max();

	for (int x = 0; x < mRows.size(); ++x)
		offset = std::min( mRows[x]->getRowFrom(), offset );
	move( -offset );
	updateLength();
}

//---------------------------------------------------------------------------------------
void ImplMultAlignment::shrink()
{
	debug_func_cerr( 5 );
	HCountVector counts(getColumnCounts());
	HAlignment map_old2new(makeAlignmentVector());
	Position n = 0;
	for (Position x = 0; x < counts->size(); ++x)
		if ((*counts)[x] > 1)
			map_old2new->addPair(x, n++, 0);
	map(map_old2new, RC);
	updateLength();
	buildAligned();
}

//---------------------------------------------------------< Input/Output routines >--------

HPositionMatrix ImplMultAlignment::getPositionMatrix(const bool & transpose) const
{
	debug_func_cerr(5);
	PositionMatrix * matrix;
	if (transpose)
	{
		matrix = new PositionMatrix(getLength(), getNumSequences(), NO_POS);
		for (int x = 0; x < mRows.size(); ++x)
		{
			AlignmentIterator it(mRows[x]->begin()), end(mRows[x]->end());
			for (; it != end; ++it)
				matrix->setValue(it->mRow, x, it->mCol);
		}
	}
	else
	{
		matrix = new PositionMatrix(getNumSequences(), getLength(), NO_POS);
		for (int x = 0; x < mRows.size(); ++x)
		{
			AlignmentIterator it(mRows[x]->begin()), end(mRows[x]->end());
			for (; it != end; ++it)
				matrix->setValue(x, it->mRow, it->mCol);
		}
	}
	return HPositionMatrix(matrix);
}

//------------------------------------------------------------------------------------
void ImplMultAlignment::write(std::ostream & output) const
{
	debug_func_cerr(5);

	for (unsigned int row = 0; row < mRows.size(); ++row)
	{
		mRows[row]->write(output);
		output << std::endl;
	}
	Position l = getLength();
	for (unsigned int col = 0; col < l; ++col)
		output << mIsAligned[col];
}

//-----------------------------------------------------------------------------------------------------------
void ImplMultAlignment::updateLength()
{
	debug_func_cerr(5);

	mLength = 0;
	mFrom = std::numeric_limits< Position >::max();
	for (int x = 0; x < mRows.size(); ++x)
	{
		mLength = std::max( mRows[x]->getRowTo(), mLength );
		mFrom = std::min( mRows[x]->getRowFrom(), mFrom );
	}
}
//-----------------------------------------------------------------------------------------------------------
void ImplMultAlignment::map(const HAlignment & other,
		const CombinationMode & mode)
{
	debug_func_cerr(5);

	switch (mode)
	{
	case CR:
		for (int x = 0; x < mRows.size(); ++x)
			mRows[x]->map(other, RC);
		break;
	case RC:
		for (int x = 0; x < mRows.size(); ++x)
			mRows[x]->map(other, RR);
		break;
	default:
		throw AlignlibException(
				"ImplMultAlignment.cpp: invalid mapping, only CR and RC are eligible.");
	}

	updateLength();
	buildAligned();
}

//-----------------------------------------------------------------------------------------------------------
HCountVector ImplMultAlignment::getColumnCounts() const
{
	debug_func_cerr(5);
	CountVector * v = new CountVector(getLength(), 0);

	for (int x = 0; x < mRows.size(); ++x)
	{
		AlignmentIterator it(mRows[x]->begin()), end(mRows[x]->end());
		for (; it != end; ++it)
			(*v)[it->mRow] += 1;
	}
	return HCountVector(v);
}

//-----------------------------------------------------------------------------------------------------------
HCountVector ImplMultAlignment::getRowCounts() const
{
	debug_func_cerr(5);
	CountVector * v = new CountVector(getNumSequences(), 0);

	for (int x = 0; x < mRows.size(); ++x)
		(*v)[x] = mRows[x]->getNumAligned();
	return HCountVector(v);
}

//-----------------------------------------------------------------------------------------------------------
HCountVector ImplMultAlignment::getGapCounts(
		const HAlignandumVector & sequences,
		AggregateType aggregate_type ) const
{
	debug_func_cerr(5);

	bool insert_termini = false;
	if (sequences != NULL && sequences->size() != 0)
	{
		if (sequences->size() != getNumSequences())
			throw AlignlibException(
					"ImplMultAlignment.cpp: number of sequences given does not match number of sequences in MultAlignment");
		insert_termini = true;
	}

	Position mali_length = getLength();

	// find total/maximum insertions before a given mali column
	// row: position in mali
	// col: position in sequence
	CountVector * new_gaps = NULL;

	if ( aggregate_type == AggMin )
		new_gaps = new CountVector(mali_length + 1, std::numeric_limits<Count>::max());
	else
		new_gaps = new CountVector(mali_length + 1, 0);

	CountVector & gaps = *new_gaps;

	for (unsigned int x = 0; x < mRows.size(); ++x)
	{
		HAlignment map_mali2row = mRows[x];

		// skip empty alignments and empty sequences
		if (map_mali2row->getLength() == 0) continue;
		if (insert_termini && (*sequences)[x]->getLength() == 0) continue;

		Position last_col = map_mali2row->getColFrom();

		if (insert_termini)
		{
			Position l = (*sequences)[x]->getFrom();
			Count d = last_col - l;

			switch( aggregate_type )
			{
			case AggMean:
			case AggSum: gaps[0] += d; break;
			case AggCount: gaps[0] += d ? 1 : 0; break;
			case AggMax: gaps[0] = std::max( d, gaps[0]); break;
			case AggMin: gaps[0] = std::min( d, gaps[0]); break;
			}
		}

		for (Position row = map_mali2row->getRowFrom() + 1;
				row < map_mali2row->getRowTo(); ++row)
		{
			Position col = map_mali2row->mapRowToCol(row);
			if (col != NO_POS)
			{
				Count d = col - last_col - 1;
				switch( aggregate_type )
				{
				case AggMean:
				case AggSum: gaps[row] += d; break;
				case AggCount: gaps[row] += d ? 1 : 0; break;
				case AggMax: gaps[row] = std::max( d, gaps[row]); break;
				case AggMin: gaps[row] = std::min( d, gaps[row]); break;
				}
				last_col = col;
			}
		}

		if (insert_termini)
		{
			Position l = (*sequences)[x]->getTo();
			Position t = map_mali2row->getColTo();
			if (t > l)
				throw AlignlibException( "ImplMultAlignment.cpp: alignment longer than sequence" );

			if (l > 0)
			{
				Count d = l - t;
				switch( aggregate_type )
				{
				case AggMean:
				case AggSum: gaps[mali_length] += d; break;
				case AggCount: gaps[mali_length] += d ? 1 : 0; break;
				case AggMax: gaps[mali_length] = std::max( d, gaps[mali_length]); break;
				case AggMin: gaps[mali_length] = std::min( d, gaps[mali_length]); break;
				}
			}
		}
	}

	return HCountVector(new_gaps);
}
}

// namespace alignlib


