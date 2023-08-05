/*
  alignlib - a library for aligning protein sequences

  $Id: ImplWeightor.h,v 1.3 2004/03/19 18:23:41 aheger Exp $

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

#ifndef IMPL_MACROS_H
#define IMPL_MACROS_H 1

#define IMPLEMENT_CLONE(handle,cls) \
handle cls::getClone() const { debug_func_cerr(5); return handle( new cls( *this )); } \
handle cls::getNew() const { debug_func_cerr(5); return handle( new cls()); }

#define DEFINE_CLONE(handle) \
/** returns a copy of the object.
 * @param return a copy of this object
*/ \
virtual handle getClone() const; \
/** returns a new object of the same type
 * @param return an object of this class
 */ \
virtual handle getNew() const;

#define DEFINE_ABSTRACT_CLONE(handle) \
/** returns a copy of the object.
 * @param return a copy of this object
*/ \
virtual handle getClone() const = 0; \
/** returns a new object of the same type
 * @param return an object of this class
 */ \
virtual handle getNew() const = 0;

#endif
