/*
  alignlib - a library for aligning protein sequences

  $Id: ImplLogOddorDirichlet.cpp,v 1.2 2004/01/07 14:35:35 aheger Exp $

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

// Actually this is a bit misleading, there is no new class here, just the data
// and the implementation of a factory function.

#include <iostream>
#include <iomanip>
#include <iterator>

#include "alignlib.h"
#include "ImplLogOddor.h"
#include "ImplRegularizorDirichlet.h"
#include "HelpersLogOddor.h"

namespace alignlib 
{

  /* these are the background frequencies as they result from the 9-component
     dirichlet mixture of Kimmen Sjoerlander (see file ImplRegularizorDirichlet for
     the complete mixture). The some of these is 1, I checked :=). 

     The 20 residues in here are sorted alphabetically.
  */

  static const char alphabet[ALPHABET_SIZE+1] = "ACDEFGHIKLMNPQRSTVWY";
  static const Frequency background[ALPHABET_SIZE] = 
  {     
      0.0804111, 0.0131282, 0.0479706, 0.0651176,  0.035627,
      0.0395005, 0.0229268, 0.0781316, 0.0706055,  0.0984159,
      0.0302298, 0.04398  , 0.0227958, 0.0455504,  0.0520589, 
      0.0672516, 0.0577926, 0.0920675, 0.00737194, 0.029067 
  };    

  HLogOddor makeLogOddorDirichlet( 
  		const Score & scale, 
  		const Score & mask_value )
  {
	  
	  HFrequencyVector frequencies(new FrequencyVector( ALPHABET_SIZE, 0.0));
	  for (int x = 0; x < ALPHABET_SIZE; ++x)
		  (*frequencies)[x] = background[x];
	  
  	  return makeLogOddorBackground( 
  			  frequencies,
  			  alphabet,
  			  scale, 
  			  mask_value );
  }

} // namespace alignlib
