/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersAlignatum.h,v 1.2 2004/01/07 14:35:32 aheger Exp $

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

#ifndef HELPERS_ALIGNATUM_H
#define HELPERS_ALIGNATUM_H 1

#include "alignlib_fwd.h"

namespace alignlib
{

/**
 *
 * @defgroup FactoryAlignatum Factory functions for Alignatum objects.
 * @{
 *
 */

/** make an @ref Alignatum object from a string.
 *
 * @param src  string to initialize with
 * @param from first residue
 * @param to   last residue
 * @return a new @ref Alignatum object.
 */
HAlignatum makeAlignatum(
		const std::string & src,
		const Position & from = NO_POS,
		const Position & to = NO_POS);

/** make an @ref Alignatum object from a string.
 *
 * @param src  string to initialize with
 * @param map_src2alignment  mapping of string to alignment.
 * @param max_length maximum length of object. Adds additional gap characters to the end.
 * @param unaligned 	add unaligned characters in lower case (as many as fit before
 * 					the next aligned character)
 *
 * @return a new @ref Alignatum object.
 */
HAlignatum makeAlignatum(
		const std::string & src,
		const HAlignment & map_src2aligned,
		const Position & max_length = 0,
		const bool & unaligned = false );

/** make an @ref Alignatum object from an @ref Alignandum object.
 *
 * @param src  @ref Alignandum object.
 * @param map_this2new @ref Alignment object mapping src to the new object.
 * @param max_length maximum length of object. Adds additional gap characters to the end.
 * @param unaligned 	add unaligned characters in lower case (as many as fit before
 * 					the next aligned character)
 * @return a new @ref Alignatum object.
 */
HAlignatum makeAlignatum(
		const HAlignandum & src,
		const HAlignment & map_this2new,
		const Position & max_length = 0,
		const bool & unaligned = false );

/** return a new @ref Alignatum object from an @ref Alignandum object.
 *
 * @param src  @ref Alignandum object.
 * @param from first residue
 * @param to   last residue
 * @return a new @ref Alignatum object.
 */
HAlignatum makeAlignatum(
		const HAlignandum & src,
		const Position & from = NO_POS,
		const Position & to = NO_POS);

/** return a new @ref @Alignatum object.
 *
 * @return a new @ref Alignatum object.
 */
HAlignatum makeAlignatum();

/**
 * @}
 */

}

#endif	/* HELPERS_ALIGNATUM_H */
