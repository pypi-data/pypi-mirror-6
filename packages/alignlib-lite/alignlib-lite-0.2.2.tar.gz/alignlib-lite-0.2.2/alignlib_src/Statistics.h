/*
  alignlib - a library for aligning protein sequences

  $Id: Statistics.h,v 1.2 2004/01/07 14:35:37 aheger Exp $

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

#ifndef STATISTICS_H
#define STATISTICS_H 1

#include <vector>
#include "alignlib_fwd.h"

namespace alignlib
{

    /** Helper functions for class Alignment:

	1. factory functions

	2. accessor functions for default objects

	3. convenience functions
    */


/*-----------------> data structures <------------------------------ */
struct NormalDistributionParameters
{
    double mMean;
    double mStandardDeviation;
    double getMean() { return mMean;}
    double getStandardDeviation() { return mStandardDeviation;}
};

struct EVDParameters
{
  double mLambda;
  double mK;
  double getLambda() { return mLambda; }
  double getK() { return mK; }
};

/*----------------> factory functions <------------------------------ */

/** create a new parameter object */
NormalDistributionParameters * makeNormalDistributionParameters();

/** create a new parameter object */
EVDParameters * makeEVDParameters();

/*----------------> convenience functions <-------------------------- */

/** iteratively align src1 and src2 and "fit" a normal distribution */
void calculateZScoreParameters(
		NormalDistributionParameters * result,
		const HAlignandum & row,
		const HAlignandum & col,
		const HAlignator & alignator,
		unsigned int n_iterations,
		unsigned int n_iterations_shuffle = 1,
		Position window_size = 0);

inline Score calculateZScore( Score score,
				 const NormalDistributionParameters * params )
{
  return ((score - params->mMean) / params->mStandardDeviation);
}

}

#endif	/* STATISTICS_H */







