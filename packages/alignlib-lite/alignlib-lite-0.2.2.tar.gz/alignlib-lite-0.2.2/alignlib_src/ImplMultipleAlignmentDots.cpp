/*
  alignlib - a library for aligning protein sequences

  $Id: ImplMultipleAlignmentDots.cpp,v 1.3 2004/03/19 18:23:41 aheger Exp $

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
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"

#include "ImplMultipleAlignmentDots.h"
#include "HelpersMultipleAlignment.h"
#include "AlignlibException.h"
#include "Alignatum.h"
#include "HelpersAlignatum.h"
#include "Alignandum.h"
#include "Alignment.h"
#include "HelpersAlignment.h"
#include "AlignmentIterator.h"
#include "HelpersEncoder.h"
#include "AlignmentFormat.h"
using namespace std;

namespace alignlib 
{

ImplMultipleAlignmentDots::MaliRow::MaliRow( MaliRow & src ) :
	mAlignatumInput(src.mAlignatumInput), 
	mMapMali2Alignatum(src.mMapMali2Alignatum) 
{
}

ImplMultipleAlignmentDots::MaliRow::MaliRow( 
		const HAlignatum & input, 
		const HAlignment & map_alignatum2mali ) : 
	mAlignatumInput(input), 
	mMapMali2Alignatum(map_alignatum2mali)
{
	debug_func_cerr(5);	
}

ImplMultipleAlignmentDots::MaliRow::~MaliRow()
{
	debug_func_cerr(5);	
}

/* factory functions */
HMultipleAlignment makeMultipleAlignmentDots( 
		bool compress_unaligned_columns,
		int max_insertion_length) 
{
	debug_func_cerr( 5 );
	debug_cerr(5, "creating: compressed=" << compress_unaligned_columns << " max_insert=" << max_insertion_length );
	return HMultipleAlignment( new ImplMultipleAlignmentDots( compress_unaligned_columns, max_insertion_length ) );
}


//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplMultipleAlignmentDots::ImplMultipleAlignmentDots ( 
		const bool compress_unaligned_columns,
		const int max_insertion_length) : ImplMultipleAlignment(),
			mCompressUnalignedColumns( compress_unaligned_columns),
			mMaxInsertionLength( max_insertion_length),
			mIsDirty( false )
{
	debug_cerr(5, "creating: compressed=" << mCompressUnalignedColumns << " max_insert=" << mMaxInsertionLength );
	debug_func_cerr( 5 );
}

//--------------------------------------------------------------------------------------------------------------
ImplMultipleAlignmentDots::~ImplMultipleAlignmentDots () 
{
	debug_func_cerr( 5 );
}

//--------------------------------------------------------------------------------------------------------------
ImplMultipleAlignmentDots::ImplMultipleAlignmentDots (const ImplMultipleAlignmentDots & src ) : 
	ImplMultipleAlignment( src ),
	mCompressUnalignedColumns( src.mCompressUnalignedColumns ),
	mMaxInsertionLength( src.mMaxInsertionLength ),
	mIsDirty( src.mIsDirty )
	{
	debug_func_cerr( 5 );

	// add clones of the new entries
	for (unsigned int row = 0; row < src.mRowData.size(); row++) 
		mRowData.push_back( HMaliRow( new MaliRow( 
				src.mRowData[row]->mAlignatumInput->getClone(), 
				src.mRowData[row]->mMapMali2Alignatum->getClone() ) )); 
	
}

//--------------------------------------------------------------------------------------------------------------
void ImplMultipleAlignmentDots::freeMemory() 
{
	ImplMultipleAlignment::freeMemory();
	debug_func_cerr(5);
	mRowData.clear();
	mIsDirty = false;
}


//--------------------------------------------------------------------------------------------
void ImplMultipleAlignmentDots::eraseRow( int row ) 
{
	ImplMultipleAlignment::eraseRow( row );
	if (row < 0 || row >= getNumSequences() )
		return;

	mRowData.erase( mRowData.begin() + row );
}	


//------------------------------------------------------------------------------------
/* add single entry to *this multiple alignment given an alignment.
 */
void ImplMultipleAlignmentDots::add( const HAlignatum & src,
		const HAlignment & alignment,
		bool mali_is_in_row,
		bool insert_gaps_mali,
		bool insert_gaps_alignatum,
		bool use_end_mali,
		bool use_end_alignatum) 
{
	debug_func_cerr(5);

	mRowData.push_back( HMaliRow( new MaliRow(src->getClone(), alignment->getClone())) );
	mRows.push_back( makeAlignatum() );
	mIsDirty = true;
}
 
//------------------------------------------------------------------------------------
/* add single entry to *this multiple alignment 
 */
void ImplMultipleAlignmentDots::add( const HAlignatum & src )
{
	debug_func_cerr(5);
	
	HAlignment ali(makeAlignmentVector());
	addDiagonal2Alignment( ali, 0, src->getFullLength(), 0);
	mRowData.push_back( HMaliRow( new MaliRow(src, ali)) );	
	mRows.push_back( makeAlignatum() );
	mIsDirty = true;
}

//------------------------------------------------------------------------------------
/** Add a full multiple alignment to the another alignment.
 */
void ImplMultipleAlignmentDots::add( const HMultipleAlignment & src )
{
	debug_func_cerr(5);

	// TODO: implement this function.
	throw AlignlibException( "not implemented yet." );
}

//------------------------------------------------------------------------------------
/** Add a full multiple alignment to the another alignment.
 */
void ImplMultipleAlignmentDots::add( 
		const HMultipleAlignment & src,
		const HAlignment & alignment,
		bool mali_is_in_row,
		bool insert_gaps_mali,
		bool insert_gaps_alignatum,
		bool use_end_mali,
		bool use_end_alignatum) 
{
	debug_func_cerr(5);

	// do not add empty mali
	if (src->isEmpty()) return;

	HImplMultipleAlignmentDots src_mali = boost::dynamic_pointer_cast<ImplMultipleAlignmentDots, MultipleAlignment>(src);
	
	for (int x = 0; x < src_mali->getNumSequences(); ++x) 
	{
		HAlignment map_mali2src = makeAlignmentVector();

		if (mali_is_in_row)
			combineAlignment( map_mali2src,
					alignment,
					src_mali->mRowData[x]->mMapMali2Alignatum,
					CR);
		else
			combineAlignment( map_mali2src,
					alignment,
					src_mali->mRowData[x]->mMapMali2Alignatum,
					RR);

		add( src_mali->mRowData[x]->mAlignatumInput,
			 map_mali2src,
			 true,
			 insert_gaps_mali, insert_gaps_alignatum,
			 use_end_mali, use_end_alignatum);
	}
	mIsDirty = true;  
}

//---------------------------------------------------------------------------------------
HMultipleAlignment ImplMultipleAlignmentDots::getClone() const 
{
	return HMultipleAlignment( new ImplMultipleAlignmentDots( *this ) );
}    

//---------------------------------------------------------------------------------------
HMultipleAlignment ImplMultipleAlignmentDots::getNew() const 
{
	return HMultipleAlignment( new ImplMultipleAlignmentDots( mCompressUnalignedColumns, mMaxInsertionLength ) );
}    

//---------------------------------------------------------< Input/Output routines >--------

//---------------------------------------------------------------------------------------
void ImplMultipleAlignmentDots::update() const 
{
	debug_func_cerr(5);
	
	// do nothing, if no changes
	if (!mIsDirty) return;

	if (isEmpty())
	{
		mLength = 0;
		return;
	}	
	
	Position mali_length = 0;

	// find number of aligned columns in mali
	for (unsigned int x = 0; x < mRows.size(); ++x) 
		mali_length = std::max( mali_length, mRowData[x]->mMapMali2Alignatum->getRowTo());

	// find total/maximum insertions before a given mali column
	// the first column is ignored
	// row: position in mali
	// col: position in sequence
	std::vector<int> gaps(mali_length + 1, 0);

	for (unsigned int x = 0; x < mRows.size(); ++x) 
	{
		HAlignment ali = mRowData[x]->mMapMali2Alignatum;

		Position last_col = ali->getColFrom();
		
		for (Position row = ali->getRowFrom() + 1; row < ali->getRowTo(); ++row) 
		{
			Position col = ali->mapRowToCol(row);
			if (col != NO_POS) 
			{
				if (mCompressUnalignedColumns) 
				{
					if (mMaxInsertionLength >= 0)
						gaps[row] = std::min( std::max( gaps[row], col - last_col - 1 ), mMaxInsertionLength);
					else
						gaps[row] = std::max( gaps[row], col - last_col - 1 );
				} else 
				{
					gaps[row] += col - last_col - 1;
				}
				last_col = col;
			}
		}
	}

	debug_cerr( 5, "length=" << mali_length << " compress=" << mCompressUnalignedColumns );

#ifdef DEBUG	
	for (unsigned int x = 0; x < gaps.size(); ++x) 
		debug_cerr( 5, "col=" << x << " gaps=" << gaps[x]);
	for (unsigned int x = 0; x < mRows.size(); ++x) 
		debug_cerr( 5, "row=" << x << " ali=" << AlignmentFormatEmissions( mRowData[x]->mMapMali2Alignatum ) 
				<< " seq=" << (*mRowData[x]->mAlignatumInput) );

#endif
	
	// build map of aligned columns to output columns
	HAlignment map_mali2representation = makeAlignmentVector(); 
	{
		Position y = 0;
		for (Position x = 0; x < mali_length; ++x) 
		{
			y += gaps[x];
			map_mali2representation->addPair( x, y++, 0 );
		}
	}

	debug_cerr( 5, "map_mali2representation\n" << *map_mali2representation );

	// record aligned columns
	{
		mIsAligned.clear();
		mIsAligned.resize( map_mali2representation->getColTo(), false);
		AlignmentIterator it(map_mali2representation->begin()), end(map_mali2representation->end());
		for( ; it != end; ++it)
			mIsAligned[it->mCol] = true;
	}
	
	// map each row in the mali to the representation
	mLength = map_mali2representation->getColTo();

	std::vector<int>used_gaps(mali_length + 1, 0);

	for (unsigned int x = 0; x < mRows.size(); ++x) 
	{
		mRows[x] = mRowData[x]->mAlignatumInput->getClone();

		HAlignment map_alignatum2representation = makeAlignmentVector(); 

		combineAlignment( map_alignatum2representation, mRowData[x]->mMapMali2Alignatum, map_mali2representation, RR);

		debug_cerr( 5, "map_alignatum2representation=\n" << *map_alignatum2representation );
		// map alignatum-object
		if (mCompressUnalignedColumns) 
		{
			mRows[x]->mapOnAlignment( map_alignatum2representation, 
					mLength,
					true );
		} 
		else 
		{
			HAlignment ali = mRowData[x]->mMapMali2Alignatum;
			// add pairs for gaps 
			Position last_col = ali->getColFrom();
			for (Position row = ali->getRowFrom(); row < ali->getRowTo(); ++row) 
			{
				Position col = ali->mapRowToCol(row);

				if (col != NO_POS) 
				{
					unsigned int u = map_mali2representation->mapRowToCol(row) - gaps[row] + used_gaps[row];
					unsigned int d = col - last_col - 1;
					while (col - last_col - 1 > 0) 
					{
						map_alignatum2representation->addPair( ++last_col, u++, 0);
					}
					used_gaps[row] += d;
					last_col = col;
				}
			}				   
			mRows[x]->mapOnAlignment( 
					map_alignatum2representation, 
					mLength,
					false );	

		}

		debug_cerr( 5, "map_alignatum2representation\n" << *map_alignatum2representation );
	}
	
	mIsDirty = false;
	
}

} // namespace alignlib





