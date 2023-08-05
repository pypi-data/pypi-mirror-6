//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: Distor.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef DISTOR_H
#define DISTOR_H 1

#include <iosfwd>
#include <string>

#include "alignlib_fwd.h"
#include "AlignlibBase.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

/**
 * @short Protocol class for calculating distance matrices from sequences.

	A @ref Distor object computes pairwise distances between all pairs of
	sequences in a @ref MultipleAlignment and stores the results in a
	@ref DistanceMatrix.

   	@author Andreas Heger
   	@version $Id: Distor.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
 */
class Distor : public virtual AlignlibBase
{
	// class member functions
	friend std::ostream & operator<<( std::ostream &, const Distor &);

public:
	// constructors and desctructors
	Distor  ();

	Distor  (const Distor &);

	virtual ~Distor ();

	DEFINE_ABSTRACT_CLONE( HDistor )

	/** fill @ref DistanceMatrix from a @ref MultipleAlignment.
	 *
	 * @param dest @ref DistanceMatrix to fill.
	 * @param mali @ref MultipleAlignment object.
	 */
	virtual void calculateMatrix(
			HDistanceMatrix & dest,
			const HMultipleAlignment & mali ) const = 0;

	/** return the maximum possible distance
	 * @return a distance
	 * */
	virtual DistanceMatrixValue getMaximumPossibleDistance() const = 0;

	/** calculate distance between two strings.
	 *
	 * @param a	string with first sequence.
	 * @param b string with second sequence.
	 * @return a distance.
	 * */
	virtual DistanceMatrixValue calculateDistance(
			const std::string & s_row_1,
			const std::string & s_row_2) const = 0;

};


}

#endif /* DISTOR_H */

