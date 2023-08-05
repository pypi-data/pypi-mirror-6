//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplDistorDummy.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef IMPL_DISTOR_DUMMY_H
#define IMPL_DISTOR_DUMMY_H 1

#include "alignlib_fwd.h"
#include "alignlib_fwd.h"
#include "ImplDistor.h"

/**
   base class for methods calculating distance matrices from
   multiple alignments of protein sequences. If you have a set
   of single pairswise alignments, do it yourself :=).

   @author Andreas Heger
   @version $Id: ImplDistorDummy.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
   @short base class for calculating distance matrices from sequences
*/

namespace alignlib
{

class ImplDistorDummy : public ImplDistor
{

 public:
    // constructors and desctructors
	ImplDistorDummy  ();

	ImplDistorDummy  (const HDistanceMatrix & matrix);

    ImplDistorDummy  (const ImplDistorDummy &);

    virtual ~ImplDistorDummy ();

    DEFINE_CLONE( HDistor );

    /** return the maximum distance obtainable between two sequences */
    virtual DistanceMatrixValue getMaximumPossibleDistance() const;

    /** calculate a distance matrix from protein sequences
	@param multali multiple alignment of protein sequences
	@param matrix  matrix to use. If not supplied, the most basic matrix type will be used.
     */
    virtual void calculateMatrix( HDistanceMatrix & dest,
    		const alignlib::HMultipleAlignment mali ) const ;

    /** Calculate distance between two rows from multiple alignment */
    virtual DistanceMatrixValue calculateDistance( const std::string & s_row_1, const std::string & s_row_2) const;

 private:
    /** the matrix for the source. I do not own it. */
    const HDistanceMatrix mMatrix;
};


}

#endif /* IMPL_DISTOR_DUMMY_H */

