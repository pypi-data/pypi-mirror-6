/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignmentSet.cpp,v 1.4 2004/06/02 12:11:37 aheger Exp $

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
#include <limits>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "ImplAlignmentSorted.h"
#include "AlignmentIterator.h"

using namespace std;

namespace alignlib
{

//-- Comparator objects - these define the sort order of residues within an alignment

/** residues are sorted by row only */
struct ComparatorRow
{
  bool operator()( const ResiduePair & x, const ResiduePair & y) const 
  { 
    return x.mRow < y.mRow; 
  } 
};

/** residues are sorted by col only */
struct ComparatorCol
{
  bool operator()( const ResiduePair & x, const ResiduePair & y) const 
  { 
    return x.mCol < y.mCol; 
  } 
};

/** residues are sorted by row and then by column */
struct ComparatorRowCol
{
  bool operator() ( const ResiduePair & x, const ResiduePair & y) const 
  { 
    if (x.mRow < y.mRow) return 1;
    if (x.mRow > y.mRow) return 0;
    if (x.mCol < y.mCol) 
      return 1;
    else
      return 0;
  }
};  

 /** residues are sorted by diagonal and then by column */
struct ComparatorDiagonalCol 
{
     bool operator() ( const ResiduePair & x, const ResiduePair & y) const 
     { 
	  Diagonal d1 = x.mCol - x.mRow;
	  Diagonal d2 = y.mCol - y.mRow;
	  if (d1 < d2) return 1;
	  if (d1 > d2) return 0;
	  if (x.mCol < y.mCol) 
	      return 1;
	  else
	      return 0;
     }
 };  


typedef std::set<ResiduePair, ComparatorRow> AlignmentSetRow;
typedef std::set<ResiduePair, ComparatorCol> AlignmentSetCol;
typedef std::set<ResiduePair, ComparatorRowCol> AlignmentSetRowCol;
typedef std::set<ResiduePair, ComparatorDiagonalCol> AlignmentSetDiagonalCol;  

//------------------------------factory functions -----------------------------
HAlignment makeAlignmentSet()
{
	return HAlignment( new ImplAlignmentSorted< AlignmentSetRow >() );
}

HAlignment makeAlignmentSetCol()
{
	return HAlignment( new ImplAlignmentSorted< AlignmentSetCol >() );
}

HAlignment makeAlignmentHash()
{
	return HAlignment( new ImplAlignmentSorted< AlignmentSetRowCol >() );
}

HAlignment makeAlignmentHashDiagonal()
{
	return HAlignment( new ImplAlignmentSorted< AlignmentSetDiagonalCol >() );
}


//------------------------------------< constructors and destructors >-----
template <class T>
ImplAlignmentSorted<T>::ImplAlignmentSorted() : 
	ImplAlignment() 
{
	debug_func_cerr(5);

}

template <class T>
ImplAlignmentSorted<T>::ImplAlignmentSorted( const ImplAlignmentSorted& src) : 
	ImplAlignment( src ) 
{
	debug_func_cerr(5);


	clearContainer();

	PairIterator it(src.mPairs.begin()), it_end(src.mPairs.end());
	for (;it != it_end; ++it) 
		mPairs.insert( *it );
}

template <class T>  
ImplAlignmentSorted<T>::~ImplAlignmentSorted( ) 
{
	debug_func_cerr(5);

	clear();
}

//------------------------------------------------------------------------------------------------------------
template <class T>
HAlignment ImplAlignmentSorted<T>::getNew() const
{
	return HAlignment( new ImplAlignmentSorted<T>() );
}

template <class T>
HAlignment ImplAlignmentSorted<T>::getClone() const
{
	return HAlignment( new ImplAlignmentSorted<T>( *this ));
}

//------------------------------------------------------------------------------------------------------------
template <class T>  
void ImplAlignmentSorted<T>::clearContainer()
{ 
	PairIterator it(mPairs.begin()), it_end(mPairs.end());
	mPairs.clear(); 
}

//------------------------------------------------------------------------------------------------------------
template <class T>  
void ImplAlignmentSorted<T>::clear() 
{ 
	ImplAlignment::clear();
	clearContainer();
}

template <class T>
AlignmentIterator ImplAlignmentSorted<T>::begin() const
{ 
	return AlignmentIterator( new ImplAlignmentSorted_Iterator(mPairs.begin()));
}

template <class T>
AlignmentIterator ImplAlignmentSorted<T>::end() const
{ 
	return AlignmentIterator( new ImplAlignmentSorted_Iterator(mPairs.end())); 
}


//----------------> accessors <------------------------------------------------------------------------------

template <class T>
ResiduePair ImplAlignmentSorted<T>::front() const { return *(mPairs.begin()); }
template <class T>  
ResiduePair ImplAlignmentSorted<T>::back()  const { return *(mPairs.rbegin()); }

template <class T>
void ImplAlignmentSorted<T>::addPair( const ResiduePair & new_pair ) 
{
	debug_func_cerr(5);

	ImplAlignment::addPair( new_pair );
	setChangedLength(); 
	mPairs.insert( new_pair ); 
} 

//----------------------------------------------------------------------------------------------------------
/** retrieves a pair of residues from the alignment */
template <class T>  
ResiduePair ImplAlignmentSorted<T>::getPair( const ResiduePair & p) const 
{
	PairIterator it = mPairs.find( p );
	if (it != mPairs.end())
		return *it;
	else
		return ResiduePair();
} 

//-----------------------------------------------------------------------------------------------------------   
template <class T>
void ImplAlignmentSorted<T>::updateBoundaries() const 
{

	Position max_size = mPairs.size();

	mRowFrom = mRowTo = mColFrom = mColTo = NO_POS;
	
	// ignore empty alignments
	if (max_size == 0)
	  return;
		
	mRowFrom = std::numeric_limits<Position>::max();
	mColFrom = std::numeric_limits<Position>::max();
	mRowTo = std::numeric_limits<Position>::min();
	mColTo = std::numeric_limits<Position>::min();
	
	PairConstIterator it(mPairs.begin()), it_end(mPairs.end());
	for (; it != it_end; ++it )
	{
    	const Position row = (*it).mRow;
    	const Position col = (*it).mCol;
    	
		// get maximum boundaries
    	if (row < mRowFrom) mRowFrom = row;
    	if (col < mColFrom) mColFrom = col;
    	if (row > mRowTo)   mRowTo = row;
    	if (col > mColTo)   mColTo = col;		
	}
	++mRowTo;
	++mColTo;
}

//----------------------------------------------------------------------------------------------------------
/** remove a pair from an alignment */
template <class T>  
void ImplAlignmentSorted<T>::removePair( const ResiduePair & p ) 
{
	debug_func_cerr(5);
	
	PairIterator it(mPairs.find(p) );

	if (it != mPairs.end()) 
	{
		setChangedLength(); 
		mPairs.erase(it);
	}
	
	ImplAlignment::removePair( p );	
} 

//----------------------------------------------------------------------------------------
/** This is a generic routine that iterates through the whole container.
 * TODO: think about template specialization for row sorted containers
 *
 */
template <class T>  
void ImplAlignmentSorted<T>::removeRowRegion( Position from, Position to) 
{

	PairIterator it(mPairs.begin()), it_end(mPairs.end());

	bool deleted = false;
	// Valgrind did not like the iterator being deleted,
	// thus this complicated loop structure. Did not complain 
	while (it != it_end) 
	{
		if ( it->mRow >= from && it->mRow < to) 
		{
			PairIterator it2 = it;
			++it;              
			mPairs.erase(it2);
			deleted = true;
		}
		else  
			++it;           
	}

	if (deleted)
	{
		updateBoundaries();
		setChangedLength();
	}	
}

/* This is a non-generic routine
template <class T>  
void ImplAlignmentSorted<T>::removeRowRegion( Position from, Position to) 
{
	bool deleted = false;
	for (Position pos = from; pos < to; pos++) 
	{
		ResiduePair p(pos, NO_POS, 0);
		PairIterator it(mPairs.find( &p ));

		if (it != mPairs.end()) 
		{
			delete *it;
			mPairs.erase(it);
			deleted = true;
		}
	}	
	if (deleted)
	{
		setChangedLength();
		updateBoundaries();
	}
}
*/

//----------------------------------------------------------------------------------------
/** This is a generic routine that iterates through the whole container
 * TODO: think about template specialization for col sorted containers 
 * */
template <class T>  
void ImplAlignmentSorted<T>::removeColRegion( Position from, Position to) 
{

	PairIterator it(mPairs.begin()), it_end(mPairs.end());

	bool deleted = false;
	// Valgrind did not like the iterator being deleted,
	// thus this complicated loop structure. Did not complain 
	while (it != it_end) 
	{
		if ( it->mCol >= from && it->mCol < to) 
		{
			PairIterator it2 = it;
			++it;              
			mPairs.erase(it2);
			deleted = true;
		}
		else  
			++it;           
	}

	if (deleted)
	{
		updateBoundaries();
		setChangedLength();
	}	
}

} // namespace alignlib
