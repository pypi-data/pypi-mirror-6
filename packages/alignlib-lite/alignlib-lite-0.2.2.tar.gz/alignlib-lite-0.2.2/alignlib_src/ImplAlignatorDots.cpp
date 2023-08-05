/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignatorDots.cpp,v 1.2 2004/01/07 14:35:34 aheger Exp $

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
#include <stdio.h>

#include <map>
#include <vector>

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "ImplAlignatorDots.h"
#include "Alignandum.h"
#include "ImplAlignmentMatrixRow.h"

#include "HelpersSubstitutionMatrix.h"
#include "HelpersToolkit.h"

#include "HelpersAlignator.h"
#include "Alignment.h"
#include "HelpersAlignment.h"

using namespace std;

namespace alignlib
{

/*---------------------factory functions ---------------------------------- */

    /** make an alignator object, which does a dot-alignment.
     */
HAlignator makeAlignatorDots(
		const HAlignator & alignator,
		Score gop,
		Score gep )
{
	return HAlignator( new ImplAlignatorDots( alignator, gop, gep, gop, gep ) );
}


	//----------------------------------------------------------------------------------------------------------------------------------------
	/* constructors and destructors */

ImplAlignatorDots::ImplAlignatorDots(
		const HAlignator & dots,
		Score row_gop, Score row_gep,
		Score col_gop, Score col_gep )
: ImplAlignator(), mDottor (dots),
mRowGop( row_gop ), mRowGep( row_gep ),
mColGop( col_gop ), mColGep( col_gep )
{
	if (mColGop == 0)
	{
		mColGop = mRowGop;
		mColGep = mRowGep;
	}
}

ImplAlignatorDots::ImplAlignatorDots()
: ImplAlignator(), mDottor (getToolkit()->getAlignator()),
mRowGop( 0 ), mRowGep( 0 ),
mColGop( 0 ), mColGep( 0 )
{
}

	  //----------------------------------------------------------------------------------------------------------
ImplAlignatorDots::ImplAlignatorDots( const ImplAlignatorDots & src )
: ImplAlignator( src ),
mDottor(src.mDottor)
{
	debug_func_cerr(5);
}


//------------------------------------------------------------------------------------------
ImplAlignatorDots::~ImplAlignatorDots()
{
  debug_func_cerr(5);
}

IMPLEMENT_CLONE( HAlignator, ImplAlignatorDots );

//------------------------------------------------------------------------------------------
//----------------------------------------------------------------------------------------------------------
void ImplAlignatorDots::setRowGop( Score gop ) { mRowGop = gop;}
void ImplAlignatorDots::setRowGep( Score gep ) { mRowGep = gep;}
void ImplAlignatorDots::setColGop( Score gop ) { mColGop = gop;}
void ImplAlignatorDots::setColGep( Score gep ) {mColGep = gep; }

Score ImplAlignatorDots::getRowGop() { return mRowGop; }
Score ImplAlignatorDots::getRowGep() { return mRowGep; }
Score ImplAlignatorDots::getColGop() { return mColGop; }
Score ImplAlignatorDots::getColGep() { return mColGep; }

//----------------------------------------------------------------------------------------------------------
void ImplAlignatorDots::startUp(HAlignment & ali,
		  const HAlignandum & row,
		  const HAlignandum & col )
  {
    debug_func_cerr(5);
    ImplAlignator::startUp(ali, row, col);

    mRowLength = mIterator->row_size();
    mColLength = mIterator->col_size();

    // the algorithms assume that dots are sorted by row,
    // so use AlignmentMatrixRow
    mMatrix = makeAlignmentMatrixRow();

    // setup matrix of dots
    mDottor->align( mMatrix, row, col );

    // get the number of dots, which corresponds to the length of the
    // alignment in this class. This will tell the matrix to put itself
    // in a defined state (sort, etc.), at the same time.
    mNDots = mMatrix->getLength();

    debug_cerr( 5, "built dotplot for alignment with " << mNDots << " dots" );

    debug_cerr( 10, "dots=\n" << *(mMatrix) );

    // get pointers to location of dots(pairs)
    const HImplAlignmentMatrix t = boost::dynamic_pointer_cast< ImplAlignmentMatrix, Alignment>(mMatrix);
    mPairs	= &t->mPairs;
    mRowIndices = t->mIndex;

    mTrace   = new int[mNDots];
    mLastDot = -1;
  }

//-------------------------------------------------------------------------------------------------------
void ImplAlignatorDots::cleanUp(HAlignment & ali,
		  const HAlignandum & row, const HAlignandum & col)
  {
    debug_func_cerr(5);


    if (mTrace != NULL)
      delete [] mTrace;

    ImplAlignator::cleanUp(ali, row, col );

  }

//----------------------------------------------------------------------------------------------------------------------------------------
void ImplAlignatorDots::align(HAlignment & result,
		  const HAlignandum & row,
		  const HAlignandum & col )
  {
    debug_func_cerr(5);

    startUp(result, row, col );

    performAlignment(result, row, col);

    traceBack(result, row, col);

    cleanUp(result, row, col);
  }

//-----------------------------------------< BackTracke >-------------------------------------------------------------
void ImplAlignatorDots::traceBack(
		HAlignment & result,
		const HAlignandum & row,
		const HAlignandum & col )
  {
    debug_func_cerr(5);

    int col_res, row_res;

    int idot   = mLastDot;
    int jleft  = row->getLength();

    while ( idot >= 0)
      {

        debug_cerr( 5, "-->idot "     << setw(5) << idot      <<
            " col[idot] "  << setw(5) << (*mPairs)[idot].mCol <<
            " row[idot] "  << setw(5) << (*mPairs)[idot].mRow <<
            " mTrace[idot] "<< setw(5) << mTrace[idot] );

        row_res = (*mPairs)[idot].mRow;
        col_res = (*mPairs)[idot].mCol;

        if (row_res < 0) continue;
        if (col_res < 0) continue;
        if (row_res > jleft) break;
        jleft = row_res;                                   // just in case

        result->addPair( ResiduePair(row_res, col_res, (*mPairs)[idot].mScore) );

        idot = mTrace[idot];
      }

    result->setScore( mScore );
  }
//------------------------------------------------------------------------------------------------------------
// find the index of a residue pairs given row and column
Position ImplAlignatorDots::getPairIndex( Position r, Position c ) const
{
  int x     = mRowIndices[r];
  bool found = false;

  if ( x == NO_POS )
  	return NO_POS;

  while ((*mPairs)[x].mRow == r )
  {
  	if ((*mPairs)[x].mCol == c)
  	{
  		found = true;
  		break;
  	}
  	x++;
  }

  if (found)
  	return x;
  else
  	return NO_POS;
}

//------------------------------------------------------------------------------------------
Score ImplAlignatorDots::getGapCost( Dot x1, Dot x2 ) const
{

  Position c1 = (*mPairs)[x1].mCol;
  Position c2 = (*mPairs)[x2].mCol;
  Position r1 = (*mPairs)[x1].mRow;
  Position r2 = (*mPairs)[x2].mRow;

  Score gap_cost = 0;
  Position d;

  if ((d = (r2 - r1)) > 1)
      gap_cost += mRowGop + d * mRowGep;

  if ((d = (c2 - c1)) > 1)
      gap_cost += mColGop + d * mColGep;

  return gap_cost;
}

//-------------------------------------------< Alignment subroutine >----------------------------------------------
void ImplAlignatorDots::performAlignment(
		HAlignment & ali,
		const HAlignandum & prow,
		const HAlignandum & pcol )
  {

  /**
     Overview over the algorithm

     1. Dots are sorted by row and then by column

     col ->
     row
     |

     ------------|
     |           |
     |           |
     |           |
 c-> |           |
     ------------x

     note: you do not have to consider dots in the same row or column, as it is
     not possible to match the same row to two different columns and vice versa.

  */

	debug_func_cerr(5);

	// check if number of dots and the size of the dotplot
	// correspond.
	assert( mNDots == mPairs->size() );

	Dot global_best_dot = NO_POS;
	Score global_best_score = 0;

	// create data structure for search region
	// sort dots in search region by increasing column
	typedef multimap <Position, Dot> MyDotSet;

	MyDotSet search_region;

	// array with scores of dots
	vector<Score> scores(mNDots,0);

	// array with dots in current row
	vector<Dot> dot_stack(mColLength, NO_POS);

	unsigned int num_row_dots = 0;
	Position last_row = 0;

	//----------------------------------> main alignment loop <----------------------------------------------------
	for ( Dot current_dot = 0; current_dot < mNDots; ++current_dot)
	{

		Position current_row = (*mPairs)[current_dot].mRow;
		Position current_col = (*mPairs)[current_dot].mCol;

		debug_cerr( 6, "working on: dot=" << current_dot << " row=" << current_row << " col=" << current_col );

		// if a new row is entered, enter dots from stack to search-area
		if (current_row != last_row)
		{
			while (num_row_dots > 0)
			{
				Dot dot = dot_stack[--num_row_dots];
				search_region.insert(pair<Position, Dot>((*mPairs)[dot].mCol, dot));
			}
			last_row = current_row;
		}

		// search search-area: always lookup starting at col 1 until current_col - 1. Try to find
       	// a positive trace leading to current dot. If it were negative, it would not be part of
       	// the optimum alignment up to current_dot.
		Dot search_best_dot   = NO_POS;
		Score search_best_score = 0;

#ifdef DEBUG
		debug_cerr( 6, "SEARCH_AREA" );

		for (MyDotSet::iterator it = search_region.begin(); it != search_region.end(); ++it)
			debug_cerr( 6, "  [" << (*it).first << ", " << (*it).second << "]" );
#endif

		MyDotSet::const_iterator it(search_region.begin()), it_end(search_region.end());
		while (it != it_end && ((*it).first < current_col))
		{

			Dot const search_dot = (*it).second;
			Score search_score = scores[search_dot];

			if (search_score > 0)
			{
				search_score += getGapCost( search_dot, current_dot);
				if (search_score >= search_best_score)
                {
					search_best_score = search_score;
					search_best_dot   = search_dot;
                }
			}
			++it;
		}

		// no positive trace found, new trace starts at current dot
		if (search_best_dot == NO_POS)
			search_best_score = (*mPairs)[current_dot].mScore;
		else
			search_best_score += (*mPairs)[current_dot].mScore;

		debug_cerr( 5, "current_dot=" << current_dot << " current_row=" << current_row << " current_col=" << current_col );
		debug_cerr( 5, "search_best_dot=" << search_best_dot << " search_best_score=" << search_best_score );

#ifdef DEBUG
		if (search_best_dot != NO_POS)
			debug_cerr( 5, "gap_cost=" << getGapCost(search_best_dot, current_dot) );
#endif

		// do local alignment, traces with score <= 0 are skipped
		if (search_best_score < 0)
			continue;

		scores[current_dot] = search_best_score;
		mTrace[current_dot] = search_best_dot;

		dot_stack[num_row_dots++] = current_dot;

		// remember end point of best trace
		if (search_best_score > global_best_score)
		{
			global_best_score = search_best_score;
			global_best_dot   = current_dot;
		}

	} // end of alignment loop

	mLastDot= global_best_dot;
	mScore  = global_best_score;

	debug_cerr( 5, "global_best_dot=" << global_best_dot << " global_best_score=" << global_best_score )

  //--------------> cleaning up <---------------------------------------------------------------

}

} // namespace alignlib







