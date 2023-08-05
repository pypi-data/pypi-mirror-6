//--------------------------------------------------------------------------------
// Project LibPhylo
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: HelpersDistor.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef HELPERS_DISTOR_H
#define HELPERS_DISTOR_H 1

#include <iosfwd>
#include <string>
#include "alignlib_fwd.h"
#include "alignlib_default.h"

namespace alignlib 
{

/**
 * 
 * @defgroup FactoryDistor Factory functions for Distor objects.
 * @{ 
 */

/** return a @ref Distor object, that calculates distances between sequences in a multiple alignment based on Kimura 
 * 
 * @return a new @ref Distor object. 
 */
HDistor makeDistorKimura();

/** return a @ref Distor object that calculates distances between sequences in a multiple alignment 
 * in the same way as Clustal
 * 
 * @return a new @ref Distor object. 
 */
HDistor makeDistorClustal();

/** return a @ref Distor object that publishes a pre-built matrix.
 *
 * @param matrix @ref DistanceMatrix to export.
 * @return a new @ref Distor object. 
 */
HDistor makeDistorDummy( const HDistanceMatrix & matrix);

/** @} */

/** @addtogroup Defaults
 * @{
 */ 

DEFINE_DEFAULT( HDistor, getDefaultDistor, setDefaultDistor );
/** @} */

}

#endif	/* HELPERS_DISTOR_H */
