//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: Matrix.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------

#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef PHYLOMATRIX_H
#define PHYLOMATRIX_H 1

#include <iostream>
#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

/**
 * @brief Protocoll class for distance or similarity matrices.
 *
   Distance and similarity matrices are symmetric. The matrices
   are indexed first by row, then by column.

   @author Andreas Heger
   @version $Id: Matrix.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
*/

class DistanceMatrix : public virtual AlignlibBase
{
  /* friends---------------------------------------------------------------------------- */
  friend std::ostream & operator<<( std::ostream &, const DistanceMatrix &);

  /* class member functions-------------------------------------------------------------- */
 public:

  /* constructors and desctructors------------------------------------------------------- */

  /** empty constructor */
  DistanceMatrix ();

  /** copy constructor */
  DistanceMatrix (const DistanceMatrix &);

  /** destructor */
  virtual ~DistanceMatrix ();

  DEFINE_ABSTRACT_CLONE( HDistanceMatrix )

  /* member access functions--------------------------------------------------------------- */

  /** return the width of matrix.
   *
   * @return a width
   */
  virtual DistanceMatrixSize getWidth() const = 0;

  /** sets the width of the matrix.
   *
   * This resets the matrix and deletes old content.
   *
   * @param width new width.
   * */
  virtual void setWidth(DistanceMatrixSize width) = 0;

  /** return the size (rows * columns) of the matrix.
   *
   * @return a size
   * */
  virtual DistanceMatrixSize getSize() const = 0;

  /** return the minimum value
   *
   * @return a value */
  virtual DistanceMatrixValue getMinimum() const = 0;

  /** return the minimum element.
   *
   * @param dest coordinates of minimum element.
   *
   * @return a value*/
  virtual DistanceMatrixValue getMinimum( Coordinate & dest) const = 0;

  /** return the maximum value.
   *
   * @return a value.
   * */
  virtual DistanceMatrixValue getMaximum() const = 0;

  /** return the maximum element.
   *
   * @param dest coordinates of maximum element.
   *
   * @return a value.
   * */
  virtual DistanceMatrixValue getMaximum( Coordinate & dest) const = 0;

  /** return value at coordinate.
   *
   * @param row row.
   * @param col col.
   * @return a value.
   * */
  virtual DistanceMatrixValue operator()(DistanceMatrixSize row, DistanceMatrixSize col) const = 0;

  /** return value at coordinate.
     *
     * @param row row.
     * @param col col.
     * @return a value.
     * */
    virtual DistanceMatrixValue getElement(DistanceMatrixSize row, DistanceMatrixSize col) const = 0;

    /** set value at coordinate.
         *
         * @param row row.
         * @param col col.
         * @return a value.
         * */

  virtual DistanceMatrixValue & operator()(DistanceMatrixSize row, DistanceMatrixSize col) = 0;

  /** set value at coordinate.
   *
   * @param row row.
   * @param col col.
   */
  virtual void setElement(DistanceMatrixSize row, DistanceMatrixSize col, DistanceMatrixValue value) = 0;

  /** swap two rows and columns.
   *
   * This function will swap both rows and columns such that
   * the resulting matrix is still symmetric.
   *
   * @param a	first row to swap.
   * @param b	second row to swap.
   * */
  virtual void swap(
		  DistanceMatrixSize a,
		  DistanceMatrixSize b ) = 0;

  /** shrink matrix.
   *
   * This function removes the last row and column.
   *
   * */
  virtual void shrink() = 0;

  /** read data from stream
   *
   * @param input input stream.
   * */
  virtual void read ( std::istream & input ) const = 0;

  /** save data into stream
   *
   * @param output output stream.
   * */
  virtual void write( std::ostream & output ) const = 0;

};

}

#endif /* _PHYLOMATRIX_H */

