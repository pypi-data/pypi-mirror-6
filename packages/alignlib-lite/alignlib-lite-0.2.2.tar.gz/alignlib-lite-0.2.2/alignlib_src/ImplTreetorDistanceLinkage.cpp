//--------------------------------------------------------------------------------
// Project alignlib
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplTreetorDistanceLinkage.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------

#include <iostream>
#include <iomanip>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "alignlib_fwd.h"
#include "ImplTreetorDistanceLinkage.h"
#include "Tree.h"
#include "DistanceMatrix.h"
#include "Distor.h"
#include "HelpersDistor.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "HelpersTreetor.h"
#include "HelpersToolkit.h"

#define MIN(x,y) (x < y ) ? x : y
#define MAX(x,y) (x > y ) ? x : y
#define AVE(x,y) (x + y) / 2

using namespace std;

namespace alignlib
{

//------------------------------------------------------< factory functions >-----------------------------------
HTreetor makeTreetorDistanceLinkage(
		const LinkageType & method )
{
	debug_func_cerr( 5 );
	return HTreetor( new ImplTreetorDistanceLinkage( method ) );
}

//---------------------------------------------------------< constructors and destructors >---------------------
ImplTreetorDistanceLinkage::ImplTreetorDistanceLinkage ( const LinkageType & method ) :
    ImplTreetorDistance(), mMethod(method)
{
	debug_func_cerr( 5 );
}


ImplTreetorDistanceLinkage::~ImplTreetorDistanceLinkage ()
{
	debug_func_cerr( 5 );
}

ImplTreetorDistanceLinkage::ImplTreetorDistanceLinkage (const ImplTreetorDistanceLinkage & src ) :
    ImplTreetorDistance(src), mMethod(src.mMethod) {
}

IMPLEMENT_CLONE( HTreetor, ImplTreetorDistanceLinkage );

//------------------------------------------------------------------------------------------------------------------------------
Node ImplTreetorDistanceLinkage::joinNodes(
		HTree & tree,
		DistanceMatrixSize cluster_1,
		DistanceMatrixSize cluster_2 ) const
		{

  DistanceMatrixValue d_ij = (*mWorkMatrix)( cluster_1, cluster_2 );
  TreeHeight height_1 = tree->getHeight( mIndices[cluster_1] );
  TreeWeight weight_1 = d_ij / 2 - height_1;

  Node new_node = tree->joinNodes( mIndices[ cluster_1 ],
					 mIndices[ cluster_2 ],
					 weight_1,
					 d_ij / 2 - tree->getHeight( mIndices[ cluster_2])
					 );

  // set the Height of the new node. This should be the same as height_2 + weight_2
  tree->setHeight( new_node, height_1 + weight_1);

  return new_node;
};

//------------------------------------------------------------------------------------------------------------------------------
void ImplTreetorDistanceLinkage::calculateMinimumDistance() const {
  // find minimum distance in matrix
  mMinimumValue = mWorkMatrix->getMinimum( mMinimumCoord );
}

//------------------------------------------------------------------------------------------------------------------------------
void ImplTreetorDistanceLinkage::updateDistanceMatrix(
		const HTree & tree,
		DistanceMatrixSize cluster_1, DistanceMatrixSize cluster_2 ) const
		{

  //------------------------------------------------------------------------------------------------------
  // calculate distance to new cluster and put them in cluster_1
  // the distance between cluster_1 and cluster_2 is skipped calculated

  DistanceMatrixSize s, n_i, n_j, n;
  DistanceMatrixValue d_ij;

  DistanceMatrixValue new_dist;

  DistanceMatrixSize last_row = mWorkMatrix->getWidth() - 1;

  for (s = 0; s < last_row; s++) {

    if (s == cluster_1 || s == cluster_2) continue;

    DistanceMatrixValue d_is = (*mWorkMatrix)( cluster_1, s );
    DistanceMatrixValue d_js = (*mWorkMatrix)( cluster_2, s );

    switch (mMethod) {

    case SINGLE_LINKAGE:
      new_dist = MIN( d_is, d_js); break;

    case COMPLETE_LINKAGE:
      new_dist = MAX( d_is, d_js ); break;

    case WPGMA:
      new_dist = AVE( d_is, d_js ); break;

    case AVERAGE_LINKAGE:
    case UPGMA:
      n_i = tree->getNumLeaves( mIndices[cluster_1] );
      n_j = tree->getNumLeaves( mIndices[cluster_2] );
      n = n_i + n_j;
      new_dist = n_i * d_is / n + n_j * d_js / n;
      break;

    case UPGMC:
	n_i = tree->getNumLeaves( mIndices[cluster_1] );
	n_j = tree->getNumLeaves( mIndices[cluster_2] );
	n = n_i + n_j;
	d_ij = (*mWorkMatrix)( cluster_1, cluster_2);

	new_dist = n_i * d_is / n + n_j * d_js / n - n_i * n_j * d_ij / (n * n);

	break;

    case WPGMC:
      d_ij = (*mWorkMatrix)( cluster_1, cluster_2);

      new_dist = (d_is + d_js) / 2 - d_ij / 4;
      break;

    default:
      throw AlignlibException( "Unkown method in ImplTreetorDistanceLinkage" );
      break;

    }

    // cout << "s=" << s << " d_is=" << d_is << " d_js " << d_js << " new_value=" << new_dist << endl;

    (*mWorkMatrix)( cluster_1, s) = new_dist;
  }
}

} /* namespace alignlib */

