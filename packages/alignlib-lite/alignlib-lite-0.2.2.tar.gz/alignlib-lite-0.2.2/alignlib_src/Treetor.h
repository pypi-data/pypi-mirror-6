//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: Treetor.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------

#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef TREETOR_H
#define TREETOR_H 1

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{
/**
   base class for algorithms that generate trees. So far this class is empty

   This class is a protocoll class and as such only defines an empty
   interface.

   @author Andreas Heger
   @version $Id: Treetor.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
   @short Algorithm class that generates trees.
*/
class Treetor : public virtual AlignlibBase
{

  /* class member functions-------------------------------------------------------------- */
 public:

  /* constructors and desctructors------------------------------------------------------- */
  /** empty constructor */
  Treetor ();

  /** copy constructor */
  Treetor (const Treetor & src);

  /** destructor */
  virtual ~Treetor ();

  DEFINE_ABSTRACT_CLONE( HTreetor )

  /** create a tree from a multiple alignment */
  virtual void calculateTree( HTree & dest,
		  const HMultipleAlignment & src) const = 0;

};

}

#endif /* TREETOR_H */

