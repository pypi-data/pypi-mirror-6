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

#ifndef IMPL_SCORER_PROFILE_SEQUENCE_H
#define IMPL_SCORER_PROFILE_SEQUENCE_H 1

#include "alignlib_fwd.h"
#include "ImplProfile.h"
#include "ImplSequence.h"
#include "ImplScorer.h"

namespace alignlib
{

  //----------------------------------------------------------------
  class ImplScorerProfileSequence : public ImplScorer
  {
    public:

    	/** empty constructor */
    	ImplScorerProfileSequence();
    	/** constructor */
    	ImplScorerProfileSequence(const HProfile & row, const HSequence & col);

      /** destructor */
      virtual ~ImplScorerProfileSequence ();

      /** copy constructor */
      ImplScorerProfileSequence( const ImplScorerProfileSequence & src);

      DEFINE_CLONE( HScorer );

      /** return a new scorer of same type initialized with row and col
       */
      virtual HScorer getNew( const HAlignandum & row, const HAlignandum & col) const;

      virtual Score getScore(
    		  const Position & row,
    		  const Position & col ) const;


  protected:
      /** pointer to member data of row/col : AlignandumSequence */
      const ScoreMatrix * mRowProfile;

      const ResidueVector * mColSequence;

      /** the profile width */
      Residue mProfileWidth;

  };

}


#endif /* SCORER_H */
