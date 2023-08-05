/*
  alignlib - a library for aligning protein sequences

  $Id: ImplLogOddor.h,v 1.2 2004/01/07 14:35:35 aheger Exp $

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

#ifndef IMPL_LOGODDOR_H
#define IMPL_LOGODDOR_H 1

#include "alignlib_fwd.h"
#include "LogOddor.h"
#include "Macros.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{

  /** Implementation for objects that onvert frequencies into log-odds scores. Different
      log odds scorer use different background frequencies.

      This implementation uses the natural-logarithm.

      @author Andreas Heger
      @version $Id: ImplLogOddor.h,v 1.2 2004/01/07 14:35:35 aheger Exp $
      @short default implementation for calculating log-odds

  */

class ImplLogOddor : public LogOddor, public ImplAlignlibBase
{
 public:
    // constructors and desctructors

    /** default constructor */
    ImplLogOddor  (
    		const Score & scale_factor = 1,
    		const Score & mask_value = -10 );

    /** copy constructor */
    ImplLogOddor  (const ImplLogOddor &);

    /** destructor */
    virtual ~ImplLogOddor ();

    /** copy frequencies to a profile and while doing so, convert the
     * frequencies into log-odd-scores */
    virtual void fillProfile(
    		ScoreMatrix & profile,
    		const FrequencyMatrix & frequencies,
    		const HEncoder & encoder ) const;

    DEFINE_CLONE( HLogOddor );

 protected:

    /** scale factor by which to scale the scores */
    const Score mScaleFactor;

    const Score mMaskValue;

};

}

#endif /* IMPL_LOGODDOR_H */

