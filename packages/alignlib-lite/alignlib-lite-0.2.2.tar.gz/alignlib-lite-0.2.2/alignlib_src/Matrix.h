/*
  alignlib - a library for aligning protein sequences

  $Id: Matrix.h,v 1.2 2004/01/07 14:35:37 aheger Exp $

  Copyright (C) 2004 Andreas Heger

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef MATRIX_H
#define MATRIX_H 1

#include <iostream>
#include <cassert>
#include <cstring>
#include <vector>
#include <algorithm>
#include <boost/shared_ptr.hpp>
#include "Macros.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{

	/** @short A simple templated, fixed-size matrix.
	 *
	 * Data is stored as a contiguous array in row/column order.
	 *
	 * @author Andreas Heger
   	 * @version $Id$
	 */

template <class T>
class Matrix : public ImplAlignlibBase
{

	typedef typename boost::shared_ptr< Matrix<T> >HMatrix;

public:
	Matrix (unsigned int r, unsigned int c, T default_value = 0) :
		AlignlibBase()
	{
		mRows = r;
		mCols = c;
		mSize = mRows * mCols;
		mMatrix = new T [mSize];
		for (unsigned int i = 0; i < mSize; i++)
			mMatrix[i] = default_value;
	}

	/** copy constructor.
	 */
	Matrix (const Matrix <T>& src) : ImplAlignlibBase(src),
		mRows(src.mRows), mCols(src.mCols), mSize(src.mSize)
		{
		mMatrix  = new T [mSize];
		memcpy( mMatrix, src.mMatrix, sizeof(T) * mSize );
		}

	/** destructor
	 */
	~Matrix() { delete [] mMatrix; }

	/** return a copy of this object */
	HMatrix getClone() const { return HMatrix(new Matrix<T>(*this) ); }

	/** return a new object of the same type */
	HMatrix getNew() const { return HMatrix(new Matrix<T>(mRows,mCols) ); }

	T* operator[](unsigned int row)
	{
		assert( row < mRows && row >= 0);
		return &mMatrix[(row * mCols)];
	}

	const T* operator[](unsigned int row) const
	{
		assert( row < mRows );
		return (&mMatrix[(row * mCols)]);
	}

	T getValue( unsigned int row, unsigned int col) const
	{
		assert( row < mRows);
		assert( col < mCols);
		return mMatrix[(row * mCols) + col ];
	}

	void addValue( unsigned int row, unsigned int col, const T & value)
	{
		assert( row < mRows );
		assert( col < mCols );
		mMatrix[(row * mCols) + col] += value;
	}

	void setValue( unsigned int row, unsigned int col, const T & value)
	{
		assert( row < mRows );
		assert( col < mCols );
		mMatrix[(row * mCols) + col] = value;
	}


	/** assignment operator
	 */
	Matrix& operator= (const Matrix <T>&  src)
	{
		if (src == *this) return (*this) ; // protect against self assignment
		mRows=src.mRows;
		mCols=src.mCols;
		mSize=mRows*mCols;

		mMatrix  = new T [mSize];
		memcpy( mMatrix, src.mMatrix, sizeof( T) * mSize );

		return (*this);
	}


	/** equality operator.
	 *
	 * @return true, if the matrices are element-wise identical.
	 */
	bool operator==(const Matrix<T>& other) const
	{
		if (mRows != other.mRows) return false;
		if (mCols != other.mCols) return false;
		for (unsigned int i = 0; i < mSize; i++)
			if (mMatrix[i] != other.mMatrix[i]) return false;
		return true;
	}

	/** return the number of rows in matrix.
	 * @return number of rows.
	 */
	unsigned int getNumRows() const { return mRows; }

	/** return the number of columns in matrix.
	 * @return number of columns.
	 */
	unsigned int getNumCols() const { return mCols; }

	/** return pointer to raw data.
	 *
	 * This is a dangerous convenience function.
	 *
	 * @return pointer to raw data.
	 */
	T * getData()  const
	{
		return mMatrix;
	}

	/** set new data matrix.
	 *
	 * This a dangerous convenience function.
	 * The old memory is not released.
	 *
	 * @param matrix pointer to new data.
	 * */
	void setData( T * matrix )
	{
		mMatrix = matrix;
	}

	/** copy data.
	 *
	 * This functions copies as many bytes as it needs.
	 * @param pointer to data to copy.
	 * */
	void copyData( T * matrix )
	{
		memcpy( mMatrix, matrix, sizeof(T) * mSize );
	}

	/** return pointer to start of a given row
	 *
	 * @param row row.
	 * @return pointer to data in row.
	 */
	T * getRow( unsigned int row) const
	{
		return &mMatrix[ row * mCols ];
	}

	/** swap two rows.
	 *
	 * @param x row.
	 * @param y row.
	 */
	void swapRows( unsigned int x, unsigned int y)
	{
		if (x == y) return;
		assert( x >= 0);
		assert( y >= 0);
		assert( x < mRows);
		assert( y < mRows);
		T * buffer = new T[mCols];
		size_t s = sizeof(T) * mCols;
		memcpy( buffer,             &mMatrix[x*mCols], s );
		memcpy( &mMatrix[x*mCols], &mMatrix[y*mCols], s );
		memcpy( &mMatrix[y*mCols], buffer           , s );
		delete [] buffer;
	}

	/** permute rows in matrix.
	 *
	 * Creates a new matrix by mapping old rows to new rows
	 * using the map in map_new2old.
	 *
	 * This is efficient, as the matrix is arranged by rows
	 * and can thus proceed row-wise.
	 *
	 * @param	map_new2old 	map that specifies which old row to take
	 * 							for a new row.
	 */
	void permuteRows( std::vector < unsigned int > & map_new2old )
	{
		assert( *(std::max_element( map_new2old.begin(), map_new2old.end())) < mRows );

		T * old_matrix = mMatrix;

		mRows = map_new2old.size();
		mSize = mRows * mCols;
		mMatrix = new T[mSize];

		for (unsigned int r = 0; r < mRows; ++r)
			memcpy( &mMatrix[r * mCols],
					&old_matrix[map_new2old[r] * mCols],
					sizeof(T) * mCols );
		delete [] old_matrix;
	}

	/** permute rows in matrix.
	 *
	 * Creates a new matrix by mapping old columns to new columns.
	 * using the map in map_new2old.
	 *
	 * This is less efficient as @ref mapRows, as the matrix is arranged in rows
	 * and copying thus proceeds element-wise.
	 *
	 * @param	map_new2old 	map that specifies which old column to take
	 * 							for a new column.
	 */
	void permuteCols( std::vector< unsigned int> & map_new2old )
	{
		assert( *(std::max_element( map_new2old.begin(), map_new2old.end())) < mCols );

		unsigned int old_cols = mCols;
		T * old_matrix = mMatrix;

		mCols = map_new2old.size();
		mSize = mRows * mCols;
		mMatrix = new T[mSize];

		for (unsigned int c = 0; c < mCols; ++c)
		{
			unsigned int m  = map_new2old[c];
			for (unsigned int r = 0; r < mRows; ++r)
				setValue( r,c, old_matrix[ r * old_cols + m] );
		}
		delete [] old_matrix;
	}

private:

	/** data location */
	T * mMatrix;
	/** rows in matrix */
	unsigned int mRows;
	/** columns in matrix */
	unsigned int mCols;
	/** size of matrix */
	unsigned int mSize;

};


/** write a matrix to stream (human readable)
 *
 * The format is a simple tab-separated format. The first
 * lines contains the number of rows and columns.
 *
 * @param out stream to output matrix into.
 * @param src matrix to output.
 * @return the output stream.
 */
template<class T>
std::ostream & operator<< (std::ostream & out, const Matrix<T> & src)
{
	std::cout << src.getNumRows() << " " << src.getNumCols() << std::endl;
	for (unsigned int i = 0; i < src.getNumRows(); i++)
	{
		for (unsigned int j = 0; j < src.getNumCols(); j++)
		{
			out << src[i][j] << "\t";
		}
		out << std::endl;
	}
	return out;
}

/** read a matrix to stream.
 *
 * The format is a simple tab-separated format. The first
 * lines contains the number of rows and columns.
 *
 * @param out stream to input matrix from
 * @param src matrix to input to.
 * @return the input stream.
 */
template<class T>
std::istream & operator>>(std::istream & input, Matrix<T> & target)
{
	input >> target.mNumRows >> target.mNumCols;
	target.mSize = target.mNumRows * target.mNumCols;
	delete [] target.mMatrix;

	unsigned int z = 0;
	for (unsigned int i = 0; i < target.getNumRows(); i++)
		for (unsigned int j = 0; j < target.getNumCols(); j++, ++z)
			input >> target.mMatrix[z];
	return input;
}





}
#endif
