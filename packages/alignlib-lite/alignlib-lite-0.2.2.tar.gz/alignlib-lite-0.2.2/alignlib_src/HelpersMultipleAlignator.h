/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersAlignator.h,v 1.4 2005/02/24 11:07:25 aheger Exp $

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

#ifndef HELPERS_MULTIPLEALIGNATOR_H
#define HELPERS_MULTIPLEALIGNATOR_H 1

#include "alignlib_fwd.h"

namespace alignlib
{

/**
 *
 * @defgroup FactoryMultipleAlignator Factory functions for MultipleAlignator objects.
 * @{
 *
 */

/** make an @ref MultipleAlignator doing simple progressive alignment.
 *
 * @param result The @ref MultipleAlignment object to save the result.
 * @param sequences a @ref AlignandumVector object containing the sequences to align.
 * @param treetor A @ref Treetor object to build trees.
 *
 * @return a new @ref MultipleAlignator object.
 * */
/*HMultipleAlignator makeMultipleAlignatorProgressive(
		HMultipleAlignment & result,
		const HAlignandumVector & sequences,
		const HTreetor & treetor );
*/

/** make an @ref MultipleAlignator doing simple alignment.
 *
 * Each sequence is in turn aligned to the growing multiple
 * alignment using pairwise profile/sequence alignment.
 *
 * @param alignator the @ref Alignator object to use for pairwise alignment.
 *
 * @return a new @ref MultipleAlignator object.
 * */
HMultipleAlignator makeMultipleAlignatorSimple(
		const HAlignator & alignator );

/** make an @ref MultipleAlignator doing a pileup alignment.
 *
 * Each sequence is in turn aligned to the first sequence
 * and stacked on top of it.
 *
 * @param alignator the @ref Alignator object to use for pairwise alignment.
 *
 * @return a new @ref MultipleAlignator object.
 * */
HMultipleAlignator makeMultipleAlignatorPileup(
		const HAlignator & alignator );

/**
 * @}
 */



}

#endif	/* HELPERS_ALIGNATOR_H */
