//--------------------------------------------------------------------------------
// Project LibPhylo
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: HelpersTreetor.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef HELPERS_TREETOR_H
#define HELPERS_TREETOR_H 1

#include <iosfwd>
#include <string>
#include "alignlib_fwd.h"
#include "alignlib_default.h"

namespace alignlib
{

/**
 *
 * @defgroup FactoryTreetor Factory functions for Treetor objects.
 * @{
 */

/** make a Treetor using linkage clustering methods.
 *
 * @param method @ref LinkageType
 * @return a new @ref Treetor object.
* */
HTreetor makeTreetorDistanceLinkage(
		const LinkageType & method = UPGMA );

/** make a Treetor using the neighbour-joining algorithm.
 *
 * @param distor @ref Distor object to compute distance.
 * @return a new @ref Treetor object.
 * */
HTreetor makeTreetorDistanceNJ();

/** @} */

/** @addtogroup Defaults
 * @{
 */

DEFINE_DEFAULT( HTreetor, getDefaultTreetor, setDefaultTreetor );

/** @} */
}

#endif	/* HELPERS_TREETOR_H */
