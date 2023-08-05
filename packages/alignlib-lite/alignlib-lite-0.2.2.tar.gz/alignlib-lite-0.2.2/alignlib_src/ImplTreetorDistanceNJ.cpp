//--------------------------------------------------------------------------------
// Project alignlib
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplTreetorDistanceNJ.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------

#include <iostream>
#include <iomanip>
#include <cassert>
#include <cstring>
#include <limits>
#include "ImplTreetorDistanceNJ.h"
#include "Tree.h"
#include "DistanceMatrix.h"
#include "Distor.h"
#include "HelpersDistor.h"
#include "AlignlibException.h"
#include "AlignlibDebug.h"
#include "HelpersToolkit.h"

using namespace std;

namespace alignlib {

//------------------------------------------------------< factory functions >------------------------------------------------
HTreetor makeTreetorDistanceNJ()
{
	return HTreetor( new ImplTreetorDistanceNJ() );
}

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplTreetorDistanceNJ::ImplTreetorDistanceNJ () :
	ImplTreetorDistance(), mR (NULL)
	{
	}

ImplTreetorDistanceNJ::~ImplTreetorDistanceNJ ()
{
}

IMPLEMENT_CLONE( HTreetor, ImplTreetorDistanceNJ );

ImplTreetorDistanceNJ::ImplTreetorDistanceNJ (const ImplTreetorDistanceNJ & src ) :
	ImplTreetorDistance(src), mR( NULL)
	{
	if (mWorkMatrix != NULL)
	{
		DistanceMatrixSize width = mWorkMatrix->getWidth();
		mR = new DistanceMatrixValue[ width ];
		memcpy( mR, src.mR, sizeof(DistanceMatrixValue) * width );
	}
	}

//------------------------------------------------------------------------------------------------------------------------------
void ImplTreetorDistanceNJ::startUp(
		HTree & tree,
		const HMultipleAlignment & mali) const
{
	cleanUp();
	ImplTreetorDistance::startUp( tree, mali);

	DistanceMatrixSize width = mWorkMatrix->getWidth();
	DistanceMatrixSize width_2 = width - 2;

	mR = new DistanceMatrixValue[ width ];

	DistanceMatrixSize i,k;

	for (i = 0; i < width; i++)
	{
		mR[i] = 0;
		for (k = 0; k < width; k++)
			mR[i] += (*mWorkMatrix)( i, k );
		mR[i] /= width_2;
	}
}

//------------------------------------------------------------------------------------------------------------------------------
void ImplTreetorDistanceNJ::cleanUp() const
{
	if (mR != NULL)
		delete [] mR;

	mR = NULL;
}


//------------------------------------------------------------------------------------------------------------------------------
Node ImplTreetorDistanceNJ::joinNodes(
		HTree & tree,
		DistanceMatrixSize cluster_1,
		DistanceMatrixSize cluster_2 ) const
{
	debug_func_cerr( 5 );

	DistanceMatrixValue d_ij = (*mWorkMatrix)( cluster_1, cluster_2 );
	DistanceMatrixValue d_ik = (d_ij + mR[cluster_1] - mR[cluster_2]) / 2;
	DistanceMatrixValue d_jk = d_ij - d_ik;

	debug_cerr( 5, "Joining nodes " <<
			mIndices[cluster_1] << " (" << d_ik << ") with " <<
			mIndices[cluster_2] << " (" << d_jk << ");" );

	return tree->joinNodes( mIndices[ cluster_1 ],
			mIndices[ cluster_2 ],
			d_ik,
			d_jk );
};

//------------------------------------------------------------------------------------------------------------------------------
void ImplTreetorDistanceNJ::swapHelpers(
		DistanceMatrixSize cluster_1,
		DistanceMatrixSize cluster_2) const
{
	DistanceMatrixValue t;

	t = mR[cluster_1];
	mR[cluster_1] = mR[cluster_2];
	mR[cluster_2] = t;
}

//------------------------------------------------------------------------------------------------------------------------------
void ImplTreetorDistanceNJ::calculateMinimumDistance() const
{

	DistanceMatrixValue min = std::numeric_limits<DistanceMatrixValue>::max();

	DistanceMatrixSize row, col;
	DistanceMatrixSize best_row = 0;
	DistanceMatrixSize best_col = 0;
	DistanceMatrixSize width = mWorkMatrix->getWidth();
	DistanceMatrixValue d;

	// iterate through rows and columns, not through indices, since ri and rj have
	// to be calculated, and looking up the row/col for a given index is slow.

	for (row = 0; row < width - 1; row++)
	{
		for (col = row + 1; col < width; col++)
		{
			if ( (d = (*mWorkMatrix)( row, col ) - (mR[row] + mR[col])) < min )
			{
				min = d;
				best_row = row;
				best_col = col;
			}
		}
	}

	mMinimumCoord.row = best_row;
	mMinimumCoord.col = best_col;

	mMinimumValue = min;
}

//------------------------------------------------------------------------------------------------------------------------------
void ImplTreetorDistanceNJ::updateDistanceMatrix(
		const HTree & tree,
		DistanceMatrixSize cluster_1,
		DistanceMatrixSize cluster_2 ) const
{

	debug_func_cerr( 5 );
	// calculate distance to new cluster and put them in cluster_1

	//------------------------------------------------------------------------------------------------------
	// see Durbin et al. for description of algorithm and symbols used here.
	// the update proceeds in three steps
	// 1. mR[s]: multiply by |L| - 2 and subract d_si and d_sj
	// 2. calculate new distance d_sk (k = new cluster, is stored in cluster_1, i.e. i)
	// 3. mR[s]: add d_sk , divide by |L| - 3.

	DistanceMatrixSize s;

	DistanceMatrixValue new_r = 0;		// mR for new cluster

	DistanceMatrixSize last_row = mWorkMatrix->getWidth() - 1;
	DistanceMatrixSize num_leaves_2 = last_row - 1;
	DistanceMatrixSize num_leaves_3 = last_row - 2;

	if (num_leaves_3 == 0)
		num_leaves_3 = 1;

	// iterate to lastrow. if s = cluster_1 d_ss, etc are 0, so nothing changes.
	DistanceMatrixValue d_ij = (*mWorkMatrix)( cluster_1, cluster_2);

	for (s = 0; s < last_row; s++) {

		// update mR
		mR[s] =  mR[s] * num_leaves_2
		- (*mWorkMatrix)( cluster_1, s)
		- (*mWorkMatrix)( cluster_2, s);

		// calculate new value for d_ms
		DistanceMatrixValue d_is = (*mWorkMatrix)( cluster_1, s );
		DistanceMatrixValue d_js = (*mWorkMatrix)( cluster_2, s );

		DistanceMatrixValue new_dist = (d_is + d_js - d_ij) / 2.0;

		(*mWorkMatrix)( cluster_1, s) = new_dist;
		new_r += new_dist;

		// update mR
		mR[s] = (mR[s] +  new_dist) / num_leaves_3;
	}
	mR[cluster_1] = new_r / num_leaves_3;
}


} /* namespace alignlib */

