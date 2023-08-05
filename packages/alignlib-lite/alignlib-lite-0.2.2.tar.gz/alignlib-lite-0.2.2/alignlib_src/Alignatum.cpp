/*
  alignlib - a library for aligning protein sequences

  $Id: Alignatum.cpp,v 1.2 2004/01/07 14:35:32 aheger Exp $

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


#include <iostream>
#include <iomanip>
#include "Alignatum.h"

#ifdef WITH_DMALLOC
#include <dmalloc.h>
#endif

using namespace std;

namespace alignlib {

//--------------------------------------------------------------------------------------
Alignatum::Alignatum() {
}    

//--------------------------------------------------------------------------------------
Alignatum::~Alignatum () {
}

//--------------------------------------------------------------------------------------
Alignatum::Alignatum(const Alignatum & src) {
}
   
std::ostream & operator<<( std::ostream & output, const Alignatum & src) {
  src.write( output );
  return output;
}

std::istream & operator>>( std::istream & input, Alignatum & target) {
  target.read( input );
  return input;
}

} // namespace alignlib
