/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignatorDummy.cpp,v 1.2 2004/01/07 14:35:34 aheger Exp $

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
#include <math.h>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "HelpersAlignment.h"
#include "HelpersToolkit.h"

#include "ImplAlignatorPrebuilt.h"

using namespace std;

namespace alignlib
{

HAlignator makeAlignatorPrebuilt( const HAlignment & ali)
{
	return HAlignator( new ImplAlignatorPrebuilt( ali ) );
}

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplAlignatorPrebuilt::ImplAlignatorPrebuilt () :
	ImplAlignator(), mAlignment ( getToolkit()->getAlignment() )
	{}

ImplAlignatorPrebuilt::ImplAlignatorPrebuilt ( const HAlignment & ali) :
	ImplAlignator(), mAlignment ( ali )
	{
	}

ImplAlignatorPrebuilt::~ImplAlignatorPrebuilt ()
{
}

ImplAlignatorPrebuilt::ImplAlignatorPrebuilt (const ImplAlignatorPrebuilt & src ) :
	ImplAlignator(src),
	mAlignment(src.mAlignment)
	{
	}

IMPLEMENT_CLONE( HAlignator, ImplAlignatorPrebuilt );

//----------------------------------------------------------------------------------------------------------
void ImplAlignatorPrebuilt::align(
		HAlignment & result,
		const HAlignandum & row,
		const HAlignandum & col )
{
	debug_func_cerr(5);

	startUp(result, row, col );

	debug_cerr( 10, "input dots" << *mAlignment );

	// copy alignment only in region given by iterator
	copyAlignment( result, mAlignment,
			mIterator->row_front(), mIterator->row_back() + 1,
			mIterator->col_front(), mIterator->col_back() + 1);

	debug_cerr( 10, "copied dots" << *result );

	cleanUp( result, row, col );
}


} // namespace alignlib
