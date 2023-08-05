//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplTreetor.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------

#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef IMPL_TREETOR_H
#define IMPL_TREETOR_H 1

#include "alignlib_fwd.h"

#include "Treetor.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{

/**
   base class for algorithms that generate trees.

   This class is the base class of implementation of
   Treetor objects.

   @author Andreas Heger
   @version $Id: ImplTreetor.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
   @short Algorithm class that generates trees.
*/
class ImplTreetor : public Treetor
{

  /* class member functions-------------------------------------------------------------- */
 public:

  /* constructors and desctructors------------------------------------------------------- */

  /** empty constructor */
  ImplTreetor ();

  /** copy constructor */
  ImplTreetor (const ImplTreetor & src);

  /** destructor */
  virtual ~ImplTreetor ();

  /** create a tree from a multiple alignment */
  virtual void calculateTree(
		  HTree & dest,
		  const HMultipleAlignment & src ) const = 0;

 private:

};

}

#endif /* IMPL_TREETOR_H */

