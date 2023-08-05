/*
  alignlib - a library for aligning protein sequences

  $Id: alignlibMethods.h,v 1.2 2004/01/07 14:35:31 aheger Exp $

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

#ifndef ALIGNLIB_METHODS_H
#define ALIGNLIB_METHODS_H 1

// define a combination algorithm in STL-style

//compare all objects in two containers with each other using an alignator-function object
//the result type used is _ResultType

template < 
    class _ResultType,
    class _InputIter1, 
    class _InputIter2, 
    class _OutputIter,
    class _Operation>
_OutputIter allvsall(
		     _InputIter1 __first1, _InputIter1 __last1,
		     _InputIter2 __first2, _InputIter2 __last2,
		     _OutputIter __result,
		     _Operation  __operation ) {
  for (  ; __first1 != __last1; ++__first1) {
    _InputIter2 x; 
    for ( x = __first2; x != __last2; ++x, ++__result) {
      *__result = (_ResultType*)__operation(*__first1, *x, new _ResultType);		// upcast, potentially dangerous
    }
  }
  return __result;
}

template < class _InputIter1 >
void clearall( _InputIter1 __first1, _InputIter1 __last1 ) {
    for (  ; __first1 != __last1; ++__first1) {
	delete *__first1;
    }
}


//now call a different function object for all objects in two containers
template <class _InputIter1, class _InputIter2, class _OutputIter, class _FunctionIter>
_OutputIter map_allvsall(
			 _InputIter1 __first1, _InputIter1 __last1,
			 _InputIter2 __first2, _InputIter2 __last2,
			 _OutputIter __result,
			 _FunctionIter __func ) {
    
  for (  ; __first1 != __last1; ++__first1) {
    _InputIter2 x; 
    for ( x = __first2; x != __last2; ++x, ++__result) {
      *__result = (*__func)->operator()(*__first1, *x);
      __func++;
    }
  }
  return __result;
}

//compare all objects in one containter with each other using an alignator-function object, but perform
//just (n-1) * n comparisons
template < class _ResultType,
  class _InputIter1, 
  class _OutputIter,
  class _BinaryOperation
>
_OutputIter allvsall_unique(
			    _InputIter1 __first1, _InputIter1 __last1,
			    _OutputIter __result,
			    _BinaryOperation __binary_op) {
  _InputIter1 i, j; 
  for ( i = __first1 ; i != __last1 - 1; ++i) {
    for ( j = i+1; j != __last1; ++j, ++__result) {
      __binary_op.Set_Alignment( new _ResultType );
      *__result = (_ResultType*)__binary_op(*i, *j);		// upcast, potentially dangerous
    }
  }
  return __result;
}

#endif /* _METHODS_H */

