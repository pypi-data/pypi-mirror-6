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

#ifndef HELPERS_ALIGNATOR_H
#define HELPERS_ALIGNATOR_H 1

#include "alignlib_fwd.h"

namespace alignlib 
{

/**
 * 
 * @defgroup FactoryAlignator Factory functions for Alignator objects.
 * @{ 
 *  
 * 
	Affine gap penalties are computed using the following
	formula:

	penalty = gop + gap_length * gep

	Thus, the gap opening penalty does not include the penalty for
	the first gap position. 
 */

/** make an @ref Alignator object performing full dynamic programming  
 * 
 * @param alignment_type 	The @ref AlignmentType (global, local, wrapping)
 * @param gop				Gap openening penalty.
 * @param gep				Gap extension penalty.
 * @param penalize_row_left		Penalize gaps on left side of row sequence (global alignment)
 * @param penalize_row_right	Penalize gaps on right side of row sequence (global alignment).
 * @param penalize_col_left		Penalize gaps on left side of col sequence (global alignment)
 * @param penalize_col_right	Penalize gaps on right side of col sequence (global alignment).
 * 
 * @return a new @ref Alignator object.
 * */
HAlignator makeAlignatorDPFull( 
		AlignmentType alignment_type,
		Score gop, Score gep, 
		bool penalize_row_left = false, 
		bool penalize_row_right = false,
		bool penalize_col_left = false, 
		bool penalize_col_right = false );

/** make @ref Alignator object that return pairs of identical residues. 
 * 
 * This alignator object returns a non-linear alignment (dotplot).
 * 
 * @return a new @ref Alignator object.
 */
HAlignator makeAlignatorIdentity();

/** make @ref Alignator object that returns pairs of similar residues 
 * 
 * Similar residues are defined as those that produce a positive
 * alignment score.
 * 
 * This alignator object returns a non-linear alignment (dotplot).
 * 
 * @return a new @ref Alignator object. 
 */
HAlignator makeAlignatorSimilarity();

/** make @ref Alignator object that returns aligned tuples.
 * 
 * Tuples are k-words. Aligned tuples are sequence identical.
 * 
 * This alignator object returns a non-linear alignment (dotplot).
 * 
 * @return a new @ref Alignator object.  
 *  
 */
HAlignator makeAlignatorTuples(int ktuple = 3 );

/** make @ref Alignator object that returns a pre-built alignment.
 * 
 * This object can function as a place-holder for objects
 * that require a helper @ref Alignator object. Instead of re-aligning
 * row and col, this object will simply return a copy of a
 * pre-computed alignment. 
 * 
 * @param ali	alignment to return on calling the align method.
 * 
 * @return a new @ref Alignator object.  
 * 
 */
HAlignator makeAlignatorPrebuilt( const HAlignment & ali );

/** make an @ref Alignator object that does a dot-alignment with wrapping around.
 * @param alignator	@ref Alignator object to build the dot matrix.
 * @param gop gap opening penalty.
 * @param gep gap extension penalty.
 * 
 * @return a new @ref Alignator object.  
 */
HAlignator makeAlignatorDotsWrap(
		const HAlignator & alignator,    		
		Score gop, 
		Score gep );

/** make an @ref Alignator object, which does a dot-alignment with wrapping around.
 * @param alignator	@ref Alignator object to build the dot matrix.
 * @param gop gap opening penalty.
 * @param gep gap extension penalty. 
 */
HAlignator makeAlignatorDots(
		const HAlignator & alignator,
		Score gop, 
		Score gep );

/** make an @ref Alignator object, which does a dot-alignment with wrapping around. */
HAlignator makeAlignatorDotsDiagonal(
		const HAlignator & alignator,     		
		Score gop, 
		Score gep, 
		Score diagnal_gop = 0,
		Score diagonal_gep = 0 );

/** make an @ref Alignator object, which aligns fragments. */
HAlignator makeAlignatorFragments(
		Score gop, 
		Score gep, 
		const HFragmentor & fragmentor );

/** make an @ref Alignator object for iterative alignment
 * 
 * Aligns two Alignandum objects iteratively using a template
 * alignator object until the alignment score drops below min_score. 
 * The template alignator object is copied.
 * 
 * @param alignator @ref Alignator object to perform alignments.
 * @param min_score	Continue until score falls below this threshold.
 */
HAlignator makeAlignatorIterative( 
		const HAlignator & alignator, 
		Score min_score);

/** Alignator object for groupie alignment. 
 * 
 * See @ref ImplAlignatorGroupies for an explanation of the
 * algorithm. 
 * 
 * @param tube_size 		size of the tube in which alignment is performed.
 * @param tuple_size		tuple size. Gaps of this size are filled.
 * @param alignator_dots	@ref Alignator to build dots.
 * @param alignator_gaps	@ref Alignator to use to fill in gaps.
 * @param gop				gap opening penalty.
 * @param gep				gap extension penalty.
 */

HAlignator makeAlignatorGroupies(
		const Position tube_size,
		const Position tuple_size,
		const HAlignator & alignator_dots,
		const HAlignator & alignator_gaps,
		const Score & gop,
		const Score & gep);

/** Alignator object for groupie alignment.
 *
 * See @ref ImplAlignatorGroupies for an explanation of the
 * algorithm. 
 *  
 * This alignator is parameterized as for the pairsdb
 * database.
 */
HAlignator makeAlignatorGroupies();

/**
 * @}
 */



}

#endif	/* HELPERS_ALIGNATOR_H */
