//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplDistor.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#include <iostream>
#include <iomanip>

#include "MultipleAlignment.h"
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "ImplDistor.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "DistanceMatrix.h"

using namespace std;

namespace alignlib {

//---------------------------------------------------------< constructors and destructors >--------------------------------------
ImplDistor::ImplDistor () : Distor(), mLength(0)
{
}

ImplDistor::~ImplDistor () {
}

ImplDistor::ImplDistor (const ImplDistor & src ) :
	Distor(src),
    mLength(src.mLength) {
}

//--------------------------------------------------------------------------------------------------------------------------------
void ImplDistor::calculateMatrix(
		HDistanceMatrix & matrix,
		const HMultipleAlignment & multali) const
		{

    DistanceMatrixSize i, j;

    DistanceMatrixSize width = multali->getNumSequences();

    if (matrix->getWidth() != width)
	throw AlignlibException( "Multiple alignment and matrix have different size in ImplDistor::operator()");

    for (i = 0; i < width - 1; i++)
      for (j = i + 1; j < width; j++)
	(*matrix)(i, j) = calculateDistance( (*multali)[i], (*multali)[j] );

}


//--------------------------------------------------------------------------------------------------------------------------------

} // namespace alignlib
