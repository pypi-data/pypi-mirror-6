/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignatorDotsWrap.cpp,v 1.2 2004/01/07 14:35:34 aheger Exp $

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
#include <iomanip>
#include <stdio.h>

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "ImplAlignatorDotsWrap.h"
#include "Alignandum.h"
#include "ImplAlignmentMatrixRow.h"

#include "HelpersSubstitutionMatrix.h"

#include "Alignment.h"
#include "HelpersAlignment.h"

using namespace std;

namespace alignlib
{

/*---------------------factory functions ---------------------------------- */

    /** make an alignator object, which does a dot-alignment. The default version can be given an AlignmentMatrix-
	object */
HAlignator makeAlignatorDotsWrap(
		  const HAlignator & dots,
		  Score row_gop, Score row_gep,
		  Score col_gop, Score col_gep )
{
	return HAlignator( new ImplAlignatorDotsWrap( dots, row_gop, row_gep, col_gop, col_gep ) );
}

ImplAlignatorDotsWrap::ImplAlignatorDotsWrap() :
	ImplAlignatorDots()
	{
	}

ImplAlignatorDotsWrap::ImplAlignatorDotsWrap(
		const HAlignator & dots,
		Score row_gop, Score row_gep,
		Score col_gop, Score col_gep )
: ImplAlignatorDots( dots, row_gop, row_gep, col_gop, col_gep)
{
}

//----------------------------------------------------------------------------------------------------------------------------------------
ImplAlignatorDotsWrap::ImplAlignatorDotsWrap( const ImplAlignatorDotsWrap & src ) : ImplAlignatorDots( src )
{
  debug_func_cerr(5);

}

//----------------------------------------------------------------------------------------------------------------------------------------
ImplAlignatorDotsWrap::~ImplAlignatorDotsWrap()
{
  debug_func_cerr(5);

}

IMPLEMENT_CLONE( HAlignator, ImplAlignatorDotsWrap );

//----------------------------------------------------------------------------------------------------------------------------------------

Score ImplAlignatorDotsWrap::getGapCost( Dot x1, Dot x2 ) const
{

  Position c1 = (*mPairs)[x1].mCol;
  Position c2 = (*mPairs)[x2].mCol;
  Position r1 = (*mPairs)[x1].mRow;
  Position r2 = (*mPairs)[x2].mRow;

  Score gap_cost = 0;
  Position d;

  if ((d = (r2 - r1)) > 1)
      gap_cost += mRowGop + d * mRowGep;

  if ((d = (c2 - c1)) > 1)
      gap_cost += mColGop + d * mColGep;
  else if (d < 1)
      gap_cost += mColGop + (mColLength - d) * mColGep;

  return gap_cost;
}

//-----------------------------------------------------------< Alignment subroutine >----------------------------------------------
void ImplAlignatorDotsWrap::performAlignment(
		HAlignment  & ali,
		const HAlignandum & prow,
		const HAlignandum & pcol )
{

	Position left;
  int bestdot, globdot;

  Score globbest, best;
  Score sa,sb,sc,sd,se,sf,s;

  int i;

  int acol, xcol = 0, fcol;
  int adot, bdot, cdot, ddot, edot, fdot, hdot, idot, xdot;
  int col_res, row_res;

  int bestpercolstackptr;					/* points to next free element in bestpercolstack */

  /* Allocate Memory for bestpercol and topdot */
  int *bestpercolstack = new int[mColLength + 1];
  int *bestpercol      = new int[mColLength + 1];
  int *topdot          = new int[mRowLength + 1];
  Score *m          = new Score[mNDots];

  adot    =-1; bdot    =-1; cdot =-1; ddot =-1; edot= -1; fdot = -1; hdot=-1;
  globdot =-1; globbest =0; best = 0; fcol =-1;
  bestpercolstackptr = STACKEMPTY;

  for (col_res = 1; col_res <= mColLength; col_res++) { bestpercol[col_res] = -1; }
  for (row_res = 1; row_res <= mRowLength; row_res++) { topdot[row_res]     = -1; }
  for (i = 0; i < mNDots; i ++) { mTrace[i]     = -1; m[i] = 0; }
  acol = 1;
  idot = 0;

  //#define DEBUG
  //----------------------------------> main alignment loop <----------------------------------------------------
  for ( idot = mRowIndices[1]; idot < mNDots; idot++ ) {	   /* iterate through nextrow starting at first position */

    if (idot < 0) continue;
    row_res = (*mPairs)[idot].mRow;                           /* row_res = row */
    col_res = (*mPairs)[idot].mCol;                           /* col_res = col, wrap around col */

    // some safety checks
#ifdef SAVE
    if (row_res > mRowLength) break;                   /* checking boundaries */
    if (col_res < 1) continue;                /* can be removed, if only dots in boundaries are supplied */
    if (col_res > mColLength) continue;
#endif

#ifdef DEBUG
    printf("--------------------------------------------\n");
    printf("idot = %i, row_res = %i, col_res = %i, score = %5.2f\n", idot, row_res, col_res, (*mPairs)[idot].mScore);
#endif
    /* calculate top row */
    if ( (hdot < 0) ||           /* enter first time */
	 (row_res > (*mPairs)[hdot].mRow) ) {  /* skip, if not in the same row as last time*/

	topdot[row_res] = idot;
	while( bestpercolstackptr > STACKEMPTY ) {
	    xdot = bestpercolstack[--bestpercolstackptr];
	    if ( (*mPairs)[xdot].mRow >= row_res ) break;                 /* stop, if entering current row */
	    xcol = (*mPairs)[xdot].mCol;
	    if (xdot < 0 )            continue;             /* safety check */
	    if (bestpercol[xcol] < 0)
		bestpercol[xcol] = xdot;
	    else if (m[xdot] > m[bestpercol[xcol]] )
		bestpercol[xcol] = xdot;
	}
	/* init all */
	acol = 1;
	adot = -1; bdot = -1; cdot = -1; edot = -1; fdot = -1;
    }
    /* update c = maximum dot along last row */
    xdot = mRowIndices[row_res - 1];
    sc = 0;
    while ( (xdot > -1)  &&
	    ((*mPairs)[xdot].mRow == row_res - 1 ) &&  /* stop, if dot in previous row any more*/
	    ((*mPairs)[xdot].mCol  < col_res - 1 )     /* end, if direct contact to new dot*/
	    ) {

      s = m[xdot] + getGapCost( xdot, idot);

      if (s > sc) {
	cdot = xdot;
	s    = sc;
      }
      xdot++;
    }

    /* compute d = match adjacent dot in previous row and column */
    if ( col_res == 1)
      i = mColLength;
    else
      i = col_res - 1;

    /* ddot -> dot in previous column, previous row */

    /* look up index in row, col, score for dot; -1 if not found */
    ddot = getPairIndex( row_res - 1, i);

    /* update a = */

    if ( ddot < 0 ) { /* only update a if d unoccupied */

      if ( adot > -1 && xdot > -1 ) { /* Hmm. previous match? */
	sa = m[adot] +
	  getGapCost( adot, idot) +
	  getGapCost( adot, idot);
      } else {
	sa=0;
      }

      /* ##>> searcharea! */
      left = 0;
      for (i = acol; i <= col_res-2; i++) {
	xdot = bestpercol[i];
	if ( xdot < 0 ) continue;
	s = m[xdot] +
	  getGapCost( xdot, idot ) +
	  getGapCost( xdot, idot );
	if (s > sa) {
	  sa=s;
	  adot=xdot;
	}
	if ((*mPairs)[xdot].mRow > left) {
	  left = (*mPairs)[xdot].mRow;
	}
	if(left == row_res-2) break;
      }
      acol = col_res;
    } else {
      adot = -1;
    }
    /* update bdot = max scoring dot in previous column */


    if ( col_res==1 )
      bdot = bestpercol[mColLength];
    else
      bdot = bestpercol[col_res-1];

    if (bdot == ddot) bdot = -1; /* dot has to be in different row */

    /* rollover */
    /* update f */
    if ( fdot > -1 ) {
      sf = m[fdot] +
	getGapCost( fdot, idot) +
	getGapCost( fdot, idot);
      if( (*mPairs)[fdot].mCol <= col_res)
	fcol = col_res + 1;
    } else
      sf=0;

    /*##>> searcharea! */
    left = 0;

    for ( i = fcol; i <= mColLength; i++) { /*# only executed for topdot or f<=col_res */
      if ( i < 0 ) continue;          /* safety */
      xdot = bestpercol[i];
      if ( xdot < 0 ) continue;
      s = m[xdot] +
	getGapCost( xdot, idot ) +
	getGapCost( xdot, idot );
      if ( s > sf ) {
	sf   = s;
	fdot = xdot;
      }

      if ((*mPairs)[xdot].mRow > left) {
	left = (*mPairs)[xdot].mRow;
      }

      if ( left == row_res-2 ) break;
    }

    fcol = mColLength + 1;

    /* update e = */
    if ( (edot > -1 && (*mPairs)[edot].mCol <= col_res) || (edot < 0) ) {
      if ( row_res > 1 ) {
	xdot = topdot[row_res-1];
      } else {
	xdot =- 1;
      }
      se   =  0;
      edot = -1;
      if (xdot >= 0) {
	for ( xdot = 0; xdot < mNDots; xdot++ ) {
	  if ((*mPairs)[xdot].mRow != row_res - 1 ) break;	/* since sorted by row first. check, if we leave the row */
	  if ((*mPairs)[xdot].mCol < 1) continue;	/* since sorted by column inside a column */
	  if ((*mPairs)[xdot].mCol > mColLength) break;
	  if ((*mPairs)[xdot].mCol >  col_res) {
	    s = m[xdot] + getGapCost( xdot, idot );
	    if (s>se) {
	      se=s;
	      edot=xdot;
	    }
	  }
	}
      }
    }


    /*  select best of d|a|b|c */
    best = 0; bestdot = -1;
    sa = sb = sc = sd = se = sf = 0;
    if ( ddot >= 0) {
      sd = m[ddot];
      if( sd > best ) { best = sd; bestdot = ddot; }
    }
    if ( adot >= 0 ) {
	sa = m[adot] + getGapCost(adot, idot );
      if( sa > best) { best = sa; bestdot = adot; }
    }
    if ( bdot >= 0 ) {
      sb = m[bdot] + getGapCost(bdot, idot );
      if( sb > best) { best = sb; bestdot = bdot; }
    }
    if ( cdot >= 0) {
      sc = m[cdot] + getGapCost(cdot, idot );
      if( sc > best) { best = sc; bestdot = cdot; }
    }
    if (edot >= 0) {
      se = m[edot] + getGapCost(edot, idot );
      if( se > best ) { best = se; bestdot = edot; }
    }
    if (fdot >= 0) {
      sf = m[fdot] + getGapCost(fdot, idot);
      if( sf > best ) { best = sf; bestdot = fdot; }
    }

    /* record mTraceback */
    best += (*mPairs)[idot].mScore;

    if (best < 0) { /* local alignment, reset to zero or start new mTrace with single match */
      best    = 0 ;
      bestdot = -1;
    }
    m[idot]     = best;
    mTrace[idot] = bestdot;

    if ( best > globbest) { /* save best dot */
      globbest = best;
      globdot  = idot;
    }

#ifdef DEBUG
    printf("idot %5i; mTrace[idot] %5i; m[idot] %5.2f; best %5.2f\n",
	   idot, mTrace[idot], m[idot], best);
    printf("adot %5i; bdot %5i; cdot %5i; ddot %5i; edot %5i; fdot %5i\n",
	   adot,bdot,cdot,ddot,edot,fdot );
    printf("sa   %5.2f; sb   %5.2f; sc   %5.2f; sd   %5.2f; se   %5.2f; sf   %5.2f\n",
	   sa, sb, sc, sd, se, sf);
    printf("acol %5i; globdot %5i; globbest %5.2f\n",
	   acol, globdot, globbest );
#endif

    /* for bestpercol */

    if ( (bestpercol[col_res] == -1) )
      bestpercolstack[bestpercolstackptr++] = idot;
    else if (best > m[bestpercol[col_res]])
      bestpercolstack[bestpercolstackptr++] = idot;

    /*  h=i */
    hdot = idot;
  }

  mLastDot= globdot;
  mScore  = globbest;

  //--------------> cleaning up <---------------------------------------------------------------

  delete [] topdot;
  delete [] bestpercolstack;
  delete [] bestpercol;
  delete [] m;

  //--------------------------------------------------------------------------------------------------
}


} // namespace alignlib
