/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersRegularizor.h,v 1.2 2004/01/07 14:35:32 aheger Exp $

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

#ifndef HELPERS_REGULARIZOR_H
#define HELPERS_REGULARIZOR_H 1

#include "alignlib_fwd.h"
#include "alignlib_default.h"

namespace alignlib
{

/**
 *
 * @defgroup FactoryRegularizor Factory functions for Regularizor objects.
 * @{
 */

/** make simple @ref Regularizor object.
 *
 * This regularizor computes frequencies from counts without
 * regularization.
 * @return a new @ref Regularizor object.
 * */
HRegularizor makeRegularizor();

/** make @ref Regularizor object according to Tatusov et al.
 *
 * This object uses the pseudocount-method according to Tatusov et al. (1994).
 *
 * For more information, see:
 *
 * Tatusov,R.L., Altschul,S.F. and Koonin,E.V. (1994) Proc. Natl. Acad. Sci. USA, 91, 12091-12095
 *
 * @param matrix 		@ref SubstitutionMatrix.
 * @param background 	vector with background residue frequencies.
 * @param alphabet		alphabet corresponding to the background counts
 * @param beta 			pseudocounts mixing parameter.
 * @param lambda 		scale factor for matrix.
 */
HRegularizor makeRegularizorTatusov(
		const HSubstitutionMatrix & matrix,
		const HFrequencyVector & background,
		const std::string & alphabet,
		const double & beta,
		const double & lambda );

/** make @ref Regularizor object according to Tatusov parameterized according to PSI-BLAST.
 *
 * For more information, see:
 *
 * Altschul SF, Madden TL, Schäffer AA, Zhang J, Zhang Z, Miller W, Lipman DJ.
 * Gapped BLAST and PSI-BLAST: a new generation of protein database search programs.
 * Nucleic Acids Res. 1997 Sep 1;25(17):3389-402.
 *
 * @return a new @ref Regularizor object.
 */
HRegularizor makeRegularizorPsiblast();

/** make @ref Regularizor object using the 9-component mixture model by Sjolander et al. (1996).
 *
 * For more information, see:
 *
 * Sjölander K, Karplus K, Brown M, Hughey R, Krogh A, Mian IS, Haussler D.
 * Dirichlet mixtures: a method for improved detection of weak but significant protein sequence homology.
 * Comput Appl Biosci. 1996 Aug;12(4):327-45.
 * PMID: 8902360
 *
 * @param fade_cutoff	do not apply regularizor if there are least this number of counts.
 *
 * @return a new @ref Regularizor object.
*/
HRegularizor makeRegularizorDirichlet( WeightedCount fade_cutoff = 0);
/** make @ref Regularizor object using the 9-component mixture model by Sjolander et al. (1996).
 *
 * For more information, see:
 *
 * Sjölander K, Karplus K, Brown M, Hughey R, Krogh A, Mian IS, Haussler D.
 * Dirichlet mixtures: a method for improved detection of weak but significant protein sequence homology.
 * Comput Appl Biosci. 1996 Aug;12(4):327-45.
 * PMID: 8902360
 *
 * This object uses a hash to speed up calls to the Gamma function.
 *
 * @param fade_cutoff	do not apply regularizor if there are least this number of counts.
 *
 * @return a new @ref Regularizor object.
*/
HRegularizor makeRegularizorDirichletHash( WeightedCount fade_cutoff = 0);

/** make @ref Regularizor object using the 9-component mixture model by Sjolander et al. (1996).
 *
 * For more information, see:
 *
 * Sjölander K, Karplus K, Brown M, Hughey R, Krogh A, Mian IS, Haussler D.
 * Dirichlet mixtures: a method for improved detection of weak but significant protein sequence homology.
 * Comput Appl Biosci. 1996 Aug;12(4):327-45.
 * PMID: 8902360
 *
 * This object uses interpolation to speed up calls to the Gamma function.
 *
 * @param fade_cutoff	do not apply regularizor if there are least this number of counts.
 *
 * @return a new @ref Regularizor object.
*/
HRegularizor makeRegularizorDirichletInterpolate( WeightedCount fade_cutoff = 0);

/** make @ref Regularizor object using the 9-component mixture model by Sjolander et al. (1996).
 *
 * For more information, see:
 *
 * Sjölander K, Karplus K, Brown M, Hughey R, Krogh A, Mian IS, Haussler D.
 * Dirichlet mixtures: a method for improved detection of weak but significant protein sequence homology.
 * Comput Appl Biosci. 1996 Aug;12(4):327-45.
 * PMID: 8902360
 *
 * Forgot what this object does.
 *
 * @param fade_cutoff	do not apply regularizor if there are least this number of counts.
 *
 * @return a new @ref Regularizor object.
*/
HRegularizor makeRegularizorDirichletPrecomputed( WeightedCount fade_cutoff = 0);

/** @} */

/** @addtogroup Defaults
 * @{
 */
DEFINE_DEFAULT( HRegularizor, getDefaultRegularizor, setDefaultRegularizor );
/** @} */

}

#endif	/* HELPERS_REGULARIZOR_H */
