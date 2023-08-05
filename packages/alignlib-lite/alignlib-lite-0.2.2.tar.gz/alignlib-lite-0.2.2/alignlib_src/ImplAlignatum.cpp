/*
 alignlib - a library for aligning protein sequences

 $Id: ImplAlignatum.cpp,v 1.6 2004/09/16 16:02:38 aheger Exp $

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
#include <iomanip>
#include <cassert>
#include <sstream>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"

#include "Alignatum.h"
#include "ImplAlignatum.h"
#include "ImplEncoder.h"
#include "Alignment.h"
#include "AlignmentIterator.h"
#include "Alignandum.h"
#include "HelpersAlignatum.h"
#include "HelpersEncoder.h"
#include "AlignlibException.h"

using namespace std;

namespace alignlib
{

//-------------------------------------------------------------------------------------------------
/** factory functions */
HAlignatum makeAlignatum()
{
	return HAlignatum(new ImplAlignatum());
}

HAlignatum makeAlignatum(
		const std::string & src,
		const Position & from,
		const Position & to )
{
	return HAlignatum(new ImplAlignatum(src, from, to ));
}

HAlignatum makeAlignatum(
		const HAlignandum & src,
		const Position & from,
		const Position & to )
{
	return HAlignatum(new ImplAlignatum(std::string(src->asString()), from, to ));
}

HAlignatum makeAlignatum(
		const std::string & src,
		const HAlignment & map_src2alignment,
		const Position & max_length,
		const bool & unaligned )
{
	HAlignatum h(new ImplAlignatum(src));
	Position length;
	if (max_length == 0)
		length = map_src2alignment->getColTo();
	else
		length = max_length;

	h->mapOnAlignment(map_src2alignment, length, unaligned );
	return h;
}

HAlignatum makeAlignatum(
		const HAlignandum & src,
		const HAlignment & map_src2alignment,
		const Position & max_length,
		const bool & unaligned )
{
	return makeAlignatum(
			src->asString(),
			map_src2alignment,
			max_length,
			unaligned );
}

//---------------------------------------------------------< constructors and destructors >--------
ImplAlignatum::ImplAlignatum() :
	mRepresentation(""), mFrom(NO_POS),
	mTo(NO_POS),
	mLength(0), mGapChar(getToolkit()->getEncoder()->getGapChar()), mSeparator('\t')
{
}

ImplAlignatum::ImplAlignatum(
		const std::string & representation,
		Position from,
		Position to ) :
	mRepresentation(representation), mFrom(from), mTo(to), mGapChar(
			getToolkit()->getEncoder()->getGapChar()), mSeparator('\t')
{

	mLength = mRepresentation.length();

	if (mFrom == NO_POS && mLength > 0)
		mFrom = 0;

	if (mTo == NO_POS)
		mTo = mFrom + mLength - countGaps();

	debug_cerr( 4, "created alignatum: from=" << mFrom << " to=" << mTo << " repr=" << mRepresentation );
}

//--------------------------------------------------------------------------------------------
/* create a newly aligned object from ImplAlignatum, but map using ali in alignment
 note, that the residues in the alignment are called 1..length while the residues
 in the aligned strings are 0..length-1
 */
ImplAlignatum::ImplAlignatum(const ImplAlignatum & src) :
	mRepresentation(src.mRepresentation), mFrom(src.mFrom), mTo(src.mTo),
			mLength(src.mLength), mGapChar(getToolkit()->getEncoder()->getGapChar()),
			mSeparator(src.mSeparator)
{
	debug_func_cerr(5);
}

//--------------------------------------------------------------------------------------------
ImplAlignatum::~ImplAlignatum()
{
	debug_func_cerr(5);
}

//--------------------------------------------------------------------------------------------
IMPLEMENT_CLONE( HAlignatum, ImplAlignatum );

//--------------------------------------------------------------------------------------------
void ImplAlignatum::mapOnAlignment(
		const HAlignment & map_old2new,
		const Position new_length,
		const bool unaligned)
{
	debug_func_cerr(5);

	std::string new_representation = "";

	// bail out on empty alignments
	if (map_old2new->getLength() == 0)
	{
		mRepresentation = "";
		mFrom = mTo = NO_POS;
		return;
	}

	// check if alignment is out-of-bounds
	if (map_old2new->getRowTo() > mLength)
		throw AlignlibException( std::string("alignment out of bounds: alignment=") +
				toString(map_old2new->getRowFrom()) +
				"-" +
				toString(map_old2new->getRowTo()) +
				" sequence length="  + toString(mLength));

	Position length = std::max(new_length, map_old2new->getColTo());

	new_representation.append(length, mGapChar);

	// get alignment start positions
	Position row_from = map_old2new->getRowFrom();
	Position row_to = map_old2new->getRowTo();

	// get residue numbers of terminal residues and save them in from/to
	// note that the order is crucial as mFrom is used in getResidueNumber
	mTo = getResidueNumber(row_to, LEFT);
	mFrom = getResidueNumber(row_from, RIGHT);

	debug_cerr( 5, "mapping: " << row_from << "->" << mFrom << "; " << row_to << "->" << mTo );

	// substitute new characters for aligned positions:
	{
		AlignmentIterator it = map_old2new->begin();
		AlignmentIterator it_end = map_old2new->end();

		for (; it != it_end; ++it)
		{
			new_representation[it->mCol] = mRepresentation[it->mRow];
		}
	}

	// add unaligned characters
	if (unaligned)
	{

		debug_cerr( 5, "adding unaligned chars" );
		AlignmentIterator it = map_old2new->begin();
		AlignmentIterator it_end = map_old2new->end();

		Position last_old = it->mRow;
		Position last_new = it->mCol;

		++it;
		// substitute new characters for aligned positions:
		for (; it != it_end; ++it)
		{
			Position old = it->mRow - 1;
			Position nnew = it->mCol - 1;
			debug_cerr( 5, "delta_old=" << old - last_old << " delta_new=" << nnew - last_new);
			while (old - last_old > 0 && nnew - last_new > 0)
			{
				if (mRepresentation[old] >= 'A' && mRepresentation[old] <= 'Z')
					new_representation[nnew] = mRepresentation[old] - 'A' + 'a';
				else
					new_representation[nnew] = 'x';
				--old;
				--nnew;
			}
			last_old = it->mRow;
			last_new = it->mCol;
		}
	}

	mRepresentation = new_representation;
	mLength = mRepresentation.length();

}



//-------------------------------------------------------------------------------------------------------
const std::string & ImplAlignatum::getString() const
{
	return mRepresentation;
}

//-------------------------------------------------------------------------------------------------------
Position ImplAlignatum::getFrom() const
{
	return mFrom;
}

//-------------------------------------------------------------------------------------------------------
Position ImplAlignatum::getTo() const
{
	return mTo;
}

//-------------------------------------------------------------------------------------------------------
void ImplAlignatum::fillAlignment(HAlignment & dest, const bool invert) const
{
	debug_func_cerr(5);
	HEncoder encoder(getToolkit()->getEncoder());
	dest->clear();
	if (!invert)
	{
		Position x = mFrom;
		for (Position y = 0; y < mRepresentation.size(); ++y)
			if (encoder->isValidChar(mRepresentation[y]))
				dest->addPair(x++, y, 0);
	}
	else
	{
		Position y = mFrom;
		for (Position x = 0; x < mRepresentation.size(); ++x)
			if (encoder->isValidChar(mRepresentation[x]))
				dest->addPair(x, y++, 0);

	}
}

/** get represenation */
const std::string & ImplAlignatum::getRepresentation() const
{
	return mRepresentation;
}

/** set representation */
void ImplAlignatum::setRepresentation(std::string & representation,
		Position first_res, Position last_res)
{

	// set first residue number to 0 if not given
	if (first_res == NO_POS)
		first_res = 0;

	mFrom = first_res;

	mRepresentation = representation;
	mLength = mRepresentation.length();

	if (last_res == NO_POS)
		mTo = mLength - countGaps();

}

//---------------------------------------------------------------------------------------------------
/** return the length of the line */
Position ImplAlignatum::getAlignedLength() const
{
	return mLength;
}

//---------------------------------------------------------------------------------------------------
/** return the length of the line without gaps */
Position ImplAlignatum::getFullLength() const
{
	return mTo - mFrom;
}

//---------------------------------------------------------------------------------------------------
/** add the specified number of gaps in the front and in the back */
void ImplAlignatum::addGaps(int before, int after)
{
	int i = 0;
	std::string x = "";

	for (i = 0; i < before; i++)
		x += mGapChar;
	x += mRepresentation;
	for (i = 0; i < after; i++)
		x += mGapChar;

	mRepresentation = x;
	mLength = mRepresentation.length();
}

//---------------------------------------------------------------------------------------------------
/** add one or more gaps in the middle */
void ImplAlignatum::insertGaps(int position, Position count)
{

	std::string insertion = "";
	for (int i = 0; i < count; i++)
		insertion += mGapChar;

	mRepresentation.insert(position, insertion);
	mLength = mRepresentation.length();
}

//------------------------------------------------------------------------------------------------
/** remove leading/or trailing gaps */
void ImplAlignatum::removeEndGaps()
{
	mRepresentation.erase(0, mRepresentation.find_first_not_of(mGapChar));
	mRepresentation.erase(mRepresentation.find_last_not_of(mGapChar) + 1,
			mRepresentation.length());
	mLength = mRepresentation.length();
}

//------------------------------------------------------------------------------------------------
/** remove one or more positions from the aligned object */
void ImplAlignatum::removeColumns(int position, Position count)
{
	mRepresentation.erase(position, position + count);
}

//---------------------------------------------------------------------------------------
int ImplAlignatum::countGaps()
{
	int ngaps = 0;
	Position length = mRepresentation.length();
	Position i = 0;

	for (; i < length; i++)
		if (mRepresentation[i] == mGapChar)
			ngaps++;

	return ngaps;
}

//------------------------------------------------------------------------------------------
bool ImplAlignatum::isConsistent(void) const
{
	int nchars = 0;
	for (Position pos = 0; pos < mRepresentation.length(); ++pos)
		if (mRepresentation[pos] != mGapChar)
			++nchars;

	return nchars == (mTo - mFrom);
}

//------------------------------------------------------------------------------------------
// The current implemenation is inefficient as it always
// starts counting from the start. For long sequences
// implement indices to short-cut the search.
Position ImplAlignatum::getResidueNumber(
		const Position pos,
		const SearchType search) const
{
	debug_func_cerr( 5 );

	Position length = mRepresentation.length();

	debug_cerr( 5, "mapping position " << pos << " in " << mFrom << "-" << mTo << " of size " << length << " repr=" << mRepresentation );

	if (mFrom == NO_POS || pos == NO_POS || pos < 0 || pos > length)
		return NO_POS;

	// short cuts
	if (pos == 0)
		return mFrom;
	if (pos == length)
		return mTo;

	Position i = 0;
	// skip over terminal gaps
	while (i < pos && mRepresentation[i] == mGapChar)
		++i;

	Position result = mFrom;
	for (; i < pos; ++i)
		if (mRepresentation[i] != mGapChar)
			++result;

	debug_cerr( 5, "i=" << i << " result=" << result);
	if (mRepresentation[i] != mGapChar)
		return result;

	switch (search)
	{
	case NO_SEARCH:
		return NO_POS;
	case LEFT:
		// the previous residue is the one we return.
		return result;
	case RIGHT:
		return std::min(result + 1, mTo);
	}

	return (result);
}

//-------------------------------------------------------------------------------------------

//-------------------------------------------------------------------------------------------------------
void ImplAlignatum::write(std::ostream & output) const
{
	output << mFrom << getFieldSeparator() << mRepresentation
			<< getFieldSeparator() << mTo;
}

/** read from stream */
void ImplAlignatum::read(std::istream & input)
{
	debug_func_cerr(5);
	input >> mFrom;
	if (mFrom == NO_POS)
	{
		mRepresentation = "";
		input >> mTo;
	}
	else
		input >> mRepresentation >> mTo;
	mLength = mRepresentation.length();
}

//-------------------------------------------------------------------------------------------

} // namespace alignlib
