//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplDistorKimura.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef IMPL_DISTOR_KIMURA_H
#define IMPL_DISTOR_KIMURA_H 1

#include "alignlib_fwd.h"
#include "ImplDistor.h"

/**
   calculate the distance between two sequences using Kimura's model (1983).

   The formula:

   d = -ln( 1 - p - 0.2 p*p)

   where p is the fractional number of amino acid differences in the two
   aligned sequences.

   If p is larger than 0.8541, then the distance becomes infinite.
   Inserting 0.85 into the above equation I get 5.2. I use this value
   as MAX_DISTANCE.

   @author Andreas Heger
   @version $Id: ImplDistorKimura.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
   @short base class for calculating distance matrices from sequences
*/


namespace alignlib
{

class ImplDistorKimura : public ImplDistor
{

 public:
    // constructors and desctructors
    ImplDistorKimura  ();

    ImplDistorKimura  (const ImplDistorKimura &);

    virtual ~ImplDistorKimura ();

    DEFINE_CLONE( HDistor );

    /** return the maximum distance obtainable between two sequences */
    virtual DistanceMatrixValue getMaximumPossibleDistance() const;

    /** Calculate distance between two rows from multiple alignment */
    virtual DistanceMatrixValue calculateDistance(
    		const std::string & s_row_1,
    		const std::string & s_row_2) const ;

};

}

#endif /* _DISTOR_KIMURA_H */

