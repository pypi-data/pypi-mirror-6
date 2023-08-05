//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplDistorKimura.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#include <iostream>
#include <iomanip>
#include <string>
#include <math.h>

#include "Encoder.h"
#include "HelpersEncoder.h"
#include "MultipleAlignment.h"
#include "ImplDistorKimura.h"
#include "AlignlibDebug.h"
#include "Toolkit.h"

using namespace std;

namespace alignlib
{

#define MAX_DIFFERENCE 0.85
#define MAX_DISTANCE 5.2030

//-------------------------> factory functions <-------------------------------------------------------------------------------
HDistor makeDistorKimura()
{
	return HDistor( new ImplDistorKimura() );
}

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplDistorKimura::ImplDistorKimura () : ImplDistor()
{
	debug_func_cerr( 5 );
}

ImplDistorKimura::~ImplDistorKimura ()
{
	debug_func_cerr( 5 );
}

ImplDistorKimura::ImplDistorKimura (const ImplDistorKimura & src ) :
	ImplDistor( src ) {
}

//--------------------------------------------------------------------------------------------------------------------------------
IMPLEMENT_CLONE( HDistor, ImplDistorKimura );

//--------------------------------------------------------------------------------------------------------------------------------
DistanceMatrixValue ImplDistorKimura::getMaximumPossibleDistance() const
{
	return MAX_DISTANCE;
}

//--------------------------------------------------------------------------------------------------------------------------------
DistanceMatrixValue ImplDistorKimura::calculateDistance(
		const std::string & s_row_1,
		const std::string & s_row_2) const
{

	debug_func_cerr(5);
	unsigned int i;
	unsigned int identities = 0;		// number of identities
	unsigned int n_nongaps = 0;		// normalize over non-gap-positions

	unsigned char gap_char = getToolkit()->getEncoder()->getGapChar();

	for (i = 0; i < s_row_1.length(); i++)
	{
		if ((s_row_1[i] != gap_char) && (s_row_2[i] != gap_char))
		{
			n_nongaps ++;
			if (s_row_1[i] == s_row_2[i])
				identities++;
		}
	}

	debug_cerr( 3, "Comparison between " << s_row_1 << " and " << s_row_2 << ": non_gaps=" << n_nongaps << " identitities=" << identities );

	double pdiff;
	if (n_nongaps > 0)
		pdiff = 1.0 - (double)identities / (double)n_nongaps;
	else
		pdiff = 1.0;

	if (pdiff > MAX_DIFFERENCE)
		return MAX_DISTANCE;
	else
		return -log( 1.0 - pdiff - 0.2 * pdiff * pdiff);
}



//--------------------------------------------------------------------------------------------------------------------------------

} // namespace alignlib
