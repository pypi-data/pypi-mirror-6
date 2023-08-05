/*
  alignlib - a library for aligning protein sequences

  $Id: ImplRegularizorDirichletHash.cpp,v 1.2 2004/01/07 14:35:36 aheger Exp $

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
#include "ImplRegularizorDirichletHash.h"

#ifdef DEBUG
static int total_hits = 0;
static int total_lookups = 0;
#endif

using namespace std;

namespace alignlib
{

/** factory functions */
	HRegularizor makeRegularizorDirichletHash( WeightedCount fade_cutoff )
	{
		return HRegularizor( new ImplRegularizorDirichletHash( fade_cutoff ) );
	}


#define SCALE_FACTOR 10000

typedef std::map< int, double > TYPE_HASH_GAMMA;
static TYPE_HASH_GAMMA gamma_hash;

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplRegularizorDirichletHash::ImplRegularizorDirichletHash ( WeightedCount fade_cutoff ) : ImplRegularizorDirichlet( fade_cutoff ) {
}

//--------------------------------------------------------------------------------------------------------------------------------
ImplRegularizorDirichletHash::~ImplRegularizorDirichletHash () {

#ifdef DEBUG
    cout << "Total lookups " << total_lookups << endl;
    cout << "of which where hits " << total_hits << endl;
#endif

}

//-------------------------------------------------------------------------------------------------------------------------------
ImplRegularizorDirichletHash::ImplRegularizorDirichletHash (const ImplRegularizorDirichletHash & src ) : ImplRegularizorDirichlet( src ) {
}


//-------------------------------------------------------------------------------------------------------
/** This function encapsulates that part of the algorithm, that needs to access the lgamma-function. It
    has been externalized, so that it can be overloaded to implement different speed-ups.

    This function uses the lgamma-function directly.
*/
inline double LookUp( double x ) {

  int key = (int)(x * SCALE_FACTOR);

  TYPE_HASH_GAMMA::iterator it;

#ifdef DEBUG
  total_lookups++;
#endif

  if ( (it = gamma_hash.find( key )) != gamma_hash.end())
{
  debug_func_cerr(5);

    return (*it).second;
  }  else {
    double value = lgamma( x );
    gamma_hash[key] = value;
    return value;
  }
}

//-------------------------------------------------------------------------------------------------------
// calculate the logarithm of the beta-function for a vector
// LBeta        = log prod_i(Gamma(xi)) / gamma( |x| )
//      = sum_i lgamma(xi) - lgamma( |x| )

inline static double lBeta ( const double * vector, const double length ) {
  double result = 0;
  int i;
  for (i = 0; i < ALPHABET_SIZE; i++)
    result += LookUp( vector[i] );

  return (result - LookUp( length ));
}

//-------------------------------------------------------------------------------------------------------
// calculate the logarithm of the beta-function for sum of two vectors. In Kimmens script |x| is
// defined as sum_xi, so |x| + |y| = | x + y | !!
// the first vector is an int
inline static double lBetaSum ( const WeightedCount * vector1,
			 const WeightedCount length1,
			 const double *vector2,
			 const WeightedCount length2) {
    double result = 0;
    int i;

    for (i = 0; i < ALPHABET_SIZE; i++)
	result += LookUp( vector1[i] + vector2[i]);

    return (result - LookUp( length1 + length2 ));
}

//-------------------------------------------------------------------------------------------------------
/** This function encapsulates that part of the algorithm, that needs to access the lgamma-function. It
    has been externalized, so that it can be overloaded to implement different speed-ups.

    This function uses the lgamma-function directly.
*/
double ImplRegularizorDirichletHash::calculateBetaDifferences(
		TYPE_BETA_DIFFERENCES beta_differences,
		const WeightedCount * n,
		WeightedCount ntotal ) const
		{

  double max_log_difference = 0;
  int j;

  for (j = 0; j < NCOMPONENTS; j++) {

    double difference = lBetaSum( n, ntotal, mA[j], mWa[j] ) - lBeta( mA[j], mWa[j] );
    beta_differences[j] = difference;

    if (fabs(max_log_difference) < fabs(difference))
      max_log_difference = difference;
  }

  return max_log_difference;
}


} // namespace alignlib
