//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplDistor.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef IMPL_DISTOR_H
#define IMPL_DISTOR_H 1

#include "alignlib_fwd.h"
#include "Distor.h"
#include "ImplAlignlibBase.h"

/**
   base class for methods calculating distance matrices from
   multiple alignments of protein sequences. If you have a set
   of single pairswise alignments, do it yourself :=).

   @author Andreas Heger
   @version $Id: ImplDistor.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
   @short base class for calculating distance matrices from sequences
*/

namespace alignlib
{

class ImplDistor : public Distor, public ImplAlignlibBase
{

 public:
    // constructors and destructors
    ImplDistor  ();

    ImplDistor  (const ImplDistor &);

    virtual ~ImplDistor ();

    /** calculate a distance matrix from protein sequences
	@param multali multiple alignment of protein sequences
	@param matrix  matrix to use. If not supplied, the most basic matrix type will be used.
     */
    virtual void calculateMatrix(
    		HDistanceMatrix & dest,
    		const HMultipleAlignment & mali ) const ;

    /** Calculate distance between two rows from multiple alignment */
    virtual DistanceMatrixValue calculateDistance(
    		const std::string & s_row_1,
    		const std::string & s_row_2) const = 0;


 protected:

    /** length of multiple alignment */
    mutable int mLength;

};


}

#endif /* _WEIGHTER_H */

