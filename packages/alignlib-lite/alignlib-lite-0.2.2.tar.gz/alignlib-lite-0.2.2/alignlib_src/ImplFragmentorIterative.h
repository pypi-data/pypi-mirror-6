/*
  alignlib - a library for aligning protein sequences

  $Id: ImplFragmentorIterative.h,v 1.3 2004/03/19 18:23:41 aheger Exp $

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

#ifndef IMPL_FRAGMENTOR_ITERATIVE_H
#define IMPL_FRAGMENTOR_ITERATIVE_H 1

#include "alignlib_fwd.h"
#include "ImplFragmentor.h"
#include "Alignment.h"

namespace alignlib
{
/**
   @short build fragments by iteratively aligning in a dotplot.

   @author Andreas Heger
   @version $Id: ImplFragmentorIterative.h,v 1.3 2004/03/19 18:23:41 aheger Exp $
*/
class ImplFragmentorIterative : public ImplFragmentor
{
  /* class member functions-------------------------------------------------------------- */
 public:
    /* constructors and desctructors------------------------------------------------------- */

	 /** constructor */
	 ImplFragmentorIterative();

	 /** constructor */
	 ImplFragmentorIterative(
    		const HAlignment & dots,
    		Score min_score,
    		Score gop,
    		Score gep);

    /** destructor */
    virtual ~ImplFragmentorIterative ();

    /** copy constructor */
    ImplFragmentorIterative( const ImplFragmentorIterative & src);

    DEFINE_CLONE( HFragmentor );
 protected:
    /** the alignator used to create dot-plots */
    HAlignment mDots;

    /** minimum score for alignment */
    Score mMinScore;

    /** gap penalties */
    Score mGop;
    Score mGep;

    /** perform the actual alignment */
    virtual void performFragmentation(
    		const HAlignment & sample,
    		const HAlignandum & row,
    		const HAlignandum & col );
};

}

#endif /* FRAGMENTOR_H */
