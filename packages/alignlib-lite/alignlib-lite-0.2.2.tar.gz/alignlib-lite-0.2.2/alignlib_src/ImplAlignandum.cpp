/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignandum.cpp,v 1.2 2004/01/07 14:35:33 aheger Exp $

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
#include <cassert>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "ImplAlignandum.h"
#include "Encoder.h"
#include "HelpersEncoder.h"
#include "HelpersToolkit.h"

using namespace std;

namespace alignlib
{

//--------------------------------------------------------------------------------------
ImplAlignandum::ImplAlignandum() :
	mFrom(NO_POS),
	mTo(NO_POS),
	mLength(0),
	mIsPrepared(false),
	mStorageType(Full)
	{
	}

ImplAlignandum::ImplAlignandum( const HEncoder & translator ) :
	mFrom(NO_POS), mTo(NO_POS), mLength(0),
	mIsPrepared(false),
	mStorageType(Full)
{
}

//--------------------------------------------------------------------------------------
ImplAlignandum::~ImplAlignandum ()
{
	debug_func_cerr(5);
}

//--------------------------------------------------------------------------------------
ImplAlignandum::ImplAlignandum(const ImplAlignandum & src) :
	mFrom(src.mFrom), mTo(src.mTo), mLength(src.mLength),
	mIsPrepared(src.mIsPrepared),
	mStorageType( src.mStorageType )
{
	debug_func_cerr(5);

	mMasked.clear();
	std::copy( src.mMasked.begin(), src.mMasked.end(),
			std::back_inserter< std::vector<bool> >(mMasked) );

}

//--------------------------------------------------------------------------------------
void ImplAlignandum::mask( const Position & from, const Position & to)
{
	Position j;
	for (j = from; j < to; j++)
		mask( j );
}

//--------------------------------------------------------------------------------------
void ImplAlignandum::mask( const Position & pos )
{
	mMasked[pos] = true;
}

//--------------------------------------------------------------------------------------
bool ImplAlignandum::isMasked( const Position & pos ) const
{
	return mMasked[pos];
}

//--------------------------------------------------------------------------------------
Position ImplAlignandum::getLength() const
{
	return (mTo - mFrom);
}

//--------------------------------------------------------------------------------------
void ImplAlignandum::useSegment(Position from, Position to)
{
	assert( from <= to );

	if (from == NO_POS)
		mFrom = 0;
	else
		mFrom = from;

	if (to == NO_POS)
		mTo = mLength;
	else
		mTo = std::min( to, mLength );
}

//--------------------------------------------------------------------------------------
Position ImplAlignandum::getFrom() const
{
	return mFrom;
}

//--------------------------------------------------------------------------------------
Position ImplAlignandum::getTo() const
{
	return mTo;
}

//--------------------------------------------------------------------------------------
void ImplAlignandum::resize( Position length)
{
	release();
	mFrom = 0;
	mTo = mLength = length;
	mMasked.resize( length, false );
}

//--------------------------------------------------------------------------------------
Position ImplAlignandum::getFullLength() const
{
	return mLength;
}

//--------------------------------------------------------------------------------------
bool ImplAlignandum::isPrepared() const
{
	return mIsPrepared;
}

//--------------------------------------------------------------------------------------
void ImplAlignandum::setPrepared( bool flag ) const
{
	mIsPrepared = flag;
}

//--------------------------------------------------------------------------------------
void ImplAlignandum::setStorageType( const StorageType & storage_type )
{
	mStorageType = storage_type;
}

//--------------------------------------------------------------------------------------
StorageType ImplAlignandum::getStorageType() const
{
	return mStorageType;
}

//--------------------------------------------------------------------------------------
char ImplAlignandum::asChar( Position pos ) const
{
	return getToolkit()->getEncoder()->decode( asResidue( pos ));
}

//--------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------
/** get a random position in a sequence ranging from 0 to max */
inline Position getRandomPosition ( Position max )
{
	return (Position)((double)max*rand()/(RAND_MAX+1.0));
}

void ImplAlignandum::shuffle( unsigned int num_iterations,
		Position window_size)
{
	if (window_size == 0)
		window_size = getLength();

	Position first_from = getFrom();

	for (unsigned x = 0; x < num_iterations; ++x)
	{

		Position i,j;
		Position to = getTo();

		while (to > first_from )
		{
			Position from = to - window_size;

			if (from < 0)
			{
				from = 0;
				window_size = to;
			}

			for (i = to - 1; i >= from; --i)
			{
				j = to - getRandomPosition(window_size) - 1;
				swap( i, j );
			}
			to -= window_size;
		}
	}
}

//--------------------------------------------------------------------------------------
// use faster implementations in subclasses, if you prefer
std::string ImplAlignandum::asString() const
{
	std::string ret_val("");

	for (Position i = 0; i < mLength; i++)
		ret_val += getToolkit()->getEncoder()->decode( asResidue(i) );

	return ret_val;
}

void ImplAlignandum::save( std::ostream & output ) const
{
	__save( output, MNNoType );
}

//--------------------------------------------------------------------------------------
void ImplAlignandum::__save( std::ostream & output, MagicNumberType type ) const
{
	debug_func_cerr( 5 );

	if (type == MNNoType )
	{
		type = MNImplAlignandum;
		output.write( (char*)&type, sizeof(MagicNumberType) );
	}

	output.write( (char*)&mIsPrepared, sizeof(bool) );
	output.write( (char*)&mFrom, sizeof(Position) );
	output.write( (char*)&mTo, sizeof(Position) );
	output.write( (char*)&mLength, sizeof(Position) );
	output.write( (char*)&mStorageType, sizeof( StorageType ) );
}

//--------------------------------------------------------------------------------------
void ImplAlignandum::load( std::istream & input)
{
	debug_func_cerr( 5 );

	input.read( (char*)&mIsPrepared, sizeof(bool) );
	input.read( (char*)&mFrom, sizeof(Position) );
	input.read( (char*)&mTo, sizeof(Position) );
	input.read( (char*)&mLength, sizeof(Position) );
	input.read( (char*)&mStorageType, sizeof( StorageType ) );

	if (input.fail())
		throw AlignlibException( "incomplete Alignandum object in stream.");

	mMasked.clear();
	mMasked.resize( mLength, false);

}


} // namespace alignlib
