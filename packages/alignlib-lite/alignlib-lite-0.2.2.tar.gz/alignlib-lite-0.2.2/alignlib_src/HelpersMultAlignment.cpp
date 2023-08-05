/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersMultipleAlignment.cpp,v 1.5 2004/03/19 18:23:40 aheger Exp $

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
#include <fstream>
#include <iomanip>
#include <vector>
#include <algorithm>

#include "AlignlibException.h"
#include "Alignandum.h"
#include "Alignment.h"
#include "HelpersAlignment.h"
#include "AlignmentIterator.h"
#include "HelpersMultAlignment.h"
#include "AlignlibDebug.h"

using namespace std;

namespace alignlib
{

bool checkMultAlignmentIdentity(
		const HMultAlignment & a,
		const HMultAlignment & b )
{
	if (a->getNumSequences() != b->getNumSequences()) return false;
	if (a->getLength() != b->getLength()) return false;

	bool is_identical = true;
	for (int x = 0; x < a->getNumSequences() && is_identical; ++x)
		is_identical = checkAlignmentIdentity( (*a)[x], (*b)[x] );
	return is_identical;
}


} // namespace alignlib

