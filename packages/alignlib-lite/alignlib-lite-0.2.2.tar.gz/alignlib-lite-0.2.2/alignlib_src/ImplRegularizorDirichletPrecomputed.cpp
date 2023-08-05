/*
  alignlib - a library for aligning protein sequences

  $Id: ImplRegularizorDirichletPrecomputed.cpp,v 1.2 2004/01/07 14:35:36 aheger Exp $

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
#include <map>

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "Regularizor.h"
#include "ImplRegularizorDirichletPrecomputed.h"

namespace alignlib
{

/** factory functions */
	HRegularizor makeRegularizorDirichletPrecomputed( WeightedCount fade_cutoff )
	{
		return HRegularizor( new ImplRegularizorDirichletPrecomputed( fade_cutoff ));
	}

typedef double Score_A_JI[NCOMPONENTS][ALPHABET_SIZE];
typedef double TYPE_WA_COLUMN[NCOMPONENTS];

#define MAX_N		1000		// i.e precomputed for 1000 observations per column
#define MAX_N_TOTAL	5000		// i.e precomputed for 5000 observations in total

// do not use statically allocated memory on heap
// as it causes problems with multi-threading
static Score_A_JI precomputed_a_jin[MAX_N]; /* lgamma(a_ji + 0..n), index is [n][j][i] */
static TYPE_WA_COLUMN precomputed_wa_jn[MAX_N_TOTAL * ALPHABET_SIZE]; /* lgamma(wa_j + 0..n), index is [n][j] */

    /** Assuming that counts are non-fractional, the following values can be precomputed:
	n = maximum number of observations for precomputation

	a_jin= a[component][aa] + 0..n	-> 9 * 20 * n values

	sum_a_j = sum(lgamma(mA[])[components] -> 9 values

	wa_jn = mWa[component] + 0..n -> 9 * n values
	wa_j  = lgamma(wa[j])
    */

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplRegularizorDirichletPrecomputed::ImplRegularizorDirichletPrecomputed ( WeightedCount fade_cutoff ) :
	ImplRegularizorDirichlet( fade_cutoff )
{

    int i, j, n;

    // a_jin
    for (n = 0; n < MAX_N; n++)
      for (j = 0; j < NCOMPONENTS; j++)
	for (i = 0; i < ALPHABET_SIZE; i++ )
	  precomputed_a_jin[n][j][i] = lgamma( (double)n + mA[j][i] );

    // wa_jn
    for (n = 0; n < MAX_N; n++)
      for (j = 0; j < NCOMPONENTS; j++)
	    precomputed_wa_jn[n][j] = lgamma( mWa[j] + (double)n );

}

//--------------------------------------------------------------------------------------------------------------------------------
ImplRegularizorDirichletPrecomputed::~ImplRegularizorDirichletPrecomputed ()
{
}

//-------------------------------------------------------------------------------------------------------------------------------
ImplRegularizorDirichletPrecomputed::ImplRegularizorDirichletPrecomputed (const ImplRegularizorDirichletPrecomputed & src ) : ImplRegularizorDirichlet( src ) {
}

//-------------------------------------------------------------------------------------------------------
/** This function encapsulates that part of the algorithm, that needs to access the lgamma-function. It
    has been externalized, so that it can be overloaded to implement different speed-ups.

    This function uses the lgamma-function directly.
*/
double ImplRegularizorDirichletPrecomputed::calculateBetaDifferences(
								     TYPE_BETA_DIFFERENCES beta_differences,
								     const WeightedCount * n,
								     WeightedCount ntotal ) const
{

  double max_log_difference = 0;
  int i,j, c;

  int counts[ALPHABET_SIZE];
  int i_ntotal = (int)ntotal;

  for (i = 0; i < ALPHABET_SIZE; i++)
      counts[i] = (int)n[i];

  for (j = 0; j < NCOMPONENTS; j++)
    {

      double difference = 0;

      for (i = 0; i < ALPHABET_SIZE; i++)
	if ((c = counts[i]) < MAX_N)
	  difference += precomputed_a_jin[c][j][i];		// lgamma( n[i] + mA[j][i]);
	else
	  difference += lgamma( c + mA[j][i]);

      if (i_ntotal < MAX_N_TOTAL)
	  difference -= precomputed_wa_jn[i_ntotal][j];		// lgamma( ntotal + |a[j]| );
      else
	  difference -= lgamma( i_ntotal + mWa[j] );

      difference -= mSumLGamma_Ai[j];				// sum_i(lgamma( mA[j][i] ));

      difference += mLGamma_Wa[j];				// lgamma( |a[j]| );

      beta_differences[j] = difference;

      if (fabs(max_log_difference) < fabs(difference))
	  max_log_difference = difference;
  }

  return max_log_difference;
}


} // namespace alignlib
