/**
  alignlib - a library for aligning protein sequences

  $Id: Iterator2D.cpp,v 1.2 2004/01/07 14:35:32 aheger Exp $

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
#include <algorithm>
#include <assert.h>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "Alignandum.h"
#include "ImplIterator2DBanded.h"

using namespace std;

namespace alignlib
{

/** factory function for creating iterator in band given by offset and width.
      Diagonals are calculated as col - row.

		col_from --------> col_to
      row_from  x  z
      |          x  z
      |         y x  z
      |          y x  z
      |           y x  z  <- mUpperDiagonal
      row_to       <- mLowerDiagonal


 */
HIterator2D makeIterator2DBanded( const HAlignandum & row,
		const HAlignandum & col,
		const Diagonal lower_diagonal,
		const Diagonal upper_diagonal )
{
	return HIterator2D( new ImplIterator2DBanded( row, col, lower_diagonal, upper_diagonal ) );
}

HIterator2D makeIterator2DBanded(
		const Diagonal lower_diagonal,
		const Diagonal upper_diagonal )
{
	return HIterator2D( new ImplIterator2DBanded( lower_diagonal, upper_diagonal ) );
}

//--------------------------------------------------------------------------------------
ImplIterator2DBanded::ImplIterator2DBanded(
		Diagonal lower_diagonal,
		Diagonal upper_diagonal ):
			ImplIterator2D(),
			mLowerDiagonal(lower_diagonal), mUpperDiagonal(upper_diagonal)
			{
			debug_func_cerr(5);
			assert(mLowerDiagonal <= mUpperDiagonal);
			}

		//--------------------------------------------------------------------------------------
		ImplIterator2DBanded::ImplIterator2DBanded( const HAlignandum & row,
				const HAlignandum & col,
				Diagonal lower_diagonal,
				Diagonal upper_diagonal ):
					ImplIterator2D( row, col),
					mLowerDiagonal(lower_diagonal), mUpperDiagonal(upper_diagonal)
					{
			debug_func_cerr(5);
			assert(mLowerDiagonal <= mUpperDiagonal);
			resetRanges( row, col);
					}

		//--------------------------------------------------------------------------------------
		ImplIterator2DBanded::~ImplIterator2DBanded ()

		{
			debug_func_cerr(5);

		}

		//--------------------------------------------------------------------------------------
		ImplIterator2DBanded::ImplIterator2DBanded(const ImplIterator2DBanded & src) :
			ImplIterator2D( src ),
			mLowerDiagonal( src.mLowerDiagonal), mUpperDiagonal( src.mUpperDiagonal )

			{
			debug_func_cerr(5);

			}

		//--------------------------------------------------------------------------------------
		void ImplIterator2DBanded::resetRanges(
				const HAlignandum & row,
				const HAlignandum & col )
		{
			debug_func_cerr(5);
			mRowFrom = std::max( (Position)(row->getFrom()),                  (Position)(col->getFrom() - mUpperDiagonal) );
			mRowTo   = std::min( (Position)(row->getTo()),                    (Position)(col->getTo()   - mLowerDiagonal)  );
			mColFrom = std::max( (Position)(row->getFrom() + mLowerDiagonal), (Position)(col->getFrom()) );
			mColTo   = std::min( (Position)(row->getTo()   + mUpperDiagonal), (Position)(col->getTo()) );

			debug_cerr( 5, "mRowFrom=" << mRowFrom << " mRowTo=" << mRowTo << " mColFrom=" << mColFrom << " mColTo=" << mColTo
					<< " row=" << row->getFrom() << "-" << row->getTo() << " col=" << col->getFrom() << "-" << col->getTo() );
		}

		IMPLEMENT_CLONE( HIterator2D, ImplIterator2DBanded );

		//--------------------------------------------------------------------------------------
		/** return a new iterator of same type initializes with for row and col
		 */
		HIterator2D ImplIterator2DBanded::getNew( const HAlignandum & row, const HAlignandum & col ) const
		{
			return HIterator2D( new ImplIterator2DBanded( row, col, mLowerDiagonal, mUpperDiagonal ) );
		}

		//--------------------------------------------------------------------------------------
		Iterator2D::const_iterator ImplIterator2DBanded::row_begin ( Position col ) const
		{
			return const_iterator( row_front(col) ) ;
		}
		Iterator2D::const_iterator ImplIterator2DBanded::row_end   ( Position col ) const
		{
			return const_iterator( row_back(col) + 1) ;
		}

		Iterator2D::const_iterator ImplIterator2DBanded::col_begin ( Position row ) const
		{
			return const_iterator( col_front(row) );
		}

		Iterator2D::const_iterator ImplIterator2DBanded::col_end   ( Position row ) const
		{
			return const_iterator( col_back(row) + 1 );
		}

		Position ImplIterator2DBanded::row_front ( Position col ) const
		{
			if (col == NO_POS )
				return mRowFrom;
			else
				return std::max((Position)(col - mUpperDiagonal), mRowFrom );
		}

		Position ImplIterator2DBanded::row_back  ( Position col ) const
		{
			if (col == NO_POS )
				return mRowTo - 1;
			else
				return std::min((Position)(col - mLowerDiagonal + 1), mRowTo ) - 1;
		}

		Position ImplIterator2DBanded::col_front ( Position row ) const
		{
			if (row == NO_POS)
				return mColFrom;
			else
				return std::max((Position)(row + mLowerDiagonal), mColFrom );
		}

		Position ImplIterator2DBanded::col_back  ( Position row ) const
		{
			if (row == NO_POS)
				return mColTo - 1;
			else
				return std::min((Position)(row + mUpperDiagonal + 1), mColTo ) - 1;
		}

} // namespace alignlib
