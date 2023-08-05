/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersEncoder.cpp,v 1.2 2004/01/07 14:35:33 aheger Exp $

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
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "alignlib_fwd.h"
#include "alignlib_default.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "Encoder.h"
#include "ImplEncoder.h"
#include "HelpersEncoder.h"

namespace alignlib 
{

//-------------------------------------------------------------------------------

const HEncoder makeEncoder( const AlphabetType & alphabet_type )
{
	debug_func_cerr( 5 );
	ImplEncoder * t;
	switch (alphabet_type) 
	{
	case Protein20: 
		t = new ImplEncoder( Protein20, "ACDEFGHIKLMNPQRSTVWY", "-.", "X" ); 
		break;
	case Protein23:
		t = new ImplEncoder( Protein23, "ABCDEFGHIKLMNPQRSTVWXYZ", "-.", "X" );
		break;
	case DNA4: 
		t = new ImplEncoder( DNA4, "ACGT", "-.", "N" );
		break;
	default:
		throw AlignlibException( "unknown alphabet" );
	}
	return HEncoder( t );
}

/** get a built-in translator object 
 * */
const HEncoder getEncoder( const AlphabetType & alphabet_type )
{
	// The static variables are initialized the first time this function is
	// called and then retain their values.
	
	// 20-letter alphabet plus X
	static const HEncoder translator_protein_20(makeEncoder( Protein20)); 

	// encoding table compatible with BLOSUM and PAML matrices
	static const HEncoder translator_protein_23(makeEncoder( Protein23));

	// 4-letter DNA alphabet
	static const HEncoder translator_dna_4(makeEncoder( DNA4));
	
	debug_func_cerr( 5 );
	switch (alphabet_type) 
	{
	case Protein20: 
		return translator_protein_20; break;		
	case Protein23:
		return translator_protein_23; break;
	case DNA4: 
		return translator_dna_4; break;
	}
	throw AlignlibException( "unknown alphabet" );
}


/** load a translator object from stream
 */
const HEncoder loadEncoder( std::istream & input )
{
	// read Alignandum type
	AlphabetType alphabet_type;

	if (input.eof()) 
		throw AlignlibException("HelpersEncoder.cpp: incomplete translator.");

	input.read( (char*)&alphabet_type, sizeof(AlphabetType) );

	if (input.eof()) 
		throw AlignlibException("HelpersEncoder.cpp: incomplete translator - could not read alphabet type.");

	HEncoder result;

	switch (alphabet_type)
	{
	case User : 
	{
		// read user alphabet
		size_t size;
		input.read( (char *)&size, sizeof( size_t ));
		char * alphabet = new char[size];
		input.read( alphabet, sizeof(char) * size);

		input.read( (char *)&size, sizeof( size_t ));
		char * gap_chars = new char[size];
		input.read( gap_chars, sizeof(char) * size);

		input.read( (char *)&size, sizeof( size_t ));
		char * mask_chars = new char[size];
		input.read( mask_chars, sizeof(char) * size);

		if (input.eof())
			throw AlignlibException( "HelpersEncoder.cpp: incomplete translator ");

		result = HEncoder( new ImplEncoder( alphabet_type, alphabet, gap_chars, mask_chars ) );

		delete [] alphabet;
		delete [] gap_chars;
		delete [] mask_chars;

		break;
	}
	case Protein20 :
		result = getEncoder( Protein20 );
		break;
	case Protein23:
		result = getEncoder( Protein23 );
		break;
	case DNA4:
		result = getEncoder( DNA4 );
		break;
	default:
		throw AlignlibException( "HelpersEncoder: unknown object found in stream" );
	}	
	return result;
}	

} // namespace alignlib
