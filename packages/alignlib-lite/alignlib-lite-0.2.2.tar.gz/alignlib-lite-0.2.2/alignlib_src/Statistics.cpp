/*
  alignlib - a library for aligning protein sequences

  $Id: Statistics.cpp,v 1.3 2004/01/07 14:35:37 aheger Exp $

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

#include <math.h>

#include <iostream>
#include <fstream>
#include <iomanip>
#include <vector>
#include <algorithm>

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "alignlib_fwd.h"
#include "AlignlibDebug.h"
#include "Alignator.h"
#include "Alignment.h"
#include "HelpersAlignment.h"
#include "Alignandum.h"
#include "Statistics.h"

using namespace std;

namespace alignlib 
{

/** factory functions */
NormalDistributionParameters * makeNormalDistributionParameters() { 
  return new NormalDistributionParameters; 
}

EVDParameters * makeEVDParameters() {
  return new EVDParameters;
}

//---------------------------------------------------------------
Score * fillScoresVector( Score * dest,
			     const HAlignandum & row, 
			     const HAlignandum & col, 
			     const HAlignator & alignator,
			     unsigned int n_iterations,
			     unsigned int n_iterations_shuffle = 1,
			     Position window_size = 0) 
			     {

  HAlignandum clone = row->getClone();
  HAlignment ali = makeAlignmentVector();
  
  for (unsigned int i = 0; i < n_iterations; i++) 
  {
    clone->shuffle( n_iterations_shuffle, window_size );
    alignator->align( ali, clone, col );
    dest[i] = ali->getScore();
  }
    
  return dest;
}


/*---------------> other functions <----------------------------- */
void calculateZScoreParameters( 
		NormalDistributionParameters * result,
		const HAlignandum & row, 
		const HAlignandum & col, 
		const HAlignator & alignator,
		unsigned int n_iterations,
		unsigned int n_iterations_shuffle,
		Position window_size) 
{

  unsigned int i;
  double total;
  double m, s;

  Score * scores = new Score[n_iterations];
  fillScoresVector( scores, row, col, alignator, n_iterations, n_iterations_shuffle, window_size );
    
  /* calculate mean */
  total = 0; for (i = 0; i < n_iterations; i++) total+= (double)scores[i];
  m = total / (double)n_iterations;
    
  /* calculate standard-deviation */
  total = 0; for (i = 0; i < n_iterations; i++) total+= ((double)scores[i] - m) * ((double)scores[i] - m);
  s = sqrt( total / (double)n_iterations);
    
  result->mMean = m;
  result->mStandardDeviation = s;
  
  delete [] scores;
}
   
  

    
} // namespace alignlib






