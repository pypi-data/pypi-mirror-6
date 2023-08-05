/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersSubstitutionMatrix.h,v 1.2 2004/01/07 14:35:33 aheger Exp $

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

#ifndef HELPERS_SUBSTITUTION_MATRIX_H
#define HELPERS_SUBSTITUTION_MATRIX_H 1

#include "alignlib_fwd.h"
#include "alignlib_default.h"

namespace alignlib 
{

/**
 * 
 * @defgroup FactorySubstitutionMatrix Factory functions for substitution matrices.
 * @{ 
 */

/** create a @ref SubstitutionMatrix with uniform match and mismatch scores. 
 * 
 * @param alphabet_size		size of the alphabet. The returned substitution matrix is symmetric for this alphabet.
 * @param match				score of a match.
 * @param mismatch			score of a mismatch.
 * 
 * @return a new @ref SubstitutionMatrix
 * */
HSubstitutionMatrix makeSubstitutionMatrix( 
		int alphabet_size,
		const Score match = 1,
		const Score mismatch = -1 );

/** @brief create a substituion matrix from a vector of scores. 
 * 
 * @param scores	vector of substitution scores. The scores are given in row/column order.
 * @param nrows		number of rows in substitution matrix.
 * @param ncols		number of cols in substiutitution matrix.
 * 
 * The size of the vector scores should be nrows * ncols.
 * 
 */
HSubstitutionMatrix makeSubstitutionMatrix( 
		const ScoreVector & scores,
		int nrows, 
		int ncols);

/** The blosum62 scoring matrix
 * 
 * @return a new @ref SubstitutionMatrix.
 */
HSubstitutionMatrix makeSubstitutionMatrixBlosum62();

/** The blosum62 scoring matrix
 * 
 * @param encoder @ref Encoder object to ensure alphabet compatibility.
 * 
 * @return a new @ref SubstitutionMatrix.
 */
HSubstitutionMatrix makeSubstitutionMatrixBlosum62( const HEncoder & encoder);

/** The blosum50 scoring matrix.
 * 
 * @return a new @ref SubstitutionMatrix.
 */
HSubstitutionMatrix makeSubstitutionMatrixBlosum50();

/** The blosum50 scoring matrix.
 * 
 * @param encoder @ref Encoder object to ensure alphabet compatibility.
 * 
 * @return a new @ref SubstitutionMatrix.
 */
HSubstitutionMatrix makeSubstitutionMatrixBlosum50( const HEncoder & encoder);

/** The pam250 scoring matrix.
 * @return a new @ref SubstitutionMatrix.
 */
HSubstitutionMatrix makeSubstitutionMatrixPam250();

/** The pam250 scoring matrix
 * 
 * @param encoder @ref Encoder object to ensure alphabet compatibility.
 * 
 * @return a new @ref SubstitutionMatrix.
 * */
HSubstitutionMatrix makeSubstitutionMatrixPam250( const HEncoder & encoder);    

/** The pam120 scoring matrix.
 * @return a new @ref SubstitutionMatrix.
 */
HSubstitutionMatrix makeSubstitutionMatrixPam120();

/** The pam120 scoring matrix.
 * 
 * @param encoder @ref Encoder object to ensure alphabet compatibility.
 * 
 * @return a new @ref SubstitutionMatrix
 */
HSubstitutionMatrix makeSubstitutionMatrixPam120( const HEncoder & encoder);    

/** The pam30 scoring matrix.
 * @return a new @ref SubstitutionMatrix.
 * */
HSubstitutionMatrix makeSubstitutionMatrixPam30();

/** The pam30 scoring matrix.
 * 
 * @param encoder @ref Encoder object to ensure alphabet compatibility.
 * 
 * @return a new @ref SubstitutionMatrix
 * */
HSubstitutionMatrix makeSubstitutionMatrixPam30( const HEncoder & encoder);

/** The blastn identity scoring matrix.
 *
 * @return a new @ref SubstitutionMatrix.
 * */
HSubstitutionMatrix makeSubstitutionMatrixDNA4();

 /** The blastn identity scoring matrix.
 * 
 * @param encoder @ref Encoder object to ensure alphabet compatibility.
 * 
 * @return a new @ref SubstitutionMatrix
 * */
HSubstitutionMatrix makeSubstitutionMatrixDNA4( const HEncoder & encoder);    

/** A backtranslation substitution matrix
 * 
 * used for aligning a generalized codon sequence.
 * 
 * approximate_match: 	AGCTN <-> W
 * match: 				AG <-> V
 * match: 				CT <-> Y
 * match:				N <-> N
 * all other: mismatch
 * @param encoder @ref Encoder object to ensure alphabet compatibility.
 * 
 * @return a new @ref SubstitutionMatrix
 * */
HSubstitutionMatrix makeSubstitutionMatrixBackTranslation( 
		const Score & match,
		const Score & mismatch,
		const Score & approximate_match,
		const HEncoder & encoder);    

/** return a new matrix read from stream.
 *
 * The format is the output of the 'pam' or 'matblas' programs.
 *  
 * @param input			stream to read from.
 * @param translator	@ref Encoder
 * @exception AlignlibException if matrix in stream is incomplete.
 * @return a new @ref SubstitutionMatrix
 * 
 */
HSubstitutionMatrix loadSubstitutionMatrix(
		std::istream & input,
		const HEncoder & translator );


/** @} */

/** @addtogroup Defaults
 * @{
 */ 

DEFINE_DEFAULT( HSubstitutionMatrix, 
		getDefaultSubstitutionMatrix,
		setDefaultSubstitutionMatrix );

/** @} */

}

#endif	/* HELPERS_SUBSTITUTION_MATRIX_H */



