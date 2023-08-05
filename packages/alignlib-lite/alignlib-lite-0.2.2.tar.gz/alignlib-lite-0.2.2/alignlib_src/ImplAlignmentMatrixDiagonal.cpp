/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignmentMatrixDiagonal.cpp,v 1.3 2004/06/02 12:11:37 aheger Exp $

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
#include "ImplAlignmentMatrixDiagonal.h"
#include "AlignmentIterator.h"
#include "AlignlibException.h"

using namespace std;

namespace alignlib 
{
  
  /** 
      The whole thing could be quicker, if the diagonal was precalculated as well.
  */

#define NODOT -1

//------------------------------factory functions -----------------------------
HAlignment makeAlignmentMatrixDiagonal() 
{
  return HAlignment( new ImplAlignmentMatrixDiagonal() );
}

//------------------------------------< constructors and destructors >-----
ImplAlignmentMatrixDiagonal::ImplAlignmentMatrixDiagonal() 
: ImplAlignmentMatrix(), mNumDiagonals(0) 
{
  debug_func_cerr(5);

}

ImplAlignmentMatrixDiagonal::ImplAlignmentMatrixDiagonal( const ImplAlignmentMatrixDiagonal& src) : 
  ImplAlignmentMatrix( src ), mNumDiagonals(src.mNumDiagonals) 
{
  debug_func_cerr(5);

}

ImplAlignmentMatrixDiagonal::~ImplAlignmentMatrixDiagonal( ) 
{
  debug_func_cerr(5);

}

//------------------------------------------------------------------------------------------------------------
HAlignment ImplAlignmentMatrixDiagonal::getNew() const 
{
    return HAlignment( new ImplAlignmentMatrixDiagonal() );
}
    
HAlignment ImplAlignmentMatrixDiagonal::getClone() const 
{
    return HAlignment( new ImplAlignmentMatrixDiagonal( *this ) );
}

//--------------> mapping functions <----------------------------------------------------------------------------
Position ImplAlignmentMatrixDiagonal::mapRowToCol( Position pos, SearchType search ) const 
{
	debug_func_cerr( 5 );
	
    if (pos >= mRowTo || pos < mRowFrom || mPairs.size() == 0) 
    	return NO_POS;
	
    if (mChangedLength) calculateLength();
    
	assert( mIndex[mNumDiagonals] == NODOT);
	
    // find the row with the smallest diagonal
    Dot ndots = mPairs.size(); 

    for (Position diagonal = 0; diagonal < mNumDiagonals; ++diagonal) 
    {
    	Dot dot = mIndex[diagonal];
    	debug_cerr( 5, "diagonal=" << diagonal << " dot=" << dot );
     
    	if (dot != NODOT) 
    	{
        	// mIndex[mNumDiagonals] = NODOT

    		Dot next_dot = mIndex[diagonal+1];
    		
    		// go along one diagonal
    		while ( dot != next_dot &&
    				dot < ndots &&
    				mPairs[dot].mRow < pos) 
    		{
    			debug_cerr( 5, "diagonal=" << diagonal << " dot=" << dot << " pair=" << mPairs[dot] );
    			++dot;
    		}
    		if (dot < ndots && mPairs[dot].mRow == pos) 
    			return mPairs[dot].mCol;
    	}
    }

    return NO_POS;
}

//-------------------------------------------------------------------------------------------------------------------- 
/* sort Residuepairs(dots) in mPairs by diagonal and then by column. Sorting is done in place using quick-sort. It might be
   faster to only sort the indices (as I did in the old version) and then copy it into a new memory location
*/

void ImplAlignmentMatrixDiagonal::sortDots() const 
{
    
  Position x, from, to;
  Dot ndots = mPairs.size(); 

  /* sort indices on diagonal */
  sortDotsByDiagonal( 0, ndots);
  
  /* sort indices in diagonal */
  from = 0;
  while ( from < ndots ) 
  {
    x    = calculateDiagonal(mPairs[from]);
    to   = from + 1;

    /* find end of row */
    while ( (to < ndots) && (x == calculateDiagonal(mPairs[to])) ) 
    	++to; 

    /* and sort per row */
    sortDotsByRow( from, to );
    from = to;
  }
  
}

//--------------------------------------------------------------------------------------------------------------
// build the index
void ImplAlignmentMatrixDiagonal::buildIndex() const 
{
  Position i;

  mNumDiagonals = (mColTo - mColFrom) + (mRowTo - mRowFrom) + 1;
  Dot ndots = mPairs.size(); 

  //  allocate and initialize memory memory
  // add one extra element as a terminator
  // to simplify mapRowToCol
  allocateIndex( mNumDiagonals + 1);
  for (i = 0; i <= mNumDiagonals; i++) { mIndex[i] = NODOT; }   

  Dot first_dot = 0;
  Diagonal diagonal = calculateNormalizedDiagonal( mPairs[0], mRowFrom, mColFrom);
  Diagonal min_diagonal = -(mRowTo - mRowFrom);

  // update mIndex
  for (i = 0; i < ndots; i++) 
  {
	  Diagonal next_diagonal = calculateNormalizedDiagonal(mPairs[i], mRowFrom, mColFrom);
	  if(diagonal != next_diagonal)
	  {
		  mIndex[diagonal - min_diagonal] = first_dot;
		  first_dot	= i;
		  diagonal = next_diagonal;
	  }
  }

  mIndex[diagonal - min_diagonal] = first_dot;

}


} // namespace alignlib
