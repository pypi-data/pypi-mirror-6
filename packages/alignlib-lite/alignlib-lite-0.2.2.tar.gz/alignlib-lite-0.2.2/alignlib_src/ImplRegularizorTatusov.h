/*
  alignlib - a library for aligning protein sequences

  $Id: ImplRegularizorTatusov.h,v 1.2 2004/01/07 14:35:35 aheger Exp $

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

#ifndef IMPL_REGULARIZOR_Tatusov_H
#define IMPL_REGULARIZOR_Tatusov_H 1

#include "alignlib_fwd.h"
#include "ImplRegularizor.h"

namespace alignlib
{

  /** Implementation of regularization according to
   * Tatusov,R.L., Altschul,S.F. and Koonin,E.V. (1994) Proc. Natl. Acad. Sci. USA, 91, 12091-12095.

     I have used the description in the Psiblast paper:

    Altschul SF, Madden TL, Schäffer AA, Zhang J, Zhang Z, Miller W, Lipman DJ.
	Gapped BLAST and PSI-BLAST: a new generation of protein database search programs.
	Nucleic Acids Res. 1997 Sep 1;25(17):3389-402

      @author Andreas Heger
      @version $Id: ImplRegularizorTatusov.h,v 1.2 2004/01/07 14:35:35 aheger Exp $
      @short protocol class for sequence weighters

  */

class ImplRegularizorTatusov : public ImplRegularizor
{
 public:
    // constructors and desctructors

    /** default constructor */
    ImplRegularizorTatusov  (
    		const HSubstitutionMatrix & matrix,
    		const HFrequencyVector & background,
    		const std::string & alphabet,
    		const Score & beta,
    		const Score & lambda );

    /** copy constructor */
    ImplRegularizorTatusov  (const ImplRegularizorTatusov &);

    /** destructor */
    virtual ~ImplRegularizorTatusov ();

    /** copy the counts into the frequencies and regularize them by doing so. */
    virtual void fillFrequencies( FrequencyMatrix & frequencies,
				  				  const WeightedCountMatrix & counts,
				  				  const HEncoder & encoder ) const;

 protected:

	 /** substitution matrix */
	 const HSubstitutionMatrix mSubstitutionMatrix;

	 /** background frequencies */
	 const HFrequencyVector mBackgroundFrequencies;

	 /** beta component : the larger, the higher the influence of pseudocounts */
	 Score mBeta;

	 /** lambda : the lambda value associated with the substitution matrix */
	 Score mLambda;

	 /** alphabet relating to the background frequencies */
	 std::string mAlphabet;
};

}

#endif /* IMPL_REGULARIZOR_Tatusov_H */

