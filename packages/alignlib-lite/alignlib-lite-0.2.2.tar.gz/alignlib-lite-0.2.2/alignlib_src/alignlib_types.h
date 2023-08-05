/*
  alignlib - a library for aligning protein sequences

  $Id: alignlib.h,v 1.5 2005/02/24 11:07:25 aheger Exp $

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

/** Declaration of types */

#ifndef ALIGNLIB_DECLS_H_
#define ALIGNLIB_DECLS_H_

namespace alignlib
{

/* type for the internal representation of residues */
typedef unsigned char Residue;

/* invalid residue */
#define NO_RESIDUE 255

/** type in which calculations are done
 */
typedef double Score;

/** type of a diagonal index. Has to be a signed type, as diagonals can be positive or negative
 */
typedef long Diagonal;

/* type of a dot index, has to be signed, since NODOT is -1 */
typedef long Dot;

/* type of a fragment index, has to be signed, since NOFRAGMENT is -1 */
typedef long Fragment;

/* type of a position in a sequence, negative positions are invalid positions, thus use a signed type. */
typedef int Position;

/* invalid position */
#define NO_POS -1

/* type of sequence weights */
typedef double SequenceWeight;

/** type of counts (positive integer values)
*/
typedef unsigned long Count;

/* type of weighted counts.
 * There is no speed difference between float and double.
 */
typedef double WeightedCount;

/* type of one entry in a frequencies-table */
typedef double Frequency;

/* type of entropy */
typedef double Entropy;

/** alignment types */
enum AlignmentType
{
	ALIGNMENT_LOCAL, ALIGNMENT_WRAP, ALIGNMENT_GLOBAL
};

/** how to map residues
 * STRICT: do not find adjacent residues
 * LEFT: map to left (smaller residue numbers) until a match is found
 * RIGHT: map to right (larger residue numbers) until a match is found
 */
enum SearchType
{
	NO_SEARCH, LEFT, RIGHT
};

enum LinkageType
{
	SINGLE_LINKAGE,           // = single linkage clustering
	COMPLETE_LINKAGE,		  // = complete linkage clustering
	AVERAGE_LINKAGE,          // = UPGMA
	UPGMA,                    // = unweighted pair group method average (UPGMA), see Theodoridis & Koutroumbas, p411
	WPGMA,                    // = weighted pair group method average (WPGMA), as above
	UPGMC,                    // = unweighted pair group method centroid (UPGMC), as above
	WPGMC                     // = weighted pair group method centroid (UPGMC), as above
};

// List of objects that allow saving state information
enum MagicNumberType
{
	MNNoType,
	MNImplAlignandum,
	MNImplSequence,
	MNImplProfile
};

// Known alphabets
enum AlphabetType
{
	User,
	Protein20,
	Protein23,
	DNA4
};

// Profile formats
enum StorageType
{
	Full,
	Sparse
};

// Multiple alignment expansion types
enum ExpansionType
{
	UnalignedIgnore,
	UnalignedSeparate,
	UnalignedStacked
};

/* type of a height of a node in the tree */
typedef double TreeHeight;

/* type of a weight of an edge in the tree */
typedef double TreeWeight;

/* type of a tree node */
typedef unsigned long Node;


struct Coordinate
{
	unsigned long row;
	unsigned long col;
};

typedef double DistanceMatrixValue;

typedef unsigned long DistanceMatrixSize;

/** enum describing the ways that two pairwise alignments can be combined
 *
 *    - RR: row with row
 *    - RC: row with column
 *    - CR: column with row
 *    - CC: column with column
 */
typedef enum { RR, RC, CR, CC } CombinationMode;

/** enum describing aggregates
 *
 */
enum AggregateType
{
	AggMin, AggMax, AggSum, AggMean, AggCount
};

/** enum describing various toolkits
 *
 */
enum ToolkitType
{
	ProteinAlignment,
	DNAAlignment,
	Genomics
};

}

#endif /*ALIGNLIB_DECLS_H_*/
