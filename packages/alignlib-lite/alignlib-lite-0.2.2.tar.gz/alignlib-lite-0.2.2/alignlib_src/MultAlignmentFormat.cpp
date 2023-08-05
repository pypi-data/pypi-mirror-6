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
#include "Alignatum.h"
#include "HelpersAlignatum.h"
#include "MultAlignmentFormat.h"
#include "HelpersMultAlignment.h"

using namespace std;

namespace alignlib
{

//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
MultAlignmentFormat::MultAlignmentFormat()
{
}

MultAlignmentFormat::MultAlignmentFormat( const MultAlignmentFormat & src)
{
	mData.clear();
	for (int x = 0; x < src.mData.size(); ++x)
		mData.push_back( src.mData[x]->getClone());
}

MultAlignmentFormat::MultAlignmentFormat( std::istream & input )
{
	load( input );
}

MultAlignmentFormat::MultAlignmentFormat( const std::string & src)
{
	std::istringstream i(src.c_str());
	load( i );
}

MultAlignmentFormat::MultAlignmentFormat(
		const HMultAlignment & src,
		const HStringVector & sequences,
		const ExpansionType & expansion_type )
{
	fill( src, sequences, expansion_type );
}

MultAlignmentFormat::~MultAlignmentFormat()
{
}

void MultAlignmentFormat::fill(
		const HMultAlignment & src,
		const HStringVector & sequences,
		const ExpansionType & expansion_type )
{
	debug_func_cerr( 5 );
	if (sequences->size() != src->getNumSequences())
		throw AlignlibException("MultAlignmentFormat.cpp: number of sequences in src and sequences do not match");

	for (int x = 0; x < src->getNumSequences(); ++x )
		if ( (*src)[x]->getColTo() > 0 && (*src)[x]->getColTo() > (*sequences)[x].size())
			throw AlignlibException("MultAlignmentFormat.cpp: sequence length in mali longer than in provided sequence");

	mData.clear();
}

void MultAlignmentFormat::copy( HMultAlignment & dest, const HAlignment & templ ) const
{
	debug_func_cerr( 5 );
	dest->clear();
	AlignatumVector::const_iterator it(mData.begin()), end(mData.end());
	for (; it!=end; ++it)
	{
		HAlignment ali (templ->getNew());
		(*it)->fillAlignment( ali, true );
		dest->add( ali );
	}
}

void MultAlignmentFormat::load( std::istream & input)
{
	debug_func_cerr( 5 );
}

void MultAlignmentFormat::save( std::ostream & output) const
{
	debug_func_cerr( 5 );
}

//--------------------------------------------------------------------------------------------------------------------------------
std::ostream & operator<< (std::ostream & output, const MultAlignmentFormat & src)
{
	src.save( output );
	return output;
}

//--------------------------------------------------------------------------------------------------------------------------------
std::istream & operator>> (std::istream & input, MultAlignmentFormat & dest)
{
	dest.load( input );
	return input;
}

//--------------------------------------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------------------------------------
MultAlignmentFormatPlain::MultAlignmentFormatPlain()
: MultAlignmentFormat()
{
}

MultAlignmentFormatPlain::MultAlignmentFormatPlain( std::istream & input )
: MultAlignmentFormat()
{
	load( input );
}

MultAlignmentFormatPlain::MultAlignmentFormatPlain( const std::string & src)
: MultAlignmentFormat()
	{
	std::istringstream i(src.c_str());
	load( i );
	}

MultAlignmentFormatPlain::MultAlignmentFormatPlain(
		const HMultAlignment & src,
		const HStringVector & sequences,
		const ExpansionType & expansion_type )
: MultAlignmentFormat()
{
	// this is a call to a virtual function within
	// constructor. These are dangerous if the base
	// class wants to use a derived function. This
	// is not the case. To ensure this, the empty constructor
	// is called.
	fill( src, sequences, expansion_type );
}

MultAlignmentFormatPlain::MultAlignmentFormatPlain(
		const HMultAlignment & src,
		const HAlignandumVector & sequences,
		const ExpansionType & expansion_type )
: MultAlignmentFormat()
{
	// this is a call to a virtual function within
	// constructor. These are dangerous if the base
	// class wants to use a derived function. This
	// is not the case. To ensure this, the empty constructor
	// is called.
	fill( src, sequences, expansion_type );
}


MultAlignmentFormatPlain::~MultAlignmentFormatPlain ()
{
}

MultAlignmentFormatPlain::MultAlignmentFormatPlain (const MultAlignmentFormatPlain & src )
: MultAlignmentFormat( src )
{
}

void MultAlignmentFormatPlain::fill(
		const HMultAlignment & src,
		const HStringVector & sequences,
		const ExpansionType & expansion_type
)
{
	debug_func_cerr(5);

	MultAlignmentFormat::fill( src, sequences, expansion_type );

	// expand gaps
	HMultAlignment work(src->getCopy( expansion_type ));

 	for (int x = 0; x < sequences->size(); ++x)
 	{
 		HAlignment map_src2mali( (*work)[x]->getClone() );
 		map_src2mali->switchRowCol();
 		mData.push_back(
 				makeAlignatum( (*sequences)[x],
 						map_src2mali,
 						work->getLength(),
 						expansion_type == UnalignedStacked ));

 	}
 	debug_cerr( 5, "added " << sequences->size() << " to data " << mData.size());
}

void MultAlignmentFormatPlain::fill(
		const HMultAlignment & src,
		const HAlignandumVector & sequences,
		const ExpansionType & expansion_type)
{
	debug_func_cerr(5);

	HStringVector seqs( new StringVector() );
 	for (int x = 0; x < sequences->size(); ++x)
 		seqs->push_back( (*sequences)[x]->asString() );
 	fill( src, seqs, expansion_type );
}

void MultAlignmentFormatPlain::load( std::istream & input)
{
	debug_func_cerr( 5 );
	std::string s;
	mData.clear();
	HAlignatum a(makeAlignatum());
	a->read( input );
	while (!input.fail())
	{
		mData.push_back( a );
		a = makeAlignatum();
		a->read( input );
	}
}

void MultAlignmentFormatPlain::save( std::ostream & output) const
{
	debug_func_cerr( 5 );
	for (int x = 0; x < mData.size(); ++x)
		output << *(mData[x]) << std::endl;
}


//--------------------------------------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------------------------------------


} // namespace alignlib
