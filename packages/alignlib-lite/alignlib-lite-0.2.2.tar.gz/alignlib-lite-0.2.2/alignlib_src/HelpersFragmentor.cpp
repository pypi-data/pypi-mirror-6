/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersFragmentor.cpp,v 1.2 2004/01/07 14:35:32 aheger Exp $

  
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
#include <math.h>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "Alignandum.h"

#include "AlignmentIterator.h"
#include "Alignment.h"
#include "HelpersAlignment.h"
#include "AlignmentFormat.h"

#include "HelpersSubstitutionMatrix.h"
#include "HelpersFragmentor.h"

using namespace std;

namespace alignlib 
{ 

  //-----------------------------------------------------------------------------------
  void writeFragments( 
		  std::ostream & output, 
		  const HFragmentVector & fragments) 
  {

    FragmentVector::const_iterator it(fragments->begin()), it_end(fragments->end());
    
    int i = 0;
    for (; it != it_end; ++it) 
    {
      output << "Fragment " << i++ << ": ";
      output << AlignmentFormatEmissions( *it ) << std::endl;
      output << endl;
    }
  }

  //-----------------------------------------------------------------------------------
  void rescoreFragmentsNumberGaps( 
		  HFragmentVector & fragments, 
		  Score gop, 
		  Score gep ) 
  {
    FragmentVector::iterator it(fragments->begin()), it_end(fragments->end());
    
    for (; it != it_end; ++it) {
      HAlignment fragment = *it;
      
      AlignmentIterator a_it(fragment->begin()), a_end(fragment->end());

      Score score = 0;
      Position last_row = (*a_it).mRow - 1;
      for (; a_it != a_end; ++a_it) {
	score += (*a_it).mScore;
	Position d;
	if ((d = (*a_it).mRow - last_row - 1) > 0)
	  score += gop + d * gep;
	last_row = (*a_it).mRow;
      }
      
      fragment->setScore( score );
    }
  }


} // namespace alignlib
