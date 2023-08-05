/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignmentMatrixUnsorted.cpp,v 1.3 2004/03/19 18:23:40 aheger Exp $

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
#include <limits>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "ImplAlignmentMatrixUnsorted.h"
#include "AlignlibException.h"


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
HAlignment makeAlignmentMatrixUnsorted() 
{
  return HAlignment( new ImplAlignmentMatrixUnsorted() );
}

//------------------------------------< constructors and destructors >-----
ImplAlignmentMatrixUnsorted::ImplAlignmentMatrixUnsorted() 
: ImplAlignmentMatrix() 
{
  debug_func_cerr(5);

}

ImplAlignmentMatrixUnsorted::ImplAlignmentMatrixUnsorted( const ImplAlignmentMatrixUnsorted& src) : 
  ImplAlignmentMatrix( src ) 
{
  debug_func_cerr(5);

}

ImplAlignmentMatrixUnsorted::~ImplAlignmentMatrixUnsorted( ) 
{
  debug_func_cerr(5);

}

//------------------------------------------------------------------------------------------------------------
HAlignment ImplAlignmentMatrixUnsorted::getNew() const 
{
    return HAlignment ( new ImplAlignmentMatrixUnsorted() );
}
    
HAlignment ImplAlignmentMatrixUnsorted::getClone() const 
{
    return HAlignment ( new ImplAlignmentMatrixUnsorted( *this ) );
}

//-------------------------------------------------------------------------------------------------------------------- 
/* sort Residuepairs(dots) in mPairs by row and then by column. Sorting is done in place using quick-sort. It might be
   faster to only sort the indices (as I did in the old version) and then copy it into a new memory location
*/

void ImplAlignmentMatrixUnsorted::sortDots() const 
{
}    

void ImplAlignmentMatrixUnsorted::eliminateDuplicates() const 
{

  mRowFrom = std::numeric_limits<Position>::max();
  mColFrom = std::numeric_limits<Position>::max();
  mRowTo = std::numeric_limits<Position>::min();
  mColTo = std::numeric_limits<Position>::min();
  
  PairConstIterator it(mPairs.begin()), it_end(mPairs.end());
  
  for (; it != it_end; ++it) {
    
    Position row = (*it).mRow;
    Position col = (*it).mCol;
    
    // get maximum boundaries
    if (row < mRowFrom) mRowFrom = row;
    if (col < mColFrom) mColFrom = col;
    if (row > mRowTo)   mRowTo = row;
    if (col > mColTo)   mColTo = col;
  }
  
  ++mRowTo;
  ++mColTo;
}    

//--------------------------------------------------------------------------------------------------------------
// build the index
void ImplAlignmentMatrixUnsorted::buildIndex() const 
{
}
  

} // namespace alignlib














