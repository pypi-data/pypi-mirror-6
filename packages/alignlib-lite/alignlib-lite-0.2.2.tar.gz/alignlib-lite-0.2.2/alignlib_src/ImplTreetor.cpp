//--------------------------------------------------------------------------------
// Project alignlib
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id: ImplTreetor.cpp,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
//--------------------------------------------------------------------------------

#include <iostream>
#include <iomanip>
#include "AlignlibDebug.h"
#include "ImplTreetor.h"
#include "Tree.h"

using namespace std;

namespace alignlib {

//-------------------------< constructors and destructors >--------------------------
ImplTreetor::ImplTreetor () : Treetor()
{
	debug_func_cerr( 5 );
}

ImplTreetor::~ImplTreetor ()
{
	debug_func_cerr( 5 );
}

ImplTreetor::ImplTreetor (const ImplTreetor & src ) : Treetor( src )
{
}

} /* namespace alignlib */

