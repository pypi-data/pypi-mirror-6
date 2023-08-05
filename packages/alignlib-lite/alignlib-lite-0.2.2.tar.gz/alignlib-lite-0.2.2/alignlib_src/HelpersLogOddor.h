/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersLogOddor.h,v 1.2 2004/01/07 14:35:32 aheger Exp $

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

#ifndef HELPERS_LOGODDOR_H
#define HELPERS_LOGODDOR_H 1

#include "alignlib_fwd.h"
#include "alignlib_default.h"
#include "LogOddor.h"

namespace alignlib 
{

/**
 * 
 * @defgroup FactoryLogOddor Factory functions for LogOddor objects.
 * @{ 
 */

/** return @ref LogOddor that uses the raw frequencies as scores.
 * 
 * @param scale_factor	scores will be multiplied by this value.
 * @param mask_value	score for a column that is masked.
 * 
 * @return a new @ref LogOddor object.
 */
HLogOddor makeLogOddor( 
		const Score & scale_factor = 1.0, 
		const Score & mask_value = -10);


/** return @ref LogOddor object that computes log odds scores using uniform background frequencies.
 * 
 * @param scale_factor	scores will be multiplied by this value.
 * @param mask_value	score for a column that is masked.
 * 
 * @return a new @ref LogOddor object.
 */
HLogOddor makeLogOddorUniform( 
		const Score & scale_factor = 1.0, 
		const Score & mask_value = -10);

/** return @ref LogOddor object that computes log-odds scores using non-uniform background frequencies.
 * 
 * @param frequencies 	vector with background frequencies ordered according to @param alphabet.
 * @param alphabet		alphabet that frequencies refer to
 * @param scale_factor	scores will be multiplied by this value.
 * @param mask_value	score for a column that is masked.
 * 
 * @return a new @ref LogOddor object.
 */
HLogOddor makeLogOddorBackground( 
		const HFrequencyVector & frequencies,
		const std::string & alphabet,
		const Score & scale_factor = 1.0,
		const Score & mask_value = -10);

/** return @ref LogOddor object that computes profile score according to Gribskov's method
 * 
 * see Gribskov et al. (1987) PNAS 84: 4355-4358
 * 
 * @param matrix		@ref SubstitutionMatrix object.
 * @param scale_factor	scores will be multiplied by this value.
 * @param mask_value	score for a column that is masked.
 * 
 * @return a new @ref LogOddor object.
 */
HLogOddor makeLogOddorGribskov( 
		const HSubstitutionMatrix & matrix,
		const Score & scale_factor = 1.0,
		const Score & mask_value = -10 ); 

/** return @ref LogOddor object that computes profile scores for Kimmen Sjoerlander's 9-component Dirichlet mixture
 * 
 * @param matrix		@ref SubstitutionMatrix object.
 * @param scale_factor	scores will be multiplied by this value.
 * @param mask_value	score for a column that is masked.
 * 
 * @return a new @ref LogOddor object.
 */
HLogOddor makeLogOddorDirichlet( 
		const Score & scale_factor = 1.0,
		const Score & mask_value = -10 ); 




/** @} */

/** @addtogroup Defaults
 * @{
 */ 
DEFINE_DEFAULT( HLogOddor, getDefaultLogOddor, setDefaultLogOddor );

/** @} */
}

#endif	/* HELPERS_LOGODDOR_H */
