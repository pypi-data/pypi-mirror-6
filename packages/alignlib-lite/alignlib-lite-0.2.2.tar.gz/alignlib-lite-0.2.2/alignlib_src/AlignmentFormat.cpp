//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: AlignmentFormatBlocks.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------    


#include <iostream>
#include <iomanip>
#include <iterator>
#include <cstring>
#include <string>
#include <sstream>

#include "alignlib_types.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "AlignmentFormat.h"
#include "HelpersEncoder.h"
#include "HelpersAlignment.h"
#include "HelpersAlignatum.h"

using namespace std;

namespace alignlib 
{

//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
AlignmentFormat::AlignmentFormat() 
: 
	mRowFrom(NO_POS), mRowTo(NO_POS), mColFrom(NO_POS), mColTo(NO_POS)
	{
	}

AlignmentFormat::AlignmentFormat( const AlignmentFormat & src) 
: 
	mRowFrom(src.mRowFrom), mRowTo(src.mRowTo), 
	mColFrom(src.mColFrom), mColTo(src.mColTo)
	{
	}

AlignmentFormat::AlignmentFormat( std::istream & input ) 
{
	load( input );
}

AlignmentFormat::AlignmentFormat( const std::string & src) 
{
	std::istringstream i(src.c_str());
	load( i );
}

AlignmentFormat::AlignmentFormat( const HAlignment & src) 
{
	fill( src );
}

AlignmentFormat::~AlignmentFormat()
{
}

void AlignmentFormat::fill( const HAlignment & src )
{
	debug_func_cerr( 5 );
	mRowFrom = src->getRowFrom();
	mRowTo = src->getRowTo();
	mColFrom = src->getColFrom();
	mColTo = src->getColTo();
}

void AlignmentFormat::copy( HAlignment & dest ) const
{
	debug_func_cerr( 5 );
	dest->clear();
}

void AlignmentFormat::load( std::istream & input)
{
	debug_func_cerr( 5 );
	input >> mRowFrom >> mRowTo >> mColFrom >> mColTo;	
}

void AlignmentFormat::save( std::ostream & output) const
{
	debug_func_cerr( 5 );
	output << mRowFrom << "\t" << mRowTo << "\t" << mColFrom << "\t" << mColTo;
}

//--------------------------------------------------------------------------------------------------------------------------------
std::ostream & operator<< (std::ostream & output, const AlignmentFormat & src)
{
	src.save( output );
	return output;
}

//--------------------------------------------------------------------------------------------------------------------------------
std::istream & operator>> (std::istream & input, AlignmentFormat & dest) 
{
	dest.load( input );
	return input;
}

//--------------------------------------------------------------------------------------------------------------------------------
inline void parseList( const std::string & str, PositionVector & dest )
{
        std::string delimiters(",");
  
	string::size_type last_pos = str.find_first_not_of( delimiters, 0);
	string::size_type pos     = str.find_first_of(delimiters, last_pos);
  
	while (string::npos != pos || string::npos != last_pos)
	{
		dest.push_back(atoi(str.substr(last_pos, pos - last_pos).c_str()));
		last_pos = str.find_first_not_of(delimiters, pos);
		pos = str.find_first_of(delimiters, last_pos);
	}	
}

//--------------------------------------------------------------------------------------------------------------------------------
inline void parseList( std::istream & input, PositionVector & dest )
{
	std::string str;
	input >> str;
	return parseList( str, dest );
}
//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
AlignmentFormatBlocks::AlignmentFormatBlocks() 
: AlignmentFormat(), mRowStarts(), mColStarts(), mBlockSizes()
{
}

AlignmentFormatBlocks::AlignmentFormatBlocks( const Position row_start,
					      const Position col_start,
					      const std::string & block_sizes,
					      const std::string & row_starts,
					      const std::string & col_starts )
  : AlignmentFormat()
{
  mRowFrom = row_start;
  mColFrom = col_start;

  parseList( block_sizes, mBlockSizes );
  parseList( row_starts, mRowStarts );
  parseList( col_starts, mColStarts );
  
  mRowTo = row_start + mRowStarts[mRowStarts.size() - 1] + mBlockSizes[mBlockSizes.size()-1];
  mColTo = row_start + mColStarts[mColStarts.size() - 1] + mBlockSizes[mBlockSizes.size()-1];
    
}
  
	
AlignmentFormatBlocks::AlignmentFormatBlocks( std::istream & input ) 
: AlignmentFormat(), mRowStarts(), mColStarts(), mBlockSizes()
{
	load( input );
}

AlignmentFormatBlocks::AlignmentFormatBlocks( const std::string & src) 
: AlignmentFormat(), mRowStarts(), mColStarts(), mBlockSizes()
	{
	std::istringstream i(src.c_str());
	load( i );
	}

AlignmentFormatBlocks::AlignmentFormatBlocks( const HAlignment & src) 
: AlignmentFormat(), mRowStarts(), mColStarts(), mBlockSizes()
{
	fill( src );
}


AlignmentFormatBlocks::~AlignmentFormatBlocks () 
{
	mRowStarts.clear();
	mColStarts.clear();
	mBlockSizes.clear();
}

AlignmentFormatBlocks::AlignmentFormatBlocks (const AlignmentFormatBlocks & src ) 
: AlignmentFormat( src )
{
	mRowStarts.clear();
	mColStarts.clear();
	mBlockSizes.clear();

	std::copy( src.mRowStarts.begin(), 
			src.mRowStarts.end(), 
			std::back_inserter< PositionVector>(mRowStarts) );
	std::copy( src.mColStarts.begin(), 
			src.mColStarts.end(), std::
			back_inserter< PositionVector>(mColStarts) );
	std::copy( src.mBlockSizes.begin(), 
			src.mBlockSizes.end(), 
			std::back_inserter< PositionVector>(mBlockSizes)) ;

}

Position AlignmentFormatBlocks::applyOffset( 
		const Position & pos,
		const Position & offset ) const
{
	debug_func_cerr(5);
	return pos - offset;
}

Position AlignmentFormatBlocks::removeOffset( 
		const Position & pos,
		const Position & offset ) const
{
	return pos + offset;
}

void AlignmentFormatBlocks::fill( const HAlignment & src)
{
	debug_func_cerr(5);

	AlignmentFormat::fill( src );

	mRowStarts.clear();
	mColStarts.clear();
	mBlockSizes.clear();

	// sanity checks
	if (src->isEmpty()) return;

	AlignmentIterator it(src->begin());
	AlignmentIterator it_end(src->end());

	Position last_col = it->mCol; 
	Position last_row = it->mRow; 

	Position d_row, d_col;

	// start iteration at col_from + 1
	debug_cerr(5, "adding pair\t" << *it << '\t' 
				<< applyOffset( it->mRow, mRowFrom ) << '\t' 
				<< applyOffset( it->mCol, mColFrom ) );
	
	mRowStarts.push_back( applyOffset( it->mRow, mRowFrom )) ;
	mColStarts.push_back( applyOffset( it->mCol, mColFrom ));
	Position block_size = 1;

	++it;

	for (; it != it_end; ++it)
	{
		Position current_row = it->mRow;
		Position current_col = it->mCol;

		if ( (current_row - last_row) > 1 || (current_col - last_col) > 1) 
		{
			debug_cerr(5, "adding pair\t" << *it << '\t' 
						<< applyOffset( current_row, mRowFrom ) << '\t' 
						<< applyOffset( current_col, mColFrom ) );

			mBlockSizes.push_back( block_size );
			mRowStarts.push_back( applyOffset( current_row, mRowFrom ));
			mColStarts.push_back( applyOffset( current_col, mColFrom ));
			block_size = 0;
		}       
		++ block_size;
		last_row = current_row;
		last_col = current_col;
	}
	mBlockSizes.push_back( block_size );

	debug_cerr(5, "number of blocks=" << mBlockSizes.size() );
}

//--------------------------------------------------------------------------------------------------------------------------------
void AlignmentFormatBlocks::copy( HAlignment & dest ) const 
{
	debug_func_cerr(5);

	debug_cerr(5, "number of blocks=" << mBlockSizes.size() );

	AlignmentFormat::copy( dest );

	for (int x = 0; x < mRowStarts.size(); ++x)
	{
		Position row = removeOffset( mRowStarts[x], mRowFrom ); 
		Position col = removeOffset( mColStarts[x], mColFrom );		
		for (int l = 0; l < mBlockSizes[x]; ++l, ++row, ++col)
			dest->addPair( row, col );
	}
}

//--------------------------------------------------------------------------------------------------------------------------------
void AlignmentFormatBlocks::save(std::ostream & output ) const
{
	debug_func_cerr(5);
	debug_cerr(5, "number of blocks to output=" << mBlockSizes.size() );

	output << mRowFrom << "\t" << mRowTo << "\t" << mColFrom << "\t" << mColTo << "\t";
	std::copy( mRowStarts.begin(), mRowStarts.end(), std::ostream_iterator<Position>(output, ","));
	output << "\t" ;
	std::copy( mColStarts.begin(), mColStarts.end(), std::ostream_iterator<Position>(output, ","));
	output << "\t";
	std::copy( mBlockSizes.begin(), mBlockSizes.end(), std::ostream_iterator<Position>(output, ","));
}

void AlignmentFormatBlocks::load(std::istream & input) 
{
	debug_func_cerr(5);
	input >> mRowFrom >> mRowTo >> mColFrom >> mColTo;

	parseList( input, mRowStarts );
	parseList( input, mColStarts );
	parseList( input, mBlockSizes );
}

//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
AlignmentFormatBlat::AlignmentFormatBlat() 
: AlignmentFormatBlocks()
{
}

// In the following methods do not use the non-empty constructors
// from Blocks, as the virtual method table has not been built and
// thus the correct methods for applyOffset are not picked up.
AlignmentFormatBlat::AlignmentFormatBlat( std::istream & input ) 
: AlignmentFormatBlocks()
{
	load( input );
}

AlignmentFormatBlat::AlignmentFormatBlat( const std::string & src) 
: AlignmentFormatBlocks()
{
	std::istringstream i(src.c_str());
	load( i );
}

AlignmentFormatBlat::AlignmentFormatBlat( const HAlignment & src) 
: AlignmentFormatBlocks()
{
	fill( src );
}

AlignmentFormatBlat::~AlignmentFormatBlat () 
{
}

AlignmentFormatBlat::AlignmentFormatBlat (const AlignmentFormatBlat & src ) 
: AlignmentFormatBlocks( src )
{
}

Position AlignmentFormatBlat::applyOffset( 
			const Position & pos,
			const Position & offset ) const
{
	debug_func_cerr(5);
	return pos;
}

Position AlignmentFormatBlat::removeOffset( 
			const Position & pos,
			const Position & offset ) const
{
	debug_func_cerr(5);
	return pos;
}

//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
AlignmentFormatEmissions::AlignmentFormatEmissions() 
: AlignmentFormat(),
mRowAlignment(""),
mColAlignment("")	
{
}

AlignmentFormatEmissions::AlignmentFormatEmissions( const HAlignment & src) 
:  AlignmentFormat(),
mRowAlignment(""),
mColAlignment("")
{
	fill( src );
}

AlignmentFormatEmissions::AlignmentFormatEmissions( std::istream & src) 
: AlignmentFormat(),
mRowAlignment(""),
mColAlignment("")	
{
	load( src );
}

AlignmentFormatEmissions::AlignmentFormatEmissions( const std::string & src) 
: AlignmentFormat(),
mRowAlignment(""),
mColAlignment("")	
{
	std::istringstream i(src.c_str());
	load( i );
}


AlignmentFormatEmissions::~AlignmentFormatEmissions () 
{
}

AlignmentFormatEmissions::AlignmentFormatEmissions (const AlignmentFormatEmissions & src ) :
	AlignmentFormat( src ), 
	mRowAlignment( src.mRowAlignment ), 
	mColAlignment( src.mColAlignment )
	{
	}

AlignmentFormatEmissions::AlignmentFormatEmissions(
		const Position row_from,
		const std::string & row,
		const Position col_from,
		const std::string & col) 
: AlignmentFormat(), 
mRowAlignment( row ), 
mColAlignment( col )
{
	mRowFrom = row_from;
	mColFrom = col_from;

	mRowTo = mRowFrom + getNumEmissions( mRowAlignment );
	mColTo = mColFrom + getNumEmissions( mColAlignment );
}

Position AlignmentFormatEmissions::getNumEmissions( const std::string & src )
{
	std::istringstream is( src.c_str() );  

	Position nemissions = 0;
	Position d = 0;   

	while (is >> d)
	{
		if (d > 0)
			nemissions += d;
	}	  
	
	return nemissions;	
	
}
		
void AlignmentFormatEmissions::fill( const HAlignment & src)
{
	debug_func_cerr(5);

	AlignmentFormat::fill( src );

	// sanity check
	if (src->isEmpty()) return;

	AlignmentIterator it(src->begin());
	AlignmentIterator it_end(src->end());

	std::ostringstream os_row;
	std::ostringstream os_col;

	Position last_col = it->mCol; 
	Position len_col = 0;
	
	while (last_col < mColFrom) 
	{
		++it;
		last_col = it->mCol;
	}

	Position last_row = it->mRow; Position len_row = 0;

	Position d_row, d_col;
	Position current_row = 0, current_col = 0;

	// start iteration at col_from + 1
	++it; len_row++; len_col++;
	for (; it != it_end; ++it)
	{
		current_row = it->mRow;
		current_col = it->mCol;

		debug_cerr( 5, "current_row: " << current_row << " " << "current_col: " << current_col);

		if (current_col > mColTo)
			break;

		if ((d_row = current_row - last_row - 1) > 0) 
		{
			os_col << "+" << len_col << "-" << d_row;

			len_col = 0;
			len_row += d_row;
		}

		if ((d_col = current_col - last_col - 1) > 0) 
		{
			os_row << "+" << len_row << "-" << d_col;
			len_row = 0;
			len_col += d_col;
		}

		last_row = current_row;
		last_col = current_col;
		len_row++; 
		len_col++;
	}

	// no ends necessary as with strstream,
	// ostringstream does it automatically.
	os_col << "+" << len_col;
	os_row << "+" << len_row;

	mRowAlignment = os_row.str();
	mColAlignment = os_col.str();
}

//--------------------------------------------------------------------------------------------------------------------------------
void AlignmentFormatEmissions::copy( HAlignment & dest ) const 
{
	debug_func_cerr(5);

	AlignmentFormat::copy( dest );

	if (mRowFrom == NO_POS || mColFrom == NO_POS)
		throw AlignlibException( "AlignmentFormat.cpp: alignment ranges not defined." );

	std::istringstream is_row( mRowAlignment.c_str() );   
	std::istringstream is_col( mColAlignment.c_str() );  

	Position row = mRowFrom;   
	Position col = mColFrom;   
	Position d_row = 0;   
	Position d_col = 0;  

	if (!(is_row >> d_row)) return;
	if (!(is_col >> d_col)) return;

	while (true) 
	{
		// cout << "0:" << d_row << " " << d_col << " " << row << " " << col << endl;
		// entry: d_row and d_col > 0
		// end: d_col or d_row or both are 0
		// emit pairs for aligned regions, i.e. d_row and d_col are positive
		while (d_row > 0 && d_col > 0) 
		{         
			dest->addPair( ResiduePair (row, col) );         
			d_row--; 
			d_col--;         
			row++; 
			col++;       
		}  

		// cout << "1:" << d_row << " " << d_col << " " << row << " " << col << endl;

		// entry: d_row and d_col < 0
		// end: d_col or d_row or both are 0
		// simply skip. This region is a gap in both sequences
		if (d_row < 0 && d_col < 0) 
		{         
			if (d_row < d_col) 
			{
				d_row -= d_col;
				d_col = 0;
			} 
			else 
			{
				d_col -= d_row;
				d_row = 0;
			}
		}

		// cout << "2:" << d_row << " " << d_col << " " << row << " " << col << endl;

		// entry: d_row > 0, d_col < 0:
		// exit: d_row or d_col or both are 0
		// emitting characters only from row
		if (d_row > 0 && d_col < 0) 
		{
			if (d_row > -d_col ) 
			{
				d_row += d_col;
				row   -= d_col;		// emit
				d_col  = 0;
			} 
			else 
			{
				d_col += d_row;
				row   += d_row;		// emit
				d_row  = 0;
			}
		}

		// cout << "3:" << d_row << " " << d_col << " " << row << " " << col << endl;

		// entry: d_row < 0, d_col > 0:
		// exit: d_row or d_col or both are 0
		// emitting characters only from col
		if (d_col > 0 && d_row < 0) 
		{
			if (d_col > -d_row ) 
			{
				d_col += d_row;
				col   -= d_row;		// emit 
				d_row  = 0;
			} 
			else 
			{
				d_row += d_col;
				col   += d_col;		// emit
				d_col  = 0;
			}
		}

		// cout << "4:" << d_row << " " << d_col << " " << row << " " << col << endl;

		if (d_row == 0) 
			if (!(is_row >> d_row)) break;	// read new d_row

		if (d_col == 0) 
			if (!(is_col >> d_col)) break;	// read new d_col

	}	  
	
	return;	
}

//--------------------------------------------------------------------------------------------------------------------------------
void AlignmentFormatEmissions::save(std::ostream & output ) const 
{
	output 
	<< mRowFrom << "\t" << mRowTo << "\t" << mRowAlignment << "\t" 
	<< mColFrom << "\t" << mColTo << "\t" << mColAlignment;
}

void AlignmentFormatEmissions::load(std::istream & input ) 
{
	input >> mRowFrom >> mRowTo >> mRowAlignment >> mColFrom >> mColTo >> mColAlignment;
}

//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
AlignmentFormatExplicit::AlignmentFormatExplicit() 
: AlignmentFormat(), 
mRowAlignment(""),
mColAlignment("")
{
}

AlignmentFormatExplicit::AlignmentFormatExplicit( 
		const HAlignment & src,
		const HAlignandum & row,
		const HAlignandum & col) 
: AlignmentFormat(),
mRowAlignment(""),
mColAlignment("")
{
	fill( src, row, col );
}
AlignmentFormatExplicit::AlignmentFormatExplicit( 
		std::istream & src )
: AlignmentFormat(),
mRowAlignment(""),
mColAlignment("")		
{
	load( src );
}
		
AlignmentFormatExplicit::AlignmentFormatExplicit( const std::string & src) 
: AlignmentFormat(), 
mRowAlignment(""),
mColAlignment("")
{
	std::istringstream i(src.c_str());
	load( i );
}

AlignmentFormatExplicit::AlignmentFormatExplicit(
		const Position row_from,
		const std::string & row,
		const Position col_from,
		const std::string & col) 
	: AlignmentFormat(), 
	mRowAlignment( row ), 
	mColAlignment( col )
{
			mRowFrom = row_from;
			mColFrom = col_from;
			mRowTo = row_from + getDefaultEncoder()->countChars( mRowAlignment );
			mColTo = col_from + getDefaultEncoder()->countChars( mColAlignment );
			
}

AlignmentFormatExplicit::~AlignmentFormatExplicit () 
{
}

AlignmentFormatExplicit::AlignmentFormatExplicit (const AlignmentFormatExplicit & src ) :
	AlignmentFormat( src ), 
	mRowAlignment( src.mRowAlignment ), 
	mColAlignment( src.mColAlignment )
{
}

void AlignmentFormatExplicit::fill( 
		const HAlignment & src,
		const HAlignandum & row,
		const HAlignandum & col )
{
	debug_func_cerr(5);
	
	AlignmentFormat::fill( src );
	
	// sanity checks
	if (src->isEmpty()) return;
	
	if (src->getRowTo() > row->getFullLength() )
		throw AlignlibException("alignment for row is out of bounds.");

	if (src->getColTo() > col->getFullLength() )	
		throw AlignlibException("alignment for col is out of bounds.");	

	HAlignment map_row2new = makeAlignmentVector();
	HAlignment map_col2new = makeAlignmentVector();

	expandAlignment( map_row2new, 
			map_col2new, 
			src, 
			true, true);

	HAlignatum row_alignatum = makeAlignatum( row, map_row2new);
	HAlignatum col_alignatum = makeAlignatum( col, map_col2new);

	mRowAlignment = row_alignatum->getString();
	mColAlignment = col_alignatum->getString();

	return;
}


//--------------------------------------------------------------------------------------------------------------------------------
void AlignmentFormatExplicit::copy( HAlignment & dest ) const 
{
	debug_func_cerr(5);

	AlignmentFormat::copy( dest );

	if (mRowFrom == NO_POS || mColFrom == NO_POS)
		throw AlignlibException( "AlignmentFormat.cpp: alignment ranges not defined." );

	char gap_char = getDefaultEncoder()->getGapChar();

	Position row = mRowFrom;   
	Position col = mColFrom;   

	for (unsigned int i = 0; i < mRowAlignment.size(); i++) 
	{

		if (mRowAlignment[i] != gap_char && mColAlignment[i] != gap_char) 
			dest->addPair( ResiduePair (row, col) );         
		
		if (mRowAlignment[i] != gap_char) 
			row++;
		
		if (mColAlignment[i] != gap_char) 
			col++;
	}
	
	return;	
}

//--------------------------------------------------------------------------------------------------------------------------------
void AlignmentFormatExplicit::save(std::ostream & output ) const 
{
	output 
	<< mRowFrom << "\t" << mRowTo << "\t" << mRowAlignment << "\n" 
							<< mColFrom << "\t" << mColTo << "\t" << mColAlignment;
}

void AlignmentFormatExplicit::load(std::istream & input ) 
{
	input >> mRowFrom >> mRowTo >> mRowAlignment >> mColFrom >> mColTo >> mColAlignment;
}

//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
AlignmentFormatDiagonals::AlignmentFormatDiagonals() 
: AlignmentFormat(), mAlignment("")
{
}
	
AlignmentFormatDiagonals::AlignmentFormatDiagonals( 
		const HAlignment & src)
: AlignmentFormat(), mAlignment("")
{
	fill( src);
}

AlignmentFormatDiagonals::AlignmentFormatDiagonals( 
		std::istream & src) 
: AlignmentFormat(), mAlignment("")
{
	load(src);
}

AlignmentFormatDiagonals::AlignmentFormatDiagonals( const std::string & src)  
	: AlignmentFormat(), mAlignment("")
	{
	std::istringstream i(src.c_str());
	load( i );
	}

AlignmentFormatDiagonals::~AlignmentFormatDiagonals () 
{
}

AlignmentFormatDiagonals::AlignmentFormatDiagonals (const AlignmentFormatDiagonals & src ) 
:	AlignmentFormat( src ), 
	mAlignment( src.mAlignment ) 
{
}

void AlignmentFormatDiagonals::fill( 
		const HAlignment & src )
{
	fill(src, false);
}
	
void AlignmentFormatDiagonals::fill( 
		const HAlignment & src,
		const bool reverse,
		const Position xrow_from,
		const Position xrow_to,
		const Position xcol_from,
		const Position xcol_to,
		const Diagonal xdiagonal_from,
		const Diagonal xdiagonal_to )
{
	debug_func_cerr(5);
	
	AlignmentFormat::fill( src );
	
	// sanity checks
	if (src->isEmpty()) return;

	HAlignment work( makeAlignmentMatrixDiagonal() );
	copyAlignment( work, src );
	
	Position row_from = xrow_from;
	Position row_to = xrow_to;
	Position col_from = xcol_from;
	Position col_to = xcol_to;
	Position diagonal_from = xdiagonal_from;
	Position diagonal_to = xdiagonal_to;

	// check parameters for filters and set them to sensible values
	if (col_from < work->getColFrom() || col_from == NO_POS)
		col_from = work->getColFrom();
	if (col_to >= work->getColTo() || col_to == NO_POS)
		col_to = work->getColTo();
	if (row_from < work->getRowFrom() || row_from == NO_POS)
		row_from = work->getRowFrom();
	if (row_to >= work->getRowTo() || row_to == NO_POS)
		row_to = work->getRowTo();

	if (diagonal_from > diagonal_to) 
	{
	  diagonal_from = std::numeric_limits<Position>::min();
	  diagonal_to   = std::numeric_limits<Position>::max();
	}

	// declare variables you need for iteration of the pairs
	AlignmentIterator it(work->begin());
	AlignmentIterator it_end(work->end());

	Diagonal last_diagonal = it->getDiagonal();
	Diagonal this_diagonal = 0;

	Position this_row	 = it->mRow;
	Position this_col	 = it->mCol;
	Position last_row	 = this_row -1;
	Position emissions = 0;
	Position initial_gaps = 0;

	bool first = true;

	std::ostringstream output;

	// now iterate over all pairs in the alignment
	for (;it!= it_end; ++it) 
	{

		this_diagonal = it->getDiagonal();
		this_row      = it->mRow;
		this_col      = it->mCol;

		debug_cerr( 5, "Pair:" << *it << std::endl            
				<< "last_diagonal=" << last_diagonal 
				<< " this_diagonal=" << this_diagonal
				<< " emissions=" << emissions 
				<< " this_row=" << this_row 
				<< " last_row=" << last_row );

		// apply filters
		if (this_col < col_from || this_col >= col_to) 
			continue;
		if (this_row < row_from || this_row >= row_to) 
			continue;
		if (this_diagonal < diagonal_from || this_diagonal > diagonal_to)
			continue;

		if (last_diagonal != this_diagonal || last_row >= this_row || first) 
		{

			if (!first) 
				output  << "+" << emissions << ";";

				// write last emission and switch to new diagonal
			if (this_diagonal < 0) 
				initial_gaps = this_col; 
			else
				initial_gaps = this_row;

			if (reverse)
				output << -this_diagonal << ":-" << initial_gaps;
			else
				output << this_diagonal << ":-" << initial_gaps;

			first = false;

			last_diagonal = this_diagonal;
			last_row = this_row;
			emissions = 1;
			continue;
		}

		// insert a gap
		if (last_row < this_row - 1) 
		{
			output << "+" << emissions << "-" << (this_row - last_row - 1);
			emissions = 0;
		}

		last_row = this_row;
		++emissions;

	}

	output << "+" << emissions;

	mAlignment = output.str();

	return;
}

//------------------------------------------------------------------------------------------------------
void AlignmentFormatDiagonals::copy( 
		HAlignment & dest ) const
		{
	copy( dest, false );
		}

void AlignmentFormatDiagonals::copy( 
		HAlignment & dest,
		const bool reverse) const 
		{
	debug_func_cerr(5);

	AlignmentFormat::copy( dest );

	if (mRowFrom == NO_POS || mColFrom == NO_POS)
		throw AlignlibException( "AlignmentFormat.cpp: alignment ranges not defined." );

	std::istringstream is_ali( mAlignment.c_str() );   

	// set these/use these parameters to shift alignment
	Position row_from = mRowFrom;
	Position col_from = mColFrom;

	// row and col are the index of the next dot to be written.
	Position row = row_from;   
	Position col = col_from;   

	// read diagonal wise
	while (!is_ali.eof()) 
	{

		// read the diagonal
		Diagonal diagonal;
		is_ali >> diagonal;
		is_ali.ignore();		// skip colon

		debug_cerr(5, "processing diagonal " << diagonal );

		// for a new diagonal, position yourself at the first residue 
		// on the diagonal
		if (diagonal < 0) 
		{
			row = -diagonal;
			col = 0;
		} else {
			row = 0;
			col = diagonal;
		}

		while (is_ali.peek() != ';' && !is_ali.eof()) 
		{
			Position d = 0;   
			is_ali >> d;
			// write a gap
			if (d < 0) 
			{
				row -= d;
				col -= d;
			} 
			else 
			{
				// emit dots
				while (d > 0) 
				{
					if (reverse)
						dest->addPair( col++, row++, 0 );       
					else 
						dest->addPair( row++, col++, 0 );       
					d--;
				}
			}	
		} 
		is_ali.ignore();		// skip semicolon
	}   

	return;	
		}

//--------------------------------------------------------------------------------------------------------------------------------
void AlignmentFormatDiagonals::save(std::ostream & output ) const 
{
	output 
	<< mRowFrom << "\t" << mRowTo << "\t" 
	<< mColFrom << "\t" << mColTo << "\t" 
	<< mAlignment;
}

void AlignmentFormatDiagonals::load(std::istream & input ) 
{
	input >> mRowFrom >> mRowTo >> mColFrom >> mColTo >> mAlignment;
}

} // namespace alignlib
