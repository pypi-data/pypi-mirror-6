//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplDistanceMatrixSymmetric.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#include <iostream>
#include <fstream>
#include <iomanip>
#include <stdlib.h>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "ImplDistanceMatrixSymmetric.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"

using namespace std;

namespace alignlib {

HDistanceMatrix makeDistanceMatrixSymmetric( DistanceMatrixSize size, DistanceMatrixValue default_value)
{
	return HDistanceMatrix( new ImplDistanceMatrixSymmetric( size, default_value ) );
}

//---------------------------------------------------------< constructors and destructors >--------------------------------------

ImplDistanceMatrixSymmetric::ImplDistanceMatrixSymmetric() : ImplDistanceMatrix()
{
}

ImplDistanceMatrixSymmetric::~ImplDistanceMatrixSymmetric ()
{
}

IMPLEMENT_CLONE( HDistanceMatrix, ImplDistanceMatrixSymmetric );

// not calling the base class constructor is dangerous!!
ImplDistanceMatrixSymmetric::ImplDistanceMatrixSymmetric (DistanceMatrixSize width, DistanceMatrixValue default_value ) : ImplDistanceMatrix()
{
	debug_func_cerr( 5 );

	mWidth  = width;
	mSize   = mWidth * (mWidth - 1) / 2;

	debug_cerr(5, "Allocating " << mSize << " bytes for a matrix of width " << mWidth );

	mMatrix = new DistanceMatrixValue[ mSize ];

	DistanceMatrixSize i;
	for (i = 0; i < mSize; i++)
		mMatrix[i] = default_value;
}

ImplDistanceMatrixSymmetric::ImplDistanceMatrixSymmetric( const ImplDistanceMatrixSymmetric & src) : ImplDistanceMatrix( src )
{

	debug_func_cerr( 5 );

	//!! to be tightened up. Do not copy twice, otherwise memory leak!!!
	// since virtual functions do not work in constructors, I have to everything myself

	mWidth = src.getWidth();
	const DistanceMatrixValue * matrix = src.mMatrix;

	mSize = mWidth * (mWidth - 1) / 2;
	mMatrix = new DistanceMatrixValue[ mSize ];

	if (!mMatrix)
		throw AlignlibException("Out of memory in ImplDistanceMatrixSymmetric");

	DistanceMatrixSize i, j;
	DistanceMatrixSize index = 0;

	for (i = 1; i < mWidth; i++)			// iterate through rows
		for (j = 0; j < i; j++) 			// iterate through columns
			mMatrix[index++] = matrix[src.getIndex(i,j)];
}

//-------------------------------------------------------------
void ImplDistanceMatrixSymmetric::shrink()
{
	debug_func_cerr( 5 );
	/* simply decrease the width of the matrix */
	mWidth --;
	mSize -= mWidth;

	debug_cerr( 5, "New matrix size: " << mWidth << "(" << mSize << ")" );

}

//-------------------------------------------------------------
void ImplDistanceMatrixSymmetric::swap( DistanceMatrixSize row_1, DistanceMatrixSize row_2 )
{
	debug_func_cerr( 5 );

	/*
	-			-
	y-			x-
	-y-			-x-
	-y--		->	-x--
	xOxx-			yyyy-
	-y--x-			-x--y-
	-y--x--			-x--y--
	-y--x---		-x--y---
   i.e. two columns have to skipped:
   1. col = row_1
   2. col = row_2
	 */

	DistanceMatrixValue t;

#define SWAP( x, y) { t = mMatrix[x], mMatrix[x] = mMatrix[y], mMatrix[y] = t;}

	DistanceMatrixSize i;

	if (row_2 < row_1)
	{
		i = row_1; row_1 = row_2; row_2 = i;
	}

	for (i = 0; i < row_1; i++)
		SWAP( getIndex(row_1,i), getIndex( row_2,i));

	for (i = row_1 + 1; i < row_2; i++)
		SWAP( getIndex(row_1,i), getIndex( row_2,i));

	for (i = row_2 + 1; i < mWidth; i++)
		SWAP( getIndex(row_1,i), getIndex( row_2,i));

#undef SWAP

}

//-------------------------------------------------------------
DistanceMatrixSize ImplDistanceMatrixSymmetric::getIndex( DistanceMatrixSize row, DistanceMatrixSize col) const
{
	debug_func_cerr( 5 );

	int x;

	if (row == col)
		return NO_INDEX;           // the diagonal is not part of the matrix

	if (row > col)
		x = row * ( row - 1) / 2 + col;
	else
		x = col * ( col - 1) / 2 + row;

	return x;
}

//-------------------------------------------------------------
DistanceMatrixSize ImplDistanceMatrixSymmetric::getRow( DistanceMatrixSize index ) const
{
	debug_func_cerr( 5 );

	DistanceMatrixSize row = 1;
	DistanceMatrixSize row_index = 0;

	while (index >= row_index)
		row_index += row++;

	return (row - 1);
}


//-------------------------------------------------------------
DistanceMatrixSize ImplDistanceMatrixSymmetric::getColumn( DistanceMatrixSize index ) const {
	// computationally inefficient, maybe use cache
	return (index - getIndex(getRow(index), 0));
}

//-------------------------------------------------------------
void ImplDistanceMatrixSymmetric::calculateSize()
{

	debug_func_cerr( 5 );

	mSize = mWidth * (mWidth - 1) / 2;
}

//--------------------------------------------------------------------------------------------------------------------------------


} // namespace alignlib
