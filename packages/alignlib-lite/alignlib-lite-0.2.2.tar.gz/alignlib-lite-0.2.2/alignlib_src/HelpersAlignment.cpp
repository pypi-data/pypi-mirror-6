/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersAlignment.cpp,v 1.10 2005/02/24 11:07:25 aheger Exp $

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
#include <sstream>
#include <iomanip>
#include <limits>
#include "alignlib_interfaces.h"
#include "alignlib_fwd.h"
#include "HelpersAlignment.h"
#include "AlignlibDebug.h"
#include "HelpersEncoder.h"

using namespace std;

namespace alignlib
{

bool checkAlignmentIdentity(
		const HAlignment & a,
		const HAlignment & b,
		const bool invert)
{

	AlignmentIterator it1(a->begin());
	AlignmentIterator it1_end(a->end());

	AlignmentIterator it2(b->begin());
	AlignmentIterator it2_end(b->end());

	if (a->getRowFrom() != b->getRowFrom() ||
			a->getRowTo() != b->getRowTo() ||
			a->getColFrom() != b->getColFrom() ||
			a->getColTo() != b->getColTo() )
		return false;

	bool is_identical = true;

	for (; it1 != it1_end && it2 != it2_end && is_identical; ++it1, ++it2)
	{
		if (!invert)
		{
			if (it1->mRow != it2->mRow && it1->mCol != it2->mCol)
				is_identical = false;
		} else
		{
			if (it1->mRow != it2->mCol && it1->mCol != it2->mRow)
				is_identical = false;
		}
	}

	return is_identical;
}

bool hasRangeOverlap(
	const HAlignment & src1,
	const HAlignment & src2,
	const CombinationMode & mode,
	const int & min_overlap = 0)
{
	// check if ranges overlap
	switch (mode)
	{
	case RR:
		if (src1->getRowFrom() > src2->getRowTo() - min_overlap ||
				src2->getRowFrom() > src1->getRowTo() - min_overlap )
			return false;
		break;
	case CR:
		if (src1->getColFrom() > src2->getRowTo() - min_overlap||
				src2->getRowFrom() > src1->getColTo() - min_overlap )
			return false;
		break;
	case RC:
		if (src1->getRowFrom() > src2->getColTo() - min_overlap ||
			src2->getColFrom() > src1->getRowTo() - min_overlap )
			return false;
		break;
	case CC:
		if (src1->getColFrom() > src2->getColTo() - min_overlap ||
				src2->getColFrom() > src1->getColTo() - min_overlap )
			return false;
		break;
	}
	return true;
}

Position getAlignmentIdentity(
			const HAlignment & a,
			const HAlignment & b,
			const CombinationMode & mode)
{

	AlignmentIterator it1(a->begin());
	AlignmentIterator it1_end(a->end());

	AlignmentIterator it2(b->begin());
	AlignmentIterator it2_end(b->end());

	if (!hasRangeOverlap(a,b,mode, 0))
		return 0;

	Position nidentical = 0;

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
			map1 = x_pair.mRow; value1 = x_pair.mCol;
			map2 = y_pair.mRow; value2 = y_pair.mCol;
			break;

		case CR:
			map1 = x_pair.mCol; value1 = x_pair.mRow;
			map2 = y_pair.mRow; value2 = y_pair.mCol;
			break;

		case RC:
			map1 = x_pair.mRow; value1 = x_pair.mCol;
			map2 = y_pair.mCol; value2 = y_pair.mRow;
			break;

		case CC:
			map1 = x_pair.mCol; value1 = x_pair.mRow;
			map2 = y_pair.mCol; value2 = y_pair.mRow;
			break;
		}

		// cout << "map1:" << map1 << " value1:" << value1 << " map2:" << map2 << " value2:" << value2 << endl;

		if (map1 == map2)
		{
			if (value1 == value2)
			{
				nidentical += 1;
			}
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

	return nidentical;
}


//---------------------------------------------------------------------------------------------------------
void readAlignmentPairs(
		HAlignment & dest,
		std::istream & input,
		bool reverse )
{
	debug_func_cerr(5);

	dest->clear();

	while (input)
	{
		Position row, col;
		Score score;

		input >> row >> col >> score;
		if (reverse)
			dest->addPair( ResiduePair(col, row, score) );
		else
			dest->addPair( ResiduePair(row, col, score) );
	}
}


//-----------------------------------------------------------------------------------------------
void copyAlignment(
		HAlignment & dest,
		const HAlignment & src,
		Position row_from,
		Position row_to,
		Position col_from,
		Position col_to,
		Diagonal diagonal_from,
		Diagonal diagonal_to )
{
  debug_func_cerr(5);

  // check if we should only iterate by row - this
  // is faster than checking the full alignment.
  bool by_row = row_from != NO_POS && row_to != NO_POS;
  // warning: by_row causes AlignmentMatrix objects to be copied
  // incorrectly!!!
  by_row = false;
  
  // check parameters for filters and set them to sensible values
  if (col_from < src->getColFrom() || col_from == NO_POS)
    col_from = src->getColFrom();
  if (col_to > src->getColTo() || col_to == NO_POS)
    col_to = src->getColTo();
  if (row_from < src->getRowFrom() || row_from == NO_POS)
    row_from = src->getRowFrom();
  if (row_to > src->getRowTo() || row_to == NO_POS)
    row_to = src->getRowTo();
  
  if (diagonal_from > diagonal_to)
    {
      diagonal_from = std::numeric_limits<Diagonal>::min();
      diagonal_to   = std::numeric_limits<Diagonal>::max();
    }

  debug_cerr( 5, "copyAlignment applying filter:"
	      << " row=" << row_from << "-" << row_to
	      << " col=" << col_from << "-" << col_to
	      << " diag=" << diagonal_from << "-" << diagonal_to
	      << " by row=" << by_row );
  
  dest->clear();

  if (by_row)
    {
      ResiduePair query;

      for (Position this_row = row_from; this_row < row_to; ++this_row )
	{
	  Position this_col = src->mapRowToCol( this_row );
	  if (this_col < 0) continue;
	  if (this_col < col_from || this_col >= col_to)
	    continue;

	  query.mRow = this_row;
	  const ResiduePair p = src->getPair( query );
	  Diagonal this_diagonal = p.getDiagonal();
	  if (this_diagonal < diagonal_from || this_diagonal > diagonal_to)
	    continue;
	  
	  dest->addPair( p );
	}
    }
  else
    {
  
      AlignmentIterator it(src->begin());
      AlignmentIterator it_end(src->end());

      for (; it != it_end; ++it)
	{
	  const ResiduePair & p = *it;
	  
	  // apply filter
	  Position this_row = p.mRow;
	  Position this_col = p.mCol;
	  Diagonal this_diagonal = p.getDiagonal();
	  debug_cerr( 5, "row=" << this_row << " col=" << this_col
		      << "rowtest=" << (this_row < row_from || this_row >= row_to)
		      << "coltest="<< (this_col < col_from || this_col >= col_to)
		      << "dtest=" << (this_diagonal < diagonal_from || this_diagonal > diagonal_to));
	  
		
	  if (this_row < row_from || this_row >= row_to)
	    continue;
	  
	  if (this_col < col_from || this_col >= col_to)
	      continue;
	  
	  if (this_diagonal < diagonal_from || this_diagonal > diagonal_to)
	    continue;
	  
	  dest->addPair( ResiduePair(p) );
	  
	}
    }
  
  return;
}
  //-----------------------------------------------------------------------------------------------
void copyAlignmentWithoutRegion(
		HAlignment & dest,
		const HAlignment & src,
		Position row_from,
		Position row_to,
		Position col_from,
		Position col_to,
		Diagonal diagonal_from,
		Diagonal diagonal_to )
{
	debug_func_cerr(5);


	// check parameters for filters and set them to sensible values
	if (col_from < src->getColFrom() || col_from == NO_POS)
		col_from = src->getColFrom();
	if (col_to > src->getColTo() || col_to == NO_POS)
		col_to = src->getColTo();
	if (row_from < src->getRowFrom() || row_from == NO_POS)
		row_from = src->getRowFrom();
	if (row_to > src->getRowTo() || row_to == NO_POS)
		row_to = src->getRowTo();

	dest->clear();

	AlignmentIterator it(src->begin());
	AlignmentIterator it_end(src->end());

	for (; it != it_end; ++it)
	{
		const ResiduePair & p = *it;

		// apply filter
		Diagonal	this_diagonal = p.getDiagonal();
		Position this_row      = p.mRow;
		Position this_col      = p.mCol;

		if (this_col >= col_from && this_col < col_to)
			continue;
		if (this_row >= row_from && this_row < row_to)
			continue;
		if (this_diagonal >= diagonal_from && this_diagonal <= diagonal_to)
			continue;

		dest->addPair( ResiduePair(p) );

	}

	return;
}
//-----------------------------------------------------------------------------------------------
void copyAlignment( HAlignment & dest,
		const HAlignment & src,
		const HAlignment & filter,
		const CombinationMode mode )
{
	debug_func_cerr(5);

	dest->clear();

	AlignmentIterator it(src->begin());
	AlignmentIterator it_end(src->end());

	for (; it != it_end; ++it)
	{
		const ResiduePair & p = *it;
		bool keep = true;

		// apply filter
		if (filter)
			switch (mode)
			{
				case RR:
					if (filter->mapRowToCol( p.mRow ) == NO_POS ) keep = false; break;
				case CR:
					if (filter->mapRowToCol( p.mCol ) == NO_POS ) keep = false; break;
				case RC:
					if (filter->mapColToRow( p.mRow ) == NO_POS ) keep = false; break;
				case CC:
					if (filter->mapColToRow( p.mCol ) == NO_POS ) keep = false; break;
			}

		if (keep)
			dest->addPair( ResiduePair(p) );
	}

	return;
}

//----------------------------------------------------------------------------------
void addAlignment2Alignment(
		HAlignment & dest,
		const HAlignment & src )
{
	debug_func_cerr(5);


	AlignmentIterator it(src->begin());
	AlignmentIterator it_end(src->end());

	for (; it != it_end; ++it)
		dest->addPair( ResiduePair(*it) );

	dest->setScore( dest->getScore() + src->getScore());

	return;
}
//----------------------------------------------------------------------------------
void addMappedAlignment2Alignment(
		HAlignment & dest,
		const HAlignment & src,
		const HAlignment & map_src2new,
		const CombinationMode mode )
{
	debug_func_cerr(5);

	AlignmentIterator it(src->begin());
	AlignmentIterator it_end(src->end());

	for (; it != it_end; ++it)
	{
		Position row = (*it).mRow;
		Position col = (*it).mCol;
		Score score = (*it).mScore;

		switch (mode) {
		case RR: row = map_src2new->mapRowToCol(row); break;
		case RC: row = map_src2new->mapColToRow(row); break;
		case CR: col = map_src2new->mapRowToCol(col); break;
		case CC: col = map_src2new->mapColToRow(col); break;
		}

		if (row != NO_POS && col != NO_POS)
			dest->addPair( ResiduePair( row, col, score) );
	}

	dest->setScore( dest->getScore() + src->getScore());

	return;
}

//----------------------------------------------------------------------------------
void addMappedAlignments2Alignment(
		HAlignment & dest,
		const HAlignment & src,
		const HAlignment & map_src_row2dest_row,
		const HAlignment & map_src_col2dest_col )
{
	debug_func_cerr(5);

	AlignmentIterator it(src->begin());
	AlignmentIterator it_end(src->end());

	for (; it != it_end; ++it)
	{
		Position row = map_src_row2dest_row->mapRowToCol((*it).mRow);
		Position col = map_src_col2dest_col->mapRowToCol((*it).mCol);
		Score score = (*it).mScore;

		if (row != NO_POS && col != NO_POS)
			dest->addPair( ResiduePair( row, col, score) );
	}

	dest->setScore( dest->getScore() + src->getScore());

	return;
}

//-----------------------------------------------------------------------------------------
Position getAlignmentShortestDistance(
			const HAlignment & src1,
			const HAlignment & src2,
			const CombinationMode mode )
{
	debug_func_cerr(5);

	Position map1 = 0;
	Position map2 = 0;

	// check if ranges overlap
	// add +1, so that adjacent alignments where To() == From()
	// have a distance of 1
	Position d = 0;
	switch (mode)
	{
	case RR:
		d = std::min(src1->getRowTo(), src2->getRowTo()) - std::max(src1->getRowFrom(),src2->getRowFrom() );
		break;
	case CR:
		d = std::min(src1->getColTo(), src2->getRowTo()) - std::max(src1->getColFrom(),src2->getRowFrom() );
		break;
	case RC:
		d = std::min(src1->getRowTo(), src2->getColTo()) - std::max(src1->getRowFrom(),src2->getColFrom() );
		break;
	case CC:
		d = std::min(src1->getColTo(), src2->getColTo()) - std::max(src1->getColFrom(),src2->getColFrom() );
		break;
	}

	debug_cerr(5, "alignments are non-overlapping: distance = " << -d+1);

	if (d <= 0) return -d+1;

	debug_cerr(5, "checking distance on residue level");

	// get closest distance
	AlignmentIterator it1(src1->begin());
	AlignmentIterator it1_end(src1->end());
	AlignmentIterator it2(src2->begin());
	AlignmentIterator it2_end(src2->end());

	d = std::numeric_limits<Position>::max();
	while ( it1 != it1_end && it2 != it2_end )
	{
		const ResiduePair & x_pair = *it1;
		const ResiduePair & y_pair = *it2;

		Position map1 = NO_POS;
		Position map2 = NO_POS;

		switch (mode)
		{
		case RR:
			map1 = x_pair.mRow;
			map2 = y_pair.mRow;
			break;
		case CR:
			map1 = x_pair.mCol;
			map2 = y_pair.mRow;
			break;
		case RC:
			map1 = x_pair.mRow;
			map2 = y_pair.mCol;
			break;
		case CC:
			map1 = x_pair.mCol;
			map2 = y_pair.mCol;
			break;
		}

		if (map1 == map2)
		{
			return 0;
		}
		else
		{
			if (map1 < map2)
			{
				++it1;
				d = std::min( d, map2 - map1 );
			}
			else
			{
				++it2;
				d = std::min( d, map1 - map2 );
			}
		}
	}
	return d;
}

//-----------------------------------------------------------------------------------------
Position getAlignmentOverlap(
			const HAlignment & src1,
			const HAlignment & src2,
			const CombinationMode mode )
{
	debug_func_cerr(5);

	// check if ranges overlap
	if (!hasRangeOverlap( src1, src2, mode, 0))
		return 0;

	// check if enough residues overlap
	AlignmentIterator it1(src1->begin());
	AlignmentIterator it1_end(src1->end());
	AlignmentIterator it2(src2->begin());
	AlignmentIterator it2_end(src2->end());

	int noverlap = 0;
	while ( it1 != it1_end && it2 != it2_end )
	{
		const ResiduePair & x_pair = *it1;
		const ResiduePair & y_pair = *it2;

		Position map1 = NO_POS;
		Position map2 = NO_POS;

		switch (mode)
		{
		case RR:
			map1 = x_pair.mRow;
			map2 = y_pair.mRow;
			break;
		case CR:
			map1 = x_pair.mCol;
			map2 = y_pair.mRow;
			break;
		case RC:
			map1 = x_pair.mRow;
			map2 = y_pair.mCol;
			break;
		case CC:
			map1 = x_pair.mCol;
			map2 = y_pair.mCol;
			break;
		}

		if (map1 == map2)
		{
			++noverlap;
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
	return noverlap;
}

//-----------------------------------------------------------------------------------------
bool hasAlignmentOverlap(
		const HAlignment & src1,
		const HAlignment & src2,
		const CombinationMode mode,
		const int min_overlap )
{
	debug_func_cerr(5);

	// check if ranges overlap
	if (!hasRangeOverlap( src1, src2, mode, min_overlap))
		return false;

	// check if enough residues overlap
	AlignmentIterator it1(src1->begin());
	AlignmentIterator it1_end(src1->end());
	AlignmentIterator it2(src2->begin());
	AlignmentIterator it2_end(src2->end());

	int noverlap = 0;
	while ( it1 != it1_end && it2 != it2_end )
	{
		const ResiduePair & x_pair = *it1;
		const ResiduePair & y_pair = *it2;

		Position map1 = NO_POS;
		Position map2 = NO_POS;

		switch (mode)
		{
		case RR:
			map1 = x_pair.mRow;
			map2 = y_pair.mRow;
			break;
		case CR:
			map1 = x_pair.mCol;
			map2 = y_pair.mRow;
			break;
		case RC:
			map1 = x_pair.mRow;
			map2 = y_pair.mCol;
			break;
		case CC:
			map1 = x_pair.mCol;
			map2 = y_pair.mCol;
			break;
		}

		if (map1 == map2)
		{
			if( ++noverlap >= min_overlap )
				return true;
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
	return false;
}

//-----------------------------------------------------------------------------------------
void combineAlignment(
		HAlignment & dest,
		const HAlignment & src1,
		const HAlignment & src2,
		const CombinationMode mode )
{
	debug_func_cerr(5);

	dest->clear();

	AlignmentIterator it1(src1->begin());
	AlignmentIterator it1_end(src1->end());
	AlignmentIterator it2(src2->begin());
	AlignmentIterator it2_end(src2->end());

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
			map1 = x_pair.mRow; value1 = x_pair.mCol;
			map2 = y_pair.mRow; value2 = y_pair.mCol;
			break;

		case CR:
			map1 = x_pair.mCol; value1 = x_pair.mRow;
			map2 = y_pair.mRow; value2 = y_pair.mCol;
			break;

		case RC:
			map1 = x_pair.mRow; value1 = x_pair.mCol;
			map2 = y_pair.mCol; value2 = y_pair.mRow;
			break;

		case CC:
			map1 = x_pair.mCol; value1 = x_pair.mRow;
			map2 = y_pair.mCol; value2 = y_pair.mRow;
			break;
		}

		// cout << "map1:" << map1 << " value1:" << value1 << " map2:" << map2 << " value2:" << value2 << endl;

		if (map1 == map2)
		{
			dest->addPair( ResiduePair(value1, value2, 0));
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

//------------------------------------------------------------------------------------------------------------
void writeAlignmentTable(
		std::ostream & output,
		const HAlignment & src,
		unsigned int ncols,
		bool with_scores)
{
	debug_func_cerr(5);

	if (src->isEmpty())
		return;

	output << "length=" << src->getLength()
	<< " score=" << src->getScore()
	<< " gaps=" << src->getNumGaps()
	<< endl;

	AlignmentIterator it = src->begin();
	AlignmentIterator it_end = src->end();

	unsigned int col = 0;

	for (; it!=it_end; ++it)
	{
		output << std::setw(6) << it->mRow << std::setw(6) << it->mCol;
		if (with_scores)
			output << setw(6) << setprecision(2) << it->mScore;
		if (++col == ncols)
		{
			output << endl;
			col = 0;
		}
		else
		{
			output << '|';
		}
	}

	return;
}



//--------------------------------------------------------------------------------------------------------------
void writeWraparoundAlignment( std::ostream & output,
		const HAlignandum & row,
		const HAlignandum & col,
		const HAlignment & ali,
		size_t max_insert_length )
{
	debug_func_cerr(5);

	int col_len = col->getLength();

	int *inserts    = new int[col_len + 1];
	int *col_counts = new int[col_len + 1];
	int *position   = new int[col_len + 1];
	int i;


	for (i = 0; i <= col_len; i++)
	{
		col_counts[i] = 0;
		inserts[i]    = 0;
		position[i]   = -1;
	}

	AlignmentIterator it = ali->begin();
	AlignmentIterator it_end = ali->end();

	int nrepeats = 1;

	// go through alignemnt by rows and maximum insertions before every row-position
	int last_col = it->mCol - 1;
	int last_row = it->mRow - 1;

	for (; it != it_end; ++it)
	{
		int current_col = it->mCol;
		int current_row = it->mRow;

		int col_ins = current_col - last_col - 1;                 // negative, if wrapping around
		int row_ins = current_row - last_row - 1;

		if (col_ins < 0) nrepeats ++;

		if (row_ins > max_insert_length) row_ins = max_insert_length;

		// if ( (col_ins > 1) && (inserts[current_col] < col_ins)) inserts[current_col] = col_ins;
		if ( (row_ins > 1) && (inserts[current_col] < row_ins))
			inserts[current_col] = row_ins;

		col_counts[current_col]++;
		last_col = current_col;
		last_row = current_row;
	}

	// count total number of insertions for calculating the total length of the alignment
	int total_inserts = 0; for (i = 1; i <= col_len; i++) total_inserts += inserts[i];

	// calculate length of alignment and starting and ending position, ali_len is chosen, so that positions in strings later start at 1
	int first_pos = 1;       while (first_pos <= col_len && col_counts[first_pos] < 1) first_pos++;
	int last_pos  = col_len; while (last_pos  >= 1       && col_counts[last_pos]  < 1) last_pos --;
	int ali_len   = last_pos - first_pos + 1 + total_inserts + 1;

	// create map for starting positions
	for (i = first_pos; i <= last_pos; i++) position[i] = 1 + position[i-1] + inserts[i];

	// allocate memory, row 0 is for row, the remaining for the columns
	char gap_char = getDefaultEncoder()->getGapChar();
	char * buffer = new char[ali_len * (nrepeats + 1)];
	for (i = 0; i < (ali_len * (nrepeats + 1)); i++) buffer[i] = gap_char;

	// build columns
	it = ali->begin();
	last_col = it->mCol - 1;
	last_row = it->mRow - 1;
	int repeat_no = 0;
	for (; it != it_end; ++it) {
		int current_col = it->mCol;
		int current_row = it->mRow;

		int col_ins        = current_col - last_col - 1;
		int row_ins        = current_row - last_row - 1;

		if (col_ins < 0) repeat_no++;                   // check if new repeat appeared

		if (col_ins > max_insert_length) col_ins = max_insert_length;
		if (row_ins > max_insert_length) row_ins = max_insert_length;

		// some remarks on the following:

		// add aligned residue and inserts for row, row is mapped onto col
		int pos = position[current_col] + ali_len * repeat_no;
		int x   = current_row;
		buffer[pos] = row->asChar( x-- );
		for (i = pos - 1; i >= pos - row_ins; i--) buffer[i] = row->asChar( x-- ) + 32;

		// add aligned residues and inserts for col
		pos = position[current_col] + ali_len * (nrepeats);
		x   = current_col;
		buffer[pos] = col->asChar( x-- );

		for (i = pos - 1; i >= pos - col_ins; i--) {
			int c = col->asChar( x );
			if (col_counts[x] < 1)
				c += 32;
			buffer[i] = c;
			x--;
		}

		last_row = current_row;
		last_col = current_col;

	}

	// write result to stream

	int pos = 0;
	for (i = 0; i <= nrepeats; i++)
	{
		output << std::string( &buffer[pos], ali_len - 1) << endl;
		pos += ali_len;
	}

	delete [] buffer;
	delete [] position;
	delete [] inserts;
	delete [] col_counts;

	return;
}

//---------------------------------------------------------------------------------------
void filterAlignmentRemovePairs(
		HAlignment & dest,
		const HAlignment & filter,
		const CombinationMode mode )
{
	debug_func_cerr(5);

	// delete pairs in-situ.
	// Note: The iterators should not be invalidated, if you remove a residue. This should work with
	// the Alignment-objects that are based on <set>
	// Another alternative would be to iterate over the filter. However, then the problem is,
	// that multiple residues would have to be deleted.

	AlignmentIterator it1(dest->begin());
	AlignmentIterator it1_end(dest->end());

	while ( it1 != dest->end())
	{

		const ResiduePair & x_pair = *it1;
		switch (mode)
		{

		case RR:
			if (filter->mapRowToCol( x_pair.mRow ))
				dest->removePair( x_pair );
			break;
		case CR:
			if (filter->mapRowToCol( x_pair.mCol ))
				dest->removePair( x_pair );
			break;
		case RC:
			if (filter->mapColToRow( x_pair.mRow ))
				dest->removePair( x_pair );
			break;
		case CC:
			if (filter->mapColToRow( x_pair.mCol ))
				dest->removePair( x_pair );
			break;
		}
		it1++;
	}

	return;
}

//-------------------------------------------------------------------------------------------------
// this works only for pairswise alignments, where both alignments are sorted by row.
void filterAlignmentRemovePairwiseSorted(
		HAlignment & dest,
		const HAlignment & filter,
		const CombinationMode mode )
{
	debug_func_cerr(5);


	// work with a temporary copy, because I am not entirely sure, if my iterators will fail,
	// if I delete residues while they are active: i.e. spend some time on improving the iterators :=)

	const HAlignment copy = dest->getClone();

	AlignmentIterator it1(copy->begin());
	AlignmentIterator it1_end(copy->end());
	AlignmentIterator it2(filter->begin());
	AlignmentIterator it2_end(filter->end());

	while ( it1 != it1_end && it2 != it2_end )
	{

		const ResiduePair & x_pair = *it1;
		const ResiduePair & y_pair = *it2;

		Position map1 = 0;
		Position map2 = 0;

		switch (mode)
		{

		case RR:
			map1 = x_pair.mRow;
			map2 = y_pair.mRow;
			break;

		case CR:
			map1 = x_pair.mCol;
			map2 = y_pair.mRow;
			break;

		case RC:
			map1 = x_pair.mRow;
			map2 = y_pair.mCol;
			break;

		case CC:
			map1 = x_pair.mCol;
			map2 = y_pair.mCol;
			break;
		}

		// cout << "map1:" << map1 << " map2:" << map2 << endl;

		if (map1 == map2) {
			dest->removePair( x_pair );
			it1++;
			it2++;
		} else {
			if (map1 < map2)
				it1++;
			else
				it2++;
		}

	}

	return;
}

void addDiagonal2Alignment(
		HAlignment & dest,
		Position row_from,
		Position row_to,
		Position col_offset)
{
	debug_func_cerr(5);

	dest->addDiagonal( row_from, row_to, col_offset );

	return;
}

//-------------------------------------------------------------------------------------------------

void fillAlignmentGaps(
		HAlignment & dest,
		const HAlignator &  alignator,
		const HAlignandum & row,
		const HAlignandum & col )
{

	debug_func_cerr( 5 );

	if ( dest->getLength() == 0) return;

	HAlignment copy = dest->getClone();
	HAlignment temp_map_row2col = makeAlignmentVector();

	AlignmentIterator it(copy->begin());
	AlignmentIterator end(copy->end());

	Position last_row = std::numeric_limits<Position>::max();;
	Position last_col = std::numeric_limits<Position>::max();

	++it;

	for (; it != end; ++it)
	{
		if (it->mRow - last_row > 1 && it->mCol - last_col > 1)
		{
			temp_map_row2col->clear();
			row->useSegment( last_row + 1, it->mRow);
			col->useSegment( last_col + 1, it->mCol);
			alignator->align( temp_map_row2col, row, col );
			addAlignment2Alignment( dest, temp_map_row2col );
			debug_cerr( 5, "filling gap between " <<
					last_row << "-" << it->mRow << " and " << last_col << "-" << it->mCol <<
					" with " << temp_map_row2col->getNumAligned() << " pairs");

		}
		last_row = it->mRow;
		last_col = it->mCol;
	}

	row->useSegment();
	col->useSegment();

	return;
}


//-------------------------------------------------------------------------------------------------
// calculate percent identity, normalised on alignment mLength
double calculatePercentIdentity(
		const HAlignment & src,
		const HAlignandum & row,
		const HAlignandum & col)
{

	if (src->getLength() == 0) return 0;

	AlignmentIterator it = src->begin();
	AlignmentIterator it_end = src->end();

	int nidentities = 0;
	int naligned = 0;

	for (; it != it_end; ++it) {
		ResiduePair p = *it;

		naligned++;
		if ( row->asResidue(p.mRow) == col->asResidue(p.mCol) )
			nidentities++;
	}

	return (double)nidentities / (double)naligned;
}


//----------------------------------------------------------------------------------------------------
double calculatePercentSimilarity( const HAlignment & src)
{

	if (src->getLength() == 0) return 0;

	AlignmentIterator it = src->begin();
	AlignmentIterator it_end = src->end();

	int nsimilarities = 0;
	int naligned = 0;

	for (; it != it_end; ++it)
	{
		naligned ++;

		if ((*it).mScore > 0)
			nsimilarities++;
	}
	return (double)nsimilarities / (double)naligned;
}

//----------------------------------------------------------------------------------------------------
void rescoreAlignment(
		HAlignment & dest,
		const HAlignandum & row,
		const HAlignandum & col,
		const HScorer & scorer )
{
	debug_func_cerr(5);

	AlignmentIterator it(dest->begin());
	AlignmentIterator it_end(dest->end());

	for (; it != it_end; ++it)
	{
		ResiduePair & p = const_cast<ResiduePair &>(*it);
		p.mScore = scorer->getScore( p.mRow, p.mCol );
	}

	return;
}

//----------------------------------------------------------------------------------------------------
void rescoreAlignment(
		HAlignment & dest,
		const Score score )
{
	debug_func_cerr(5);

	AlignmentIterator it(dest->begin());
	AlignmentIterator it_end(dest->end());

	for (; it != it_end; ++it)
	{
		ResiduePair & p = const_cast<ResiduePair &>(*it);
		p.mScore = score;
	}

	return;
}


//----------------------------------------------------------------------------------------------------
void calculateAffineScore(
		HAlignment & dest,
		const Score gop,
		const Score gep)
{
	debug_func_cerr(5);

	Score score = 0;

	AlignmentIterator it(dest->begin());
	AlignmentIterator it_end(dest->end());

	Position last_row = std::numeric_limits<Position>::max();
	Position last_col = std::numeric_limits<Position>::max();

	for (; it != it_end; ++it)
	{
		Position d;
		Position row = it->mRow;
		Position col = it->mCol;

		if ( (d = (row - last_row - 1)) > 0)
			score += gop + d * gep;

		if ( (d = (col - last_col - 1)) > 0)
			score += gop + d * gep;

		score += it->mScore;
		last_row = row;
		last_col = col;
	}

	dest->setScore(score);
	return;
}

//----------------------------------------------------------------------------------------------------
/*fill an alignment with a repeat unit from a wrap-around alignment */
/* code still broken with the skip_negative_ends */
void fillAlignmentRepeatUnit(
		HAlignment & dest,
		const HAlignment & src,
		Position first_row_residue,
		bool skip_negative_ends)
{
	debug_func_cerr( 5 );

	if (first_row_residue == 0)
		first_row_residue = src->getRowFrom();

	AlignmentIterator it(src->begin());
	AlignmentIterator it_end(src->end());

	dest->clear();

	while ( (it != it_end) && (it->mRow < first_row_residue)) ++it;
	if (it == it_end) return;

	Position last_col = it->mCol - 1;

	skip_negative_ends = false;
	if (skip_negative_ends)
		while ( (it != it_end) && (it->mCol > last_col) )
		{
			if (it->mScore > 0) break;
			last_col = it->mCol;
		}

	Position last_positive = it->mRow;
	while ( (it != it_end) && (it->mCol > last_col) )
	{
		last_col = it->mCol;
		dest->addPair( ResiduePair(it->mRow, last_col, it->mScore) );
		if (it->mScore > 0) last_positive = it->mRow;
		++it;
	}

	if (skip_negative_ends)
		dest->removeRowRegion( last_positive + 1, dest->getRowTo());

	return;
}

//------------------------------------------------------------------------------------------------------
inline Position insertResidues( HAlignment & dest,
		Position last_res,
		Position current_res,
		Position current_combined)
{

	for( Position i = last_res; i < current_res; i++)
		dest->addPair( ResiduePair(i, current_combined++, 0.0));
	return current_combined;
}


/*
 */
void expandAlignment( HAlignment & dest1,
		HAlignment & dest2,
		const HAlignment & src,
		bool insert_gaps_row,
		bool insert_gaps_col,
		bool use_end_row,
		bool use_end_col,
		Position row_length,
		Position col_length)
{
	debug_func_cerr( 5 );

	dest1->clear();
	dest2->clear();

	AlignmentIterator it(src->begin());
	AlignmentIterator it_end(src->end());

	// current position in combined alignment
	Position current_combined = 0;
	Position current_row = it->mRow;
	Position current_col = it->mCol;

	// add positions before first aligned position
	if (use_end_row)
		current_combined = insertResidues( dest1, 0, current_row, current_combined);
	if (use_end_col)
		current_combined = insertResidues( dest2, 0, current_col, current_combined);

	Position last_row = current_row;
	Position last_col = current_col;

	// iteration over alignmnet
	for ( ; it != it_end; ++it )
	{
		Score current_score = it->mScore;
		current_row = it->mRow;
		current_col = it->mCol;

		// add gaps before match:
		// 1. row
		if (insert_gaps_col)
			current_combined = insertResidues( dest1, last_row, current_row, current_combined);

		// 2. col
		if (insert_gaps_row)
			current_combined = insertResidues( dest2, last_col, current_col, current_combined);

		// add match
		dest1->addPair(ResiduePair(current_row, current_combined, current_score));
		dest2->addPair(ResiduePair(current_col, current_combined, current_score));

		current_combined++;

		last_row = current_row + 1;
		last_col = current_col + 1;

	}

	// add positions after last aligned position
	if (use_end_row)
		current_combined = insertResidues( dest1, last_row, row_length, current_combined);
	if (use_end_col)
		current_combined = insertResidues( dest2, last_col, col_length, current_combined);

}
//-----------------------------------------------------------------------------------------
/* remove all those residues from an alignmnent, which are not
     in sequence. This ensures, that col_i < col_i+1 and row < row_i+1
     Only use with AlignmentVector

 */
void flattenAlignment( HAlignment & dest )
{
	debug_func_cerr( 5 );

	AlignmentIterator it(dest->begin());
	AlignmentIterator it_end(dest->end());

	Position last_row = dest->getRowFrom() - 1;
	Position last_col = dest->getColFrom() - 1;

	Position max_row = dest->getRowTo();

	for (; it != it_end; ++it) {

		const ResiduePair & p = *it;

		Position current_row = p.mRow;
		Position current_col = p.mCol;

		// if there is an intersection, save current alignment
		if (current_row <= last_row || current_col <= last_col) {
			dest->removePair( p );
		} else {
			last_row = current_row;
			last_col = current_col;
		}

		// patch, as iterator becomes invalidated
		if (current_row == max_row)
			break;

	}

	return;
}


//-----------------------------------------------------------------------------------------
/* split an alignment, if there are gaps larger than a certain threshold either in row or
    col or both.
 */
HFragmentVector splitAlignment(
		const HAlignment & src,
		const int max_gap_width,
		bool split_row, bool split_col)
{
	debug_func_cerr( 5 );

	AlignmentIterator it(src->begin());
	AlignmentIterator it_end(src->end());

	HFragmentVector result(new FragmentVector());

	Position last_col = src->getColFrom() -1;
	Position last_row = src->getRowFrom() -1;

	HAlignment current_ali = src->getNew();

	for (; it != it_end; ++it) {

		const ResiduePair & p = *it;
		Position current_row = p.mRow;
		Position current_col = p.mCol;

		if ( (split_col && ((current_col - last_col) > max_gap_width)) ||
				(split_row && ((current_row - last_row) > max_gap_width))) {

			result->push_back( current_ali );

			current_ali = src->getNew();
		}

		current_ali->addPair( ResiduePair(p) );

		last_row = current_row;
		last_col = current_col;

	}

	result->push_back( current_ali );

	return result;
}

//-----------------------------------------------------------------------------------------
/* split an alignment at points of intersection with another alignment.
 */
HFragmentVector splitAlignment(
		const HAlignment & src1,
		const HAlignment & src2,
		const CombinationMode mode )
{

	debug_func_cerr( 5 );

	AlignmentIterator it1(src1->begin());
	AlignmentIterator it1_end(src1->end());

	AlignmentIterator it2(src2->begin());
	AlignmentIterator it2_end(src2->end());

	HFragmentVector result(new FragmentVector());

	bool in_row1 = true;
	bool in_row2 = true;

	switch (mode)
	{
	case RR: break;
	case CR:
		in_row1 = false; break;
	case RC:
		in_row2 = false; break;
	case CC:
		in_row1 = false; in_row2 = false; break;
	}

	Position other_pos = ((in_row2) ? src2->getRowFrom() : src2->getColFrom());

	HAlignment current_ali = src1->getNew();

	for (; it1 != it1_end; ++it1)
	{

		const ResiduePair & p = *it1;

		Position current_pos = (in_row1) ? p.mRow : p.mCol;

		// if there is an intersection, save current alignment
		if (current_pos > other_pos)
		{

			/* test if alignment has residues in it
	 (might not be the case in first iteration). */
			if (current_ali->getLength() > 0)
			{
				result->push_back( current_ali );
				current_ali = src1->getNew();
			}

			// advance to next pos in other alignment
			while ( other_pos < current_pos && ++it2 != it2_end)
				other_pos = (in_row2) ? it2->mRow : it2->mCol;

			if (it2 == it2_end)
				other_pos = std::numeric_limits<Position>::max();
		}

		current_ali->addPair( ResiduePair(p) );
	}

	result->push_back( current_ali );

	return result;

}

//-----------------------------------------------------------------------------------------
void fillAlignmentGaps(
		HAlignment & dest,
		const Position max_length )
{
	debug_func_cerr(5);

	if (dest->getLength() == 0) return;

	AlignmentIterator it(dest->begin());
	AlignmentIterator it_end(dest->end());

	Position last_row = it->mRow;
	Position last_col = it->mCol;

	for (; it != it_end; ++it )
	{

		Position this_row = it->mRow;
		Position this_col = it->mCol;

		Position gap_row = this_row - last_row - 1;

		if ( gap_row > 0 &&
				gap_row <= max_length &&
				gap_row == (this_col - last_col - 1) )
		{
			while (++last_row < this_row)
			{
				++last_col;
				dest->addPair( ResiduePair(last_row, last_col, 0));
			}
		}

		last_row = this_row;
		last_col = this_col;
	}

	return;
}

/* remove small fragments from alignment.
    This method removes fragments from an alignment. A fragment
    is a part of an alignment, that is short (max_fragment_length)
    and surrounded by large gaps (min_gap_length).
    Fragments are only removed in col.
 */

void removeFragments( HAlignment & dest,
		unsigned int window_size,
		unsigned int min_gap_length,
		Position row_length ) {


	/* use a sliding window of size window_size, and count
     the following indicators for the central residue:

     num_left_gaps: number of gaps on left hand side of first
     residue in window
     num_right_gaps: number of gaps on right hand side of last
     residue in window

     left_pos: position of leftmost residue in window
     right_pos: position of rightmost residue in window

     delete a residue:
     if	num_left_gaps  larger than min_gap_length
     and num_right_gaps larger than min_gap_length
     and num_residues

	 */

	if (row_length == 0)
		row_length = dest->getRowTo();

	for (Position this_pos = dest->getRowFrom(); this_pos < dest->getRowTo(); this_pos ++) {

		// adjust left position
		Position left_pos = this_pos - window_size;
		while (dest->mapRowToCol( left_pos ) == NO_POS) left_pos ++;

		// adjust right position
		Position right_pos = this_pos + window_size;
		while (dest->mapRowToCol( right_pos ) == NO_POS) right_pos --;

		//--------------------------------------------------------------------------
		// count number of gaps on left and right side. This can probably be
		// made more efficient.
		// at the ends calculate number of gaps until end of row.
		unsigned int num_left_gaps = window_size - (this_pos - left_pos);

		if (left_pos == dest->getRowFrom()) {
			num_left_gaps = left_pos - 1;
		} else {
			Position x = left_pos;
			while (x > dest->getRowFrom() && dest->mapRowToCol( --x ) == NO_POS) num_left_gaps ++;
		}

		unsigned int num_right_gaps = window_size - (right_pos - this_pos);

		if (right_pos == dest->getRowTo())
		{
			num_right_gaps = row_length - right_pos;
		} else
		{
			Position x = right_pos;
			while (x < dest->getRowTo() && dest->mapRowToCol( ++x ) == NO_POS) num_right_gaps ++;
		}

		// std::cout << "center=" << this_pos << " left=" << left_pos << " gl=" << num_left_gaps
		// << " right=" << right_pos << " gr=" << num_right_gaps << endl;

		//------------------------------------------------------------------------
		// check if region is to be deleted
		if ( (num_left_gaps > min_gap_length) &&
				(num_right_gaps > min_gap_length) )
		{
			dest->removeRowRegion( left_pos, right_pos );
			this_pos += window_size;
		}

		// go to next non-gap position
		while (this_pos <= dest->getColTo() && dest->mapRowToCol(this_pos) == NO_POS) this_pos++;

	}

}

//-----------------------------------------------------------------------------------------------
/* starting from the end of an alignment, remove
    residues as long as the score increases when these
    residues are removed.
 */
void pruneAlignment(
		HAlignment & src,
		Score gop,
		Score gep )
{
	debug_func_cerr(5);

	//-----------------------------------------------------------
	// remove starting from left
	{
		AlignmentIterator it(src->begin());
		AlignmentIterator it_end(src->end());

		const ResiduePair & p = *it;

		Score score = -p.mScore;
		Position last_row = src->getRowFrom();
		Position last_col = src->getColFrom();

		++it;

		for (; it != it_end, score > 0; ++it) {

			const ResiduePair & p = *it;
			// apply filter
			Position this_row      = p.mRow;
			Position this_col      = p.mCol;
			Position d;

			if ( (d = this_row - last_row - 1) > 0)
				score -= gop + d * gep;
			if ( (d = this_col - last_col - 1) > 0)
				score -= gop + d * gep;

			score -= p.mScore;

			last_row = this_row;
			last_col = this_col;
		}

		if (--last_row >= src->getRowFrom())
			src->removeRowRegion( src->getRowFrom(), last_row );
		if (--last_col >= src->getColFrom())
			src->removeColRegion( src->getColFrom(), last_col );
	}

	//-----------------------------------------------------------
	// remove starting from right. Ideally you would use reverse
	// iterators, but as I have not implemented them yet, I use this
	// patch.
	{

		Position last_row = src->getRowTo();
		Position last_col = src->getColTo();
		const ResiduePair & p = src->getPair( ResiduePair( last_row, last_col) );
		Score score = -p.mScore;

		Position this_row = last_row - 1;

		for (; last_row >= src->getRowFrom(), score > 0; --this_row)
		{

			Position this_col = src->mapRowToCol( this_row );

			if (!this_col)
				continue;

			const ResiduePair & p = src->getPair( ResiduePair( this_row, this_col) );

			// apply filter

			Position d;

			if ( (d = last_row - this_row - 1) > 0)
				score -= gop + d * gep;
			if ( (d = last_col - this_col - 1) > 0)
				score -= gop + d * gep;

			score -= p.mScore;

			last_row = this_row;
			last_col = this_col;
		}

		if (++last_row <= src->getRowTo())
			src->removeRowRegion( last_row, src->getRowTo() );
		if (++last_col <= src->getColTo())
			src->removeColRegion( last_col, src->getColTo() );
	}

}

} // namespace alignlib

