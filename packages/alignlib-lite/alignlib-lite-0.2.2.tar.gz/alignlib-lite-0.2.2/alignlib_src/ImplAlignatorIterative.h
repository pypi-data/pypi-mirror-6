/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignator.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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

#ifndef IMPL_ALIGNATOR_ITERATIVE_H
#define IMPL_ALIGNATOR_ITERATIVE_H 1

#include "alignlib_fwd.h"
#include "ImplAlignator.h"

namespace alignlib
{
	/** Alignator for iterative alignment.
	 */

  class ImplAlignatorIterative : public ImplAlignator
  {
   public:
      // constructors and desctructors

	   /** empty constructor */
	   ImplAlignatorIterative  ();

	   /** default constructor */
	   ImplAlignatorIterative  ( const HAlignator &, Score min_score );

      /** copy constructor */
      ImplAlignatorIterative  (const ImplAlignatorIterative &);

      /** destructor */
      virtual ~ImplAlignatorIterative();

      DEFINE_CLONE( HAlignator );

      /** method for aligning two arbitrary objects */
      virtual void align( HAlignment &, const HAlignandum &, const HAlignandum & );

   protected:
	   /** perform one iterative alignment step
	    */
	   virtual void alignIteratively( HAlignment &, const HAlignandum & , const HAlignandum & );

   private:
	   /** alignator to use for the alignment */
      HAlignator mAlignator;

      /** alignment stops at minimum score */
      Score mMinScore;

  };
}

#endif /* ALIGNATOR_ITERATIVE_H */
