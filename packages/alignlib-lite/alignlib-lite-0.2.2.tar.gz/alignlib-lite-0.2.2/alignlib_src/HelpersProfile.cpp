/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersProfile.cpp,v 1.4 2004/03/19 18:23:40 aheger Exp $

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
#include <iomanip>
#include <stdio.h>
#include <math.h>

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"

#include "Alignandum.h"
#include "MultipleAlignment.h"
#include "Alignment.h"
#include "AlignmentIterator.h"
#include "Encoder.h"
#include "Weightor.h"
#include "LogOddor.h"
#include "Regularizor.h"

#include "HelpersEncoder.h"
#include "HelpersWeightor.h"
#include "HelpersRegularizor.h"
#include "HelpersLogOddor.h"
#include "HelpersMultipleAlignment.h"

#include "HelpersAlignandum.h"

#include "ImplProfile.h"
#include "ImplSequence.h"

using namespace std;

namespace alignlib 
{


//------------------------------------------------------------------------------------------
/** write counts from profile in binary format to stream */
/*
void writeProfileBinaryCounts( std::ostream & output, const HAlignandum src) {

	// first check, that we actually do have a profile here.a
	const ImplProfile * p = dynamic_cast<const ImplProfile*>(src);

	// If not, there is nothing to write 
	if (!p) 
		return;

	const CountColumn * counts = p->getData().mCountsPointer;

	output.write( (char*)&(counts), p->getLength() * ALPHABET_SIZE * sizeof( Count));

}
*/
//------------------------------------------------------------------------------------------
/** write counts from profile in binary format to stream, store as ints with bytes bytes (not supported yet). */
/*
void writeProfileBinaryCountsAsInt( std::ostream & output, const HAlignandum src, int bytes, float scale_factor) {


	// first check, that we actually do have a profile here.
	const ImplProfile * p = dynamic_cast<const ImplProfile*>(src);

	// If not, there is nothing to writea
	if (!p) 
		return;

	const CountColumn * counts = p->getData().mCountsPointer;

	int length = p->getLength();

	int i, j;

	typedef int TYPE_INT_COUNTS_COLUMN[ALPHABET_SIZE];

	// allocate memory for converted profile
	TYPE_INT_COUNTS_COLUMN * int_counts = new TYPE_INT_COUNTS_COLUMN[ length + 1];

	for (i = 1; i <= length; i++)
		for (j = 0; j < ALPHABET_SIZE; j++) 
			int_counts[i][j] = (int)(counts[i][j] * scale_factor);

	output.write( (char*)&(int_counts), length * ALPHABET_SIZE * sizeof( int ));

	delete [] int_counts;

}
*/
//------------------------------------------------------------------------------------------
/** read counts of a profile from stream in binary format stored as integers */
/*
HAlignandum extractProfileBinaryCountsAsInt( std::istream & input, 
		const Position max_length,
		int bytes, 
		float scale_factor,
		const Regularizor * regularizor,
		const LogOddor * logoddor ) {

	if (!regularizor) 
		regularizor = getDefaultRegularizor();

	if (!logoddor)
		logoddor = getDefaultLogOddor();

	TYPE_INT_COUNTS_COLUMN * int_counts = new TYPE_INT_COUNTS_COLUMN[max_length];

	int i,j;
	for (i= 0; i < ALPHABET_SIZE; i++) 
		int_counts[0][i] = 0;

	int col = 0;

	while (col < max_length) {
		if (input.eof() || input.peek() == EOF)
			break;

		input.read( (char*)&(int_counts[col]), ALPHABET_SIZE * sizeof( int ) );
		col++;
	}
	col--;

	ImplProfile * p = new ImplProfile( regularizor, logoddor );

	p->resize(col);
	p->useSegment();
	p->allocateCounts();
	Count * counts = p->mCounts;

	for (i = 0; i < col; i++)
	{
		Count * column[ width * col ];
		for (j = 0; j < width; j++) 
			counts[i][j] = (Count)(int_counts[i][j] / scale_factor);
	}
	
	p->setPrepared(false);

	delete [] int_counts;

	return p;

}
*/

//------------------------------------------------------------------------------------------
/** read counts of a profile from stream in binary format */
/*
HAlignandum extractProfileBinaryCounts( std::istream & input, 
		const Position max_length,
		const Regularizor * regularizor,
		const LogOddor * logoddor ) {

	if (!regularizor)
		regularizor = getDefaultRegularizor();

	if (!logoddor)
		logoddor = getDefaultLogOddor();


	CountColumn * counts = new CountColumn[max_length + 1];
	for (int i= 0; i < ALPHABET_SIZE; i++) 
		counts[0][i] = 0;

	int col = 0;

	while (col < max_length) {
		if (input.eof() || input.peek() == EOF)
			break;

		input.read( (char*)&(counts[col]), ALPHABET_SIZE * sizeof( Count) );
		col++;
	}

	ImplProfile * p = new ImplProfile( regularizor, logoddor );

	p->resize(col);
	p->useSegment();
	p->allocateCounts();

	memcpy( p->mCounts, counts, sizeof( CountColumn) * (col) );

	delete [] counts;

	p->setPrepared(false);

	return p;

}
*/


//------------------------------------------------------------------------------------------
/** rescale counts from a profile by multiplying each entry by the scale_factor */
/*
HAlignandum rescaleProfileCounts( HAlignandum dest,
		double scale_factor ) {

	// type cast to check, if we really have a profile
	ImplProfile * p_source = dynamic_cast<ImplProfile*>(dest);

	Position col, length;
	int i;
	length = p_source->getFullLength();

	for ( col = 0; col < length; col++) 
		for (i = 0; i < ALPHABET_SIZE; i++) 
			p_source->mCounts[col][i] *= scale_factor;

	return dest;

}
*/

//------------------------------------------------------------------------------------------
/** normalize counts from a profile so that all sum to total_weight per column*/
/*
HAlignandum normalizeProfileCounts( HAlignandum dest,
		Count total_weight) {

	// type cast to check, if we really have a profile
	ImplProfile * p_source = dynamic_cast<ImplProfile*>(dest);

	Position col, length;
	int i;

	length = p_source->getFullLength();

	for ( col = 0; col < length; col++) {

		Count ntotal = 0;
		for (i = 0; i < ALPHABET_SIZE; i++) 
			ntotal += p_source->mCounts[col][i];

		if (ntotal > 0) {
			double scale_factor = total_weight / ntotal;
			for (i = 0; i < ALPHABET_SIZE; i++) 
				p_source->mCounts[col][i] *= scale_factor;
		}
	}

	return dest;

}
*/
//------------------------------------------------------------------------------------------
/** substitutes columns in profile dest by columns in profile row using the mapping provided, where dest is in col and source is in row
 */
/*
HAlignandum substituteProfileWithProfile( HAlignandum dest, const HAlignandum source, const HAlignment map_source2dest ) {

	// check, if we do have two profiles
	//!! to be implemented: some sensible warning messages
	const ImplProfile * p_source = dynamic_cast<const ImplProfile*>(source);
	const ImplProfile * p_dest = dynamic_cast<const ImplProfile*>(dest);

	AlignmentConstIterator it(map_source2dest->begin());
	AlignmentConstIterator it_end(map_source2dest->end());

	for (; it != it_end; ++it) {
		Position row = it->mRow;
		Position col = it->mCol;

		for (int i = 0; i < ALPHABET_SIZE; i++) 
			p_dest->mCounts[col][i] = p_source->mCounts[row][i];
	}

	if (dest->isPrepared()) 
		dest->prepare();

	return dest;
}
*/

//------------------------------------------------------------------------------------------
/** reset a profile to a new length. Clear old values.
 */
/*
ProfileFrequencies * exportProfileFrequencies( HAlignandum dest ) {

	// clear profile
	ImplProfile * profile = dynamic_cast<ImplProfile*>(dest);

	Position from = dest->getFrom();
	Position to = dest->getTo();
	Position length = to - from;

	bool was_prepared = false;

	if (!dest->isPrepared()) {
		dest->prepare();
		was_prepared = false;
	}

	ProfileFrequencies * result = new ProfileFrequencies(length);
	unsigned int i = 0;

	(*result)[0].resize( ALPHABET_SIZE, 0);

	for (Position col = from; col < to; ++i, ++col) {
		(*result)[i].resize( ALPHABET_SIZE, 0);
		for (unsigned int row = 0; row < ALPHABET_SIZE; ++row) 
			(*result)[i][row] = profile->mFrequencies[col][row];
	}

	if (!was_prepared) 
		dest->release();

	return result;
}
*/


//------------------------------------------------------------------------------------------
/** fill a profile with counts. The counts matrix has to be length + 1, the first row is
    not used
 */
/*
HAlignandum makeProfile( const CountsMatrix * src) {

  // check if counts are ok
  assert( src->getNumCols() == ALPHABET_SIZE );

  // type cast to check, if we really have a profile
  ImplProfile * p_dest = dynamic_cast<ImplProfile*>(dest);

  // delete old counts and set new length
  p_dest->release();
  p_dest->resize( src->getNumRows() -1 );
  p_dest->allocateCounts();

  // retrieve pointer to member data
  AlignandumDataProfile & data   = (AlignandumDataProfile &)p_dest->getData();
  CountColumn  * profile_counts = data.mCountsPointer;

  // copy counts
  unsigned int row, col;

  for (row = 0; row < src->getNumRows(); row++)
    for (col = 0; col < ALPHABET_SIZE; col++) 
      profile_counts[row][col] = src[row][col];

  return dest;
}

 */

//------------------------------------------------------------------------------------------------------------------------
/*
*/

// TODO: sort out categories and alphabet-size
/*
//------------------------------------------------------------------------------------------------------
CountsMatrix * makeCountsByCategory( 
		const HMultipleAlignment mali, 
		const HEncoder & translator,
		const unsigned int * map_residue2category ) 
		{

	// build profile. Counts are calculated automatically
	assert( false );
	HImplProfile profile = boost::dynamic_pointer_cast<ImplProfile, Alignandum>
		(makeProfile( mali, 
			translator, 
			makeWeightor(),
			makeRegularizor(), 
			makeLogOddor() )); 

	const WeightedCountMatrix * counts = profile->getWeightedCountMatrix();

	Position length = counts->getNumRows();
	Residue width = counts->getNumCols();
	
	// deterimine number of categories
	unsigned int num_categories;

	if (map_residue2category == NULL)
		num_categories = 20;
	else {
		num_categories = 0;
		for (unsigned int i = 0; i < 20; i++) 
			if (num_categories < map_residue2category[i]) 
				num_categories = map_residue2category[i];
	}
	num_categories++;

	// allocate and initialize result structure
	CountsMatrix * result = new CountsMatrix(length, num_categories);

	// go through counts and map counts to classes. Iterate
	// row-wise, so that mapping has to be done only once.
	for (Residue col = 0; col < width; ++col) 
	{

		unsigned int category;
		if (map_residue2category == NULL)
			category = col;
		else
			category = map_residue2category[col];

		for (Position row = 0; row < length; ++row)
			(*result)[col][category] += (unsigned int)counts->getValue( row, col );
	}

	delete profile;

	return result;
}
*/

/** make a map from residues to categories. The following order has been suggested by Hannes for
    surface area calculations:
    'G': 0, 'P': 0
    'K': 1, 'R': 1,
    'D': 2, 'E': 2,
    'H': 3, 'F': 3, 'W':3, 'Y': 3, 'C': 3,
    'N': 4, 'Q': 4, 'S':4, 'T': 4,
    'A': 5, 'I': 5, 'L': 5,'M': 5, 'V': 5,
 */

const unsigned int MapResidue2CategorySurface[20] = { 
		5, 3, 2, 2, 3,     /* A */
		0, 3, 5, 1, 5,     /* G */  
		5, 4, 0, 4, 1,     /* M */
		4, 4, 5, 3, 3,     /* S */
};

const unsigned int MapResidue2CategoryAll[20] = {
		0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 
};

const unsigned int * getMapResidue2CategorySurface() {
	return MapResidue2CategorySurface;
}

const unsigned int * getMapResidue2CategoryAll() {
	return MapResidue2CategoryAll;
}

/** return a vector of entropies calculated for a CountsMatrix
 */
HEntropyVector makeEntropyVector( const WeightedCountMatrix * src) 
{

	unsigned int length      = src->getNumRows();
	unsigned int categories  = src->getNumCols();

	HEntropyVector result(new EntropyVector(length,0));

	for (unsigned int l = 0; l < length; l++) {
		double total = 0;
		for (unsigned int c = 0; c < categories; c++) {
			total += (*src)[l][c];
		}
		double e = 0;
		double counts;
		for (unsigned int c = 0; c < categories; c++) 
		{
			if ( (counts = (*src)[l][c]) > 0) 
			{
				double p = (double)counts / (double)total;
				e -= p * log(p);
			}
		}	
		(*result)[l] = e;
	}

	return result;
}



} // namespace alignlib


