//--------------------------------------------------------------------------------
// Project LibPhylo
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: HelpersTree.cpp,v 1.2 2004/06/02 12:14:34 aheger Exp $
//--------------------------------------------------------------------------------

#include <iostream>
#include <string>
#include <vector>

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "Tree.h"
#include "HelpersTree.h"

using namespace std;

namespace alignlib
{

void writeNewHampshire(
		std::ostream & output,
		const HTree & tree,
		const HStringVector & labels )
{
	debug_func_cerr( 5 );

	Node node;
	std::vector<Node> node_stack;

	Node root = tree->getRoot();

	node_stack.push_back( root ); // push root on stack

	bool docomma = false;

	Node numleaves = tree->getNumLeaves();

	if (labels->size() > 0 && labels->size() != numleaves)
		throw AlignlibException( "writeNewHampshire: number of leaves and number of labels are different");

	Node last_interior_node = 2 * numleaves - 1;
	TreeWeight weight = 0;

	debug_cerr( 5, "starting traversal from root " << root << " with " << numleaves << " leaves" );

	while (!node_stack.empty())
	{

		node = node_stack.back();
		node_stack.pop_back();

		debug_cerr( 5, "Processing node " << node << " root=" << root );

		if (node != root && node < last_interior_node )
			weight = tree->getWeight( node, tree->getParent( node ));


		if (node < numleaves)
		{                   // process leaves: print name:branchlength
			if (docomma)
				output << ",";

			if (labels->size() > 0)
			{
				output << (*labels)[node];
			} else
			{
				output << node;
			}

			output << ":" << weight;
			docomma = true;

		}
		else
		{
			if (node <= last_interior_node)
			{             // process interior nodes
				if (docomma) output << "," << endl;

				// 1) print a '('
				output << "(";

				// 2) push on stack: ), right child, left child

				node_stack.push_back( node + numleaves );
				node_stack.push_back( tree->getRightChild(node) );
				node_stack.push_back( tree->getLeftChild(node) );

				// 3) record branch lengths
				docomma = false;

			}
			else
			{                                      // close interior node
				// print a ):branchlength (if root, just print ")" )
				if (node == root + numleaves)
				{
					output << ")\n";
				}
				else
				{
					node = node - numleaves;
					output << "):" << tree->getWeight( node, tree->getParent(node) );
				}

				docomma = true;
			}
		}
	}
}


} // namespace alignlib
