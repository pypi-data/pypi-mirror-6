/*
  alignlib - a library for aligning protein sequences

  $Id: Regularizor.h,v 1.2 2004/01/07 14:35:37 aheger Exp $

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

#ifndef REGULARIZOR_H
#define REGULARIZOR_H 1

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"
namespace alignlib
{

  /** @short Protocoll class for objects, that regularize residue counts.

      This class is a protocol class and as such defines only the general interface.

	  Regularizers are used in profile computation. They change observed residue
	  counts into estimates of residue frequencies. Estimates might take into
	  account the number of observations per column.

      @author Andreas Heger
      @version $Id: Regularizor.h,v 1.2 2004/01/07 14:35:37 aheger Exp $

  */

class Regularizor : public virtual AlignlibBase
{
 public:
    // constructors and desctructors

    /** default constructor */
    Regularizor  ();

    /** copy constructor */
    Regularizor  (const Regularizor &);

    /** destructor */
    virtual ~Regularizor ();

    DEFINE_ABSTRACT_CLONE( HRegularizor )

    /** regularize a @ref WeightedCountMatrix.
     *
     * @param frequencies @ref FrequencyMatrix to store result.
     * @param counts @ref WeightedCountMatrix with observed residue counts.
     * @param encoder 	@ref Encoder object.
     * */
    virtual void fillFrequencies(
    		FrequencyMatrix & frequencies,
    		const WeightedCountMatrix & counts,
    		const HEncoder & translator ) const = 0;

};

}

#endif /* REGULARIZOR_H */

