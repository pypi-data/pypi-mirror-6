//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplTreetorDistanceNJ.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------

#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef IMPL_TREETOR_DISTANCE_NJ_H
#define IMPL_TREETOR_DISTANCE_NJ_H 1

#include <iostream>
#include "alignlib_fwd.h"
#include "ImplTreetorDistance.h"

namespace alignlib
{

/**
   Calculate neighbour-joining tree. The root is placed in the middle
   between the last two joined clusters.

   @author Andreas Heger
   @version $Id: ImplTreetorDistanceNJ.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
   @short calculate neighbour-joining tree
*/

class ImplTreetorDistanceNJ : public ImplTreetorDistance
{
 public:

  /* constructors and desctructors------------------------------------------------------- */

	 /** empty constructor */
	 ImplTreetorDistanceNJ ();

	 /** constructor */
	 ImplTreetorDistanceNJ ( const HDistor & distor );


  /** copy constructor */
  ImplTreetorDistanceNJ (const ImplTreetorDistanceNJ & src);

  /** destructor */
  virtual ~ImplTreetorDistanceNJ ();

  DEFINE_CLONE( HTreetor );

  /* member access functions--------------------------------------------------------------- */

 protected:
  /** swap indices in helper arrays */
  virtual void swapHelpers( DistanceMatrixSize cluster_1, DistanceMatrixSize cluster_2) const;

  /** calculate the minimum distance for the working matrix */
  virtual void calculateMinimumDistance() const;

  /** update the distance matrix and other helper variables */
  virtual void updateDistanceMatrix(
		  const HTree & tree,
		  DistanceMatrixSize cluster_1,
		  DistanceMatrixSize cluster_2 ) const;

  /** join two nodes and return the index of the added node */
  virtual Node joinNodes(
		  HTree & tree,
		  DistanceMatrixSize cluster_i,
		  DistanceMatrixSize cluster_2 ) const;

  /** initialize helper variables that you might need */
  virtual void startUp(  HTree & tree,
		  const HMultipleAlignment & mali) const;

  /** clean up helper variables */
  virtual void cleanUp() const;

 private:
  /** average distance from cluster i to all other clusters */
  mutable DistanceMatrixValue * mR;

};

}

#endif /* _ALIGNATUMSEQUENCE_H */

