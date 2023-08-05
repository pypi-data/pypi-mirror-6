/*
  alignlib - a library for aligning protein sequences

  $Id: ImplSequence.cpp,v 1.2 2004/01/07 14:35:36 aheger Exp $

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
#include <fstream>
#include <string>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"

#include "HelpersAlignandum.h"
#include "ImplSequence.h"
#include "AlignlibException.h"
#include "Encoder.h"
#include "HelpersEncoder.h"

using namespace std;

namespace alignlib
{

//---------------------------------< implementation of factory functions >--------------

//----------------------------------------------------------------------------------
/** create a sequence from a NULL-terminated string */
HAlignandum makeSequence( const char * sequence )
{
	return makeSequence( std::string(sequence) );
}

//----------------------------------------------------------------------------------
/** create a sequence from a string */
HAlignandum makeSequence( const std::string & sequence )
{
	return HAlignandum( new ImplSequence( sequence ) );
}


//--------------------------------------------------------------------------------------
ImplSequence::ImplSequence() :
	ImplAlignandum(),
	mSequence()
{
}

//--------------------------------------------------------------------------------------
ImplSequence::ImplSequence( const std::string & src ) :
	ImplAlignandum(),
	mSequence()
	{
	Position length = src.size();

	resize( length );

	const HEncoder & encoder(getToolkit()->getEncoder());

	for (int i = 0; i < length; ++i)
		mSequence[i] = encoder->encode( src[i] );

	setPrepared(true );
	}

//--------------------------------------------------------------------------------------
ImplSequence::ImplSequence( const ImplSequence & src ) :
	ImplAlignandum( src ), mSequence(src.mSequence)
{
	debug_func_cerr(5);
}


//--------------------------------------------------------------------------------------
ImplSequence::~ImplSequence()
{
	debug_func_cerr(5);
}

//--------------------------------------------------------------------------------------
void ImplSequence::resize( Position length )
{
	ImplAlignandum::resize(length);

	mSequence = ResidueVector( length, getToolkit()->getEncoder()->getGapCode() );
}

IMPLEMENT_CLONE( HAlignandum, ImplSequence );

//--------------------------------------------------------------------------------------
Residue ImplSequence::asResidue(Position n) const
{
	return mSequence[n];
}

//--------------------------------------------------------------------------------------
void ImplSequence::prepare() const
{
}

//--------------------------------------------------------------------------------------
void ImplSequence::release() const
{
}

//--------------------------------------------------------------------------------------
void ImplSequence::mask( const Position & x)
{
	mSequence[ x ] = getToolkit()->getEncoder()->getMaskCode();
	ImplAlignandum::mask( x );
}

//--------------------------------------------------------------------------------------
const ResidueVector * ImplSequence::getSequence() const
{
	return &mSequence;
}

//--------------------------------------------------------------------------------------
void ImplSequence::swap( const Position & x, const Position & y )
{
	assert( x >= 0);
	assert( x < getFullLength() );
	assert( y >= 0);
	assert( y < getFullLength() );
	std::swap( mSequence[x], mSequence[y] );
}

//--------------------------------------------------------------------------------------
void ImplSequence::write( std::ostream & output ) const
{
	output << getToolkit()->getEncoder()->decode( mSequence );
}

//--------------------------------------------------------------------------------------
void ImplSequence::__save( std::ostream & output, MagicNumberType type ) const
{
	debug_func_cerr( 5 );

	if (type == MNNoType )
	{
		type = MNImplSequence;
		output.write( (char*)&type, sizeof(MagicNumberType ) );
	}

	ImplAlignandum::__save( output, type );

	for ( Position x = 0; x < getFullLength(); ++ x)
		output.write( (char*)&mSequence[x], sizeof(Residue) );
}

//--------------------------------------------------------------------------------------
void ImplSequence::load( std::istream & input)
{
	debug_func_cerr( 5 );

	ImplAlignandum::load( input );

	mSequence.resize( getFullLength() );

	for ( Position x = 0; x < getFullLength(); ++ x)
		input.read( (char*)&mSequence[x], sizeof(Residue) );

	if (input.fail())
		throw AlignlibException( "incomplete sequence in stream.");

}



} // namespace alignlib
