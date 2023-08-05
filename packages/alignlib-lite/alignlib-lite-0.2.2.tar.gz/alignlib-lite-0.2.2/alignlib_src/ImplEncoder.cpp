/*
  alignlib - a library for aligning protein sequences

  $Id: ImplEncoder.cpp,v 1.4 2004/09/16 16:02:38 aheger Exp $

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


#include <string.h>
#include <iostream>
#include <cstring>
#include <limits>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "ImplEncoder.h"

using namespace std;

namespace alignlib
{

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplEncoder::ImplEncoder () :
	Encoder(),
	mAlphabetType( User ), mAlphabet( ""), mGapChars( "" ), mMaskChars(""),
	mTableSize(0), mEncodingTable(0), mDecodingTable(0), mAlphabetSize( 0 )
	{
	debug_func_cerr( 5 );
	}

//--------------------------------------------------------------------------------------------------------------------------------
ImplEncoder::~ImplEncoder ()
{
	debug_func_cerr( 5 );
	if ( mEncodingTable != NULL )
		delete [] mEncodingTable;

	if ( mDecodingTable != NULL )
		delete [] mDecodingTable;
}

//--------------------------------------------------------------------------------------------------------------------------------
ImplEncoder::ImplEncoder (const ImplEncoder & src ) :
	Encoder(src),
	mAlphabet( src.mAlphabet ),
	mTableSize( src.mTableSize ),
	mEncodingTable( NULL ),
	mDecodingTable( NULL ),
	mAlphabetSize( src.mAlphabetSize )
{
	debug_func_cerr( 5 );

	if (src.mEncodingTable != NULL)
	{
		mEncodingTable = new Residue[ mTableSize ];
		memcpy( mEncodingTable,
				src.mEncodingTable,
				sizeof(char) * mTableSize );
		mDecodingTable = new char[ mTableSize ];
		memcpy( mDecodingTable,
				src.mDecodingTable,
				sizeof(char) * mTableSize );


	}
	mAlphabetType = src.mAlphabetType;
}

//--------------------------------------------------------------------------------------------------------------------------------
ImplEncoder::ImplEncoder ( const AlphabetType & alphabet_type,
								 const std::string & alphabet,
								 const std::string & gap_chars,
								 const std::string & mask_chars ) :
									 mAlphabetType( alphabet_type ),
									 mAlphabet( alphabet ),
									 mGapChars( gap_chars ),
									 mMaskChars( mask_chars ),
									 mEncodingTable( NULL ),
									 mAlphabetSize( 0 )
{

	debug_func_cerr( 5 );

	// assertions to check for empty input
	if (mGapChars.size() == 0)
		throw AlignlibException( "ImplEncoder.cpp: no gap characters specified.");

	if (mMaskChars.size() == 0)
		throw AlignlibException( "ImplEncoder.cpp: no mask characters specified.");

	if (mAlphabet.size() == 0 )
		throw AlignlibException( "ImplEncoder.cpp: alphabet is empty.");

	// build encoding and decoding table
	mTableSize = std::numeric_limits<char>::max();

	mEncodingTable = new Residue[ mTableSize + 1 ];
	mDecodingTable = new char[ mTableSize + 1];

	for ( Residue x = 0; x <= mTableSize; ++x )
	{
		mEncodingTable[x] = mTableSize;
		mDecodingTable[x] = mMaskChars[0];
	}
	 mAlphabetSize = 0;

	for ( Residue x = 0; x < mAlphabet.size() ; ++x)
	{
		mEncodingTable[(unsigned int)toupper(mAlphabet[x])] = mAlphabetSize;
		mEncodingTable[(unsigned int)tolower(mAlphabet[x])] = mAlphabetSize;
		mDecodingTable[mAlphabetSize] = mAlphabet[x];
		++mAlphabetSize;
	}

	Residue mask_code = mAlphabetSize;
	char mask_char = mMaskChars[0];

	// masking characters can appear in the alphabet (to ensure they use a specific index)
	for ( Residue x = 0; x < mMaskChars.size() ; ++x)
	{
		if (mEncodingTable[mMaskChars[x]] == mTableSize )
		{
			mEncodingTable[(unsigned int)toupper(mMaskChars[x])] = mask_code;
			mEncodingTable[(unsigned int)tolower(mMaskChars[x])] = mask_code;
			mDecodingTable[mAlphabetSize] = mask_char;
			++mAlphabetSize;
		}
	}

	// set all unknown characters to the masking character
	for ( Residue x = 0; x <= mTableSize; ++x )
		if (mEncodingTable[x] == mTableSize)
			mEncodingTable[x] = mask_code;

	// map gap characters to maximum index
	for ( Residue x = 0; x < mGapChars.size(); ++x)
		mEncodingTable[(unsigned int)mGapChars[x]] = mTableSize;
	mDecodingTable[mTableSize] = mGapChars[0];

	mGapCode = encode( mGapChars[0] );
	mMaskCode = encode( mMaskChars[0] );
}

//--------------------------------------------------------------------------------------------------------------------------------
IMPLEMENT_CLONE( HEncoder, ImplEncoder );

//--------------------------------------------------------------------------------------------------------------------------------
char ImplEncoder::operator[]( const Residue & residue ) const
{
	return mDecodingTable[residue];
}

//--------------------------------------------------------------------------------------------------------------------------------
Residue ImplEncoder::operator[]( const char & c ) const
{
	return mEncodingTable[(unsigned int)c];
}

//--------------------------------------------------------------------------------------------------------------------------------
char ImplEncoder::decode( const Residue residue) const
{
	return mDecodingTable[residue];
}

//--------------------------------------------------------------------------------------------------------------------------------
Position ImplEncoder::countChars( const std::string & ali ) const
{

	Position nchars = 0;
	for (unsigned int i = 0; i < ali.size(); i++)
		if (encode(ali[i]) != mGapCode)
			++nchars;
	return nchars;
}


//--------------------------------------------------------------------------------------------------------------------------------
std::string ImplEncoder::decode( const ResidueVector & src ) const
{
	debug_func_cerr(5);

	char * result = new char[src.size() + 1];

	int i;
	for (i = 0; i < src.size(); i++)
		result[i] = mDecodingTable[src[i]];

	result[src.size()] = '\0';
	std::string s( result );
	delete [] result;
	return s;
}

//--------------------------------------------------------------------------------------------------------------------------------
Residue ImplEncoder::encode( const char residue) const
{
	return mEncodingTable[(unsigned int)residue];
}

//--------------------------------------------------------------------------------------------------------------------------------
ResidueVector ImplEncoder::encode( const std::string & src ) const
{
	// TODO: this is inefficient, as ResidueVector is copied on return.
	// Solution? use dest as argument.
	ResidueVector result( src.size() );
	for ( int i = 0; i < src.size(); i++)
		result[i] = mEncodingTable[src[i]];

	return result;
}

//--------------------------------------------------------------------------------------------------------------------------------
bool ImplEncoder::isValidChar( const char query ) const
{
	return ( mAlphabet.find( query ) != std::string::npos ||
			mMaskChars.find( query ) != std::string::npos );
}

//--------------------------------------------------------------------------------------------------------------------------------
int ImplEncoder::getAlphabetSize() const
{
	return mAlphabetSize ;
}

//--------------------------------------------------------------------------------------------------------------------------------
std::string ImplEncoder::getAlphabet() const
{
	return mAlphabet;
}

//--------------------------------------------------------------------------------------------------------------------------------
AlphabetType ImplEncoder::getAlphabetType() const
{
	return mAlphabetType;
}

//--------------------------------------------------------------------------------------------------------------------------------
Residue ImplEncoder::getMaskCode() const
{
	return mMaskCode;
}

//--------------------------------------------------------------------------------------------------------------------------------
Residue ImplEncoder::getGapCode() const
{
	return mGapCode;
}

//--------------------------------------------------------------------------------------------------------------------------------
std::string ImplEncoder::getMaskChars() const
{
	return mMaskChars;
}

//--------------------------------------------------------------------------------------------------------------------------------
std::string ImplEncoder::getGapChars() const
{
	return mGapChars;
}

//--------------------------------------------------------------------------------------------------------------------------------
char ImplEncoder::getMaskChar() const
{
	return mMaskChars[0];
}

//--------------------------------------------------------------------------------------------------------------------------------
char ImplEncoder::getGapChar() const
{
	return mGapChars[0];
}

//--------------------------------------------------------------------------------------
void ImplEncoder::write( std::ostream & output ) const
{
	for ( Residue x = 0; x < mAlphabet.size(); ++x )
		output << (int)x << '\t' << mAlphabet[x] << '\t' << (int)encode(mAlphabet[x]) << '\t' << decode(encode(mAlphabet[x]))<< std::endl;

	output << getGapChar() << '\t' << (int)getGapCode() << std::endl;
	output << getMaskChar() << '\t' << (int)getMaskCode() << std::endl;
}

//--------------------------------------------------------------------------------------
void ImplEncoder::save( std::ostream & output ) const
{
	debug_func_cerr( 5 );
	output.write( (char *)&mAlphabetType, sizeof( AlphabetType) );

	if ( mAlphabetType == User )
	{
		output.write( (char *)mAlphabet.size(), sizeof( size_t ) );
		output.write( (char *)mAlphabet.c_str(), mAlphabet.size() * sizeof( char ) );
		output.write( (char *)mGapChars.size(), sizeof( size_t ) );
		output.write( (char *)mGapChars.c_str(), mGapChars.size() * sizeof( char ) );
		output.write( (char *)mMaskChars.size(), sizeof( size_t ) );
		output.write( (char *)mMaskChars.c_str(), mMaskChars.size() * sizeof( char ) );
	}
}

//--------------------------------------------------------------------------------------
// This will map alphabet and mask characters, but not gap characters.
//
HResidueVector ImplEncoder::map( const HEncoder & other ) const
{
	debug_func_cerr( 5 );
	HResidueVector map_other2this( new ResidueVector( other->getAlphabetSize(), getMaskCode()) );

	for ( Residue x = 0; x < other->getAlphabetSize(); ++x)
		(*map_other2this)[x] = encode( other->decode( x ) );

	return map_other2this;
}

/** build a map for a list of characters.
 *
 * All characters than can not be mapped will be mapped to the mask
 * character.
 *
 * @return residue code of each charater in alphabet.
 */
HResidueVector ImplEncoder::getMap( const std::string & alphabet ) const
{
	debug_func_cerr( 5 );

	HResidueVector map_alphabet( new ResidueVector( alphabet.size(), getMaskCode()) );

	for ( Residue x = 0; x < alphabet.size(); ++x)
		(*map_alphabet)[x] = encode( alphabet[x] );

	return map_alphabet;

}



//--------------------------------------------------------------------------------------------------------------------------------

} // namespace alignlib
