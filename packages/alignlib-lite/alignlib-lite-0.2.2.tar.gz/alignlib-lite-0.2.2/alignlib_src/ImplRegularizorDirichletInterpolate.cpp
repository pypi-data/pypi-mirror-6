/*
  alignlib - a library for aligning protein sequences

  $Id: ImplRegularizorDirichletInterpolate.cpp,v 1.2 2004/01/07 14:35:36 aheger Exp $

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
#include "ImplRegularizorDirichletInterpolate.h"

#ifdef DEBUG
static int total_lookups = 0;
static int total_hits_1 = 0;
static int total_hits_2 = 0;
static int total_hits_3 = 0;
#define MAX_ERROR  1E-6		// the maximum error tolerated
#endif

using namespace std;

namespace alignlib
{

/** factory functions */
	HRegularizor makeRegularizorDirichletInterpolate( WeightedCount fade_cutoff )
	{
		return HRegularizor( new ImplRegularizorDirichletInterpolate( fade_cutoff ));
	}

// precompute values from 0 to 10 very accurately: step-size = 10/1000000 = 1/100000
#define N_ELEMENTS_1 10000000
#define LAST_ELEMENT_1 10
#define SCALE_FACTOR_1 1000000

// precompute values from 10 to 20 less accurate: step-size = 10/10000 = 1/1000 (these values be linearily interpolated)
#define N_ELEMENTS_2 10000
#define LAST_ELEMENT_2 20
#define SCALE_FACTOR_2 1000
#define STEP_SIZE_2 0.001

// precompute values from 20 to 1020 less accurate: step-size = 1000/10000 = 1/10 (these values will be linearly interpolated)
#define N_ELEMENTS_3 1000
#define LAST_ELEMENT_3 1020
#define SCALE_FACTOR_3 10
#define STEP_SIZE_3 0.1

static double gamma_array_1[N_ELEMENTS_1];
static double gamma_array_2[N_ELEMENTS_2];
static double gamma_array_3[N_ELEMENTS_3];

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplRegularizorDirichletInterpolate::ImplRegularizorDirichletInterpolate ( WeightedCount fade_cutoff ) :
	ImplRegularizorDirichlet( fade_cutoff ) {

  // precompute the gamma-values:
  int i;

  // array 1
  double step_size = 1.0 / double(SCALE_FACTOR_1);
  double x = 0;
#ifdef DEBUG
  cout << MAX_ERROR << endl;
  cout << "step_size:" << step_size << " from: " << x << endl;
#endif
  for (i = 0; i < N_ELEMENTS_1; i++, x+= step_size)
      gamma_array_1[i] = lgamma( x );

  // array 2
  x = LAST_ELEMENT_1;
  step_size = 1.0 / double(SCALE_FACTOR_2);
#ifdef DEBUG
    cout << "step_size:" << step_size << " from: " << x << endl;
#endif

  for (i = 0; i < N_ELEMENTS_2; i++, x+= step_size)
      gamma_array_2[i] = lgamma( x );

  // array 3
  x = LAST_ELEMENT_2;
  step_size = 1.0 / double(SCALE_FACTOR_3);
#ifdef DEBUG
  cout << "step_size:" << step_size << " from: " << x << endl;
#endif

  for (i = 0; i < N_ELEMENTS_3; i++, x+= step_size)
      gamma_array_3[i] = lgamma( x );


// note: the lgamma-function has a negative minimum between 1 and 2!
// #ifdef DEBUG
//   cout << "Precomputed values for gamma-function: 1" << endl;
//   for (i = 0; i < N_ELEMENTS_1; i++) {
//       cout << i << ":" << gamma_array_1[i] << " ";
//       if (!(i % 5))
// 	  cout << endl;
//   }
//   cout << endl;
//   cout << "Precomputed values for gamma-function: 2" << endl;
//   for (i = 0; i < N_ELEMENTS_2; i++) {
//       cout << i << ":" << gamma_array_2[i] << " ";
//       if (!(i % 5))
// 	  cout << endl;
//   }
// 	cout << " 2 " << (int)((x - LAST_ELEMENT_1) * N_ELEMENTS_2);
//   cout << endl;
// #endif
}

//--------------------------------------------------------------------------------------------------------------------------------
ImplRegularizorDirichletInterpolate::~ImplRegularizorDirichletInterpolate () {

#ifdef DEBUG
    cout << "Total lookups " << total_lookups << endl;
    cout << "of which where hits in array 1:" << total_hits_1 << " (" << ((double)total_hits_1 / (double)total_lookups * 100.0) << "%)" << endl;
    cout << "of which where hits in array 2:" << total_hits_2 << " ("  <<((double)total_hits_2 / (double)total_lookups * 100.0) << "%)" << endl;
    cout << "of which where hits in array 3:" << total_hits_3 << " ("  <<((double)total_hits_3 / (double)total_lookups * 100.0) << "%)" << endl;
#endif

}

//-------------------------------------------------------------------------------------------------------------------------------
ImplRegularizorDirichletInterpolate::ImplRegularizorDirichletInterpolate (const ImplRegularizorDirichletInterpolate & src ) : ImplRegularizorDirichlet( src ) {
}

//-------------------------------------------------------------------------------------------------------
/** This function encapsulates that part of the algorithm, that needs to access the lgamma-function. It
    has been externalized, so that it can be overloaded to implement different speed-ups.

    This function uses precomputed tables.
    Note: int truncates.

*/
inline double LookUp( double x )
{
  debug_func_cerr(5);


    // do not extrapolate, but call lgamma for this one
    if (x >= LAST_ELEMENT_3) {
      return lgamma(x);
    }

    if (x >= LAST_ELEMENT_2) {
      double scaled_key = (x - (double)LAST_ELEMENT_2) * (double)SCALE_FACTOR_3;
      int key = (int)(scaled_key);
#ifdef DEBUG
      total_hits_3++;
//       cout << "3: " << x << " "
// 	   << gamma_array_3[key] << " " <<  gamma_array_3[key+1] << " " << (double)STEP_SIZE_3 << " " << (scaled_key - (double)key) << " "
// 	   << (gamma_array_3[key] + (gamma_array_3[key+1] - gamma_array_3[key]) * (scaled_key - (double)key))
// 	   << endl;
#endif
      // interpolate
      return (gamma_array_3[key] + (gamma_array_3[key+1] - gamma_array_3[key]) * (scaled_key - (double)key));
    }

    if ( x >= LAST_ELEMENT_1) {
      double scaled_key = (x - (double)LAST_ELEMENT_1) * (double)SCALE_FACTOR_2;
      int key = (int)(scaled_key);

#ifdef DEBUG
      total_hits_2++;
//       cout << "2: " << x << " "
// 	   << gamma_array_2[key] << " " <<  gamma_array_2[key+1] << " "
// 	   << (gamma_array_2[key] + (gamma_array_2[key+1] - gamma_array_2[key]) * (scaled_key - (double)key))
// 	   << endl;
#endif
      return (gamma_array_2[key] + (gamma_array_2[key+1] - gamma_array_2[key])  * (scaled_key - (double)key));
    }

#ifdef DEBUG
    total_hits_1++;
#endif
    return (gamma_array_1[ (int)(x  * SCALE_FACTOR_1) ]);
}

#ifdef DEBUG

  // see, where the errors are made

  double CheckLookUp( double x ) {
    double lg = lgamma(x);
    double r = LookUp(x);

    double error = lg -r;

    if (fabs(error) > MAX_ERROR)
      cout << x << " Error= " << error << endl;

    return r;
  }

#define LookUp CheckLookUp
#endif


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
double ImplRegularizorDirichletInterpolate::calculateBetaDifferences( TYPE_BETA_DIFFERENCES beta_differences,
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
