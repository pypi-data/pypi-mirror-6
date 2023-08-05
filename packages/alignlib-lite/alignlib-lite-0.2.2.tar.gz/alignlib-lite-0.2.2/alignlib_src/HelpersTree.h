//--------------------------------------------------------------------------------
// Project LibPhylo
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: HelpersTree.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef HELPERS_TREE_H
#define HELPERS_TREE_H 1

#include <iosfwd>
#include <string>
#include "alignlib_fwd.h"

namespace alignlib
{

/**
 *
 * @defgroup FactoryTree Factory functions for Tree objects.
 * @{
 */

/** create an empty tree.
 *
 * @param num_leaves number of leaves in tree.
 *
 * @return a new @ref Tree object.*/
HTree makeTree( const Node num_leaves = 0);

/** @} */

/** @defgroup ToolsetTree Toolset for Tree objects.
 * @{
 */

/** write a tree in NewHampshire format
 *
 * @param output output stream.
 * @param tree @ref Tree object to output.
 * @param labels optional vector to labels.
 *
 * */
void writeNewHampshire( std::ostream & output,
		const HTree & tree,
		const HStringVector & labels );

/** @} */
}

#endif	/* HELPERS_TREE_H */
