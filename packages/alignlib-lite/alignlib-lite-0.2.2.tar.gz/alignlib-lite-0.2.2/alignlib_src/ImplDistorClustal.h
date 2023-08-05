//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplDistorClustal.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef IMPL_DISTOR_CLUSTAL_H
#define IMPL_DISTOR_CLUSTAL_H 1

#include "alignlib_fwd.h"
#include "ImplDistor.h"

/**
   calculate the distance between two sequences using the same way
   as Clustal:

   amino acid difference p
   0 to 75%     => Clustal's model          d = -ln( 1 - p - 0.2 p*p)
   75.1 to 99.9%        => Dayhoff's model
   100%^                => MAX_DIST = 1000

   Since a distance according to Dayhoff's has to be calculated numerically,
   I use a table of precomputed values.

   For instructions on how to calculate pam-distance between protein sequences,
   take a look at

   http://www.inf.ethz.ch/personal/gonnet/DarwinManual/node155.html

   @author Andreas Heger
   @version $Id: ImplDistorClustal.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
   @short calculate a distance matrix using Clustal procedure
*/

namespace alignlib {

class ImplDistorClustal : public ImplDistor {

 public:
    // constructors and desctructors
    ImplDistorClustal  ();

    ImplDistorClustal  (const ImplDistorClustal &);

    virtual ~ImplDistorClustal ();

    DEFINE_CLONE( HDistor );

    /** return the maximum distance obtainable between two sequences */
    virtual DistanceMatrixValue getMaximumPossibleDistance() const;

    /** Calculate distance between two rows from multiple alignment */
    virtual DistanceMatrixValue calculateDistance( const std::string & s_row_1, const std::string & s_row_2) const ;

};

}

#endif /* _DISTOR_CLUSTAL_H */

