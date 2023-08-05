/*
  alignlib - a library for aligning protein sequences

  $Id: alignlib.h,v 1.5 2005/02/24 11:07:25 aheger Exp $

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

#include <stdio.h>
#include <stdlib.h>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"

namespace alignlib
{

#ifdef DEBUG

  unsigned int AlignlibDebug::mRecurse = 0;
  unsigned int AlignlibDebug::mVerbosity = 5;

  AlignlibDebug::AlignlibDebug(std::ostream& os, unsigned int i, const std::string& s)
    : mName(s), mPriority(i), mStream(os)
    {

	  char * verb = getenv("ALIGNLIB_DEBUG");
	  if (verb != NULL)
		  mVerbosity = atoi( verb );

      if (showDebug(mPriority))
	mStream << (mRecurse ? std::string(indent * mRecurse, ' ') : std::string())
	      << mName << " [entry]" << std::endl;

      ++mRecurse;
    }

  AlignlibDebug::~AlignlibDebug()
    {
      --mRecurse;

      if (showDebug(mPriority))
	mStream << (mRecurse ? std::string(indent * mRecurse, ' ') :std::string())
		<< mName << " [exit]" << std::endl;
    }

  std::string AlignlibDebug::getPrefix()
    {
      return std::string(indent * (mRecurse), ' ');
    }

  bool AlignlibDebug::showDebug(unsigned int v)
    {
      return v <= mVerbosity;
    }

  void AlignlibDebug::setVerbosity( unsigned int v )
    {
      mVerbosity = v;
    }

#endif // Debug
}

