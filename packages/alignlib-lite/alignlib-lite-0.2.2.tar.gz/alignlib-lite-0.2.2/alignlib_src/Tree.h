//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: Tree.h,v 1.3 2004/06/02 12:14:35 aheger Exp $
//--------------------------------------------------------------------------------

#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef TREE_H
#define TREE_H 1

#include <iosfwd>
#include <string>
#include <vector>
#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

/**
    @short Protocol class for binary rooted trees.

    The height of a vertex/node is measured as distance
    from the root.

    Vertices in the tree are identified by numerical indices.

    This class is a protocol class and as such defines only the general interface.

    @author Andreas Heger
    @version $Id: Tree.h,v 1.3 2004/06/02 12:14:35 aheger Exp $
*/

class Tree : public virtual AlignlibBase
{

  /* friends---------------------------------------------------------------------------- */
  friend std::ostream & operator<<( std::ostream &, const Tree &);

  /* class member functions-------------------------------------------------------------- */
 public:

  /* constructors and desctructors------------------------------------------------------- */
  Tree();

  /** copy constructor */
  Tree (const Tree & src);

  /** destructor */
  virtual ~Tree ();

  DEFINE_ABSTRACT_CLONE( HTree )

  /* member access functions--------------------------------------------------------------- */

  /** returns the number of leaves */
  virtual Node getNumLeaves() const = 0;

  /** set the number of leaves in the tree.
   *
   * This erases the Tree and allocates memory
   	 for a new one with num_leaves leaves
   	@param num_leaves number of leaves in tree.
   */
  virtual void setNumLeaves( unsigned int num_leaves ) = 0;

  /** set the height of a vertex
   *
   * @param node tree node.
   * @param height height of the vertex (measured from root).
   * */
  virtual void setHeight( Node node, TreeHeight height ) = 0;

  /** get the height of a vertex
   *
   * @param node tree node.
   * @return the height of a vertex.
   * */
  virtual TreeHeight getHeight( Node node ) const = 0;

  /** set the weight of an edge between parent and child.
   * @param child	child
   * @param parent  parent
   * @param weight 	weight for edge
   * */
  virtual void setWeight(
		  	Node child,
		  	Node parent,
		  	TreeWeight weight ) = 0;

  /** get the weight of an edge between parent and child.
   * @param child	child
   * @param parent  parent
   * @return the edge weight between parent and child.
   * */
  virtual TreeWeight getWeight(
		  Node child,
		  Node parent ) const = 0;

  /** returns the empty node
   */
  virtual Node getNoNode() const = 0;

  /** returns the root of the tree.
   * @return the root of the tree.
   */
  virtual Node getRoot() const = 0;

  /** returns the parent of a node
   * @param node tree node
   * @return the parent of a node
   */
  virtual Node getParent( Node node ) const = 0;

  /** returns the left child of a node
   * @param node tree node
   * @return the left child of a node.
   * */
  virtual Node getLeftChild( Node node ) const = 0;

  /** returns the right of a node
   * @param node tree node
   * @return the right child of a node.
   * */
  virtual Node getRightChild( Node node ) const = 0;

  /** returns the number of leaves of a node
   *
   * @param node tree node
   * @return the total amount of leaves under a node.
   * */
  virtual Node getNumLeaves( Node node ) const = 0;

  /** returns a vector with the leaf nodes
   * @return a vector of leaf nodes.
   * */
  virtual HNodeVector getNodesLeaves() const = 0;

  /** returns a vector of nodes sorted according to breadth-first-traversal,
   * first encounter
   * @return a vector of nodes.
   * */
  virtual HNodeVector getNodesBreadthFirstVisit() const = 0;

  /** returns a vector of nodes sorted according to depth-first-traversal,
   * first encounter
   * @return a vector of nodes.
   * */
  virtual HNodeVector getNodesDepthFirstVisit() const = 0;

  /** returns a vector of nodes sorted according to depth-first-traversal,
   * last encounter
   * @return a vector of nodes.
   * */
  virtual HNodeVector getNodesDepthFirstFinish() const = 0;

  /* ---------------------------------------------------------------------------------------- */
  /** removes the root */
  virtual void removeRoot() = 0 ;

  /** sets the root */
  virtual Node setRoot(
		  const Node node_1,
		  const Node node_2,
		  TreeWeight weight ) = 0;

  /** find the last parent for node.
   *
   * If the tree is fully built, this function will return
   * the root of the tree.
   *
   * @param node to start search with.
   * @return a node.
   */
  virtual Node findLastParent( const Node node ) const = 0;

  /** @brief join two nodes to create a new node.
   *
   * Add a node to a tree for bottom-up construction, i.e. a construction which starts by
   	joining leaves. This function returns a reference to the internal node that was just
    created from two already existing nodes.

    @param node_1	node which is joined
    @param node_2	node which is joined
    @param weight_1	weight of edge 1 to new node
    @param weight_2	weight of edge 2 to new node
    @return the newly create node.
  */
  virtual Node joinNodes(
		  const Node node_1,
		  const Node node_2,
		  const TreeWeight weight_1,
		  const TreeWeight weight_2 ) = 0;

  virtual void write( std::ostream & output ) const = 0;

};

}

#endif /* TREE_H */

