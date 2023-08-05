/*
  alignlib - a library for aligning protein sequences

  $Id: ImplMultipleAlignment.cpp,v 1.6 2004/03/19 18:23:41 aheger Exp $

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

#include "HelpersAlignandum.h"
#include "ImplMultipleAlignment.h"
#include "HelpersMultipleAlignment.h"
#include "HelpersEncoder.h"
#include "AlignlibException.h"
#include "Alignatum.h"
#include "Alignandum.h"
#include "Alignment.h"
#include "HelpersAlignment.h"
#include "AlignmentIterator.h"

using namespace std;

namespace alignlib 
{

/* factory functions */

/** create an empty multiple alignment */
HMultipleAlignment makeMultipleAlignment() 
{
	return HMultipleAlignment( new ImplMultipleAlignment() );
}


//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplMultipleAlignment::ImplMultipleAlignment () : 
	mLength(0)
{
}

//--------------------------------------------------------------------------------------------------------------
ImplMultipleAlignment::~ImplMultipleAlignment () 
{
	freeMemory();
}

//--------------------------------------------------------------------------------------------------------------
ImplMultipleAlignment::ImplMultipleAlignment (const ImplMultipleAlignment & src ) : 
	mLength (src.mLength) {
	

	// clear old entries
	freeMemory();

	// add clones of the new entries
	for (unsigned int row = 0; row < src.mRows.size(); row++) 
		add( src.mRows[row]->getClone() );

	mIsAligned.clear();
	std::copy(src.mIsAligned.begin(), src.mIsAligned.end(), std::back_inserter( mIsAligned ));
}

//--------------------------------------------------------------------------------------------------------------
void ImplMultipleAlignment::freeMemory() 
{
	debug_func_cerr(5);
	mRows.clear();
	mIsAligned.clear();
}

//--------------------------------------------------------------------------------------------------------------
Position ImplMultipleAlignment::getLength() const 
{
	update();
	return mLength;
}

//--------------------------------------------------------------------------------------------------------------
void ImplMultipleAlignment::update() const
{
}

//--------------------------------------------------------------------------------------------------------------
void ImplMultipleAlignment::setLength( Position length) 
{
	if (mLength != 0)
		throw AlignlibException("In ImplMultipleAlignment.cpp: length given for non-empty alignment");
	mLength = length;
}

//--------------------------------------------------------------------------------------------------------------
int ImplMultipleAlignment::getNumSequences() const 
{
	return mRows.size();
}

//-----------------------------------------------------------------------------------------------------------
const std::string & ImplMultipleAlignment::operator[]( int row ) const 
{
	if (isEmpty())
		throw AlignlibException("In ImplMultipleAlignment.cpp: alignment is empty");
	
	if (row < 0 || row >= mRows.size() )
		throw AlignlibException("In ImplMultipleAlignment.cpp: out-of-range access");
	
	update();
	
	return mRows[row]->getString();
}

//-----------------------------------------------------------------------------------------------------------
HAlignatum ImplMultipleAlignment::getRow( int row ) const 
{
	if (isEmpty())
		throw AlignlibException("In ImplMultipleAlignment.cpp: alignment is empty");
	if (row < 0 || row >= mRows.size() )
		throw AlignlibException("In ImplMultipleAlignment.cpp: out-of-range access");
	
	update();
	
	return mRows[row];
}

//-----------------------------------------------------------------------------------------------------------
void ImplMultipleAlignment::clear() 
{
	freeMemory();
	mLength = 0;
}

//-----------------------------------------------------------------------------------------------------------
void ImplMultipleAlignment::eraseRow( int row ) 
{
	if (isEmpty())
		throw AlignlibException("In ImplMultipleAlignment.cpp: alignment is empty");
	if (row < 0 || row >= mRows.size() )
		throw AlignlibException("In ImplMultipleAlignment.cpp: out-of-range access");

	mRows.erase( mRows.begin() + row );
	if (mRows.size() == 0)
		mLength = 0;
}

//-----------------------------------------------------------------------------------------------------------
bool ImplMultipleAlignment::isAligned( const Position & col )
{
	update();
	if (col < 0 || col >= getLength())
		throw AlignlibException("In ImplMultipleAlignment.cpp: out-of-range access");
	return mIsAligned[ col ];
}

//------------------------------------------------------------------------------------
/* add single entry to *this multiple alignment given an alignment.
   in the alignment, the other alignment is in row, *this alignment is in col.
   In contrast to the next method, here src has not to be realigned
 */
void ImplMultipleAlignment::add( const HAlignatum & src )
{
	debug_func_cerr(5);

	// if the alignment is empty and no length has been specified, simply add the first element and you are done.
	// the first element determines the length of the multiple alignment
	if ( mRows.empty() && mLength == 0) 
	{
		mLength = src->getAlignedLength();
		mRows.push_back( src->getClone() );
		mIsAligned.clear();
		mIsAligned.resize( mLength, true );
	}
	else
	{
		// add a prealigned string to the multiple alignment. Precondition is
		// that the multiple alignment and the aligned string have to have the
		// same length.
		if (mLength != src->getAlignedLength())
			throw AlignlibException("In ImplMultipleAlignment.cpp: wrong length of aligned object for adding to MA");
	
		mRows.push_back( src );
	}
}

//------------------------------------------------------------------------------------
/* add single entry to *this multiple alignment given an alignment.
   in the alignment, the other alignment is in row, *this alignment is in col.
   In contrast to the next method, here src has not to be realigned
 */
void ImplMultipleAlignment::add( 
		const HAlignatum & src,
		const HAlignment & alignment,
		bool mali_is_in_row,
		bool insert_gaps_mali,
		bool insert_gaps_alignatum,
		bool use_end_mali,
		bool use_end_alignatum) 
{
	debug_func_cerr(5);

	// if the alignment is empty and no length has been specified, simply add the first element and you are done.
	// the first element determines the length of the multiple alignment
	if ( mRows.empty() && mLength == 0) 
	{
		mLength = src->getAlignedLength();
		mRows.push_back( src );
		return;
	}
	
	// the string is not prealigned to the multiple alignment. We have to
	// do this by ourselves.

	HAlignment map_this2new = makeAlignmentVector();
	HAlignment map_alignatum2new = makeAlignmentVector();

	if (mali_is_in_row)
		expandAlignment( map_this2new, 
				map_alignatum2new, 
				alignment, 
				insert_gaps_mali,
				insert_gaps_alignatum,
				use_end_mali,
				use_end_alignatum,
				getLength(),
				src->getAlignedLength());
	else
		expandAlignment( map_alignatum2new, 
				map_this2new, 
				alignment, 
				insert_gaps_alignatum,
				insert_gaps_mali,
				use_end_alignatum,
				use_end_mali,
				src->getAlignedLength(),
				getLength());

	mLength = std::max( map_this2new->getColTo(), map_alignatum2new->getColTo());

	// proceed row-wise and remap each alignatum-object
	if (insert_gaps_mali)
		for (unsigned int row = 0; row < mRows.size(); row++) 
			mRows[row]->mapOnAlignment( map_this2new, mLength );

	// map alignatum-object
	src->mapOnAlignment( map_alignatum2new, mLength );	

	// insert into alignment
	mRows.push_back( src );	

	mLength = src->getAlignedLength();
	
	updateAligned( map_this2new, map_alignatum2new );

}

void ImplMultipleAlignment::updateAligned( 
		const HAlignment & map_this2new,
		const HAlignment & map_other2new)
{

	mIsAligned.clear();
	mIsAligned.resize( mLength, true);
	return;
	
	// update aligned columns 
	// aligned = previously aligned or now aligned
	std::vector<bool> cp1( mLength, false);
	{
		AlignmentIterator it( map_this2new->begin() ), end( map_this2new->end());	
		for( ; it != end; ++it) cp1[it->mCol] = mIsAligned[it->mRow];
	}
	std::vector<bool> cp2( mLength, false);
	{
		AlignmentIterator it( map_other2new->begin() ), end( map_other2new->end());	
		for( ; it != end; ++it) cp2[it->mCol] = true;
	}
	mIsAligned.clear();
	mIsAligned.resize( mLength, false);

	for (Position x = 0; x < mLength; ++x)
		mIsAligned[x] = cp1[x] && cp2[x];
		
}

//------------------------------------------------------------------------------------
/** Add a full multiple alignment to the another alignment.
 */
void ImplMultipleAlignment::add( const HMultipleAlignment & src)
{
	debug_func_cerr(5);

	// do not add empty mali
	if (src->getNumSequences() == 0) 
		return;

	//--------------------------------------------------------------------
	// if src and this are the same, create a temporary copy of the multiple alignment. Otherwise, 
	// you will have trouble when inserting gaps into the multiple alignment
	// TODO: check if this is correct
	HMultipleAlignment copy(src);

	if (this == &*src) 
		copy = HMultipleAlignment( this->getClone() );

	// if the current alignment is empty, simply set current length to length of first residue
	if ( mRows.empty() )
		mLength = copy->getLength();

	// add a aligantum objects without mapping. Precondition is
	// that the multiple alignment and the aligned string have to have the
	// same length.
	if (mLength != copy->getLength())
		throw AlignlibException("In ImplMultipleAlignment.cpp: wrong length of aligned object for adding to MA");
	
	for (int row = 0; row < copy->getNumSequences(); row++) 
		mRows.push_back( copy->getRow(row)->getClone() );
	
	for (Position x = 0; x < mLength; ++x)
		mIsAligned[x] = true;

}

//------------------------------------------------------------------------------------
/** Add a full multiple alignment to the another alignment.
 */
void ImplMultipleAlignment::add( 
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
	if (src->getNumSequences() == 0) 
		return;

	//--------------------------------------------------------------------
	// if src and this are the same, create a temporary copy of the multiple alignment. Otherwise, 
	// you will have trouble when inserting gaps into the multiple alignment
	// TODO: check if this is correct
	HMultipleAlignment copy(src);

	if (this == &*src) 
		copy = HMultipleAlignment( this->getClone() );
	
	// if the current alignment is empty, simply set current length to length of first residue
	if ( mRows.empty() )
		mLength = copy->getLength();

	if ( mRows.empty() )
		throw AlignlibException("In ImplMultipleAlignment.cpp: cannot add mali to empty mali with mapping");

	// the string is not prealigned to the multiple alignment. We have to
	// do this by ourselves.

	HAlignment map_this2new = makeAlignmentVector();
	HAlignment map_alignatum2new = makeAlignmentVector();
	
	if (mali_is_in_row)
		expandAlignment( map_this2new, 
				map_alignatum2new, 
					alignment, 
					insert_gaps_mali,
					insert_gaps_alignatum,
					use_end_mali,
					use_end_alignatum,
					getLength(),
					copy->getLength());
		else
			expandAlignment( map_alignatum2new, 
					map_this2new, 
					alignment, 
					insert_gaps_alignatum,
					insert_gaps_mali,
					use_end_alignatum,
					use_end_mali,
					copy->getLength(),
					getLength());

	debug_cerr( 5, "map_alignatum2new=" << *map_alignatum2new );
	debug_cerr( 5, "map_this2new" << *map_this2new );

	mLength = std::max( map_this2new->getColTo(), map_alignatum2new->getColTo());

	// proceed row-wise and remap each alignatum-object in the current alignment
	for (unsigned int row = 0; row < mRows.size(); row++) 
		mRows[row]->mapOnAlignment( map_this2new, mLength);
	
	// now add alignatum objects from the other alignment
	for (int row = 0; row < copy->getNumSequences(); row++) 
	{
		HAlignatum new_alignatum(copy->getRow(row)->getClone());
		new_alignatum->mapOnAlignment( map_alignatum2new, mLength );
		mRows.push_back( new_alignatum );
	}
	
	updateAligned( map_this2new, map_alignatum2new );
}

//---------------------------------------------------------------------------------------
HMultipleAlignment ImplMultipleAlignment::getClone() const 
{
	return HMultipleAlignment( new ImplMultipleAlignment( *this ) );
}    

//---------------------------------------------------------------------------------------
HMultipleAlignment ImplMultipleAlignment::getNew() const 
{
	return HMultipleAlignment( new ImplMultipleAlignment( ) );
}    

//---------------------------------------------------------------------------------------
bool ImplMultipleAlignment::isEmpty() const 
{
	return mRows.empty();
}

//---------------------------------------------------------< Input/Output routines >--------

//------------------------------------------------------------------------------------
void ImplMultipleAlignment::write( std::ostream & output ) const 
{
	debug_func_cerr(5);

	for (unsigned int row = 0; row < mRows.size(); ++row) 
	{
		mRows[row]->write( output );    
		output << std::endl;
	}
	Position l = getLength();
	for (unsigned int col = 0; col < l; ++col) 
		output << mIsAligned[col];
}

} // namespace alignlib


