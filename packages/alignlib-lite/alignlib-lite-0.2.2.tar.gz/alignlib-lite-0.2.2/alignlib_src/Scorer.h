/*
  alignlib - a library for aligning protein sequences

  $Id: Fragmentor.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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

#ifndef SCORER_H
#define SCORER_H 1

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

	/** @short Protocol class for objects that compute match scores.

    Scores compute the score of matching two positions between
    two @ref Alignandum objects. This class is a helper class for
    @ref Alignator objects. @ref Scorer objects abstract the way a score
    is computed from the task of finding the optimal alignment done
    by @ref Alignator objects.

    This class is a protocol class and as such defines only the general interface.

    @author Andreas Heger
    @version $Id$
	*/

	//----------------------------------------------------------------
  class Scorer : public virtual AlignlibBase
  {
    public:

      /** empty constructor */
      Scorer();

      /** destructor */
      virtual ~Scorer ();

      /** copy constructor */
      Scorer( const Scorer & src);

      DEFINE_ABSTRACT_CLONE( HScorer )

      /** return a new scorer of same type but initialized
       *  for the two @ref Alignandum objects row and col.
       *
       * @param row	@ref Alignandum object to be aligned.
       * @param col @ref Alignandum object to be aligned.
       */
      virtual HScorer getNew(
    		  const HAlignandum & row,
    		  const HAlignandum & col) const = 0;

      /** return score of matching row to col
       */
      virtual Score getScore(
    		  const Position & row,
    		  const Position & col ) const = 0;
  };

}


#endif /* SCORER_H */
