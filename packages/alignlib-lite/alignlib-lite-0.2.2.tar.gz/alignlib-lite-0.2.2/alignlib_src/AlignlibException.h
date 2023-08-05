/*
  alignlib - a library for aligning protein sequences

  $Id: AlignlibException.h,v 1.2 2004/01/07 14:35:31 aheger Exp $

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

#ifndef _ALIGNEXCEPTION_H
#define _ALIGNEXCEPTION_H 1
#include <exception>
#include <sstream>

namespace alignlib
{

/**
   Base class for exceptions thrown by alignlib.


   @author Andreas Heger
   @version $Id: AlignlibException.h,v 1.2 2004/01/07 14:35:31 aheger Exp $
   @short Base class for exceptions thrown by alignlib.

*/
class AlignlibException : public std::exception
{
 public:
	AlignlibException( const char *);

	AlignlibException( const std::string & message );

    virtual const char * what() const throw();

    virtual ~AlignlibException() throw();

 private:
	 std::string mMessage;
};

/** convenience conversion function for constructing error messages
 */
template <class T>
std::string toString(T t)
{
  std::ostringstream oss;
  oss << t;
  return oss.str();
}

#define THROW( msg ) \
	throw AlignlibException( std::string(__FILE__) + ":" + toString(__LINE__) + ":" + std::string(__FUNCTION__) + "(): " + msg);

}

#endif /* _ALIGNEXCEPTION_H */

