/*
  alignlib - a library for aligning protein sequences

  $Id: ImplRegularizorDirichletInterpolate.h,v 1.2 2004/01/07 14:35:36 aheger Exp $

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

#ifndef IMPL_REGULARIZOR_DIRICHLET_INTERPOLATE_H
#define IMPL_REGULARIZOR_DIRICHLET_INTERPOLATE_H 1

#include "alignlib_fwd.h"
#include "ImplRegularizorDirichlet.h"

namespace alignlib {


    /** When you use this class as a regularizor, the regularizor is
	switched of, when there are more than FADE_CUTOFF observation
	in a column.

	@author Andreas Heger
	@version $Id: ImplRegularizorDirichletInterpolate.h,v 1.2 2004/01/07 14:35:36 aheger Exp $
	@short protocol class for sequence weighters

    */

class ImplRegularizorDirichletInterpolate : public ImplRegularizorDirichlet
{
 public:
    // constructors and desctructors

    /** default constructor */
    ImplRegularizorDirichletInterpolate ( WeightedCount fade_cutoff );

    /** copy constructor */
    ImplRegularizorDirichletInterpolate ( const ImplRegularizorDirichletInterpolate &);

    /** destructor */
    virtual ~ImplRegularizorDirichletInterpolate ();

 protected:

    /** This function encapsulates that part of the algorithm, that needs to access the lgamma-function. It
	has been externalized, so that it can be overloaded to implement different speed-ups.

	It returns the maximum difference.

	The implemention here hashes the calls to the lgamma-function
    */
    virtual double calculateBetaDifferences(
    		TYPE_BETA_DIFFERENCES beta_differences,
    		const WeightedCount * n,
    		WeightedCount ntotal ) const;


 private:

};


}

#endif /* IMPL_REGULARIZOR_DIRICHLET_INTERPOLATE_H */

