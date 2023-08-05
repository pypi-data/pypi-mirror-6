//--------------------------------------------------------------------------------
// Project alignlib
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplTreetorDistance.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------

#include <iostream>
#include <iomanip>
#include <cassert>
#include "MultipleAlignment.h"

#include "ImplTreetorDistance.h"
#include "Tree.h"
#include "DistanceMatrix.h"
#include "HelpersDistanceMatrix.h"
#include "Toolkit.h"
#include "HelpersToolkit.h"
#include "Distor.h"
#include "AlignlibDebug.h"

using namespace std;

namespace alignlib
{

//----------< constructors and destructors >--------------------------------------
ImplTreetorDistance::ImplTreetorDistance () :
	ImplTreetor()
	{}

ImplTreetorDistance::~ImplTreetorDistance ()
{
}

ImplTreetorDistance::ImplTreetorDistance (const ImplTreetorDistance & src ) :
	ImplTreetor( src )
{
}

//------------------------------------------------------------------------------------------------------------------------------
void ImplTreetorDistance::startUp(
		HTree & tree,
		const HMultipleAlignment & mali) const
{
	debug_func_cerr( 5 );

	// create a distance matrix
	assert( mali->getNumSequences() > 0);
	mWorkMatrix = makeDistanceMatrixSymmetric( mali->getNumSequences());

	// call Distor for multiple alignment to fill matrix with distances
	HDistor distor = getToolkit()->getDistor();
	distor->calculateMatrix( mWorkMatrix, mali );
}

//------------------------------------------------------------------------------------------------------------------------------
void ImplTreetorDistance::cleanUp() const
{
}

//------------------------------------------------------------------------------------------------------------------------------
void ImplTreetorDistance::swapHelpers(
		DistanceMatrixSize cluster_1,
		DistanceMatrixSize cluster_2) const
{
}

//------------------------------------------------------------------------------------------------------------------------------
void ImplTreetorDistance::calculateTree(
		HTree & tree,
		const HMultipleAlignment & mali ) const
{

	debug_func_cerr( 5 );
	startUp( tree, mali );

	DistanceMatrixSize swap_temp;	// for swapping indices

#define SWAP(x,y) { swap_temp = x; x = y; y = swap_temp; }

	//------------------------------------------------------------------------------------------
	// start up
	DistanceMatrixSize width = mWorkMatrix->getWidth();
	DistanceMatrixSize i;

	/* in this algorithm I assume that the matrix I use is only a half-matrix using the lower diagonal */
	tree->setNumLeaves( width );					// allocate memory for tree

	mIndices = new Node[width];			        /* allocate array to keep track of indices */

	for (i = 0; i < width; i++) mIndices[i] = i;

	//----------------------------------------------------------------------------------------------------
	// Perform hierarchical clustering

	DistanceMatrixSize last_row = width - 1;

	/* shrink distance matrix, until it contains only a single cluster */
	while (last_row > 0)
	{

	  debug_cerr( 6, "Last row " << last_row );
	  debug_cerr( 6, "Work matrix " << endl << *mWorkMatrix );

    // find minimum distance in matrix
    /*
	-
	--
	---
	----
	-x---
	------
	-------
	--------
      */
    calculateMinimumDistance();
    DistanceMatrixSize min_row = mMinimumCoord.row;
    DistanceMatrixSize min_col = mMinimumCoord.col;

    debug_cerr( 5, "Joining nodes -> "
			    << "minimum distance :" << mMinimumValue << " "
			    << "node 1: " << mIndices[min_row] << " (" << min_row << ") "
			    << "node 2: " << mIndices[min_col] << " (" << min_col << ") " );

    //------------------------------------------------------------------------------------------------------
    // move rows around, so that the last two joined cluster are in the two last rows

    /*
	-			-
	y-			--
	-y-			---
	-y--		->	----
	xOxx-			-----
	-y--x-			------
	-y--x--			xxxxxxx
	-y--x---		yyyyyyyy
    */

    DistanceMatrixSize second_row = last_row - 1;		// second to last row

    // exchange row with last row
    mWorkMatrix->swap( min_row, last_row);
    SWAP( mIndices[min_row], mIndices[last_row]);
    swapHelpers( min_row, last_row);

    // exchange col with second to last row
    mWorkMatrix->swap( min_col, second_row);
    SWAP( mIndices[min_col], mIndices[second_row]);
    swapHelpers( min_col, second_row);

    //------------------------------------------------------------------------------------------------------
    // join the two nodes in the tree giving the correct edge weights
    Node new_node = joinNodes( tree, second_row, last_row );

    debug_cerr( 6, "-> new node " << new_node );

    //------------------------------------------------------------------------------------------------------
    // calculate distance to new cluster and put them in second to last row
    updateDistanceMatrix( tree, second_row, last_row);

    /* delete last row, update mIndices, so that the last row now
       contains the number of the new cluster id */
    /*
	-	       	-
	--	       	--
	---	       	---
	----	     ->	----
	-----		-----
	------		------
	xxxxxxx		xxxxxxx
	yyyyyyyy
    */

    mWorkMatrix->shrink();

    mIndices[last_row - 1] = new_node;

    last_row = mWorkMatrix->getWidth() - 1;

  }

  delete [] mIndices;
  cleanUp();	// cleans up mWorkMatrix

}

} /* namespace alignlib */

