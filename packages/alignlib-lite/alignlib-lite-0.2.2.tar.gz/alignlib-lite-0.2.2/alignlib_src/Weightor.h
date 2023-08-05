/*
  alignlib - a library for aligning protein sequences

  $Id: Weightor.h,v 1.3 2004/03/19 18:23:42 aheger Exp $

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

#ifndef WEIGHTOR_H
#define WEIGHTOR_H 1

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

/** @short Protocoll class for @ref Weightor objects.

    Given a multiple alignment of sequences, a @ref Weightor returns a vector of
    weights, for each sequence one weight. The vector has to be deleted
    by the caller.

    The object takes a multiple alignment and return an array of weights.

    This class is a protocol class and as such defines only the general interface.

    @author Andreas Heger
    @version $Id: Weightor.h,v 1.3 2004/03/19 18:23:42 aheger Exp $

*/
class Weightor : public virtual AlignlibBase
{
 public:

    /** default constructor */
    Weightor();

    /** copy constructor */
    Weightor(const Weightor &);

    /** destructor */
    virtual ~Weightor();

    DEFINE_ABSTRACT_CLONE( HWeightor )

    /** fill a counts matrix from a multiple alignment
     *
     * @param counts 	@ref WeightedCountMatrix to fill.
     * @param src		@ref MultipleAlignment object to compute weights from.
     * @param encoder 	@ref Encoder object.
     */
    virtual void fillCounts(
    		WeightedCountMatrix & counts,
    		const HMultipleAlignment & src,
    		const HEncoder & translator ) const = 0;

};

}

#endif /* _WEIGHTOR_H */


