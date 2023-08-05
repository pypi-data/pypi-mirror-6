/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersSubstitutionMatrix.cpp,v 1.2 2004/01/07 14:35:33 aheger Exp $

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


#include <iostream>
#include <sstream>
#include <fstream>
#include <iomanip>
#include <stdlib.h>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "alignlib_default.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"

#include "HelpersPalette.h"

using namespace std;

namespace alignlib 
{

	HPalette makePalette()
	{
		HPalette p(new Palette() );
		(*p)[0] = "#BEBEBE";
		return p;
	}

	HPalette makePaletteMView()
	{
		HPalette p( new Palette() );
		
		typedef char MyPaletteType[10];
		const MyPaletteType MVIEW_COLORS[26] = 
		{
				/*A*/	"#00CD00",
				/*B*/	"#000000",
				/*C*/	"#FF8C00",
				/*D*/	"#2222CC",
				/*E*/	"#2222CC",
				/*F*/	"#228B22",
				/*G*/	"#00CD00",
				/*H*/	"#228B22",
				/*I*/	"#00CD00",
				/*J*/   "#000000",
				/*K*/	"#CD2222",
				/*L*/	"#00CD00",
				/*M*/	"#00CD00",
				/*N*/	"#A020F0",
				/*O*/   "#000000",
				/*P*/	"#00CD00",
				/*Q*/	"#A020F0",
				/*R*/	"#CD2222",
				/*S*/	"#A020F0",
				/*T*/	"#A020F0",
				/*U*/	"#000000",
				/*V*/	"#00CD00",
				/*W*/	"#228B22",
				/*X*/	"#474747",
				/*Y*/	"#228B22",
				/*Z*/	"#000000", 
		};
		
		unsigned int i = 0;
		for (unsigned char x = 'A'; x <= 'Z'; ++x, ++i)
		{
			(*p)[x] = MVIEW_COLORS[i]; 
		}
		(*p)[0] = "#BEBEBE";
		return p;
	}
	

} // namespace alignlib









