/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersSubstitutionMatrix.cpp,v 1.2 2004/01/07 14:35:33 aheger Exp $

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


#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "alignlib_fwd.h"
#include "alignlib_default.h"
#include "AlignlibDebug.h"

#include "HelpersScorer.h"
#include "HelpersSubstitutionMatrix.h"
#include "ImplSequence.h"
#include "ImplProfile.h"
#include "ImplScorerSequenceSequence.h"
#include "ImplScorerSequenceProfile.h"
#include "ImplScorerProfileSequence.h"
#include "ImplScorerProfileProfile.h"
#include "AlignlibException.h"

using namespace std;

namespace alignlib 
{


/** guess scoring object from row and col type

  If auxilliary objects are needed (e.g., SubstitutionMatrix), the default
  one is chosen.

  try casting down the hiearchy of Alignandum-objects and then using a switch statement 
  register the correct match function. There are different implementations for this:

  1. multiple dispatch, but then everytime I write code for aligning/creating dots, ...
  I have to add new corresponding functions in Alignandum objects. I rather like the code
  in one file, even if it is large.

  2. using an emulated virtual table. This is an elegant solution (see Meyers), but needs
  a lot of coding.

  I do not expect, that there will be that many Alignandum-objects, so I use the
  dynamics_cast - way.
 */

HScorer makeScorer( 
		const HAlignandum & row, 
		const HAlignandum & col, 
		const HSubstitutionMatrix & matrix)
{
	debug_func_cerr( 5 );
	const HSequence s1(boost::dynamic_pointer_cast< Sequence, Alignandum>(row));  
	const HProfile  p1(boost::dynamic_pointer_cast< Profile, Alignandum>(row));  
	const HSequence s2(boost::dynamic_pointer_cast< Sequence, Alignandum>(col));  
	const HProfile  p2(boost::dynamic_pointer_cast< Profile, Alignandum>(col));  

	debug_cerr( 5, "extracting Alignandum type" << s1 << " " << s2 << " " << p1 << " " << p2 );
	// setup static pointers to the data locations
	if (s1 && s2)
		return HScorer( new ImplScorerSequenceSequence( s1, s2, matrix ) ); 

	if (p1 && p2)
		return HScorer( new ImplScorerProfileProfile( p1, p2 ) );

	if (s1 && p2)
		return HScorer( new ImplScorerSequenceProfile( s1, p2 ) );

	if (p1 && s2) 
		return HScorer( new ImplScorerProfileSequence( p1, s2 ) );

	throw AlignlibException("HelpersScorer.cpp: Could not guess scoring method");
}

HScorer makeScorer( const HAlignandum & row, const HAlignandum & col )
{
	return makeScorer( row, col, getDefaultSubstitutionMatrix() );
}

}

