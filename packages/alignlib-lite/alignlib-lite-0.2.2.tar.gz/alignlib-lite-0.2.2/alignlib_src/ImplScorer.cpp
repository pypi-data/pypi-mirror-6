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
#include "AlignlibException.h"
#include "AlignlibDebug.h"
#include "HelpersScorer.h"

#include "ImplScorer.h"

using namespace std;

namespace alignlib
{

/** return placeholder scorer *
 */
HScorer makeScorer( )
{
	return HScorer( new ImplScorer() );
}

//--------------------------------------------------------------------------------------
ImplScorer::ImplScorer()
: Scorer()
{
	debug_func_cerr( 5 );
}

//--------------------------------------------------------------------------------------
ImplScorer::ImplScorer(
		const HAlignandum & row,
		const HAlignandum & col )
: Scorer()
{
			debug_func_cerr( 5 );

}

//--------------------------------------------------------------------------------------
ImplScorer::~ImplScorer ()
{
	debug_func_cerr( 5 );
}

//--------------------------------------------------------------------------------------
ImplScorer::ImplScorer(const ImplScorer & src) : Scorer(src)
{
}

HScorer ImplScorer::getNew(
				const HAlignandum & row,
				const HAlignandum & col) const
{
	debug_func_cerr(5);
	return makeScorer( row, col );
}

IMPLEMENT_CLONE( HScorer, ImplScorer );

Score ImplScorer::getScore( const Position & row, const Position & col) const
{
	throw AlignlibException( "asked from a score from the default scorer ");
}

}


