/*
  alignlib - a library for aligning protein sequences

  $Id: AlignmentIterator.h,v 1.3 2004/03/19 18:23:39 aheger Exp $

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

#ifndef ALIGNATA_ITERATOR_H
#define ALIGNATA_ITERATOR_H 1

#include <iosfwd>
#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

    /** @short Class for constant iterators over Alignment objects.
     *
     * The AlignmentIterator classes take any of the
     * iterators of aligned pairs of alignata-objects (see @ref Alignata::Iterator)
	 * and converts it into an iterator that is STL-compatible in its syntax (i.e.
	 * no overloading, etc.).
	 *
	 * There are two additional indirections:
	 * @ref AlignmentIterator -> Alignment::Iterator -> container iterator
	 *
	 *
		@author Andreas Heger
		@version $Id: AlignmentIterator.h,v 1.3 2004/03/19 18:23:39 aheger Exp $
		@ref Alignment
    */

class AlignmentIterator
{
 public:
    AlignmentIterator() : mIterator(NULL) {};

    AlignmentIterator( Alignment::Iterator * it) : mIterator(it) {} ;

    AlignmentIterator( const AlignmentIterator & src ) { mIterator = src.mIterator->getClone();};

    ~AlignmentIterator() { delete mIterator; };

    /** assignment operator */
    inline AlignmentIterator & operator=( const AlignmentIterator & other )
    {
    	if (this != &other)
    	{
    		/* mIterator = other.mIterator; does not work, I guess, because of shallow copying */
    		delete mIterator;
    		mIterator = other.mIterator->getClone();
    	}
      return *this;
    }

    /** comparison operator */
    inline bool operator==( const AlignmentIterator & other) const
    {
    	// according to STL the following invariant holds:
    	// x == y if and only if &*x == &*y
      return ( (*mIterator).getPointer() == (*other.mIterator).getPointer() );
    }

    /** comparison operator */
    inline bool operator!=( const AlignmentIterator & other) const
    {
      return ( (*mIterator).getPointer() != (*other.mIterator).getPointer() );
    }

    /** indirection operator */
    inline const ResiduePair * operator->() const
    {
    	return &(mIterator->getReference());
    }

    /** dereference operator */
    inline const ResiduePair & operator*() const
    {
    	return mIterator->getReference();
    }

    /** prefix ++ operator */
    inline AlignmentIterator & operator++()
    {
    	mIterator->next(); return *this;
    }

    /** postfix ++ operator */
    inline AlignmentIterator operator++(int)
    {
    	AlignmentIterator tmp = *this; mIterator->next(); return tmp;
    }

    /** prefix -- operator */
    inline AlignmentIterator & operator--()
    {
    	mIterator->previous(); return *this;
    }

    /** postfix -- operator */
    inline AlignmentIterator  operator--(int)
    {
      AlignmentIterator tmp = *this; mIterator->previous(); return tmp;
    }

 private:

	 // Todo: check if a reference will suffice.
    Alignment::Iterator * mIterator;
};



}

#endif /* _ALIGNATA_H */

