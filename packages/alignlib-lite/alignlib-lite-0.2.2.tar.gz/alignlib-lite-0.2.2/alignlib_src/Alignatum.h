/*
  alignlib - a library for aligning protein sequences

  $Id: Alignatum.h,v 1.5 2004/03/19 18:23:39 aheger Exp $

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

#ifndef ALIGNATUM_H
#define ALIGNATUM_H 1

#include <iosfwd>
#include <string>
#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

/** @short Protocol class for aligned objects.

    Objects of this type represent an aligned string. It provides methods
    for inserting and deleting gaps in the aligned string.

    @author Andreas Heger
    @version $Id: Alignatum.h,v 1.5 2004/03/19 18:23:39 aheger Exp $
*/
class Alignatum : public virtual AlignlibBase
{
    // class member functions
    friend std::ostream & operator<<( std::ostream &, const Alignatum &);

 public:
    // constructors and desctructors
    /** when building a new Alignatum sequence by cloning and an alignment, this specifies,
	if the new sequence is in row or column
    */

    /** constructor */
    Alignatum  ();

    /** copy constructor */
    Alignatum  (const Alignatum &);

    /* destructor */
    virtual ~Alignatum ();

    DEFINE_ABSTRACT_CLONE( HAlignatum )

    /*-----> accessors <----------------------------------------------------- */

    /** return the aligned string
    */
    virtual const std::string & getString() const = 0;

    /** return the number of the first residue.
     */
    virtual Position getFrom() const = 0;

    /** return the number of one past the last residue.
    */
    virtual Position getTo() const = 0;

    /** return the aligned length.
     */
    virtual Position getAlignedLength() const = 0;

    /** return the length of the object.
    */
    virtual Position getFullLength() const = 0;

    /** add gaps in the front and in the back
     * @param before 	number of gaps to add in front.
     * @param back		number of gaps to add at the back.
     * */
    virtual void addGaps(int front, int back) = 0;

    /** check for consistency.
     *
     * Check if the number of aligned characters matches
     * the residue boundaries.
     */
    virtual bool isConsistent() const = 0;

    /** return residue number of a position.
     *
     * This functions returns NO_POS if residue number if out of bounds.
     *
     * @param pos		position.
     * @param search	if position maps to a gap, optionally do search for
     * 					next residue number.
     */
    virtual Position getResidueNumber(
    		const Position pos,
    		const SearchType search = NO_SEARCH) const = 0;

    /** add gaps in the middle of the aligned object.
    *
	*	@param position where gap(s) should be inserted
	*	@param count the number of gaps to be inserted
    */
    virtual void insertGaps(
    		int position,
    		Position count = 1) = 0;

    /** remove leading/or trailing gaps.
     */
    virtual void removeEndGaps() = 0;

    /** remove one or more positions from the aligned object
     */
    virtual void removeColumns( int position, Position count = 1) = 0;

    /** map the object using an alignment.
     *
     * @param map_old2new	@ref Alignment mapping previous positions to new positions.
     * @param new_length	@ref add gaps at the end so that the aligned length is new_length.
     * @param unaligned_chars	If true, lower case unaligned characters will be
								put before the next aligned character (as much as can be fit)
    */
    virtual void mapOnAlignment(
    		const HAlignment & map_old2new,
    		const Position new_length = 0,
    		const bool unaligned_chars = false ) = 0;

    /** return an @ref Alignment object mapping aligned positions to the string representation.
     *
     * The current default encoder is used to check for valid characters.
     *
     * @param dest 		the alignment that is to be filled.
     * @param invert 	return the inverted the alignment
     * @return a handle to dest
     */
    virtual void fillAlignment(
    		HAlignment & dest,
			const bool invert = false) const = 0;

    /** write object to stream. */
    virtual void  write( std::ostream & output ) const = 0;

    /** read object from stream. */
    virtual void  read( std::istream & input ) = 0;

};


}

#endif /* ALIGNATUM_H */

