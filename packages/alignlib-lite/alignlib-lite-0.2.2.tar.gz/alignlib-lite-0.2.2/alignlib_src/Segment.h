/*
  alignlib - a library for aligning protein sequences

  $Id: Fragmentor.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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

#ifndef SEGMENT_H
#define SEGMENT_H 1

#include "alignlib_fwd.h"

namespace alignlib
{

	/** @short A segment
   
	A segment is defined by a start and an end. 
	    
    @author Andreas Heger
    @version $Id$
	*/

	//----------------------------------------------------------------
  class Segment
  {
    public:
      
    	/** empty constructor */
        Segment(); 

        /** empty constructor */
        Segment( const Position & start, const Position & end); 

        /** destructor */
        ~Segment();
      
        /** copy constructor */
        Segment( const Segment & src);

        /** @short return true if segment is empty */
        bool isEmpty() const;

        /** @short return the size the segment */
        Position getSize() const;

        /** start of the segment */
        Position mStart;
        
        /** end of the segment */
        Position mEnd;
      
  };
  
}


#endif /* SEGMENT_H */
