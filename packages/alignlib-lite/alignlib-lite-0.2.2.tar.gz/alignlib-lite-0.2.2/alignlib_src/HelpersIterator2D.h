/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersIterator2D.h,v 1.2 2004/01/07 14:35:32 aheger Exp $

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

#ifndef HELPERS_ITERATOR2D_H
#define HELPERS_ITERATOR2D_H 1

#include <iosfwd>

#include "alignlib_fwd.h"
#include "alignlib_fwd.h"
#include "alignlib_default.h"

namespace alignlib 
{
    
  // 1. factory functions */
  HIterator2D makeIterator2DFull( 
		  const HAlignandum & row,
		  const HAlignandum & col);
  
  HIterator2D makeIterator2DFull(); 
  
  HIterator2D makeIterator2DBanded( 
		  const HAlignandum & row,
		  const HAlignandum & col,
		  const Diagonal lower_diagonal = 0,
		  const Diagonal upper_diagonal = 0);

  HIterator2D makeIterator2DBanded( 
		  const Diagonal lower_diagonal = 0,
		  const Diagonal upper_diagonal = 0);

  /** @addtogroup Defaults
   * @{
   */ 
  
  // 2. accessory functions for default objects  
  DEFINE_DEFAULT( HIterator2D, getDefaultIterator2D, setDefaultIterator2D );

  /** @} */
}

#endif	/* HELPERS_ITERATOR2D_H */
