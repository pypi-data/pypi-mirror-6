//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplDistanceMatrix.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#include <iostream>
#include <fstream>
#include <iomanip>
#include <stdlib.h>
#include <cstring> // for memcpy
#include <cassert>
#include <limits>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "ImplDistanceMatrix.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"

using namespace std;

namespace alignlib {

//define swap_temp for this macro to work
#define SWAP(x,y) { swap_temp = x; x = y; y = swap_temp; }

//---------------------------------------------------------< constructors and destructors >--------------------------------------

ImplDistanceMatrix::ImplDistanceMatrix() : mWidth(0), mSize(0), mMatrix( NULL)
{
	debug_func_cerr( 5 );
}

ImplDistanceMatrix::ImplDistanceMatrix( DistanceMatrixSize width, DistanceMatrixValue default_value)
{
	debug_func_cerr( 5 );

	allocateMemory();

	DistanceMatrixSize i;
	for (i = 0; i < mSize; i++)
		mMatrix[i] = default_value;
}

ImplDistanceMatrix::ImplDistanceMatrix( DistanceMatrixSize width, DistanceMatrixValue * source)
{
	debug_func_cerr( 5 );

	mWidth  = width;
	mMatrix = source;

	calculateSize();
}


ImplDistanceMatrix::~ImplDistanceMatrix ()
{
	debug_func_cerr( 5 );

	freeMemory();
}


ImplDistanceMatrix::ImplDistanceMatrix (const ImplDistanceMatrix & src ) :
	mWidth( src.mWidth ), mSize( src.mSize )
	{

	debug_func_cerr( 5 );

	// have to allocate memory myself, because virtual functions do not work inside constructors
	// so calling CalculateSize() is not an option

	mMatrix = new DistanceMatrixValue[ mSize ];

	if (!mMatrix)
		throw AlignlibException("Out of memory in ImplDistanceMatrix::AllocateMemory");

	memcpy( mMatrix, src.mMatrix, mSize * sizeof( DistanceMatrixValue) );

	}


//--------------------------------------------------------------------------------------------
DistanceMatrixValue ImplDistanceMatrix::getMinimum( Coordinate & x) const
{
	debug_func_cerr( 5 );

	DistanceMatrixValue min = std::numeric_limits<DistanceMatrixValue>::max();

	DistanceMatrixSize i;
	DistanceMatrixSize best_index = 0;

	for (i = 0; i < mSize; i++)
	{
		if (mMatrix[i] < min)
		{
			min = mMatrix[i];
			best_index = i;
		}
	}

	x.row = getRow( best_index );
	x.col = getColumn( best_index );

	return min;
}

//--------------------------------------------------------------------------------------------
DistanceMatrixValue ImplDistanceMatrix::getMinimum() const
{
	debug_func_cerr( 5 );

	Coordinate x;

	return getMinimum(x);
}

//-------------------------------------------------------------
void ImplDistanceMatrix::setWidth(DistanceMatrixSize width)
{
	debug_func_cerr( 5 );

	mWidth = width;
	allocateMemory();
}

//--------------------------------------------------------------------------------------------
DistanceMatrixValue ImplDistanceMatrix::getMaximum( Coordinate & x) const
{
	debug_func_cerr( 5 );

	DistanceMatrixValue max = -999999;

	DistanceMatrixSize i;
	DistanceMatrixSize best_index = 0;

	for (i = 0; i < mSize; i++) {
		if (mMatrix[i] > max)
		{
			max = mMatrix[i];
			best_index = i;
		}
	}

	x.row = getRow( best_index );
	x.col = getColumn( best_index );
	return max;
}

DistanceMatrixValue ImplDistanceMatrix::getMaximum() const
{
	Coordinate x;

	return getMaximum(x);
}


//--------------------------------------------------------------------------------------------
void ImplDistanceMatrix::allocateMemory()
{
	debug_func_cerr( 5 );

	// clear old memory, be careful!, use copy constructor to copy matrices
	DistanceMatrixSize saved_width = mWidth;
	freeMemory();
	mWidth = saved_width;

	debug_cerr( 5, "Allocating " << mSize << " bytes for a matrix of width " << mWidth );

	calculateSize();
	mMatrix = new DistanceMatrixValue[ mSize ];

	if (!mMatrix)
		throw AlignlibException("Out of memory in ImplDistanceMatrix::allocateMemory");

}

//--------------------------------------------------------------------------------------------
void ImplDistanceMatrix::freeMemory()
{
	debug_func_cerr( 5 );

	if (mMatrix != NULL)
		delete [] mMatrix;

	mMatrix = NULL;
	mWidth  = 0;
	mSize   = 0;

}

//-------------------------------------------------------------
DistanceMatrixSize ImplDistanceMatrix::getWidth() const
{
	return mWidth;
}

//-------------------------------------------------------------
DistanceMatrixSize ImplDistanceMatrix::getSize() const
{
	return mSize;
}

//-------------------------------------------------------------
DistanceMatrixValue ImplDistanceMatrix::operator()( DistanceMatrixSize row, DistanceMatrixSize col) const
{

	debug_func_cerr( 5 );

	debug_cerr( 5, "Looking up " << row << " " << col << ": index is " << getIndex( row, col ) );

	return mMatrix[getIndex( row, col)];
}

//-------------------------------------------------------------
DistanceMatrixValue ImplDistanceMatrix::getElement( DistanceMatrixSize row, DistanceMatrixSize col) const
{
	return mMatrix[getIndex( row, col)];
}

//-------------------------------------------------------------
DistanceMatrixValue & ImplDistanceMatrix::operator()( DistanceMatrixSize row, DistanceMatrixSize col)
{
	return mMatrix[getIndex(row,col)];
}
//-------------------------------------------------------------
void ImplDistanceMatrix::setElement( DistanceMatrixSize row, DistanceMatrixSize col, DistanceMatrixValue value)
{
	mMatrix[getIndex(row,col)] = value;
}

//-------------------------------------------------------------
DistanceMatrixSize ImplDistanceMatrix::getIndex( DistanceMatrixSize row, DistanceMatrixSize col) const
{
	return (row * mWidth + col);
}

//-------------------------------------------------------------
DistanceMatrixSize ImplDistanceMatrix::getRow( DistanceMatrixSize index ) const
{
	return ( (DistanceMatrixSize)(index / mWidth)  );
}

//-------------------------------------------------------------
DistanceMatrixSize ImplDistanceMatrix::getColumn( DistanceMatrixSize index ) const
{
	return ( index % mWidth );
}

//-------------------------------------------------------------
void ImplDistanceMatrix::calculateSize()
{

	debug_func_cerr(5);

	mSize = mWidth * mWidth;
}

//---------------------------------------------------------< Input/Output routines >---------------------------------------------
void ImplDistanceMatrix::write( std::ostream & output ) const
{
	// write so that output can be used in phylip

	cout << " " << mWidth << " " << mSize << endl;

	DistanceMatrixSize i, j;

	for (i = 0; i < mWidth; i++) {
		cout << i << "\t";
		for (j = 0; j < mWidth; j++)
			cout << setw(10) << setprecision(4) << operator()( i, j) << " ";
		cout << endl;
	}
}

//---------------------------------------------------------< Input/Output routines >---------------------------------------------
void ImplDistanceMatrix::read( std::istream & input ) const
{
}

//--------------------------------------------------------------------------------------------------------------------------------


} // namespace alignlib
