/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersEncoder.h,v 1.2 2004/01/07 14:35:33 aheger Exp $

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

#ifndef HELPERS_TRANSLATOR_H
#define HELPERS_TRANSLATOR_H 1

#include "alignlib_fwd.h"
#include "alignlib_default.h"

namespace alignlib 
{

/**
 * 
 * @defgroup FactoryEncoder Factory functions for Encoder objects.
 * @{ 
 */

/** return an encoder for built-in alphabet.
 * 
 * @param alphabet 
 * @return a @ref Encoder object.
 */
const HEncoder getEncoder( const AlphabetType & alphabet );

/** make an encoder for built-in alphabet.
 * 
 * @param alphabet 
 * 
 * @return a new @ref Encoder object.
 */
const HEncoder makeEncoder( const AlphabetType & alphabet );

/** load a Encoder object from stream. 
 * 
 * @param stream input stream.
 * @return a new @ref Encoder object.
 */	
const HEncoder loadEncoder( std::istream & stream );

/** @} */

/** @addtogroup Defaults
 * @{
 */ 

DEFINE_DEFAULT( HEncoder, getDefaultEncoder, setDefaultEncoder );

/** @} */
}

#endif	/* HELPERS_TRANSLATOR_H */
