/*
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
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "alignlib_fwd.h"
#include "AlignlibDebug.h"
#include "Alignandum.h"
#include "ImplIterator2D.h"

using namespace std;

namespace alignlib
{

//--------------------------------------------------------------------------------------
ImplIterator2D::ImplIterator2D() : 
	Iterator2D(),
	mRowFrom(NO_POS), mRowTo(NO_POS),
	mColFrom(NO_POS), mColTo(NO_POS)
	{
	}

//--------------------------------------------------------------------------------------
ImplIterator2D::ImplIterator2D( 
		const HAlignandum & row, 
		const HAlignandum & col ) : 
			Iterator2D(),
			mRowFrom(NO_POS), mRowTo(NO_POS),
			mColFrom(NO_POS), mColTo(NO_POS) 
			{
			debug_func_cerr(5);

			resetRanges( row, col );
			}    

		//--------------------------------------------------------------------------------------
		ImplIterator2D::~ImplIterator2D ()
		{
			debug_func_cerr(5);
		}

		//--------------------------------------------------------------------------------------
		ImplIterator2D::ImplIterator2D(const ImplIterator2D & src) :
			mRowFrom( src.mRowFrom ), mRowTo( src.mRowTo ),
			mColFrom( src.mColFrom ), mColTo( src.mColTo )

			{
			debug_func_cerr(5);

			}

		//--------------------------------------------------------------------------------------
		void ImplIterator2D::resetRanges( const HAlignandum & row, const HAlignandum & col )
		{
			mRowFrom = row->getFrom();
			mRowTo   = row->getTo();    
			mColFrom = col->getFrom();
			mColTo   = col->getTo();    
		}

		//--------------------------------------------------------------------------------------
		Iterator2D::const_iterator ImplIterator2D::row_begin ( Position col ) const
		{
			return const_iterator( row_front(col) ) ;
		}
		Iterator2D::const_iterator ImplIterator2D::row_end   ( Position col ) const
		{
			return const_iterator( row_back(col) + 1 ) ;
		}

		Iterator2D::const_iterator ImplIterator2D::col_begin ( Position row ) const
		{
			return const_iterator( col_front(row) );
		}

		Iterator2D::const_iterator ImplIterator2D::col_end   ( Position row ) const
		{
			return const_iterator( col_back(row) + 1);
		}

		Position ImplIterator2D::row_size ( Position col ) const
		{
			return row_back(col) - row_front(col) + 1;
		}

		Position ImplIterator2D::col_size ( Position row ) const
		{
			return col_back(row) - col_front(row) + 1;
		}

} // namespace alignlib
