/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersWeightor.h,v 1.2 2004/01/07 14:35:33 aheger Exp $

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

#ifndef HELPERS_WEIGHTOR_H
#define HELPERS_WEIGHTOR_H 1

#include "alignlib_fwd.h"
#include "alignlib_default.h"

namespace alignlib 
{


 /**
 * 
 * @defgroup FactoryWeightor Factory functions for Weightor objects.
 * @{ 
 */

/** @brief make a new @ref Weightor object without weighting.
 * 
 * @return a new @ref Weightor object.
 */
HWeightor makeWeightor();

/** @brief make a new @ref Weightor object using the Henikoff weighting scheme. 
 * 
 * For more information, see:
 * 
 * Henikoff,S. and Henikoff,J.G. (1994) J. Mol. Biol., 243, 574-578
 * 
 * @param rescale_counts if true, weights are scaled to the number of sequences.
 * 			Otherwise, they will sum to one.
 * 
 * @return a new @ref Weightor object.
 */
HWeightor makeWeightorHenikoff( const bool rescale_counts = false );

/** @} */

/** @addtogroup Defaults
 * @{
 */     
DEFINE_DEFAULT( HWeightor, getDefaultWeightor, setDefaultWeightor );
/** @} */

}

#endif	/* HELPERS_WEIGHTOR_H */
