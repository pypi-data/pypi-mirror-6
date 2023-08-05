/*
  alignlib - a library for aligning protein sequences

  $Id: ImplFragmentorIterative.cpp,v 1.2 2004/01/07 14:35:35 aheger Exp $

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
#include "alignlib_fwd.h"
#include "AlignlibDebug.h"

#include "Fragmentor.h"

#include "Alignment.h"
#include "HelpersAlignment.h"

#include "AlignmentIterator.h"

#include "Alignandum.h"
#include "AlignlibException.h"

#include "HelpersSubstitutionMatrix.h"

#include "Alignator.h"
#include "HelpersAlignator.h"

#include "HelpersToolkit.h"

#include "ImplFragmentorIterative.h"

using namespace std;

namespace alignlib
{

/*---------------------factory functions ---------------------------------- */

/** make an alignator object, which does a dot-alignment. The default version can be given an AlignmentMatrix-
      object */
HFragmentor makeFragmentorIterative(
		const HAlignment & dots,
		Score min_score,
		Score gop, Score
		gep)
{
	return HFragmentor( new ImplFragmentorIterative( dots, min_score, gop, gep) );
}


//----------------------------------------------------------------------------------------------------

ImplFragmentorIterative::ImplFragmentorIterative() :
			ImplFragmentor(),
			mDots(getToolkit()->getAlignment()),
			mMinScore( 0),
			mGop(0),
			mGep(0) {
		}

ImplFragmentorIterative::ImplFragmentorIterative(
		const HAlignment & dots,
		Score min_score,
		Score gop,
		Score gep) :
			ImplFragmentor(),
			mDots(dots),
			mMinScore( min_score),
			mGop(gop),
			mGep(gep) {
		}


		ImplFragmentorIterative::~ImplFragmentorIterative()
		{
			debug_func_cerr(5);

		}

		ImplFragmentorIterative::ImplFragmentorIterative( const ImplFragmentorIterative & src ) :
			ImplFragmentor(src),
			mDots(src.mDots),
			mMinScore( src.mMinScore ),
			mGop(src.mGop),
			mGep(src.mGep) {
		}

		IMPLEMENT_CLONE( HFragmentor, ImplFragmentorIterative);

		//------------------------------------------------------------------------------------------------
		void ImplFragmentorIterative::performFragmentation(
				const HAlignment & sample,
				const HAlignandum & row,
				const HAlignandum & col )
		{
			// TODO: check for copy or reference
			HAlignment original_dots = mDots;
			// true, if mDots contains a copy of orignal alignata object.
			// Make sure, you do not delete it.
			bool is_copy = false;

			while ( 1 )
			{
				HAlignator dottor(makeAlignatorPrebuilt( mDots ));
				HAlignator alignator(makeAlignatorDots( dottor, mGop, mGep ));

				HAlignment result = sample->getNew();
				alignator->align( result, row, col );

#ifdef DEBUG
				if (AlignlibDebug::mVerbosity >= 5)
				{
					std::cerr << "starting alignment: " << *mDots << std::endl;
					std::cerr << "result: " << *result << endl;
				}
#endif

				if (result->getScore() >= mMinScore)
				{
					mFragments->push_back( result );

					// delete dots from dot-plot. Delete all dots in region
					HAlignment copy = makeAlignmentMatrixUnsorted();

					copyAlignmentWithoutRegion( copy,
							mDots,
							result->getRowFrom(),
							result->getRowTo(),
							result->getColFrom(),
							result->getColTo());

					// substitute new copy instead of old copy
					mDots = copy;
					is_copy = true;

				} else
				{
					break;
				}

			}

		}


} // namespace alignlib




