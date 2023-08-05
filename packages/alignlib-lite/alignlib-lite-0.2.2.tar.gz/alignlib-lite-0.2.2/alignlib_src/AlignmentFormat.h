#ifndef ALIGNMENTFORMAT_H_
#define ALIGNMENTFORMAT_H_

//--------------------------------------------------------------------------------
// Project alignlib
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id$
//--------------------------------------------------------------------------------

#if HAVE_CONFIG_H
#include <config.h>
#endif

#include <iosfwd>
#include <string>
#include <limits>

#include "alignlib_fwd.h"

namespace alignlib 
{

/** 
 * 
 * @defgroup AlignmentFormats Alignment formats.
 * @{
 * 
 * Alignment formats convert @ref Alignment objects into various alignment formats and back.
 * Member data is publicly available for easy access in your own formatting functions.
 * 
 * Usage example:
 * @code
 * HAligment ali = makeAlignmentVector();
 * ali->fill(...);
 * 
 * // write blocks
 * AlignmentFormatBlocks blocks_out(ali);
 * 
 * std::cout << ali << std::endl; 
 * // read blocks
 * AlignmentFormatBlocks blocks_in;
 * std::cin >> blocks_in >> std::endl;
 * blocks_in.copy( ali );
 * 
 * @endcode
 */

/** Base class for alignment formats.
 * 
 * 	This is a convenience structure for importing/exporting
 *	pairwise alignments.
 * 
 *  This class keeps track of alignment coordinates.
 * 
 *  @author Andreas Heger
 *  @version $Id$
 *  @short Base class for alignment formats. 
 * 
 */
struct AlignmentFormat
{
	// class member functions
	friend std::ostream & operator<<( std::ostream &, const AlignmentFormat &);
	friend std::istream & operator>>( std::istream &, AlignmentFormat &);
		
	// constructors and desctructors
	AlignmentFormat ();

	AlignmentFormat( const HAlignment & src);
	
	AlignmentFormat( std::istream & src);

	AlignmentFormat( const std::string & src);

	AlignmentFormat( const AlignmentFormat &);

	virtual ~AlignmentFormat();

	/** fill format from alignment
	 * 
	 *	@param src Alignment to parse
	 */
	virtual void fill( const HAlignment & src);

	/** fill alignment from format
	 * 
	 * 	@param dest Alignment 
	 */
	virtual void copy( HAlignment & dest ) const;
	
	/** save alignment to stream
	 */
	virtual void save( std::ostream & ) const;
	
	/** load alignment from stream
	 */
	virtual void load( std::istream &);
	
	/** start of aligned blocks in row*/
	Position mRowFrom;
	
	/** end of aligned blocks
	 */
	Position mRowTo;
	
	/** start of aligned blocks in col 
	 */
	Position mColFrom;
	
	/** end of aligned blocks in col  
	 */
	Position mColTo;
};

/**
	Data structure for aligned blocks alignment format.
	
	This is a convenience structure for importing/exporting
	pairwise alignments.
	
	The aligned blocks format displays gap-less blocks in 
	an alignment. Each block is defined by a start position
	in row, a start position in col and a length.
	
	Coordinates in row and col are stored relative to 
	the alignment coordinates and thus always start
	at 0.

	The printable alignment contains of 7 fields:

	row_start  integer
	row_end    integer
	col_start  integer
	col_end    integer
	row_starts (',' separated list of integers)
	col_starts (',' separated list of integers)
	block_sizes (',' separated list of integers)
	
   	@author Andreas Heger
   	@version $Id$
   	@short Data structure of aligned blocks.
 
*/ 
struct AlignmentFormatBlocks : public AlignmentFormat
{
	// constructors and desctructors
	AlignmentFormatBlocks ();

	AlignmentFormatBlocks( const HAlignment & src);
	
	AlignmentFormatBlocks( std::istream & src);

	AlignmentFormatBlocks( const Position row_start,
			       const Position col_start,
			       const std::string & block_sizes,
			       const std::string & row_starts,
			       const std::string & col_starts );

	AlignmentFormatBlocks( const std::string & src);
	
	AlignmentFormatBlocks (const AlignmentFormatBlocks &);

	virtual ~AlignmentFormatBlocks ();

	/** fill blocks from alignment
		@param src Alignment to parse
	 */
	virtual void fill( const HAlignment & src);

	/** fill Alignment object with blocks
	 * 	@param dest Alignment 
	 */
	virtual void copy( HAlignment & dest ) const;

	/** save alignment to stream
	 */
	virtual void save( std::ostream & ) const;
	
	/** load alignment from stream
	 */
	virtual void load( std::istream &);
	
	/** vector with starts of aligned blocks. 
	 * 
	 * The start positions are relative to the offset in @mRowFrom */
	PositionVector mRowStarts;

	/** vector with ends of aligned blocks.
	 * 
	 * The start positions are relative to the offset in @mColFrom */
	PositionVector mColStarts;
	
	/** vector with block sizes */
	PositionVector mBlockSizes;

	protected:

		/** apply offset to a coordinate */
		virtual Position applyOffset( 
				const Position & pos,
				const Position & offset ) const;	

		/** remove offset from a coordinate */
		virtual Position removeOffset( 
				const Position & pos,
				const Position & offset ) const;	

		
};

/**
	Data structure for blat alignment format.
	
	This format is identical to @ref AlignmentFormatBlocks
	except that the Block start positions are not relative
	to the alignment start, but are absolute.
	
   	@author Andreas Heger
   	@version $Id$
   	@short Data structure of aligned blocks.
 
*/ 
struct AlignmentFormatBlat : public AlignmentFormatBlocks
{
	// constructors and desctructors
	AlignmentFormatBlat ();

	AlignmentFormatBlat( const HAlignment & src);
	
	AlignmentFormatBlat( std::istream & src);

	AlignmentFormatBlat( const std::string & src);
	
	AlignmentFormatBlat (const AlignmentFormatBlat &);

	virtual ~AlignmentFormatBlat ();

	protected:
	
	/** apply offset to a coordinate */
	virtual Position applyOffset( 
			const Position & pos,
			const Position & offset ) const;	

	/** remove offset from a coordinate */
	virtual Position removeOffset( 
			const Position & pos,
			const Position & offset ) const;	

	
};



/**
	Data structure for "Emissions" alignment format.
	
	This is a convenience structure for importing/exporting
	pairwise alignments.
	
	This format stores the alignment in two strings for 
	row and col, respectively. Each string represents
	the emissions (prefixed by +) and insertions 
	(prefixed by -) for the alignment.
	
   	@author Andreas Heger
   	@version $Id$
   	@short Data structure of "Emissions" alignment format.
 
*/ 

struct AlignmentFormatEmissions : public AlignmentFormat
{
	// constructors and desctructors
	AlignmentFormatEmissions ();

	AlignmentFormatEmissions( const HAlignment & src);

	AlignmentFormatEmissions( std::istream & src);

	AlignmentFormatEmissions( const std::string & src);
	
	AlignmentFormatEmissions (const AlignmentFormatEmissions &);

	AlignmentFormatEmissions(
			const Position row_from,
			const std::string & row,
			const Position col_from,
			const std::string & col);

	virtual ~AlignmentFormatEmissions ();

	/** return the number of emissions in an alignment string.
	 * 
	 * @param src Alignment string
	 */
	virtual Position getNumEmissions( const std::string & src );
	
	/** fill blocks from alignment
		@param src Alignment to parse
	 */
	virtual void fill( const HAlignment & src);

	/** fill Alignment object with blocks
	 * 	@param dest Alignment 
	 */
	virtual void copy( HAlignment & dest ) const;
	
	/** save alignment to stream
	 */
	virtual void save( std::ostream & ) const;
	
	/** load alignment from stream
	 */
	virtual void load( std::istream &);

	/** the alignment for row 
	 * 
	 */
	std::string mRowAlignment;

	/** the alignment for col
	 * 
	 */
	std::string mColAlignment;
	
};

/**
	Data structure for "Explicit" alignment format.
	
	This is a convenience structure for importing/exporting
	pairwise alignments.

	This format represents the alignment as two strings
	for row and col, respectively. The alignment is 
	represented as aligned characters.
	
   	@author Andreas Heger
   	@version $Id$
   	@short Data structure of "Explicit" alignment format.
 
*/ 

struct AlignmentFormatExplicit : public AlignmentFormat
{
	// constructors and desctructors
	AlignmentFormatExplicit ();

	AlignmentFormatExplicit( 
			const HAlignment & src,
			const HAlignandum & row,
			const HAlignandum & col);
	
	AlignmentFormatExplicit( std::istream & src);

	/** build formatted alignment from one string.
	 * 
	 * @param src Alignment string
	 * The alignment format is 
	 *    - row_from
	 *    - row_to
	 *    - row_ali
	 *    - col_from
	 *    - col_to
	 *    - col_ali
	 * 
	 * The fields are separated by whitespace characters.
	 */
	AlignmentFormatExplicit( const std::string & src);

	/** build alignment from two aligned strings
	 * 
	 * @param row_from	residue number of first aligned residue in row
	 * @param row       aligned string for row
	 * @param col_from	residue number of first aligned residue in col
	 * @param col		aligned string for col
	 */
	AlignmentFormatExplicit( 
			const Position row_from,
			const std::string & row,
			const Position col_from,
			const std::string & col);
	
	AlignmentFormatExplicit (const AlignmentFormatExplicit &);

	virtual ~AlignmentFormatExplicit ();

	/** fill blocks from alignment
		@param src Alignment to parse
	 */
	virtual void fill( const HAlignment & src,
			const HAlignandum & row,
			const HAlignandum & col);

	/** fill Alignment object with blocks
	 * 	@param dest Alignment 
	 */
	virtual void copy( HAlignment & dest) const;
	
	/** save alignment to stream
	 */
	virtual void save( std::ostream & ) const;
	
	/** load alignment from stream
	 */
	virtual void load( std::istream &);
	
	/** the alignment for row 
	 * 
	 */
	std::string mRowAlignment;

	/** the alignment for col
	 * 
	 */
	std::string mColAlignment;
	
};

/**
	Data structure for "Diagonals" alignment format
	
	This is a convenience structure for importing/exporting
	pairwise alignments.
	
	The diagonals alignment stores the alignment a single
	string. The string records emissions and insertions
	along each digaonal. This alignment format is useful for
	storing dotplots.

    Although any alignment class can be written in this format, 
    it is best to use for those that are sorted by diagonal, for
    example, MatrixDiagonal. This achieves the highest compression.
     	
    The "Diagonals" format is related to the "Emissions" format. Gaps
    are prefixed by '-' and emissions are prefixed by '+'.

    diagonal:-n1+n2-n3+n4;diagonal;...
	     
   	@author Andreas Heger
   	@version $Id$
   	@short Data structure of "Diagonals" alignment format.
 
*/ 

struct AlignmentFormatDiagonals : public AlignmentFormat
{
	// constructors and desctructors
	AlignmentFormatDiagonals ();

	AlignmentFormatDiagonals( const HAlignment & src);
	
	AlignmentFormatDiagonals( std::istream & src);
	
	AlignmentFormatDiagonals( const std::string & src);
	
	AlignmentFormatDiagonals (const AlignmentFormatDiagonals &);

	virtual ~AlignmentFormatDiagonals ();

	/** fill format from alignment

	 	 @param src Alignment to parse
	 	 @param reverse		reverse column and row 
	 	 @param row_from	beginning of segment to use
	     @param row_to	end of segment to use
	     @param col_from	beginning of segment to use
	     @param col_to	end of segment to use
	     @param diagonal_form beginning of tube to use
	     @param diagonal_to end of tube to use

		 The alignment can be restricted to a region specifying the columns. 
		 A further filter can be applied, that only saves a band. 

	     If diagonal_from is larger than diagonal_to, then the whole range is used.
	     
	 */
	
	virtual void fill( 
			const HAlignment & src,
			const bool reverse,
			const Position row_from = NO_POS,
			const Position row_to = NO_POS,
			const Position col_from = NO_POS,
			const Position col_to = NO_POS,
			const Diagonal diagonal_from = std::numeric_limits<Diagonal>::min(), 
			const Diagonal diagonal_to = std::numeric_limits<Diagonal>::max());

	virtual void fill( 
			const HAlignment & src );
	
	/** fill Alignment object from format
		@param dest 	Alignment to fill
		@param reverse 	reverse column and row. 
	 */
	virtual void copy(
			HAlignment & dest,
			const bool reverse) const;	

	virtual void copy( HAlignment & dest ) const;
		
	/** save alignment to stream
	 */
	virtual void save( std::ostream & ) const;
	
	/** load alignment from stream
	 */
	virtual void load( std::istream &);

	/** the alignment 
	 * 
	 */
	std::string mAlignment;
	
};

/** @} */

}

#endif
