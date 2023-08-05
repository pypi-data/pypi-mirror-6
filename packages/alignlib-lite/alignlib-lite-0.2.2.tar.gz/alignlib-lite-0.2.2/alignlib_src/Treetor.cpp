//--------------------------------------------------------------------------------
// Project alignlib
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: Treetor.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------

#include <iostream>
#include <iomanip>
#include "Treetor.h"

using namespace std;

namespace alignlib {


//---------------------------------------------------------< constructors and destructors >--------------------------------------
Treetor::Treetor () : AlignlibBase()
{
}

Treetor::~Treetor () {
}

Treetor::Treetor (const Treetor & src )  : AlignlibBase(src)
{
}


//---------------------------------------------------------< Input/Output routines >---------------------------------------------

std::ostream & operator<< (std::ostream & output, const Treetor & src) {
    return output;
}

std::istream & operator>> (std::istream & input, Treetor & src) {
    return input;
}

} /* namespace alignlib */

