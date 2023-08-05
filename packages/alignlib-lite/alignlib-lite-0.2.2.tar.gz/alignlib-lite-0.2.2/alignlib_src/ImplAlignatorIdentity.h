/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignatorIdentity.h,v 1.3 2004/03/19 18:23:41 aheger Exp $

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

#ifndef IMPL_ALIGNATOR_IDENTITY_H
#define IMPL_ALIGNATOR_IDENTITY_H 1

#include "alignlib_fwd.h"
#include "ImplAlignator.h"

namespace alignlib
{

class Alignandum;

/** @short align identical residues (dot-matrix creation).

    @author Andreas Heger
    @version $Id: ImplAlignatorIdentity.h,v 1.3 2004/03/19 18:23:41 aheger Exp $
*/
class ImplAlignatorIdentity : public ImplAlignator
{
 public:
    // constructors and desctructors

    /** default constructor */
    ImplAlignatorIdentity  ();

    /** copy constructor */
    ImplAlignatorIdentity  (const ImplAlignatorIdentity &);

    /** destructor */
    virtual ~ImplAlignatorIdentity ();

    /** method for aligning two arbitrary objects */
    virtual void align(HAlignment & dest,
    		const HAlignandum & row, const HAlignandum & col );

    DEFINE_CLONE(HAlignator);
};

}

#endif /* IMPL_ALIGNATOR_H */

