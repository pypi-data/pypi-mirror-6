//--------------------------------------------------------------------------------
// Project LibPhylo
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: HelpersDistanceMatrix.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef HELPERS_PHYLOMATRIX_H
#define HELPERS_PHYLOMATRIX_H 1

#include <iosfwd>
#include "alignlib_fwd.h"
#include "alignlib_fwd.h"

namespace alignlib 
{

    /** Helper functions for class Phylomatrix:
	
	1. factory functions
	
	2. accessor functions for default objects
	
	3. convenience functions
    */
    
    /* -------------------------------------------------------------------------------------------------------------------- */
    /* 1. factory functions */

    /** create an empty symmetric matrix */
    HDistanceMatrix makeDistanceMatrixSymmetric( 
    		DistanceMatrixSize size = 0, 
    		DistanceMatrixValue default_value = 0);

    /* -------------------------------------------------------------------------------------------------------------------- */
    /* 2. accessor functions for default objects */
    
    /* -------------------------------------------------------------------------------------------------------------------- */
    /* 3. convenience functions */
    
    /** fill matrix with values from source */
    void fillDistanceMatrix( 
    		HDistanceMatrix & dest, 
    		DistanceMatrixValue * source );

}

#endif	/* HELPERS_MATRIX_H */
