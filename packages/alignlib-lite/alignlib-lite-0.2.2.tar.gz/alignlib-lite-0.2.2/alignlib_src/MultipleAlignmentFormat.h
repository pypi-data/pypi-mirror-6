#ifndef MULTIPLE_ALIGNMENT_FORMAT_H_
#define MULTIPLE_ALIGNMENT_FORMAT_H_

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

#include "alignlib_fwd.h"

namespace alignlib 
{

/** 
 * 
 * @defgroup MulitpleAlignmentFormats MultipleAlignment formats.
 * @{
 * 
 * MulitpleAlignment formats convert @ref MulitpleAlignment objects into various text based formats and back.
 * Member data is publicly available for easy access in your own formatting functions.
 * 
 * Usage example:
 * @code
 * 
 * @endcode
 */

/** Base class for multiple alignment formats.
 * 
 * 	This is a convenience structure for importing/exporting
 *	multiple alignments.
 * 
 *  This class keeps track of alignment coordinates.
 * 
 *  @author Andreas Heger
 *  @version $Id$
 *  @short Base class for multiple alignment formats. 
 * 
 */
struct MultipleAlignmentFormat
{
	// class member functions
	friend std::ostream & operator<<( std::ostream &, const MultipleAlignmentFormat &);
	friend std::istream & operator>>( std::istream &, MultipleAlignmentFormat &);
		
	// constructors and desctructors
	MultipleAlignmentFormat ();

	MultipleAlignmentFormat( const HMultipleAlignment & src);
	
	MultipleAlignmentFormat( std::istream & src);

	MultipleAlignmentFormat( const std::string & src);

	MultipleAlignmentFormat( const MultipleAlignmentFormat &);

	virtual ~MultipleAlignmentFormat();

	/** fill format from multiple alignment
	 * 
	 *	@param src multiple alignment to parse
	 */
	virtual void fill( const HMultipleAlignment & src);

	/** fill alignment from format
	 * 
	 * 	@param dest Alignment 
	 */
	virtual void copy( HMultipleAlignment & dest ) const;
	
	/** save alignment to stream
	 */
	virtual void save( std::ostream & ) const;
	
	/** load alignment from stream
	 */
	virtual void load( std::istream &);
	
	/** string representation of the mali */
	std::string mRepresentation;
	
};

/**
	Plain multiple alignment format.
	
	The mali is output in rows.
	
   	@author Andreas Heger
   	@version $Id$
   	@short Plain multiple alignment format
 
*/ 
struct MultipleAlignmentFormatPlain : public MultipleAlignmentFormat
{
	// constructors and desctructors
	MultipleAlignmentFormatPlain ();

	MultipleAlignmentFormatPlain( const HMultipleAlignment & src);
	
	MultipleAlignmentFormatPlain( std::istream & src);

	MultipleAlignmentFormatPlain( const std::string & src);
	
	MultipleAlignmentFormatPlain (const MultipleAlignmentFormatPlain &);

	virtual ~MultipleAlignmentFormatPlain ();

	/** fill blocks from alignment
		@param src Alignment to parse
	 */
	virtual void fill( const HMultipleAlignment & src);

	/** fill Alignment object with blocks
	 * 	@param dest Alignment 
	 */
	virtual void copy( HMultipleAlignment & dest ) const;

};

/**
	HTML formatted output. Residues are colored according to a palette
		
   	@author Andreas Heger
   	@version $Id$
   	@short Plain multiple alignment format
 
*/ 
struct MultipleAlignmentFormatHTML : public MultipleAlignmentFormat
{
	// constructors and desctructors
	MultipleAlignmentFormatHTML ();

	MultipleAlignmentFormatHTML( const HMultipleAlignment & src, const HPalette & palette );
	
	MultipleAlignmentFormatHTML( std::istream & src);

	MultipleAlignmentFormatHTML( const std::string & src);
	
	MultipleAlignmentFormatHTML (const MultipleAlignmentFormatHTML &);

	virtual ~MultipleAlignmentFormatHTML ();

	/** fill blocks from alignment
		@param src Alignment to parse
	 */
	virtual void fill( const HMultipleAlignment & src, const HPalette & palette);

	/** fill Alignment object with blocks
	 * 	@param dest Alignment 
	 */
	virtual void copy( HMultipleAlignment & dest ) const;
	
};


/** @} */

}

#endif
