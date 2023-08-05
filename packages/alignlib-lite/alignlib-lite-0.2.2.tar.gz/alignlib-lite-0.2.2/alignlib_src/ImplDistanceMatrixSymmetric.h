//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplDistanceMatrixSymmetric.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------

#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef IMPL_PHYLOMATRIX_SYMMETRIC_H
#define IMPL_PHYLOMATRIX_SYMMETRIC_H 1

#include <iosfwd>

#include "ImplDistanceMatrix.h"

namespace alignlib {

/**

   @author Andreas Heger
   @version $Id: ImplDistanceMatrixSymmetric.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
   @short contains a DistanceMatrix
*/

class ImplDistanceMatrixSymmetric : public ImplDistanceMatrix {
 public:

  /* constructors and desctructors------------------------------------------------------- */

  /** empty constructor */
  ImplDistanceMatrixSymmetric ();

  /** create DistanceMatrix of width and set all values to default_value */
  ImplDistanceMatrixSymmetric( DistanceMatrixSize width, DistanceMatrixValue default_value);

  /** load array */
  ImplDistanceMatrixSymmetric( DistanceMatrixSize width, DistanceMatrixValue * source);

  /** copy constructor */
  ImplDistanceMatrixSymmetric (const ImplDistanceMatrixSymmetric &);

  /** destructor */
  virtual ~ImplDistanceMatrixSymmetric ();

  DEFINE_CLONE( HDistanceMatrix );

  /* member access functions--------------------------------------------------------------- */

  /** delete last row/column from DistanceMatrix */
  virtual void shrink();

  /** swap two columns/rows */
  virtual void swap( DistanceMatrixSize col_1, DistanceMatrixSize col_2 );

 protected:

  /** get row for given index */
  virtual DistanceMatrixSize getRow( DistanceMatrixSize index ) const;

  /** get column for given index */
  virtual DistanceMatrixSize getColumn( DistanceMatrixSize index ) const;

  /** return mapped index for row and column */
  virtual DistanceMatrixSize getIndex(DistanceMatrixSize row, DistanceMatrixSize col) const;

  /** calculate the size of the DistanceMatrix */
  virtual void calculateSize();

};


}

#endif /* _ALIGNATUMSEQUENCE_H */

