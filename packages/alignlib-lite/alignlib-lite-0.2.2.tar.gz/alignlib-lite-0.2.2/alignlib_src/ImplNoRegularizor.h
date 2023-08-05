/*
  alignlib - a library for aligning protein sequences

  $Id: ImplNoRegularizor.h,v 1.2 2004/01/07 14:35:35 aheger Exp $

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

#ifndef IMPL_NO_REGULARIZOR_H
#define IMPL_NO_REGULARIZOR_H 1

#include "alignlib_fwd.h"
#include "Regularizor.h"

namespace alignlib 
{

  /** Implementation of a class that regularizes count columns.
      
      @author Andreas Heger
      @version $Id: ImplNoRegularizor.h,v 1.2 2004/01/07 14:35:35 aheger Exp $
      @short protocol class for sequence weighters
      
  */

class ImplNoRegularizor : public Regularizor 
{
 public:
    // constructors and desctructors

    /** default constructor */
    ImplNoRegularizor  ();
    
    /** copy constructor */
    ImplNoRegularizor  (const ImplNoRegularizor &);

    /** destructor */
    virtual ~ImplNoRegularizor ();
    
    /** copy the counts into the frequencies and regularize them by doing so. */
    virtual void fillFrequencies( FrequencyMatrix * frequencies, 
				  const WeightedCountMatrix * counts ) const;

};


}

#endif /* IMPL_NO_REGULARIZOR_H */

