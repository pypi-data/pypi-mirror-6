/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersMultipleAlignment.h,v 1.5 2004/03/19 18:23:40 aheger Exp $

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

#ifndef HELPERS_MULTIPLE_ALIGNMENT_H
#define HELPERS_MULTIPLE_ALIGNMENT_H 1

#include <vector>
#include "alignlib_fwd.h"
#include "MultipleAlignment.h"

namespace alignlib 
{

/**
 * 
 * @defgroup FactoryMultipleAlignment Factory functions for MultipleAlignment objects.
 * @{ 
 */

/** @return a new @ref MultipleAlignment object.
 * 
 * This object renders the rows in the multiple alignment
 * each time the multiple alignment is changed by adding
 * a new row.
 * 
 * @return a new @ref MultipleAlignment object.
 * */
HMultipleAlignment makeMultipleAlignment(); 

/** @return a new @ref MultipleAlignment object.
 * 
 * This object renders the rows in the multiple alignment
 * only when required.
 * 
 * @param compress_unaligned_columns if true, unaligned columns are not output.
 * @param max_insertion_length maximum size for insertions in mali. If -1, all insertions are output.
 * @return a new @ref MultipleAlignment object.
 */ 
HMultipleAlignment makeMultipleAlignmentDots( 
		bool compress_unaligend_columns = true,
		int max_insertion_length = -1);

/** @} */


/** defgroup ToolsetMultipleAlignment Toolset for MultipleAlignment objects.
 * @{
 * 
 */

/** fill multiple alignment ali 
 * 
 * This function fills a multiple alignment from a string of
 * concatenated sequences. The sequences are concatenated without
 * a separator and are all of the same length.
 *
 * @param dest	destination @ref Mulitplealignment object
	@param sequences	string of concatenated sequences.
	@param nsequences	number of sequences in string.
 */
void fillMultipleAlignment( 
		HMultipleAlignment & dst,
		const std::string & sequences,
		int nsequences);

/** copy a multiple alignment.
 * 
 * @param dest	destination @ref Mulitplealignment object.
 * @param src	source @ref Mulitplealignment object.
 * @param first_row	start copying at first row.
 * @param last_row	stop copying in last row.
 */
void copyMultipleAlignment( 
		HMultipleAlignment & dest, 
		const HMultipleAlignment & src,
		unsigned int first_row = 0,
		unsigned int last_row = 0 );
/** @} */

/** calculate conserved residues in a multiple alignment.
 	get Convservation-string for multiple alignment. This returns a string, where 
	each residue is marked, which is conserved at least > cutoff %
	@param mali mali to calculate conservation for
	@param min_frequency minimum frequency of a conserved column
	@returns a string marking conserved positions
	*/        
    std::string calculateConservation( 
    		const HMultipleAlignment & mali, 
    		const Frequency min_frequency);

    /** a vector for storing double values. */
    //typedef std::vector<double> VectorDouble;

/** fill multiple alignment ali from contents of a file */
/*
    HMultipleAlignment fillMultipleAlignment( HMultipleAlignment ali,
					       const char * filename);
 */

/** fill multiple alignment ali from contents of a file, use an Alignatum-object for parsing
 */
/* HMultipleAlignment fillMultipleAlignment( HMultipleAlignment ali, 
					       const char * filename, 
					       const Alignatum * alignatum_template);
 */
/** fill multiple alignment ali from contents of a file, use an Alignatum-object for parsing */
/*
    HMultipleAlignment fillMultipleAlignment( HMultipleAlignment ali, 
					       const char * filename, 
					       const Alignatum * alignatum_template);
 */
/** extract a multiple Alignment object from a stream in FASTA format */
/*
    HMultipleAlignment extractMultipleAlignmentFasta( HMultipleAlignment ali, 
						       std::istream & input );
 */
/** calculate counts in mali categorised. The first row in Matrix is empty, so that
	the numbering is consistent with the numbering of columns in the multiple alignment.
	Only include num_rows rows in the alignment. If num_rows is not set (0), all
	rows are taken.
 */
/*
    CountsMatrix * makeCountsByCategory( const HMultipleAlignment & mali, 
					 const unsigned int * map_residue2category = NULL);
 */
/** make a map from residues to categories. The following order has been suggested by Hannes for
	surface area calculations:
          'K': 1, 'R': 1,
	'D': 2, 'E': 2,
	'H': 3, 'F': 3, 'W':3, 'Y': 3, 'C': 3,
	'N': 4, 'Q': 4, 'S':4, 'T': 4,
	'A': 5, 'I': 5, 'L': 5,'M': 5, 'V': 5,
	'G': 6, 'P': 6
 */
const unsigned int * getMapResidue2CategorySurface();

/** mapping, where each residue is mapped to its own 
	category 
 */
const unsigned int * getMapResidue2CategoryAll();


/** return a vector of entropies calculated for a CountsMatrix
 */
HEntropyVector makeEntropyVector( const WeightedCountMatrix * src);

}

#endif	/* HELPERS_MULTIPLE_ALIGNMENT_H */
