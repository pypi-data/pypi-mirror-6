/*
  alignlib - a library for aligning protein sequences

  $Id: ImplRegularizorTatusov.cpp,v 1.2 2004/01/07 14:35:35 aheger Exp $

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

#include <math.h>
#include <iostream>

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "ImplRegularizorTatusov.h"
#include "HelpersSubstitutionMatrix.h"

using namespace std;

namespace alignlib
{

//----------------------------------------------------------< factory functions >------------------------------------------------------
HRegularizor makeRegularizorTatusov(
		const HSubstitutionMatrix & matrix,
		const HFrequencyVector & background,
		const std::string & alphabet,
		const double & beta,
		const double & lambda )
{
	return HRegularizor(new ImplRegularizorTatusov( matrix, background, alphabet, beta, lambda ));
}

// Background frequencies according to Robinson & Robinson (1991) Proc Natl Acad Sci U S A. Oct 15;88(20):8880-4.
// According to their manuscript, they find:

/*
450431 in total
35155	Ala	8669	Cys	24161	Asp	28354	Glu	17367	Phe
33229	Gly	9906	His	23161	Ile	25872	Lys	40625	Leu
10101	Met	20212	Asn	23435	Pro	19208	Gln	23105	Arg
32070	Ser	26311	Thr	29012	Val	5990	Trp	14488	Tyr

0.078047	Ala	0.019246	Cys	0.053640	Asp	0.062949	Glu	0.038556	Phe
0.073772	Gly	0.021992	His	0.051420	Ile	0.057438	Lys	0.090191	Leu
0.022425	Met	0.044873	Asn	0.052028	Pro	0.042644	Gln	0.051295	Arg
0.071198	Ser	0.058413	Thr	0.064409	Val	0.013298	Trp	0.032165	Tyr
*/

// Can this duplication be avoided?
static const Score array[] = {0.078047, 0.053640, 0.062949, 0.038556, 0.038556,
		 					  0.073772, 0.021992, 0.051420, 0.057438, 0.090191,
		 					  0.022425, 0.044873, 0.052028, 0.042644, 0.051295,
		 					  0.071198, 0.058413, 0.064409, 0.013298, 0.032165};
static const HFrequencyVector BackgroundPsiblast( new FrequencyVector( array, array + sizeof(array) / sizeof(*array)));

//	BackgroundPsiblast( ( array, array + sizeof(array) / sizeof(*array)) );

HRegularizor makeRegularizorPsiblast()
{
	// parameterized according to psiblast
	return HRegularizor(new ImplRegularizorTatusov(
			makeSubstitutionMatrixBlosum62(),
			BackgroundPsiblast,
			"ACDEFGHIKLMNPQRSTVWY",
			10, 0.3176 ));
}

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplRegularizorTatusov::ImplRegularizorTatusov(
		const HSubstitutionMatrix & matrix,
		const HFrequencyVector & background,
		const std::string & alphabet,
		const double & beta,
		const double & lambda ) :
	mSubstitutionMatrix( matrix ),
	mBackgroundFrequencies( background ),
	mAlphabet( alphabet ),
	mBeta( beta),
	mLambda( lambda )
{
	debug_func_cerr(5);

	if (mAlphabet.size() != mBackgroundFrequencies->size())
		THROW( "size of alphabet(" + toString( mAlphabet.size() ) +
				") and frequency vector (" + toString( mBackgroundFrequencies->size() ) + ") of unequal size")

}

//--------------------------------------------------------------------------------------------------------------------------------
ImplRegularizorTatusov::~ImplRegularizorTatusov ()
{
	debug_func_cerr(5);
}

//-------------------------------------------------------------------------------------------------------------------------------
ImplRegularizorTatusov::ImplRegularizorTatusov (const ImplRegularizorTatusov & src ) :
	mSubstitutionMatrix(src.mSubstitutionMatrix),
	mBackgroundFrequencies( src.mBackgroundFrequencies ),
	mBeta( src.mBeta ),
	mLambda( src.mLambda )
{
}

//-------------------------------------------------------------------------------------------------------
/**
 *  */
void ImplRegularizorTatusov::fillFrequencies(
		FrequencyMatrix & frequencies,
		const WeightedCountMatrix & counts,
		const HEncoder & encoder ) const
{
	debug_func_cerr(5);

	/// fill frequencies with raw frequencies
	ImplRegularizor::fillFrequencies( frequencies, counts, encoder );

	Position width = counts.getNumCols();
	Position length = counts.getNumRows();
	Position nchars = mBackgroundFrequencies->size();

	if (width < mBackgroundFrequencies->size())
		THROW ("background size (" + toString(mBackgroundFrequencies->size()) + ") larger than characters in profile (" +
				toString( width) + ")");

	// get nc - the alignment diversity
	double nc = calculateDiversity( counts );
	double alpha = nc -1;
	double alpha_beta = alpha + mBeta;
	int i;

	WeightedCount ntotal;

	debug_cerr( 4, "nc=" << nc << " alpha=" << alpha << " beta=" << mBeta << " lambda=" << mLambda );

	// gi in the PSIBLAST paper
	Score * pseudocounts = new Score[width];

	const HFrequencyVector & bg = mBackgroundFrequencies;

	for (Position column = 0; column < length; column++)
	{
		Frequency * f = frequencies.getRow( column );

		// compute the pseudocounts gi
		for (Residue i = 0; i < nchars; ++i)
		{
			Score total = 0;
			Position ii = encoder->encode( i );
			for (Residue j = 0; j < nchars; ++j)
			{
				Position jj = encoder->encode( i );
				total += f[ii] * (*bg)[i] * exp( mLambda * mSubstitutionMatrix->getValue( ii, jj) );
			}
			pseudocounts[i] = total;
		}

		// mix pseudocounts with observations
		for (Residue i = 0; i < nchars; i++)
		{
			Position ii = encoder->encode( i );
			f[ii] = (alpha * f[ii] + mBeta * pseudocounts[i]) / alpha_beta;
		}
	}
	delete [] pseudocounts;
}

} // namespace alignlib
