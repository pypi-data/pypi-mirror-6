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

#include "Encoder.h"
#include "HelpersEncoder.h"
#include "Matrix.h"
#include "HelpersSubstitutionMatrix.h"

using namespace std;

namespace alignlib 
{

static Score blosum62[23 * 23] = 
{
       /* A   B   C   D   E    F   G   H   I   K    L   M   N   P   Q    R   S   T   V   W    X   Y   Z */
/* A */   4, -2,  0, -2, -1,  -2,  0, -2, -1, -1,  -1, -1, -2, -1, -1,  -1,  1,  0,  0, -3,  -1, -2, -1,
/* B */  -2,  6, -3,  6,  2,  -3, -1, -1, -3, -1,  -4, -3,  1, -1,  0,  -2,  0, -1, -3, -4,  -1, -3,  2,
/* C */   0, -3,  9, -3, -4,  -2, -3, -3, -1, -3,  -1, -1, -3, -3, -3,  -3, -1, -1, -1, -2,  -1, -2, -4,
/* D */  -2,  6, -3,  6,  2,  -3, -1, -1, -3, -1,  -4, -3,  1, -1,  0,  -2,  0, -1, -3, -4,  -1, -3,  2,
/* E */  -1,  2, -4,  2,  5,  -3, -2,  0, -3,  1,  -3, -2,  0, -1,  2,   0,  0, -1, -2, -3,  -1, -2,  5,  
/* F */  -2, -3, -2, -3, -3,   6, -3, -1,  0, -3,   0,  0, -3, -4, -3,  -3, -2, -2, -1,  1,  -1,  3, -3,
/* G */   0, -1, -3, -1, -2,  -3,  6, -2, -4, -2,  -4, -3,  0, -2, -2,  -2,  0, -2, -3, -2,  -1, -3, -2,
/* H */  -2, -1, -3, -1,  0,  -1, -2,  8, -3, -1,  -3, -2,  1, -2,  0,   0, -1, -2, -3, -2,  -1,  2,  0,
/* I */  -1, -3, -1, -3, -3,   0, -4, -3,  4, -3,   2,  1, -3, -3, -3,  -3, -2, -1,  3, -3,  -1, -1, -3,
/* K */  -1, -1, -3, -1,  1,  -3, -2, -1, -3,  5,  -2, -1,  0, -1,  1,   2,  0, -1, -2, -3,  -1, -2,  1,  
/* L */  -1, -4, -1, -4, -3,   0, -4, -3,  2, -2,   4,  2, -3, -3, -2,  -2, -2, -1,  1, -2,  -1, -1, -3,
/* M */  -1, -3, -1, -3, -2,   0, -3, -2,  1, -1,   2,  5, -2, -2,  0,  -1, -1, -1,  1, -1,  -1, -1, -2,
/* N */  -2,  1, -3,  1,  0,  -3,  0,  1, -3,  0,  -3, -2,  6, -2,  0,   0,  1,  0, -3, -4,  -1, -2,  0,
/* P */  -1, -1, -3, -1, -1,  -4, -2, -2, -3, -1,  -3, -2, -2,  7, -1,  -2, -1, -1, -2, -4,  -1, -3, -1,
/* Q */  -1,  0, -3,  0,  2,  -3, -2,  0, -3,  1,  -2,  0,  0, -1,  5,   1,  0, -1, -2, -2,  -1, -1,  2,  
/* R */  -1, -2, -3, -2,  0,  -3, -2,  0, -3,  2,  -2, -1,  0, -2,  1,   5, -1, -1, -3, -3,  -1, -2,  0,
/* S */   1,  0, -1,  0,  0,  -2,  0, -1, -2,  0,  -2, -1,  1, -1,  0,  -1,  4,  1, -2, -3,  -1, -2,  0,
/* T */   0, -1, -1, -1, -1,  -2, -2, -2, -1, -1,  -1, -1,  0, -1, -1,  -1,  1,  5,  0, -2,  -1, -2, -1,
/* V */   0, -3, -1, -3, -2,  -1, -3, -3,  3, -2,   1,  1, -3, -2, -2,  -3, -2,  0,  4, -3,  -1, -1, -2,
/* W */  -3, -4, -2, -4, -3,   1, -2, -2, -3, -3,  -2, -1, -4, -4, -2,  -3, -3, -2, -3, 11,  -1,  2, -3,  
/* X */  -1, -1, -1, -1, -1,  -1, -1, -1, -1, -1,  -1, -1, -1, -1, -1,  -1, -1, -1, -1, -1,  -1, -1, -1,
/* Y */  -2, -3, -2, -3, -2,   3, -3,  2, -1, -2,  -1, -1, -2, -3, -1,  -2, -2, -2, -1,  2,  -1,  7, -2,
/* Z */  -1,  2, -4,  2,  5,  -3, -2,  0, -3,  1,  -3, -2,  0, -1,  2,   0,  0, -1, -2, -3,  -1, -2,  5, 		
};

static Score blosum50[23 * 23] = {
/*	     A   B   C   D   E  F   G   H   I   K  L   M   N   P   Q  R   S   T   V   W  X   Y   Z */ 
/* A */  5, -2, -1, -2, -1,-3,  0, -2, -1, -1,-2, -1, -1, -1, -1,-2,  1,  0,  0, -3,-1, -2, -1, 
/* B */ -2,  5, -3,  5,  1,-4, -1,  0, -4,  0,-4, -3,  4, -2,  0,-1,  0,  0, -4, -5,-1, -3,  2, 
/* C */ -1, -3, 13, -4, -3,-2, -3, -3, -2, -3,-2, -2, -2, -4, -3,-4, -1, -1, -1, -5,-2, -3, -3, 
/* D */ -2,  5, -4,  8,  2,-5, -1, -1, -4, -1,-4, -4,  2, -1,  0,-2,  0, -1, -4, -5,-1, -3,  1, 
/* E */ -1,  1, -3,  2,  6,-3, -3,  0, -4,  1,-3, -2,  0, -1,  2, 0, -1, -1, -3, -3,-1, -2,  5, 
/* F */ -3, -4, -2, -5, -3, 8, -4, -1,  0, -4, 1,  0, -4, -4, -4,-3, -3, -2, -1,  1,-2,  4, -4, 
/* G */  0, -1, -3, -1, -3,-4,  8, -2, -4, -2,-4, -3,  0, -2, -2,-3,  0, -2, -4, -3,-2, -3, -2, 
/* H */ -2,  0, -3, -1,  0,-1, -2, 10, -4,  0,-3, -1,  1, -2,  1, 0, -1, -2, -4, -3,-1,  2,  0, 
/* I */ -1, -4, -2, -4, -4, 0, -4, -4,  5, -3, 2,  2, -3, -3, -3,-4, -3, -1,  4, -3,-1, -1, -3, 
/* K */ -1,  0, -3, -1,  1,-4, -2,  0, -3,  6,-3, -2,  0, -1,  2, 3,  0, -1, -3, -3,-1, -2,  1, 
/* L */ -2, -4, -2, -4, -3, 1, -4, -3,  2, -3, 5,  3, -4, -4, -2,-3, -3, -1,  1, -2,-1, -1, -3, 
/* M */ -1, -3, -2, -4, -2, 0, -3, -1,  2, -2, 3,  7, -2, -3,  0,-2, -2, -1,  1, -1,-1,  0, -1, 
/* N */ -1,  4, -2,  2,  0,-4,  0,  1, -3,  0,-4, -2,  7, -2,  0,-1,  1,  0, -3, -4,-1, -2,  0, 
/* P */ -1, -2, -4, -1, -1,-4, -2, -2, -3, -1,-4, -3, -2, 10, -1,-3, -1, -1, -3, -4,-2, -3, -1, 
/* Q */ -1,  0, -3,  0,  2,-4, -2,  1, -3,  2,-2,  0,  0, -1,  7, 1,  0, -1, -3, -1,-1, -1,  4, 
/* R */ -2, -1, -4, -2,  0,-3, -3,  0, -4,  3,-3, -2, -1, -3,  1, 7, -1, -1, -3, -3,-1, -1,  0, 
/* S */  1,  0, -1,  0, -1,-3,  0, -1, -3,  0,-3, -2,  1, -1,  0,-1,  5,  2, -2, -4,-1, -2,  0, 
/* T */  0,  0, -1, -1, -1,-2, -2, -2, -1, -1,-1, -1,  0, -1, -1,-1,  2,  5,  0, -3, 0, -2, -1, 
/* V */  0, -4, -1, -4, -3,-1, -4, -4,  4, -3, 1,  1, -3, -3, -3,-3, -2,  0,  5, -3,-1, -1, -3, 
/* W */ -3, -5, -5, -5, -3, 1, -3, -3, -3, -3,-2, -1, -4, -4, -1,-3, -4, -3, -3, 15,-3,  2, -2, 
/* X */ -1, -1, -2, -1, -1,-2, -2, -1, -1, -1,-1, -1, -1, -2, -1,-1, -1,  0, -1, -3,-1, -1, -1, 
/* Y */ -2, -3, -3, -3, -2, 4, -3,  2, -1, -2,-1,  0, -2, -3, -1,-1, -2, -2, -1,  2,-1,  8, -2, 
/* Z */ -1,  2, -3,  1,  5,-4, -2,  0, -3,  1,-3, -1,  0, -1,  4, 0,  0, -1, -3, -2,-1, -2,  5, 		
		};

static Score pam30[23*23] = {
/*       A B C D E F GH I K L M N P Q R S T V W X Y Z*/
/* A */  6, -3, -6, -3, -2, -8, -2, -7, -5, -7, -6, -5, -4, -2, -4, -7, 0, -1, -2, -13, -3, -8, -3, 
/* B */ -3, 6, -12, 6, 1, -10, -3, -1, -6, -2, -9, -10, 6, -7, -3, -7, -1, -3, -8, -10, -5, -6, 0, 
/* C */ -6, -12, 10, -14, -14, -13, -9, -7, -6, -14, -15, -13, -11, -8, -14, -8, -3, -8, -6, -15,-9, -4, -14,
/* D */ -3, 6,-14,8,2,-15,-3, -4, -7, -4, -12,-11,2,-8, -2, -10,-4, -5, -8, -15,-5, -11,1,
/* E */ -2, 1,-14,2,8,-14,-4, -5, -5, -4, -9, -7, -2, -5, 1,-9, -4, -6, -6, -17,-5, -8, 6,
/* F */ -8, -10,-13,-15,-14,9,-9, -6, -2, -14,-3, -4, -9, -10,-13,-9, -6, -9, -8, -4, -8, 2,-13,
/* G */ -2, -3, -9, -3, -4, -9, 6,-9, -11,-7, -10,-8, -3, -6, -7, -9, -2, -6, -5, -15,-5, -14,-5,
/* H */ -7, -1, -7, -4, -5, -6, -9, 9,-9, -6, -6, -10,0,-4, 1,-2, -6, -7, -6, -7, -5, -3, -1,
/* I */ -5, -6, -6, -7, -5, -2, -11,-9, 8,-6, -1, -1, -5, -8, -8, -5, -7, -2, 2,-14,-5, -6, -6,
/* K */ -7, -2, -14,-4, -4, -14,-7, -6, -6, 7,-8, -2, -1, -6, -3, 0,-4, -3, -9, -12,-5, -9, -4,
/* L */ -6, -9, -15,-12,-9, -3, -10,-6, -1, -8, 7,1,-7, -7, -5, -8, -8, -7, -2, -6, -6, -7, -7,
/* M */ -5, -10,-13,-11,-7, -4, -8, -10,-1, -2, 1,11, -9, -8, -4, -4, -5, -4, -1, -13,-5, -11,-5,
/* N */ -4, 6,-11,2,-2, -9, -3, 0,-5, -1, -7, -9, 8,-6, -3, -6, 0,-2, -8, -8, -3, -4, -3,
/* P */ -2, -7, -8, -8, -5, -10,-6, -4, -8, -6, -7, -8, -6, 8,-3, -4, -2, -4, -6, -14,-5, -13,-4,
/* Q */ -4, -3, -14,-2, 1,-13,-7, 1,-8, -3, -5, -4, -3, -3, 8,-2, -5, -5, -7, -13,-5, -12,6,
/* R */ -7, -7, -8, -10,-9, -9, -9, -2, -5, 0,-8, -4, -6, -4, -2, 8,-3, -6, -8, -2, -6, -10,-4,
/* S */  0,-1, -3, -4, -4, -6, -2, -6, -7, -4, -8, -5, 0,-2, -5, -3, 6,0,-6, -5, -3, -7, -5,
/* T */ -1, -3, -8, -5, -6, -9, -6, -7, -2, -3, -7, -4, -2, -4, -5, -6, 0,7,-3, -13,-4, -6, -6,
/* V */ -2, -8, -6, -8, -6, -8, -5, -6, 2,-9, -2, -1, -8, -6, -7, -8, -6, -3, 7,-15,-5, -7, -6,
/* W */ -13,-10,-15,-15,-17,-4, -15,-7, -14,-12,-6, -13,-8, -14,-13,-2, -5, -13,-15,13, -11,-5, -14,
/* X */ -3, -5, -9, -5, -5, -8, -5, -5, -5, -5, -6, -5, -3, -5, -5, -6, -3, -4, -5, -11,-5, -7, -5,
/* Y */ -8, -6, -4, -11,-8, 2,-14,-3, -6, -9, -7, -11,-4, -13,-12,-10,-7, -6, -7, -5, -7, 10, -9,
/* Z */ -3, 0,-14,1,6,-13,-5, -1, -6, -4, -7, -5, -3, -4, 6,-4, -5, -6, -6, -14,-5, -9, 6,
};


static Score pam120[23*23] = {
/*       A  B  C  D  E   F  G  H  I  K   L  M  N  P  Q   R  S  T  V  W   X  Y  Z  */
/* A */  3, 0,-3, 0, 0, -4, 1,-3,-1,-2, -3,-2,-1, 1,-1, -3, 1, 1, 0,-7, -1,-4,-1,
/* B */  0, 4,-6, 4, 3, -5, 0, 1,-3, 0, -4,-4, 3,-2, 0, -2, 0, 0,-3,-6, -1,-3, 2,
/* C */ -3,-6, 9,-7,-7, -6,-4,-4,-3,-7, -7,-6,-5,-4,-7, -4, 0,-3,-3,-8, -4,-1,-7,
/* D */  0, 4,-7, 5, 3, -7, 0, 0,-3,-1, -5,-4, 2,-3, 1, -3, 0,-1,-3,-8, -2,-5, 3,
/* E */  0, 3,-7, 3, 5, -7,-1,-1,-3,-1, -4,-3, 1,-2, 2, -3,-1,-2,-3,-8, -1,-5, 4,  
/* F */ -4,-5,-6,-7,-7,  8,-5,-3, 0,-7,  0,-1,-4,-5,-6, -5,-3,-4,-3,-1, -3, 4,-6,
/* G */  1, 0,-4, 0,-1, -5, 5,-4,-4,-3, -5,-4, 0,-2,-3, -4, 1,-1,-2,-8, -2,-6,-2,
/* H */ -3, 1,-4, 0,-1, -3,-4, 7,-4,-2, -3,-4, 2,-1, 3,  1,-2,-3,-3,-3, -2,-1, 1,
/* I */ -1,-3,-3,-3,-3,  0,-4,-4, 6,-3,  1, 1,-2,-3,-3, -2,-2, 0, 3,-6, -1,-2,-3,
/* K */ -2, 0,-7,-1,-1, -7,-3,-2,-3, 5, -4, 0, 1,-2, 0,  2,-1,-1,-4,-5, -2,-5,-1,  
/* L */ -3,-4,-7,-5,-4,  0,-5,-3, 1,-4,  5, 3,-4,-3,-2, -4,-4,-3, 1,-3, -2,-2,-3,
/* M */ -2,-4,-6,-4,-3, -1,-4,-4, 1, 0,  3, 8,-3,-3,-1, -1,-2,-1, 1,-6, -2,-4,-2,
/* N */ -1, 3,-5, 2, 1, -4, 0, 2,-2, 1, -4,-3, 4,-2, 0, -1, 1, 0,-3,-4, -1,-2, 0,
/* P */  1,-2,-4,-3,-2, -5,-2,-1,-3,-2, -3,-3,-2, 6, 0, -1, 1,-1,-2,-7, -2,-6,-1,
/* Q */ -1, 0,-7, 1, 2, -6,-3, 3,-3, 0, -2,-1, 0, 0, 6,  1,-2,-2,-3,-6, -1,-5, 4,  
/* R */ -3,-2,-4,-3,-3, -5,-4, 1,-2, 2, -4,-1,-1,-1, 1,  6,-1,-2,-3, 1, -2,-5,-1,
/* S */  1, 0, 0, 0,-1, -3, 1,-2,-2,-1, -4,-2, 1, 1,-2, -1, 3, 2,-2,-2, -1,-3,-1,
/* T */  1, 0,-3,-1,-2, -4,-1,-3, 0,-1, -3,-1, 0,-1,-2, -2, 2, 4, 0,-6, -1,-3,-2,
/* V */  0,-3,-3,-3,-3, -3,-2,-3, 3,-4,  1, 1,-3,-2,-3, -3,-2, 0, 5,-8, -1,-3,-3,
/* W */ -7,-6,-8,-8,-8, -1,-8,-3,-6,-5, -3,-6,-4,-7,-6,  1,-2,-6,-8,12, -5,-2,-7,  
/* X */ -1,-1,-4,-2,-1, -3,-2,-2,-1,-2, -2,-2,-1,-2,-1, -2,-1,-1,-1,-5, -2,-3,-1,
/* Y */ -4,-3,-1,-5,-5,  4,-6,-1,-2,-5, -2,-4,-2,-6,-5, -5,-3,-3,-3,-2, -3, 8,-5,
/* Z */ -1, 2,-7, 3, 4, -6,-2, 1,-3,-1, -3,-2, 0,-1, 4, -1,-1,-2,-3,-7, -1,-5, 4,
};

static Score pam250[23*23] = {
/*       A  B  C  D  E   F  G  H  I  K   L  M  N  P  Q   R  S  T  V  W   Y  Z */ 
/* A */  2, 0,-2, 0, 0, -4, 1,-1,-1,-1, -2,-1, 0, 1, 0, -2, 1, 1, 0,-6, -3, 0, 
/* B */  0, 2,-4, 3, 2, -5, 0, 1,-2, 1, -3,-2, 2,-1, 1, -1, 0, 0,-2,-5, -3, 2, 
/* C */ -2,-4,12,-5,-5, -4,-3,-3,-2,-5, -6,-5,-4,-3,-5, -4, 0,-2,-2,-8,  0,-5, 
/* D */  0, 3,-5, 4, 3, -6, 1, 1,-2, 0, -4,-3, 2,-1, 2, -1, 0, 0,-2,-7, -4, 3, 
/* E */  0, 2,-5, 3, 4, -5, 0, 1,-2, 0, -3,-2, 1,-1, 2, -1, 0, 0,-2,-7, -4, 3, 
/* F */ -4,-5,-4,-6,-5,  9,-5,-2, 1,-5,  2, 0,-4,-5,-5, -4,-3,-3,-1, 0,  7,-5, 
/* G */  1, 0,-3, 1, 0, -5, 5,-2,-3,-2, -4,-3, 0,-1,-1, -3, 1, 0,-1,-7, -5,-1, 
/* H */ -1, 1,-3, 1, 1, -2,-2, 6,-2, 0, -2,-2, 2, 0, 3,  2,-1,-1,-2,-3,  0, 2, 
/* I */ -1,-2,-2,-2,-2,  1,-3,-2, 5,-2,  2, 2,-2,-2,-2, -2,-1, 0, 4,-5, -1,-2, 
/* K */ -1, 1,-5, 0, 0, -5,-2, 0,-2, 5, -3, 0, 1,-1, 1,  3, 0, 0,-2,-3, -4, 0, 
/* L */ -2,-3,-6,-4,-3,  2,-4,-2, 2,-3,  6, 4,-3,-3,-2, -3,-3,-2, 2,-2, -1,-3, 
/* M */ -1,-2,-5,-3,-2,  0,-3,-2, 2, 0,  4, 6,-2,-2,-1,  0,-2,-1, 2,-4, -2,-2, 
/* N */  0, 2,-4, 2, 1, -4, 0, 2,-2, 1, -3,-2, 2,-1, 1,  0, 1, 0,-2,-4, -2, 1, 
/* P */  1,-1,-3,-1,-1, -5,-1, 0,-2,-1, -3,-2,-1, 6, 0,  0, 1, 0,-1,-6, -5, 0, 
/* Q */  0, 1,-5, 2, 2, -5,-1, 3,-2, 1, -2,-1, 1, 0, 4,  1,-1,-1,-2,-5, -4, 3, 
/* R */ -2,-1,-4,-1,-1, -4,-3, 2,-2, 3, -3, 0, 0, 0, 1,  6, 0,-1,-2, 2, -4, 0, 
/* S */  1, 0, 0, 0, 0, -3, 1,-1,-1, 0, -3,-2, 1, 1,-1,  0, 2, 1,-1,-2, -3, 0, 
/* T */  1, 0,-2, 0, 0, -3, 0,-1, 0, 0, -2,-1, 0, 0,-1, -1, 1, 3, 0,-5, -3,-1, 
/* V */  0,-2,-2,-2,-2, -1,-1,-2, 4,-2,  2, 2,-2,-1,-2, -2,-1, 0, 4,-6, -2,-2, 
/* W */ -6,-5,-8,-7,-7,  0,-7,-3,-5,-3, -2,-4,-4,-6,-5,  2,-2,-5,-6,17,  0,-6, 
/* Y */ -3,-3, 0,-4,-4,  7,-5, 0,-1,-4, -1,-2,-2,-5,-4, -4,-3,-3,-2, 0, 10,-4, 
/* Z */  0, 2,-5, 3, 3, -5,-1, 2,-2, 0, -3,-2, 1, 0, 3,  0, 0,-1,-2,-6, -4, 3, 
};

  // BLASTN identity matrix
static Score dna4[5*5] = {
  5, -4, -4, -4, -4
  -4, 5, -4, -4, -4
  -4, -4, 5, -4, -4 
  -4, -4, -4, 5, -4
  -4, -4, -4, -4, -4
};
  
/** create a substitution matrix
 */
HSubstitutionMatrix makeSubstitutionMatrix( 
		int alphabet_size, 
		Score match,
		Score mismatch ) 
{
	debug_func_cerr( 5 );
	HSubstitutionMatrix matrix(new SubstitutionMatrix( alphabet_size, alphabet_size, mismatch ));

	unsigned int row;
	for (row = 0; row < alphabet_size; row++) 
		matrix->setValue(row,row, match);

	return matrix;
}

// define make functions for hard-coded substitution matrices
// define factory functions with/without a translator
#define MAKE_SUBSTITUTION_MATRIX(name,size,data) \
	HSubstitutionMatrix name () \
	{ debug_func_cerr(5); \
		HSubstitutionMatrix matrix(makeSubstitutionMatrix(size)); \
		matrix->copyData(data); \
		return matrix; } \
	HSubstitutionMatrix name ( const HEncoder & translator ) \
	{ debug_func_cerr(5); \
		HSubstitutionMatrix matrix(makeSubstitutionMatrix(size)); \
		matrix->copyData(data); \
		HEncoder t(getEncoder( Protein23 ) ); \
		HResidueVector map_new2old ( t->map(translator) ); \
		std::vector<unsigned int>m; \
		std::copy( map_new2old->begin(), map_new2old->end(), back_inserter( m )); \
		matrix->permuteRows(m); \
		matrix->permuteCols(m); \
		return matrix; }

MAKE_SUBSTITUTION_MATRIX( makeSubstitutionMatrixBlosum62, 23, blosum62 );
MAKE_SUBSTITUTION_MATRIX( makeSubstitutionMatrixBlosum50, 23, blosum50 );
MAKE_SUBSTITUTION_MATRIX( makeSubstitutionMatrixPam250, 23, pam250 );
MAKE_SUBSTITUTION_MATRIX( makeSubstitutionMatrixPam120, 23, pam120 );
MAKE_SUBSTITUTION_MATRIX( makeSubstitutionMatrixPam30, 23, pam30 );
MAKE_SUBSTITUTION_MATRIX( makeSubstitutionMatrixDNA4, 5, dna4 );

/** fill a substitution matrix */
HSubstitutionMatrix makeSubstitutionMatrix( 
		const ScoreVector & scores,
		int nrows, int ncols)
{
	debug_func_cerr( 5 );
	
	assert( nrows * ncols == scores.size() );
	HSubstitutionMatrix matrix(new SubstitutionMatrix( nrows, ncols, 0));
	
	unsigned int row = 0;
	unsigned int col = 0;
	for (int x = 0; x < scores.size(); ++ x)
	{
		matrix->setValue( row, col++, scores[x] );
		if (col > ncols)
		{
			++nrows;
			col = 0;
		}
	}
	return matrix;
}
		
/** read substitution matrix from 
 *  PAM formatted output.
 */
HSubstitutionMatrix loadSubstitutionMatrix( 
		std::istream & input,
		const HEncoder & translator )
{
	debug_func_cerr( 5 );
	
	Residue nchars = translator->getAlphabetSize();
	HSubstitutionMatrix matrix(new SubstitutionMatrix( nchars, nchars, 0));
	
	std::vector<Residue> map_col;

#define BUFFER_SIZE 1000
	
	Score value;
	char c;
	char buffer[BUFFER_SIZE];
	while (!input.eof())
	{
		input.getline( buffer, BUFFER_SIZE );
		
		if (buffer[0] == '#') continue;
		
		istringstream parser( buffer );
		
		// first line: build map of column to matrix
		// stop at "*"
		if (buffer[0] == ' ')
		{	
			while (!parser.eof())
			{
				parser >> c;
				if (c == '*') break;
				map_col.push_back( translator->encode(c) );
			}
		}
		else
		{
			parser >> c;
			if (c == '*') break;			
			Residue row_code = translator->encode(c);
			debug_cerr(5, ">> processing row " << c << " with code "<< (int)row_code );
			Residue col = 0;
			parser >> value;
			while (!parser.eof() )
			{
				matrix->setValue( row_code, map_col[col++], value );
				parser >> value;
			}
		}	
	}
	return matrix;
}

inline void setMatrixScores( 
		HSubstitutionMatrix & matrix,
		const HEncoder & encoder,
		const Score & score,
		const std::string & a,
		const std::string & b)
{
	for (int x = 0; x < a.size(); ++x)
	{
		Residue rx = encoder->encode(a[x]);
		for (int y = 0; y < b.size(); ++y)
		{	
			Residue ry = encoder->encode(b[y]);
			matrix->setValue(rx,ry, score);
			matrix->setValue(ry,rx, score);
		}
	}
}

HSubstitutionMatrix makeSubstitutionMatrixBackTranslation( 
		const Score & match,
		const Score & mismatch,
		const Score & approximate_match,
		const HEncoder & encoder)    
{
	debug_func_cerr( 5 );
	
	HSubstitutionMatrix matrix(makeSubstitutionMatrix( 
			std::max(encoder->getAlphabetSize(), (int)encoder->getGapCode() + 1), 
			match,
			mismatch ));

	// 
	// AGCTN <-> W
	setMatrixScores( matrix, encoder, approximate_match, "AGCTN", "W");
	// AG <-> V
	setMatrixScores( matrix, encoder, match, "AG", "R");
	// CT <-> Y
	setMatrixScores( matrix, encoder, match, "CT", "Y");
	// ACGTNVY <-> N
	setMatrixScores( matrix, encoder, match, "ACGTNRY", "N");
	// ACGTNVY <-> -
	setMatrixScores( matrix, encoder, mismatch, "ACGTNRY", "-");
	// - <-> -
	setMatrixScores( matrix, encoder, match, "-", "-");

	return matrix;
}


} // namespace alignlib









