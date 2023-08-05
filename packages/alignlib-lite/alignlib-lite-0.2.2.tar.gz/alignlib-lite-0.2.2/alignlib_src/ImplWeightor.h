/*
  alignlib - a library for aligning protein sequences

  $Id: ImplWeightor.h,v 1.3 2004/03/19 18:23:41 aheger Exp $

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

#ifndef IMPL_WEIGHTOR_H
#define IMPL_WEIGHTOR_H 1

#include "alignlib_fwd.h"

#include "Weightor.h"
#include "Macros.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{

/** @short Base implementation class for @ref Weightor.

    This class provides some helper functions that are needed
    in the derived classes.

    @author Andreas Heger
    @version $Id: ImplWeightor.h,v 1.3 2004/03/19 18:23:41 aheger Exp $
*/
class ImplWeightor : public Weightor, public ImplAlignlibBase
{
 public:
    // constructors and desctructors

    /** default constructor */
    ImplWeightor();

    /** copy constructor */
    ImplWeightor(const ImplWeightor &);

    /** destructor */
    virtual ~ImplWeightor();

    DEFINE_CLONE( HWeightor );

    /** return a vector of weights for a multiple alignment. The ordering in the result will be the same
	as in the multiple alignment. Note, that the caller has to delete the weights. */
    virtual void fillCounts(
    		WeightedCountMatrix & counts,
    		const HMultipleAlignment & src,
    		const HEncoder & translator ) const;


 protected:

	 /** rescale the weights to the desired value. If value is 0, the weights are scaled to the number of sequences */
    virtual void rescaleWeights( HSequenceWeights & weights,
    		int nsequences,
    		SequenceWeight value = 0) const;

    /** calculate weights per sequence */
    virtual HSequenceWeights calculateWeights(
    		const HMultipleAlignment & src,
    		const HEncoder & translator ) const;
};


}

#endif /* IMPL_WEIGHTER_H */

