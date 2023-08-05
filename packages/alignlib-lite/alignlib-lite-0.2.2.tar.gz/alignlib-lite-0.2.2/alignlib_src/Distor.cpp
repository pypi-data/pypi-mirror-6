//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: Distor.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------


#include <iostream>
#include <iomanip>
#include "Distor.h"

using namespace std;

namespace alignlib {

//---------------------------------------------------------< constructors and destructors >--------------------------------------
Distor::Distor () : AlignlibBase()
{
}

Distor::~Distor () {
}

Distor::Distor (const Distor & src ) : AlignlibBase(src)
{
}

//--------------------------------------------------------------------------------------------------------------------------------

std::ostream & operator<< (std::ostream & output, const Distor & src) {
    return output;
}


} // namespace alignlib
