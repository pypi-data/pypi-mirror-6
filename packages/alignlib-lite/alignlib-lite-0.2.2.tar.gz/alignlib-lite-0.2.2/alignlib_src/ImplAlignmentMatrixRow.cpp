/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignmentMatrixRow.cpp,v 1.3 2004/06/02 12:11:37 aheger Exp $

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
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignmentIterator.h"
#include "AlignlibException.h"
#include "ImplAlignmentMatrixRow.h"

using namespace std;

namespace alignlib 
{

  /** Note: There are two arrays that have to be taken care of: mPairs and mIndex. If you
      need to copy one, you have to copy the other one as well. The same applies to deletion.

      clear() does not free the memory for mPairs and mIndices. This class works by preallocating
      memory, otherwise you would need to realloc memory every time one or more pairs are added.
      Alternatively, you could implement this class as a stack, that dynamically allocates memory.
      
      If you need to safe memory, allocate only as much as you need by giving the correct number
      of pairs to the constructor, or alternatively, create a big class and then create a copy 
      of the object with the copy constructor.

      When modifying the dots, the allocated size of the memory stays always the same.

  */

#define NODOT -1 

//------------------------------factory functions -----------------------------
HAlignment makeAlignmentMatrixRow() 
{
  debug_func_cerr(5);

  return HAlignment( new ImplAlignmentMatrixRow() );
}

//------------------------------------< constructors and destructors >-----
ImplAlignmentMatrixRow::ImplAlignmentMatrixRow() 
: ImplAlignmentMatrix() 
{
  debug_func_cerr(5);

}

ImplAlignmentMatrixRow::ImplAlignmentMatrixRow( const ImplAlignmentMatrixRow& src) : 
  ImplAlignmentMatrix( src ) 
{
  debug_func_cerr(5);

}

ImplAlignmentMatrixRow::~ImplAlignmentMatrixRow( ) 
{
  debug_func_cerr(5);

}

//------------------------------------------------------------------------------------------------------------
HAlignment ImplAlignmentMatrixRow::getNew() const 
{
  return HAlignment( new ImplAlignmentMatrixRow() );
}
    
HAlignment ImplAlignmentMatrixRow::getClone() const 
{
  return HAlignment( new ImplAlignmentMatrixRow( *this ) );
}


//--------------> mapping functions <----------------------------------------------------------------------------
Position ImplAlignmentMatrixRow::mapRowToCol( Position pos, SearchType search ) const 
{
	if (mChangedLength) calculateLength();
    Position index;
    if (pos >= mRowFrom && pos < mRowTo)
    	if ( (index = mIndex[pos]) != NO_POS )
    		return mPairs[index].mCol;

    return NO_POS;
}

//-------------------------------------------------------------------------------------------------------------------- 
/* sort Residuepairs(dots) in mPairs by row and then by column. Sorting is done in place using quick-sort. It might be
   faster to only sort the indices (as I did in the old version) and then copy it into a new memory location
*/

void ImplAlignmentMatrixRow::sortDots() const 
{
  debug_func_cerr( 5 );
  /* sort indices on row */
  sortDotsByRow( 0, mPairs.size() );
  
}


//--------------------------------------------------------------------------------------------------------------
// build the index
void ImplAlignmentMatrixRow::buildIndex() const {
  // 2 .calculate index
  // delete old instance of mIndex, if it exists
  if (mIndex != NULL) {                            
    delete [] mIndex;
    mIndex = NULL;
  }

  //  allocate memory 
  allocateIndex( mRowTo );
  for (Position i = 0; i < mRowTo; i++) { mIndex[i] = NODOT; }   
  
  Position last_row = getRowFrom();
  Dot first_dot = 0;

  for (unsigned int i = 0; i < mPairs.size(); i++) {
    if(last_row != mPairs[i].mRow) {
      mIndex[last_row] = first_dot;
      first_dot = i;
      last_row = mPairs[i].mRow;
    }
  }

  mIndex[last_row] = first_dot;

}
  

} // namespace alignlib
