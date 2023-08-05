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
#include "Segment.h"

using namespace std;

namespace alignlib 
{

//---------------------------------------------------------< constructors and destructors >--------------------------------------
Segment::Segment () :
mStart(NO_POS), mEnd(NO_POS)
{
}

Segment::Segment ( const Position & start, const Position & end) :
mStart(start), mEnd(end)
{
}

Segment::~Segment () {
}

Segment::Segment (const Segment & src ) :
mStart(src.mStart), mEnd(src.mEnd)
{
}

Position Segment::getSize() const
{
	if ((mStart == NO_POS) || (mEnd == NO_POS) || (mEnd <= mStart ))
		return 0;
	else
		return mEnd - mStart;
}

bool Segment::isEmpty() const
{
	return ((mStart == NO_POS) || (mEnd == NO_POS) || (mEnd <= mStart ));
}
	
//--------------------------------------------------------------------------------------------------------------------------------

std::ostream & operator<< (std::ostream & output, const Segment & src) {
	output << src.mStart << ".." << src.mEnd;
    return output;
}


} // namespace alignlib
