/*
  alignlib - a library for aligning protein sequences

  $Id: ImplRegularizorDirichlet.cpp,v 1.2 2004/01/07 14:35:35 aheger Exp $

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

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "Regularizor.h"
#include "ImplRegularizorDirichlet.h"
#include "Matrix.h"

using namespace std;

namespace alignlib
{

#define DEFAULT_FADE_CUTOFF 20
#define NO_FADE_CUTOFF 1000000

/** factory functions */
HRegularizor makeRegularizorDirichlet( WeightedCount fade_cutoff )
{
	return HRegularizor( new ImplRegularizorDirichlet( fade_cutoff ) );
}

//--------------------------------------------------------------------------------------------------------------------------
/** very important: the residues here are sorted alphabetically!!!!!!! */

static const char ALPHABET[ALPHABET_SIZE+1] = "ACDEFGHIKLMNPQRSTVWY";

/* the mixture coefficients q_i */
static double q[NCOMPONENTS] = { 0.182962,0.057607,0.089823,0.079297,0.083183,0.091122,0.115962,0.06604,0.234006 } ;

/* the mixtures a_i */
static double a[NCOMPONENTS][ALPHABET_SIZE] =
{
		{ 0.270671, 0.039848, 0.017576, 0.016415, 0.014268, 0.131916, 0.012391, 0.022599, 0.020358, 0.030727,
				0.015315, 0.048298, 0.053803, 0.020662, 0.023612, 0.216147, 0.147226, 0.065438, 0.003758, 0.009621 },
		{ 0.021465, 0.0103  , 0.011741, 0.010883, 0.385651, 0.016416, 0.076196, 0.035329, 0.013921, 0.093517,
				0.022034, 0.028593, 0.013086, 0.023011, 0.018866, 0.029156, 0.018153, 0.0361,   0.07177,  0.419641},
		{ 0.561459, 0.045448, 0.438366, 0.764167, 0.087364, 0.259114, 0.21494,  0.145928, 0.762204, 0.24732,
				0.118662, 0.441564, 0.174822, 0.53084 , 0.465529, 0.583402, 0.445586, 0.22705,  0.02951,  0.12109 },
		{ 0.070143, 0.01114 , 0.019479, 0.094657, 0.013162, 0.048038, 0.077,    0.032939, 0.576639, 0.072293,
				0.02824 , 0.080372, 0.037661, 0.185037, 0.506783, 0.073732, 0.071587, 0.042532, 0.011254, 0.028723 },
		{ 0.041103, 0.014794, 0.00561 , 0.010216, 0.153602, 0.007797, 0.007175, 0.299635, 0.010849, 0.999446,
				0.210189, 0.006127, 0.013021, 0.019798, 0.014509, 0.012049, 0.035799, 0.180085, 0.012744, 0.026466 },
		{ 0.115607, 0.037381, 0.012414, 0.018179, 0.051778, 0.017255, 0.004911, 0.796882, 0.017074, 0.285858,
				0.075811, 0.014548, 0.015092, 0.011382, 0.012696, 0.027535, 0.088333, 0.94434,  0.004373, 0.016741 },
		{ 0.093461, 0.004737, 0.387252, 0.347841, 0.010822, 0.105877, 0.049776, 0.014963, 0.094276, 0.027761,
				0.01004 , 0.187869, 0.050018, 0.110039, 0.038668, 0.119471, 0.065802, 0.02543,  0.003215, 0.018742 },
		{ 0.452171, 0.114613, 0.06246,  0.115702, 0.284246, 0.140204, 0.100358, 0.55023,  0.143995, 0.700649,
				0.27658 , 0.118569, 0.09747,  0.126673, 0.143634, 0.278983, 0.358482, 0.66175,  0.061533, 0.199373 },
		{ 0.005193, 0.004039, 0.006722, 0.006121, 0.003468, 0.016931, 0.003647, 0.002184, 0.005019, 0.00599,
				0.001473, 0.004158, 0.009055, 0.00363,  0.006583, 0.003172, 0.00369, 0.002967,  0.002772, 0.002686 }
};

static double precomputed_lgamma_wa_j[NCOMPONENTS];	/* lgamma( wa_j), index is [j] */
static double precomputed_sum_lgamma_a_j[NCOMPONENTS];	/* sum_i(lgamma(a_ji)), index is [j] */

IMPLEMENT_CLONE( HRegularizor, ImplRegularizorDirichlet );

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplRegularizorDirichlet::ImplRegularizorDirichlet ( const WeightedCount & fade_cutoff ) :
	mFadeCutoff ( fade_cutoff )
{
	debug_func_cerr(5);

	// set cutoff for fading
	if (mFadeCutoff <= 0)
		mFadeCutoff = NO_FADE_CUTOFF;

	// set helper arrays

	double x[ALPHABET_SIZE];
	double total;
	int i,j,k;

	/* check later on, if mWa has already been calculated before */

	/* calculate null model: uniform aa frequencies -> bg[]*/
	for (i = 0; i < ALPHABET_SIZE; i ++)
		x[i] = 0;

	for (k = 0; k < NCOMPONENTS; k++)
		for (i = 0; i < ALPHABET_SIZE; i ++)
			x[i] = x[i] + q[k] * a[k][i];

	/* normalize null modell */
	total = 0;
	for (i = 0; i < ALPHABET_SIZE; i++)
		total = total + x[i];

	if (total == 0)                             // deal with empty columns
		total = 1;

	/* calculate |aj| -> wa[] */
	for (k = 0; k < NCOMPONENTS; k++) {
		total = 0;
		for (i = 0; i < ALPHABET_SIZE; i ++)
			total = total + a[k][i];
		mWa[k] = total;
	}

	// lgamma(wa_j)
	for (j = 0; j < NCOMPONENTS; j++)
		precomputed_lgamma_wa_j[j] = lgamma( mWa[j] );

	// sum_lgamma_a_j
	for (j = 0; j < NCOMPONENTS; j++) {
		precomputed_sum_lgamma_a_j[j] = 0;
		for (i = 0; i < ALPHABET_SIZE; i++ )
			precomputed_sum_lgamma_a_j[j] += lgamma(a[j][i]);
	}

	// export to children:
	mA = &a[0];
	mLGamma_Wa = &precomputed_lgamma_wa_j[0];
	mSumLGamma_Ai = &precomputed_sum_lgamma_a_j[0];

}

//--------------------------------------------------------------------------------------------------------------------------------
ImplRegularizorDirichlet::~ImplRegularizorDirichlet ()
{
	debug_func_cerr(5);
}

//-------------------------------------------------------------------------------------------------------------------------------
ImplRegularizorDirichlet::ImplRegularizorDirichlet (const ImplRegularizorDirichlet & src ) :
	mFadeCutoff(src.mFadeCutoff)
{
}

//-------------------------------------------------------------------------------------------------------
// calculate the logarithm of the beta-function for a vector
// LBeta        = log prod_i(Gamma(xi)) / gamma( |x| )
//      = sum_i lgamma(xi) - lgamma( |x| )

inline static double lBeta ( const double * vector, const double length )
{
	double result = 0;
	int i;
	for (i = 0; i < ALPHABET_SIZE; i++)
		result += lgamma( vector[i] );

	return (result - lgamma( length ));
}

//-------------------------------------------------------------------------------------------------------
// calculate the logarithm of the beta-function for sum of two vectors. In Kimmens script |x| is
// defined as sum_xi, so |x| + |y| = | x + y | !!
// the first vector is an int
inline static double lBetaSum ( const WeightedCount * vector1,
		const WeightedCount length1,
		const double *vector2,
		const WeightedCount length2)
{
	double result = 0;
	int i;

	for (i = 0; i < ALPHABET_SIZE; i++)
		result += lgamma( vector1[i] + vector2[i]);

	return (result - lgamma( length1 + length2 ));
}

//-------------------------------------------------------------------------------------------------------
/** This function encapsulates that part of the algorithm, that needs to access the lgamma-function. It
    has been externalized, so that it can be overloaded to implement different speed-ups.

    This function uses the lgamma-function directly.
 */
double ImplRegularizorDirichlet::calculateBetaDifferences(
		TYPE_BETA_DIFFERENCES beta_differences,
		const WeightedCount * n,
		WeightedCount ntotal ) const
		{

	double max_log_difference = 0;
	int j;

	for (j = 0; j < NCOMPONENTS; j++) {

		double difference = lBetaSum( n, ntotal, a[j], mWa[j] ) - lBeta( a[j], mWa[j] );
		beta_differences[j] = difference;

		if (fabs(max_log_difference) < fabs(difference))
			max_log_difference = difference;
	}

	return max_log_difference;
}

//-------------------------------------------------------------------------------------------------------
/** This function fills the frequencies from the Dirichlet mixture.
 */

void ImplRegularizorDirichlet::fillColumn(  Frequency * frequencies,
		TYPE_BETA_DIFFERENCES beta_differences,
		const WeightedCount * n,
		WeightedCount ntotal,
		const HEncoder & encoder) const
		{

	int i,j;
	double Xi[ALPHABET_SIZE];


	// calculate the ratio of the two beta functions. The ratio might get very small, so that floating point
	// representation is not possible with double. Therefore subtract the maximum ratio of this. The factor,
	// which will be constant multiplier, gets eliminated automatically when normalizing the Xi.
	// max_log_difference is < 0

	double max_log_difference = calculateBetaDifferences( beta_differences , n, ntotal );

	// calculate the Xi
	if (ntotal == 0) {                          // if there were no observations, mask this column
		for (i = 0; i < ALPHABET_SIZE; i++)
			Xi[i] = 0;                              // i.e. set frequency to 0
	} else {
		for (i = 0; i < ALPHABET_SIZE; i++) {
			Xi[i] = 0;
			for (j = 0; j < NCOMPONENTS; j++) {
				double exponent = beta_differences[j] - max_log_difference;
				Xi[i] += q[j] * exp( exponent ) * (a[j][i] + n[i] ) / (mWa[j] + ntotal);
			}
		}
	}

	// normalise the Xi
	Score xtotal = 0;
	for (i = 0; i < ALPHABET_SIZE; i++)
		xtotal += Xi[i];

	if (xtotal > 0)
		for (i = 0; i < ALPHABET_SIZE; i++)
			frequencies[encoder->encode(ALPHABET[i])] = (Frequency)(Xi[i] / xtotal);
}

//-------------------------------------------------------------------------------------------------------
/** see Kimmen's PhD-Thesis, pp42ff.
      I use equations 6.38 and 6.39 for calculating the pi
      using the logarithm of the beta-function, as Kimmen suggests.
      This method calculates the Xi and stores it in the profile. You have
      to call NormalizeColumn to get the correct estimated probabilites.
 */
void ImplRegularizorDirichlet::fillFrequencies(
		FrequencyMatrix & frequencies,
		const WeightedCountMatrix & counts,
		const HEncoder & encoder ) const
{
	debug_func_cerr(5);

	Position width = counts.getNumCols();
	Position length = counts.getNumRows();

	int i;

	Position column;
	WeightedCount ntotal;

	// helper variables for the conversion of log to floating point
	TYPE_BETA_DIFFERENCES beta_differences;

	for (column = 0; column < length; column++)
	{
		const WeightedCount * n = counts.getRow( column );

		ntotal = 0;

		// get ntotal = number of observations
		for (i = 0; i < width; i++)
			ntotal += n[i];

		if (ntotal < mFadeCutoff )
		{
			// use Dirichlet-Mixture
			fillColumn( frequencies.getRow( column ),
					beta_differences,
					n,
					ntotal,
					encoder);

		}
		else
		{
			Frequency * col = frequencies.getRow( column );
			// calculate raw frequencies
			for (i = 0; i < width; i++)
				col[encoder->encode(ALPHABET[i])] = (Frequency)(n[i] / ntotal);

		}
	}
}

} // namespace alignlib
