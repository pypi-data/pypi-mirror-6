 /*
  alignlib - a library for aligning protein sequences

  $Id$

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
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"

#include "ImplMultipleAlignatorPileup.h"
#include "HelpersAlignment.h"
#include "HelpersAlignandum.h"
#include "HelpersToolkit.h"
#include "MultAlignmentFormat.h"
using namespace std;

namespace alignlib
{

	HMultipleAlignator makeMultipleAlignatorPileup(
			const HAlignator & alignator )
	{
		debug_func_cerr(5);
		return HMultipleAlignator( new ImplMultipleAlignatorPileup(alignator));
	}


  //----------------------------------------------------------------------------------------
  ImplMultipleAlignatorPileup::ImplMultipleAlignatorPileup(
		  const HAlignator & alignator ) :
  mAlignator( alignator )
  {
	  debug_func_cerr( 5 );
  }

  ImplMultipleAlignatorPileup::ImplMultipleAlignatorPileup() :
	mAlignator( getToolkit()->getAlignator() )
	{
			  debug_func_cerr( 5 );
	}

  ImplMultipleAlignatorPileup::~ImplMultipleAlignatorPileup()
  {
      debug_func_cerr(5);
  }

  ImplMultipleAlignatorPileup::ImplMultipleAlignatorPileup( const ImplMultipleAlignatorPileup & src ) :
	  ImplMultipleAlignator(src), mAlignator(src.mAlignator)
  {
  }

  IMPLEMENT_CLONE( HMultipleAlignator, ImplMultipleAlignatorPileup );

  //--------------------------------------------------------------------------
  void ImplMultipleAlignatorPileup::align(
		  HMultAlignment & result,
		  const HAlignandumVector & hsequences ) const
  {
      debug_func_cerr(5);

      AlignandumVector & sequences(*hsequences);

	  result->clear();

	  if (sequences.size() == 0) return;
	  if (sequences[0]->getLength() == 0)
	  {
		  for (int x = 0; x < sequences.size(); ++x)
			  result->add( makeAlignmentVector() );
		  return;
	  }

	  // add the first sequence
	  HAlignment ali(makeAlignmentVector());
	  Position offset = sequences[0]->getFrom();
	  ali->addDiagonal(
			  0,
			  sequences[0]->getLength(),
			  offset );
	  result->add( ali );

	  // align the other sequences always to the first sequence
	  for (int x = 1; x < sequences.size(); ++x)
	  {
		  HAlignment ali(makeAlignmentVector());
		  if (sequences[x]->getLength() > 0)
		  {
			  mAlignator->align( ali, sequences[0], sequences[x]);
			  ali->moveAlignment( -offset, 0);
		  }
		  result->add( ali );
	  }
  }

} // namespace alignlib
