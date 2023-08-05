//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplTree.h,v 1.3 2004/06/02 12:14:34 aheger Exp $
//--------------------------------------------------------------------------------

#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef IMPLTREE_H
#define IMPLTREE_H 1

#include <iosfwd>
#include <string>

#include "alignlib_fwd.h"
#include "Tree.h"
#include "ImplAlignlibBase.h"

// define new tags for our graphs attributes
// this has to go into the main namespace:
// enum vertex_predecessor_t	{ vertex_predecessor  = 300 };

namespace alignlib
{
/**
    Base class for trees.

    Trees are of course graphs. As such, they can be implemented using graph
    libraries (e.g., LEDA), or they can be implemented from scratch. If time
    permits, I will offer both choices.

    A tree is a weighted graph. Since it has a top node (root), each node has
    a height, which is a function of the weights of its children.

    This class is a protocol class and as such defines only the general interface.

    @author Andreas Heger
    @version $Id: ImplTree.h,v 1.3 2004/06/02 12:14:34 aheger Exp $
    @short protocol class for phylogenetic trees.
*/

#define NO_NODE 999999

struct NODE_INFO
{
  NODE_INFO() :
    mLeftChild(NO_NODE), mRightChild(NO_NODE), mParent(NO_NODE),
    mNumChildren(0), mWeight(0), mHeight(0) {};
  Node mLeftChild;
  Node mRightChild;
  Node mParent;
  std::size_t mNumChildren;
  TreeWeight mWeight;
  TreeHeight mHeight;
};

class ImplTree : public Tree, public ImplAlignlibBase
{

  /* friends---------------------------------------------------------------------------- */
  friend std::ostream & operator<<( std::ostream &, const ImplTree &);

  /* class member functions-------------------------------------------------------------- */
 public:

  /* constructors and desctructors------------------------------------------------------- */
  /** empty constructor */
  ImplTree ();

  /** create an empty tree, leaving space for num_leaves */
  ImplTree( std::size_t num_leaves);

  /** copy constructor */
  ImplTree (const ImplTree & src);

  /** destructor */
  virtual ~ImplTree ();

  //------------------------------------------------------------------------------------------------------------
  /** return a new object of the same type */
  virtual HTree getNew() const;

  /** return an identical copy */
  virtual HTree getClone() const;

  /* member access functions--------------------------------------------------------------- */

  /** returns the number of leaves */
  virtual Node getNumLeaves() const;

  /** sets the number of leaves. This erases the Tree and allocates memory
      for a new one with num_leaves leaves */
  virtual void setNumLeaves( unsigned int num_leaves );

  /** set the height of a vertex */
  virtual void setHeight( Node node, TreeHeight height );

  /** set the weight of an edge */
  virtual void setWeight( Node child, Node parent, TreeHeight weight );

  /** get the weight of an edge */
 virtual TreeWeight getWeight( Node child, Node parent ) const;

  /** get the height of a vertex */
  virtual TreeHeight getHeight( Node node ) const ;

  /** returns the empty node */
  virtual Node getNoNode() const;

  /** returns the root */
  virtual Node getRoot() const;

  /** returns the parent of a node */
  virtual Node getParent( Node node ) const;

  /** returns the left child of a node */
  virtual Node getLeftChild( Node node ) const;

  /** returns the right of a node */
  virtual Node getRightChild( Node node ) const;

  /** returns the number of children of a node */
  virtual Node getNumLeaves( Node node) const;

  /** returns a vector of leaves nodes */
  virtual HNodeVector getNodesLeaves() const;

  /** returns a vector of nodes sorted according to breadth-first-traversal,
   * first encounter */
  virtual HNodeVector getNodesBreadthFirstVisit() const;

  /** returns a vector of nodes sorted according to depth-first-traversal,
   * first encounter */
  virtual HNodeVector getNodesDepthFirstVisit() const;

  /** returns a vector of nodes sorted according to depth-first-traversal,
   * last encounter */
  virtual HNodeVector getNodesDepthFirstFinish() const;

  /* ---------------------------------------------------------------------------------------- */
  /** removes the root */
  virtual void removeRoot();

  /** sets the root */
  virtual Node setRoot( const Node node_1,
			     const Node node_2,
			     TreeWeight weight ) ;

  /** find root */
  virtual Node findLastParent( const Node node ) const;

  /** Add a node to a tree for bottom-up construction, i.e. a construction which starts by
      joining leaves. This function returns a reference to the internal node that was just
      created from two already existing nodes.

      @param node_1	node which is joined
      @param node_2	node which is joined
      @param weight_1	weight of edge 1 to new internal node
      @param weight_2	weight of edge 2 to new internal node
  */
  virtual Node joinNodes(
		  const Node node_1,
		  const Node node_2,
		  const TreeWeight weight_1,
		  const TreeWeight weight_2 );


  virtual void write( std::ostream & output ) const;

 private:

  /** number of leaves in the tree */
  int mNumLeaves;

  /** current free vertex */
  Node mCurrentNode;

  /** the tree */
  NODE_INFO * mTree;

  /** mark Leaves, i.e. set number of children for each leaf as one */
  virtual void recordLeaves() ;

  /** helper function for recursive postorder traversal */
  void traversePostOrder( Node node, HNodeVector & nodes) const;

};

}

#endif /* IMPLTREE_H */






