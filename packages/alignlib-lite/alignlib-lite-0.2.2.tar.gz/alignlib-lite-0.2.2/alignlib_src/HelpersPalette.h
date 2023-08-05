/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersSubstitutionMatrix.h,v 1.2 2004/01/07 14:35:33 aheger Exp $

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

#ifndef HELPERS_PALETTE_MATRIX_H
#define HELPERS_PALETTE_MATRIX_H 1

#include "alignlib_fwd.h"
#include "alignlib_default.h"

namespace alignlib 
{

/**
 * 
 * @defgroup FactoryPalette Factory functions for palettes.
 * @{ 
 */

/** create a default @ref Palette.
 * 
 * @return a new @ref Palette
 * */
HPalette makePalette(); 

/** create a @ref Palette with mview colours.
 * 
 * @return a new @ref Palette
 * */
HPalette makePaletteMView(); 

/** @} */

/** @addtogroup Defaults
 * @{
 */ 

DEFINE_DEFAULT( HPalette, 
		getDefaultPalette,
		setDefaultPalette );

/** @} */

}

#endif	/* HELPERS_SUBSTITUTION_MATRIX_H */



