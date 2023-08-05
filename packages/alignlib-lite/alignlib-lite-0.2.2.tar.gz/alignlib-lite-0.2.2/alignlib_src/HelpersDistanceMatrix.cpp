//--------------------------------------------------------------------------------
// Project LibPhylo
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: HelpersMatrix.cpp,v 1.2 2004/06/02 12:14:34 aheger Exp $
//--------------------------------------------------------------------------------

#include <iostream>
#include <string>

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "alignlib_fwd.h"
#include "AlignlibDebug.h"

#include "HelpersDistanceMatrix.h"
#include "DistanceMatrix.h"

using namespace std;

namespace alignlib
{

  /** copy the contents of source element wise into the DistanceMatrix */
  void fillDistanceMatrix(
		  HDistanceMatrix & dest,
		  DistanceMatrixValue * source)
  {
	  debug_func_cerr( 5 );

      DistanceMatrixSize row, col, index = 0;

      for (row = 0; row < dest->getWidth(); row++)
    	  for (col = 0; col < dest->getWidth(); col++)
    	  {
    		  (*dest)(row,col) = source[index++];
    	  }

      return;
  }

} // namespace alignlib
