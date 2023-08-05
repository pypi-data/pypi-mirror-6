/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersMultAlignment.h,v 1.5 2004/03/19 18:23:40 aheger Exp $

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


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef HELPERS_MULT_ALIGNMENT_H
#define HELPERS_MULT_ALIGNMENT_H 1

#include <vector>
#include "alignlib_fwd.h"
#include "MultAlignment.h"

namespace alignlib
{

/**
 *
 * @defgroup FactoryMultAlignment Factory functions for MultAlignment objects.
 * @{
 */

/** @return a new @ref MultAlignment object.
 *
 * This object renders the rows in the multiple alignment
 * each time the multiple alignment is changed by adding
 * a new row.
 *
 * @return a new @ref MultAlignment object.
 * */
HMultAlignment makeMultAlignment();

/** @} */


/** defgroup ToolsetMultAlignment Toolset for MultAlignment objects.
 * @{
 *
 */

/** check if two multiple alignments are identical
 *
 * This function iterates over both multiple alignments and checks if the
 * the same coordinates are returned.
 *
 * @param a @ref Alignment object.
 * @param b @ref Alignment object.
 * @return true, if both alignments are identical.
 */
bool checkMultAlignmentIdentity(
		const HMultAlignment & a,
		const HMultAlignment & b );

/** @} */

}
#endif	/* HELPERS_MULTIPLE_ALIGNMENT_H */
