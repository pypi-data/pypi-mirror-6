/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersAlignment.h,v 1.3 2004/10/14 23:34:09 aheger Exp $

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

#ifndef HELPERS_ALIGNATA_H
#define HELPERS_ALIGNATA_H 1

#include <iosfwd>
#include <string>
#include <limits>
#include "alignlib_fwd.h"

namespace alignlib
{

/**
 *
 * @defgroup FactoryAlignment Factory functions for Alignment objects.
 * @{
 *
 * @ref Alignment objects differ
 *    - in the way aligned residue pairs are sorted
 *    - in constraints on uniqueness
 *
 * Uniqueness is indicated by r:c where
 *    - 1:1 one row can map to only one column and vice versa.
 *    - 1:n	one row can map to multiple columns
 *    - n:1 one column can map to multiple rows
 *    - n:n any row can map to multiple columns and vice versa.
 */

/** make a @ref Alignment object.
 *
 *    - sort order: by row
 * Degeneracy: n:1
 *
 * This object uses a std::vector container and is fastest for mapping
 * rows to columns at the expense of memory usage.
 *
 * @return a new @ref Alignment object.
 */
HAlignment makeAlignmentVector();

/** make a @ref Alignment object.
 *
 *    - sort order: by row
 * Degeneracy: n:1
 *
 * This object uses a std::set container.
 *
 * @return a new @ref Alignment object.
 */
HAlignment makeAlignmentSet();

/** make a @ref Alignment object.
 *
 *    - sort order: by column
 * Degeneracy: n:1
 *
 * This object uses a std::set container.
 *
 * @return a new @ref Alignment object.
 */
HAlignment makeAlignmentSetCol();

/** make a @ref Alignment object.
 *
 *    - sort order: by row, then column
 * Degeneracy: 1:1
 *
 * This object uses a std::set container.
 *
 * @return a new @ref Alignment object.
 */
HAlignment makeAlignmentHash();

/** make a @ref Alignment object.
 *
 *    - sort order: by diagonal.
 * Degeneracy: 1:1
 *
 * This object uses a std::set container.
 *
 * @return a new @ref Alignment object.
 */
HAlignment makeAlignmentHashDiagonal();

/** make a @ref Alignment object.
 *
 *    - sort order: by row, then col.
 * Degeneracy: n:n
 *
 * This object uses an indexed list of residue pairs.
 *
 * @return a new @ref Alignment object.
 */
HAlignment makeAlignmentMatrixRow();

/** make a @ref Alignment object.
 *
 *    - sort order: by row, then col.
 * Degeneracy: n:n
 *
 * This object uses an indexed list of residue pairs.
 *
 * @return a new @ref Alignment object.
 */
HAlignment makeAlignmentMatrixUnsorted();

/** make a @ref Alignment object.
 *
 *    - sort order: undefined
 *    - degeneracy: n:n
 *
 * This object uses an indexed list of residue pairs.
 *
 * @return a new @ref Alignment object.
 */
HAlignment makeAlignmentMatrixDiagonal();

/** make a @ref Alignment object.
 *
 *    - sort order: by row.
 * Degeneracy: n:1
 *
 * This object stores the alignment in a compressed form
 * without alignment scores. Suitable for large (genomic)
 * alignments.
 *
 * @return a new @ref Alignment object.
 */
HAlignment makeAlignmentBlocks();

/**
 * @}
 */

/**
 *
 * @defgroup ToolsAlignatum Toolset for Alignment objects.
 * @{
 *
 */


/** check if two alignments are identical
 *
 * This function iterates over both alignments and checks if the
 * the same coordinates are returned. Thus, alignments that are
 * sorted differently are not identical.
 *
 * @param a @ref Alignment object.
 * @param b @ref Alignment object.
 * @param invert	check row in a is col in b and vice versa.
 * @return true, if both alignments are identica.
 */
bool checkAlignmentIdentity(
		const HAlignment & a,
		const HAlignment & b,
		const bool invert = false );

/** return the number of pairs in
 *
 * This function iterates over both alignments and checks if the
 * the same coordinates are returned. Thus, alignments that are
 * sorted differently are not identical.
 *
 * @param a @ref Alignment object.
 * @param b @ref Alignment object.
 * @param mode Combination mode, see @ref combineAlignment.
 * @return return the number of identical pairs in the two alignments
 */
Position getAlignmentIdentity(
			const HAlignment & a,
			const HAlignment & b,
			const CombinationMode & mode );

/** check if two @Alignment objects overlap
 *
 * This function checks if two alignments overlap
 * by at least @param min_overlap residues.
 *
 * The two aligments must be sorted according to the parameter @param mode.
 *
 * @param src1 @ref Alignment object with input.
 * @param src2 @ref Alignment object with input.
 * @param mode Combination mode, see @ref combineAlignment.
 * @param min_overlap minimum number of overlapping residues.
 * @return returns true if the two alignments overlap.
 */
bool hasAlignmentOverlap(
		const HAlignment & src1,
		const HAlignment & src2,
		const CombinationMode mode,
		int min_overlap = 1);

/** return number of shared resides between two @Alignment objects
 *
 * The two aligments must be sorted according to the parameter @param mode.
 *
 * @param src1 @ref Alignment object with input.
 * @param src2 @ref Alignment object with input.
 * @param mode Combination mode, see @ref combineAlignment.
 * @return returns the number of overlapping residues.
 */
Position getAlignmentOverlap(
			const HAlignment & src1,
			const HAlignment & src2,
			const CombinationMode mode );

/** return shortest distance between two @Alignment objects
 *
 * This function returns the shortes distance between two @Aligment objects.
 *
 * The distance of overlapping alignments is 0; the distance of
 * adjacent aligments is 1, and so on.
 *
 * The function works also for interleaved alignments.
 *
 * The two aligments must be sorted according to the parameter @param mode.
 *
 * @param src1 @ref Alignment object with input.
 * @param src2 @ref Alignment object with input.
 * @param mode Combination mode, see @ref combineAlignment.
 * @return the shortest distance between any two residues in the two alignments.
 */
Position getAlignmentShortestDistance(
			const HAlignment & src1,
			const HAlignment & src2,
			const CombinationMode mode );

/** combine two @Alignment objects.
 *
 * This function merges two alignments by joining them
 * via row/row, row/column, column/row or column/column.
 * This is useful for mapping a whole alignment.
 * For example,
 *
 * @code
 * combineAlignment( map_a2c, map_a2b, map_b2c, CR )
 * @endcode
 *
 * will fill map_a2c from map_a2b and map_b2c.
 *
 * @param dest @ref Alignment object with the result.
 * @param src1 @ref Alignment object with input.
 * @param src2 @ref Alignment object with input.
 * @param mode Combination mode.
 */
void combineAlignment(
		HAlignment & dest,
		const HAlignment & src1,
		const HAlignment & src2,
		const CombinationMode mode);

/** @brief copy one alignment into another.

	This function will copy src into dest.

	Only alignment pairs outside a region specified
	by row, column or diagonal coordinates will
	be copied.

	@param dest	destionatn @ref Alignment object
	@param src  source @ref Alignment object
     @param row_from	beginning of segment to use
     @param row_to	end of segment to use
     @param col_from	beginning of segment to use
     @param col_to	end of segment to use
     @param diagonal_form beginning of tube to use
     @param diagonal_to end of tube to use
 */
void copyAlignment(
		HAlignment & dest,
		const HAlignment & src,
		Position row_from = NO_POS,
		Position row_to = NO_POS,
		Position col_from = NO_POS,
		Position col_to = NO_POS,
		Diagonal diagonal_from = std::numeric_limits<Diagonal>::min(),
		Diagonal diagonal_to   = std::numeric_limits<Diagonal>::max()
);

/** @brief copy one alignment into another.

	This function will copy src into dest.

	Only alignment pairs outside a region specified
	by row, column or diagonal coordinates will
	be copied.

	@param dest	destionatn @ref Alignment object
	@param src  source @ref Alignment object
    @param row_from	beginning of segment to use
     @param row_to	end of segment to use
     @param col_from	beginning of segment to use
     @param col_to	end of segment to use
     @param diagonal_form beginning of tube to use
     @param diagonal_to end of tube to use
 */
void copyAlignmentWithoutRegion(
		HAlignment & dest,
		const HAlignment & src,
		Position row_from = NO_POS,
		Position row_to = NO_POS,
		Position col_from = NO_POS,
		Position col_to = NO_POS,
		Diagonal diagonal_from = 1,
		Diagonal diagonal_to = 0
);

/** @brief copy one alignment into another.

	This function will copy src into dest.

	Only alignment pairs that are part of filter
	will be copied.

	@param dest	destination @ref Alignment object
	@param src  source @ref Alignment object
	@param filter @ref Alignment object acting as filter.
	@param mode	determines how pairs a matched between src and filter.

*/
void copyAlignment( HAlignment & dest,
		const HAlignment & src,
		const HAlignment & filter,
		const CombinationMode mode);

/** @brief add Alignment to another.
 *
	@param dest	destination @ref Alignment object
	@param src  source @ref Alignment object
 *
 */
void addAlignment2Alignment( HAlignment & dest, const HAlignment & src );

/** @brief add Alignment to another with mapping.
 *
	@param dest	destination @ref Alignment object
	@param src  source @ref Alignment object
	@param map_src2new	map of src.
	@param mode	determines if row/col are mapped.
 */
void addMappedAlignment2Alignment( HAlignment & dest,
		const HAlignment & src,
		const HAlignment & map_src2new,
		const CombinationMode mode );

/** @brief add Alignment to another with mapping.
 *
	@param dest	destination @ref Alignment object
	@param src  source @ref Alignment object
	@param map_src_row2dest_row	map of row in src.
	@param map_src_col2dest_col map of col in src.
 */
void addMappedAlignments2Alignment( HAlignment & dest,
		const HAlignment & src,
		const HAlignment & map_src_row2dest_row,
		const HAlignment & map_src_col2dest_col );


/** add a diagonal to an alignment.
 *
 * @param dest @ref 	Alignment object
 * @param row_from	  	row start
 * @param row_to	  	row end
 * @param col_offset	column offset.
 * */
void addDiagonal2Alignment(
		HAlignment & dest,
		Position row_from,
		Position row_to,
		Position col_offset = 0);

/** fill gaps in an alignment.
 *
 * If there is a gap of the same length in both row and
    col, the corresponding residues are added to the alignment.

    Only gaps of maximum size max_length are filled.

 * @param dest @ref Alignment object.
   @param max_length maximal gap size to fill.

 */
void fillAlignmentGaps(
		HAlignment & dest,
		const Position max_length );

/** fill gaps in an alignment by alignment within gaps.
 *
 * @param dest 		@ref Alignment object.
 * @param alignator @ref Alignator object to do the alignment.
 * @param row	    @ref Alignandum object to align.
 * @param col 		@ref Alignandum object to align.
 */
void fillAlignmentGaps(
		HAlignment & dest,
		const HAlignator & alignator,
		const HAlignandum & row,
		const HAlignandum & col );

/** remove residues from an alignment that are part of another alignment.
 *
 * @param dest 		@ref Alignment object.
 * @param filter 	@ref Alignment that acts as filter.
   @param mode	 	specifies residue lookup. If mode = RR, then every pair is eliminated from dest,
     				where the row is also present as a row-residue in filter.
 */
void filterAlignmentRemovePairs( HAlignment & dest,
		const HAlignment & filter,
		const CombinationMode mode );

/** remove residues from an alignment that are part of another alignment.
 *
 * @param dest 		@ref Alignment object.
 * @param filter 	@ref Alignment that acts as filter.
   @param mode	 	specifies residue lookup. If mode = RR, then every pair is eliminated from dest,
     				where the row is also present as a row-residue in filter.

 */
void filterAlignmentRemovePairwiseSorted(
		HAlignment & dest,
		const HAlignment & filter,
		const CombinationMode mode );

/** rescore all pairs in an alignment.
 *
 * The score of a pair is set by querying a @ref scorer object.
 *
 * @param dest @ref Alignment object.
 * @param row  @ref Alignandum object.
 * @param col  @ref Alignandum object.
 * @param scorer @ref Scorer object.
 */
void rescoreAlignment(
		HAlignment & dest,
		const HAlignandum & row,
		const HAlignandum & col,
		const HScorer & scorer );

/** rescore residues in an alignment.
 *
 * All residue pairs are set to the same score.
 *
 * @param dest @ref Alignment object.
 * @param score pair score.
 */
void rescoreAlignment(
		HAlignment & dest,
		const Score score = 0);

/** calculate affine alignment score.
 *
 * This function uses the residue pair scores
 * and affine gap penalties to calculate an
 * alignment score. The score is set in dest.
 *
 * @param dest @ref Alignment object.
 * @param gop gap opening penalty.
 * @param gep gap elongation penalty.
 */
void calculateAffineScore( HAlignment & dest,
		const Score gop,
		const Score gep );


/** fill an alignment with a repeat unit from a wrap-around alignment */
void fillAlignmentRepeatUnit(
		HAlignment & dest,
		const HAlignment & source,
		const Position first_row_residue = NO_POS,
		const bool skip_negative_ends = false);

/** @brief expand one alignment to two interleaved alignments.

  	This function is useful for building multiple alignemnts.

    For example: With two sequences of length 10 and alignment src between them:

	<pre>
    src = 3 4 | 4 5 | 5 7 | 9 9
	</pre>
    the result would be:

	<pre>
    A: insert_gaps_row = true, insert_gaps_col = true, use_end_row = true, use_end_col = true
    dest1 = 1 1 | 2 2 |     |     |     | 3 6 | 4 7 |     | 5 9 | 6 10 | 7 11 | 8 12 |      | 9 14 | 10 15 |       |
    dest2 =     |     | 1 3 | 2 4 | 3 5 | 4 6 | 5 7 | 6 8 | 7 9 |      |      |      | 8 13 | 9 14 |       | 10 16 |

    B: insert_gaps_row = false, insert_gaps_col = true, use_end_row = true, use_end_col = false
    dest1 = 1 1 | 2 2 | 3 3 | 4 4 | 5 5 | 6  6 | 7  7 | 8  8 | 9  9 | 10 10 |
    dest2 =     |     | 4 3 | 5 4 | 7 5 |      |      |      | 9  9 |

    C: insert_gaps_row = false, insert_gaps_col = true, use_end_row = false, use_end_col = false
    dest1 = 3 1 | 4 2 | 5 3 | 6  4 | 7  5 | 8  6 | 9  7 |
    dest2 = 4 1 | 5 2 | 7 3 |      |      |      | 9  7 |

    D: insert_gaps_row = false, insert_gaps_col = false, use_end_row = false, use_end_col = false
    dest1 = 3 1 | 4 2 | 5 3 | 9  4 |
    dest2 = 4 1 | 5 2 | 7 3 | 9  4 |

    E: insert_gaps_row = true, insert_gaps_col = true, use_end_row = false, use_end_col = false
    dest1 = 3 1 | 4 2 |     | 5 4 | 6  5 | 7  6 | 8  7 |     | 9 9 |
    dest2 = 4 1 | 5 2 | 6 3 | 7 4 |      |      |      | 8 8 | 9 9 |
	</pre>

    A is used for building multiple alignments, where no part of the sequences are missing.

    B is used for building multiple alignments of a representative with related sequences
    stacked on top of it. No gaps will be inserted into the representative, i.e. the
    multiple alignment will have a constant number of columns.

    E can be used for displaying pairwise alignments.

    Note:

    If there is a gap in both sequences, the residues in the first alignment dest1 are
    aligned to the right of the gap, while the residues in the second alignment dest2
    are aligned to the right.

    @param	map_row2combined  @ref Alignment object containing the result.
    @param	map_col2combined  @ref Alignment object containing the result.
    @param  src @ref Alignment object containing the input.
    @param	insert_gaps_row	if true, insert gaps in row
    @param	insert_gaps_col if true, insert gaps in col
    @param	use_end_row if true, use overhanging ends in row.
    @param	use_end_col if true, use overhanging ends in col
    @param	row_length  total length of row
    @param	col_length  total length of col
 */

void expandAlignment(
		HAlignment & map_row2combined,
		HAlignment & map_col2combined,
		const HAlignment & src,
		const bool insert_gaps_row = true,
		const bool insert_gaps_col = true,
		const bool use_end_row = false,
		const bool use_end_col = false,
		const Position row_length = NO_POS,
		const Position col_length = NO_POS);


/** @brief remove all those residues from an alignmnent that are not in sequential order.

   This function ensures, that col_i < col_i+1 and row < row_i+1

 * @param dest @ref Alignment object.

 */
void flattenAlignment( HAlignment & dest );

/** @brief split an alignment at gaps.
 *
 * This function splits an alignment into fragments at gaps larger
 * than a threshold.
 *
 * @param src @ref Alignment to split.
 * @param max_gap_width maximum gap size.
 * @param split_row	if true, split at gaps in row.
 * @param split_col if true, split at gaps in col.
 *
 * @return a @ref FragmentVector.
 */
HFragmentVector splitAlignment(
		const HAlignment & src,
		const int max_gap_width,
		bool split_row = true,
		bool split_col = true);

/** split an alignment at points of intersection with another alignment.
 */
HFragmentVector splitAlignment(
		const HAlignment & src1,
		const HAlignment & src2,
		const CombinationMode mode );

/** remove low-scoring ends from an alignment.
 *
 *
 * Starting from the ends of an alignment, remove
   residues which do not contribute to a positive score.
   Gaps are treated with affined gap penalties.

 * @param src @ref Alignment object.
   @param gop gap opening penalty.
   @param gep gap extension penalty.

 */
void pruneAlignment(
		HAlignment & src,
		const Score gop,
		const Score gep);

/** @brief calculate percent similarity of an alignment.
 *
 * The percent similarity is defined as the number
 * of aligned residue pairs with positive score divided
 * by the total number of aligned residue pairs.
 *
 * @param src @ref Alignment object.
 *
 * return the percent similarity.
 * */
double calculatePercentSimilarity(
		const HAlignment & src);

/** @brief calculate percent identity of an alignment.
 *
 * The percent similarity is defined as the number
 * of identical residue pairs divided by the total number
 * of aligned residue pairs.
 *
 * @param src @ref Alignment object.
 * @param row @ref Alignandum object.
 * @param col @ref Alignandum object.
 *
 * @return an alignment score.
 */
double calculatePercentIdentity (
		const HAlignment & src,
		const HAlignandum & row,
		const HAlignandum & col);

/** @brief remove small fragments from alignment.
 *
 * This function removes fragments from an alignment. A fragment
 * is a part of an alignment that is short (fragment_length)
 * and surrounded by large gaps (min_gap_length).
 *
 * For example,
 * @code
 * removeFragments( dest, 1, 3 )
 * @endcode
 * will remove all residue pairs surrounded by at least 3 gaps on either side.
 *
 * @param dest @ref Alignment object.
 * @param fragment_length	maximum number of residues to be deleted if surrounded by gaps.
 * @param min_gap_length	minimum number of gaps on each side for a fragment to be deleted.
 * @param row_length	total size of row (to calculate gaps at C-terminus).
 */
void removeFragments(
		HAlignment & dest,
		const unsigned int fragment_length,
		const unsigned int min_gap_length,
		const Position row_length = NO_POS);

}

/**
 * @}
 */

#endif	/* HELPERS_ALIGNATA_H */






