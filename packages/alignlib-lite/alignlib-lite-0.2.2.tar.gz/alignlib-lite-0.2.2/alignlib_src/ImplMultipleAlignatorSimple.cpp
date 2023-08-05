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

#include "ImplMultipleAlignatorSimple.h"
#include "HelpersAlignment.h"
#include "HelpersAlignandum.h"
#include "HelpersToolkit.h"

#include "MultAlignmentFormat.h"
using namespace std;

namespace alignlib
{

HMultipleAlignator makeMultipleAlignatorSimple(const HAlignator & alignator)
{
	debug_func_cerr(5);
	return HMultipleAlignator(new ImplMultipleAlignatorSimple(alignator));
}

//----------------------------------------------------------------------------------------
ImplMultipleAlignatorSimple::ImplMultipleAlignatorSimple() :
	mAlignator(getToolkit()->getAlignator())
{
}

ImplMultipleAlignatorSimple::ImplMultipleAlignatorSimple(
		const HAlignator & alignator) :
	mAlignator(alignator)
{
	debug_func_cerr( 5 );
}

ImplMultipleAlignatorSimple::~ImplMultipleAlignatorSimple()
{
	debug_func_cerr(5);
}

ImplMultipleAlignatorSimple::ImplMultipleAlignatorSimple(
		const ImplMultipleAlignatorSimple & src) :
	ImplMultipleAlignator(src), mAlignator(src.mAlignator)
{
}

IMPLEMENT_CLONE( HMultipleAlignator, ImplMultipleAlignatorSimple );

//--------------------------------------------------------------------------
void ImplMultipleAlignatorSimple::align(HMultAlignment & result,
		const HAlignandumVector & hsequences) const
{
	debug_func_cerr(5);

	AlignandumVector & sequences(*hsequences);

	result->clear();

	if (sequences.size() == 0)
		return;

	HAlignandumVector aligned(new AlignandumVector());

	// add empty sequences
	int x = 0;
	while (x < sequences.size() && sequences[x]->getLength() == 0)
	{
		HAlignment ali(makeAlignmentVector());
		result->add(ali);
		aligned->push_back(sequences[x]);
		++x;
	}

	// add first non-empty sequence
	{
		HAlignment ali(makeAlignmentVector());
		ali->addDiagonal(
				0,
				sequences[x]->getLength(),
				sequences[x]->getFrom() );
		result->add(ali);
		aligned->push_back(sequences[x]);
		++x;
	}

	debug_cerr( 3, "starting: multiple alignment\n" << MultAlignmentFormatPlain( result, aligned ) );

	// align the other sequences, expanding the mali
	// as we go along.
	for (; x < sequences.size(); ++x)
	{
		HAlignment ali(makeAlignmentVector());

		if (sequences[x]->getLength() > 0)
		{
			debug_cerr( 3, "iteration: multiple alignment before expansion\n" << MultAlignmentFormatPlain( result, aligned ) );
			result->expand(aligned);
			debug_cerr( 3, "iteration: multiple alignment after expansion\n" << MultAlignmentFormatPlain( result, aligned ) );
			HAlignandum profile(makeProfile(result, aligned));
			mAlignator->align(ali, profile, sequences[x]);
		}
		result->add(ali);
		aligned->push_back(sequences[x]);
		debug_cerr( 3, "iteration: multiple alignment\n" << MultAlignmentFormatPlain( result, aligned ) );
	}
	result->expand(aligned);
}

} // namespace alignlib
