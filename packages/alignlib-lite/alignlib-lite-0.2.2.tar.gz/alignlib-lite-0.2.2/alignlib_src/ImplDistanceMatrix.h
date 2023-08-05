//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplMatrix.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------

#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef IMPL_PHYLOMATRIX_H
#define IMPL_PHYLOMATRIX_H 1

#include <iosfwd>

#include "DistanceMatrix.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{

/**

   -> memory is allocated when the matrix is created and not given free, until it
   is deleted (i.e. no partial memory freeing during shrinks)

   @author Andreas Heger
   @version $Id: ImplMatrix.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
   @short contains a matrix
*/

  // i.e., for invalid requests return first element. This is bad, but
  // did not want to do all the checking
#define NO_INDEX 0

class ImplDistanceMatrix : public DistanceMatrix, public ImplAlignlibBase
{
 public:

  /* constructors and desctructors------------------------------------------------------- */

  /** empty constructor */
  ImplDistanceMatrix ();

  /** create DistanceMatrix of width and set all values to default_value */
  ImplDistanceMatrix( DistanceMatrixSize width, DistanceMatrixValue default_value);

  /** load array */
  ImplDistanceMatrix( DistanceMatrixSize width, DistanceMatrixValue * source);

  /** copy constructor */
  ImplDistanceMatrix (const ImplDistanceMatrix &);

  /** destructor */
  virtual ~ImplDistanceMatrix ();

  /* member access functions--------------------------------------------------------------- */
  /** return width of DistanceMatrix */
  virtual DistanceMatrixSize getWidth() const;

  /** sets the width of DistanceMatrix, old DistanceMatrix is deleted */
  virtual void setWidth(DistanceMatrixSize width);

  /** return size (rows * columns) of DistanceMatrix */
  virtual DistanceMatrixSize getSize() const;

  /** return the minimum value of the DistanceMatrix */
  virtual DistanceMatrixValue getMinimum() const;

  /** return the minimum value of the DistanceMatrix + coordinates */
  virtual DistanceMatrixValue getMinimum( Coordinate & coordinates) const;

  /** return the maximum value of the DistanceMatrix */
  virtual DistanceMatrixValue getMaximum() const;

  /** return the maximum value of the DistanceMatrix */
  virtual DistanceMatrixValue getMaximum( Coordinate & coordinates) const;

  /** return element */
  virtual DistanceMatrixValue operator()(DistanceMatrixSize row, DistanceMatrixSize col) const;
  virtual DistanceMatrixValue getElement(DistanceMatrixSize row, DistanceMatrixSize col) const;

  /** set element */
  virtual DistanceMatrixValue & operator()(DistanceMatrixSize row, DistanceMatrixSize col);
  virtual void setElement(DistanceMatrixSize row, DistanceMatrixSize col, DistanceMatrixValue value);

  /** swap two columns/rows */
  virtual void swap( DistanceMatrixSize col_1, DistanceMatrixSize col_2 ) = 0;

  /** shrink matrix by one */
  virtual void shrink() = 0;

  /** read information from stream */
  virtual void read ( std::istream & input ) const;

  virtual void write( std::ostream & output ) const;

 protected:

  /** get row for given index */
  virtual DistanceMatrixSize getRow( DistanceMatrixSize index ) const;

  /** get column for given index */
  virtual DistanceMatrixSize getColumn( DistanceMatrixSize index ) const;

  /** return mapped index for row and column */
  virtual DistanceMatrixSize getIndex(DistanceMatrixSize row, DistanceMatrixSize col) const;

  /** allocate memory */
  virtual void allocateMemory();

  /** allocate memory */
  virtual void freeMemory();

  /** calculate the memory size of the DistanceMatrix given its width*/
  virtual void calculateSize();

  /** the width of the DistanceMatrix */
  DistanceMatrixSize mWidth;

  /** the size of the DistanceMatrix in terms of elements of type TYPE_DistanceMatrix*/
  DistanceMatrixSize mSize;

  /** a pointer to the matrix */
  DistanceMatrixValue * mMatrix;

};


}

#endif /* _ALIGNATUMSEQUENCE_H */

