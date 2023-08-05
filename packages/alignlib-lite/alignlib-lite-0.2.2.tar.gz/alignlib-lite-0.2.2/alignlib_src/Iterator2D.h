/*
  alignlib - a library for aligning protein sequences

  $Id: Fragmentor.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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

#ifndef ITERATOR2D_H
#define ITERATOR2D_H 1

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"
#include <vector>

namespace alignlib
{

template< class T>
class const_countable_iterator : public std::iterator< std::random_access_iterator_tag, T>
{
public:

	typedef const T value_type;
	typedef const T & reference;

	const_countable_iterator(const T & v) : mValue(v) {}
	const_countable_iterator( const const_countable_iterator & src ) : mValue(src.mValue) {}
	~const_countable_iterator() {}

	/** assignment operator */
	inline const_countable_iterator & operator=( const const_countable_iterator & src ) {
		if (*this != src)
			mValue(src.mValue);
		return *this;
	}

	/** comparison operator */
	inline bool operator==( const const_countable_iterator & other) const {
		return ( (mValue) == (other.mValue));
	}
	/** comparison operator */
	inline bool operator!=( const const_countable_iterator & other) const {
		return ( (mValue) != (other.mValue));
	}

	/** indirection operator */
	inline const T operator->() const { return mValue; }

	/** dereference operator */
	inline const T & operator*() const { return mValue; }

	/** prefix ++ */
	inline const_countable_iterator & operator++() { ++mValue; return *this; }

	/** postfix ++ */
	inline const_countable_iterator operator++(int) { mValue++; return mValue-1; }

	/** prefix -- */
	inline const_countable_iterator & operator--() { --mValue; return *this;}

	/** postfix -- */
	inline const_countable_iterator operator--(int) { mValue--; return mValue+1; }
private:
	T mValue;
};

/**
   @short Protocoll class for 2D iterators.

	2D iteratores iterate over a matrix in row/column order. They are
	used by @ref Alignator objects to restrict the dynamic programming
	matrix.

   This class is a protocol class and as such defines only the general interface.

   @author Andreas Heger
   @version $Id: Fragmentor.h,v 1.3 2004/03/19 18:23:40 aheger Exp $
*/
class Iterator2D : public virtual AlignlibBase
{

public:

	typedef const_countable_iterator<Position> const_iterator;

	/** empty constructor */
	Iterator2D();

	/** destructor */
	virtual ~Iterator2D ();

	/** copy constructor */
	Iterator2D( const Iterator2D & src);

	DEFINE_ABSTRACT_CLONE( HIterator2D )

	/** return a new iterator of same type initialized with row and col
	 *
	 * @param row @ref Alignandum object.
	 * @param col @ref Alignandum object.
	 *
	 */
	virtual HIterator2D getNew( const HAlignandum & row, const HAlignandum & col ) const = 0;

	/** reset ranges of iterator for new row and col objects
	 *
	 * @param row @ref Alignandum object.
	 * @param col @ref Alignandum object.
	 */
	virtual void resetRanges( const HAlignandum & row, const HAlignandum & col ) = 0;

	/** return iterator over for particular column.
	 *
	 * @param col column to iterate over. If no position is given, the iteration is over
	 * 		the maximum range for any column.
	 * @return iterator pointing towards first element in row.
	 * */
	virtual const_iterator row_begin ( Position col = NO_POS ) const = 0;

	/** return iterator over for particular column.
	 *
	 * @param col column to iterate over. If no position is given, the iteration is over
	 * 		the maximum range for any column.
	 * @return iterator pointing towards the last element +1 in row.
	 * */
	virtual const_iterator row_end   ( Position col = NO_POS ) const = 0;

	/** return iterator over for particular row.
	 *
	 * @param row column to iterate over. If no position is given, the iteration is over
	 * 		the maximum range for any row.
	 * @return iterator pointing towards first element in col.
	 * */

	virtual const_iterator col_begin ( Position row = NO_POS ) const = 0;

	/** return iterator over for particular row.
	 *
	 * @param row column to iterate over. If no position is given, the iteration is over
	 * 		the maximum range for any row.
	 * @return iterator pointing towards last element + 1 in col.
	 * */
	virtual const_iterator col_end   ( Position row = NO_POS ) const = 0;

	/** return first element in a row.
	 *
	 * @param col column. If no position is given, the minimum row residue for any column is returned
	 * @return first residue in row.
	 * */
	virtual Position row_front ( Position col = NO_POS ) const = 0;

	/** return last element in a row.
	 *
	 * @param col column. If no position is given, the maximum row residue for any column is returned
	 * @return last residue in row.
	 * */
	virtual Position row_back  ( Position col = NO_POS ) const = 0;

	/** return first element in a colum.
	 *
	 * @param row row. If no position is given, the minimum column residue for any column is returned
	 * @return first residue in column.
	 * */
	virtual Position col_front ( Position row = NO_POS ) const = 0;
	/** return last element in a colum.
	 *
	 * @param row row. If no position is given, the maximum column residue for any column is returned
	 * @return last residue in column.
	 * */
	virtual Position col_back  ( Position row = NO_POS ) const = 0;

	/** return maximum row range for a column.
	 *
	 * @param col column. If no position is given, the maximum range over any column is returned.
	 * @return maximum range in col.
	 */
	virtual Position row_size( Position col = NO_POS ) const = 0;

	/** return maximum column range for a row.
	 *
	 * @param row row. If no position is given, the maximum range over any row is returned.
	 * @return maximum range in row.
	 */
	virtual Position col_size( Position row = NO_POS ) const = 0;

};

}

#endif /* ITERATOR2D_H */
