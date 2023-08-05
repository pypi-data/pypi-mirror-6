//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: MultipleAlignmentFormat.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------    


#include <iostream>
#include <iomanip>
#include <iterator>
#include <cstring>
#include <string>
#include <sstream>

#include "alignlib_types.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "MultipleAlignmentFormat.h"
#include "HelpersMultipleAlignment.h"

using namespace std;

namespace alignlib 
{

//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
MultipleAlignmentFormat::MultipleAlignmentFormat() : mRepresentation("")
{
}

MultipleAlignmentFormat::MultipleAlignmentFormat( const MultipleAlignmentFormat & src) :
	mRepresentation(src.mRepresentation)
{
}

MultipleAlignmentFormat::MultipleAlignmentFormat( std::istream & input ) 
{
	load( input );
}

MultipleAlignmentFormat::MultipleAlignmentFormat( const std::string & src) 
{
	std::istringstream i(src.c_str());
	load( i );
}

MultipleAlignmentFormat::MultipleAlignmentFormat( const HMultipleAlignment & src) 
{
	fill( src );
}

MultipleAlignmentFormat::~MultipleAlignmentFormat()
{
}

void MultipleAlignmentFormat::fill( const HMultipleAlignment & src )
{
	debug_func_cerr( 5 );
}

void MultipleAlignmentFormat::copy( HMultipleAlignment & dest ) const
{
	debug_func_cerr( 5 );
	dest->clear();
}

void MultipleAlignmentFormat::load( std::istream & input)
{
	debug_func_cerr( 5 );
	input >> mRepresentation;
}

void MultipleAlignmentFormat::save( std::ostream & output) const
{
	debug_func_cerr( 5 );
	output << mRepresentation;
}

//--------------------------------------------------------------------------------------------------------------------------------
std::ostream & operator<< (std::ostream & output, const MultipleAlignmentFormat & src)
{
	src.save( output );
	return output;
}

//--------------------------------------------------------------------------------------------------------------------------------
std::istream & operator>> (std::istream & input, MultipleAlignmentFormat & dest) 
{
	dest.load( input );
	return input;
}

//--------------------------------------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------------------------------------
MultipleAlignmentFormatPlain::MultipleAlignmentFormatPlain() 
: MultipleAlignmentFormat()
{
}

MultipleAlignmentFormatPlain::MultipleAlignmentFormatPlain( std::istream & input ) 
: MultipleAlignmentFormat()
{
	load( input );
}

MultipleAlignmentFormatPlain::MultipleAlignmentFormatPlain( const std::string & src) 
: MultipleAlignmentFormat()
	{
	std::istringstream i(src.c_str());
	load( i );
	}

MultipleAlignmentFormatPlain::MultipleAlignmentFormatPlain( const HMultipleAlignment & src) 
: MultipleAlignmentFormat()
{
	fill( src );
}


MultipleAlignmentFormatPlain::~MultipleAlignmentFormatPlain () 
{
}

MultipleAlignmentFormatPlain::MultipleAlignmentFormatPlain (const MultipleAlignmentFormatPlain & src ) 
: MultipleAlignmentFormat( src )
{
}

void MultipleAlignmentFormatPlain::fill( const HMultipleAlignment & src)
{
	debug_func_cerr(5);

	MultipleAlignmentFormat::fill( src );
 	for (int x = 0; x < src->getNumSequences(); ++x)
	{
		mRepresentation += src->getRow(x)->getString() + '\n'; 
	}
	
}

//--------------------------------------------------------------------------------------------------------------------------------
void MultipleAlignmentFormatPlain::copy( HMultipleAlignment & dest ) const 
{
	debug_func_cerr(5);

	MultipleAlignmentFormat::copy( dest );
	assert( false );
}

//--------------------------------------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------------------------------------
MultipleAlignmentFormatHTML::MultipleAlignmentFormatHTML() 
: MultipleAlignmentFormat()
{
}

MultipleAlignmentFormatHTML::MultipleAlignmentFormatHTML( std::istream & input ) 
: MultipleAlignmentFormat()
{
	load( input );
}

MultipleAlignmentFormatHTML::MultipleAlignmentFormatHTML( const std::string & src) 
: MultipleAlignmentFormat()
	{
	std::istringstream i(src.c_str());
	load( i );
	}

MultipleAlignmentFormatHTML::MultipleAlignmentFormatHTML( 
		const HMultipleAlignment & src, 
		const HPalette & palette ) 
: MultipleAlignmentFormat()
{
	fill( src, palette );
}


MultipleAlignmentFormatHTML::~MultipleAlignmentFormatHTML () 
{
}

MultipleAlignmentFormatHTML::MultipleAlignmentFormatHTML (const MultipleAlignmentFormatHTML & src ) 
: MultipleAlignmentFormat( src )
{
}

void MultipleAlignmentFormatHTML::fill( 
		const HMultipleAlignment & src,
		const HPalette & palette )
{
	// TODO: speed up with streams or raw C char buffers
	debug_func_cerr(5);

	MultipleAlignmentFormat::fill( src );

	std::string consensus = calculateConservation( src, 0.5 );
	
	debug_cerr( 5, "consensus is " << consensus );
	
	for (int x = 0; x < src->getNumSequences(); ++x)
	{
		std::string row = src->getRow(x)->getString(); 
		unsigned char last_color = 0;
		mRepresentation += "<FONT COLOR=\"" + (*palette)[last_color] + "\">";
		
		assert( consensus.size() == row.size() );
		
		for (int i = 0; i < row.size(); ++i) 
		{
			
			// map character to code
			unsigned char this_char = row[i];			
			unsigned char color_char = 0;

			// color by consensus
			if (consensus[i] == this_char &&
					palette->find(this_char) != palette->end())
			{
				color_char = this_char;
			}

			if (last_color != color_char) 
			{
				mRepresentation += "</FONT><FONT COLOR=\"" + (*palette)[color_char] + "\">";
				last_color = color_char;
			}
			mRepresentation += this_char;
		}
		mRepresentation += "</FONT>\n";		  			
	}
	
}

//--------------------------------------------------------------------------------------------------------------------------------
void MultipleAlignmentFormatHTML::copy( HMultipleAlignment & dest ) const 
{
	debug_func_cerr(5);

	MultipleAlignmentFormat::copy( dest );
	assert( false );
}





} // namespace alignlib
