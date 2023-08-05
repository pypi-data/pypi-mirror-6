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

#ifndef IMPL_LOGODDOR_BACKGROUND_H
#define IMPL_LOGODDOR_BACKGROUND_H 1

#include "alignlib_fwd.h"
#include "ImplLogOddor.h"

namespace alignlib
{

  /** Implementation for objects that onvert frequencies into log-odds scores. Different
      log odds scorer use different Uniform frequencies.

      This implementation uses the natural-logarithm.

      @author Andreas Heger
      @version $Id: ImplLogOddor.h,v 1.2 2004/01/07 14:35:35 aheger Exp $
      @short default implementation for calculating log-odds

  */

class ImplLogOddorBackground : public ImplLogOddor
{
 public:
    // constructors and desctructors

	    /** default constructor */
    ImplLogOddorBackground  (
    		const HFrequencyVector & frequencies,
    		const std::string & alphabet,
    		const Score & scale_factor = 1,
    		const Score & mask_value = 10);

    /** default constructor */
    ImplLogOddorBackground  (
    		const Score & scale_factor = 1,
    		const Score & mask_value = 10);

    /** copy constructor */
    ImplLogOddorBackground  (const ImplLogOddorBackground & src);

    DEFINE_CLONE( HLogOddor );

    /** destructor */
    virtual ~ImplLogOddorBackground ();

    /** copy frequencies to a profile and while doing so, convert the frequencies into log-odd-scores */
    virtual void fillProfile(
    		ScoreMatrix & profile,
    		const FrequencyMatrix & frequencies,
    		const HEncoder & encoder ) const;

 private:
    /** sustitution matrix to use */
    HFrequencyVector mBackgroundFrequencies;

    /** the alphabet that the frequencies refer to */
    std::string mAlphabet;
};

}

#endif /* IMPL_LOGODDOR_H */

