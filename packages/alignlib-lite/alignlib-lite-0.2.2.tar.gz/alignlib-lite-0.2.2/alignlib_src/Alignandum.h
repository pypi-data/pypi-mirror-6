/*
  alignlib - a library for aligning protein sequences

  $Id: Alignandum.h,v 1.2 2004/01/07 14:35:31 aheger Exp $

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

#ifndef ALIGNANDUM_H
#define ALIGNANDUM_H 1

#include <iosfwd>
#include <string>
#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

/**
    @short Protocol class of alignable objects, typically sequences or profiles.

    Objects can restrict access to a sequence range. Ranges are given in open/closed
    notation starting from 0. Thus, the segment 0..5 includes residues 0,1,2,3,4.
    Positions are given in 0-based coordinates.

    This class is a protocol class and as such defines only the general interface.

    @author Andreas Heger
    @version $Id: Alignandum.h,v 1.2 2004/01/07 14:35:31 aheger Exp $
 */

class Alignandum : public virtual AlignlibBase
{
	/* friends ---------------------------------------------------------------------------- */
	friend  std::ostream & operator<<( std::ostream &, const Alignandum &);

public:
	/* constructors and desctructors------------------------------------------------------- */

	/** empty constructor */
	Alignandum();

	/** copy constructor */
	Alignandum( const Alignandum &);

	/** destructor */
	virtual ~Alignandum();

	/* accessors ------------------------------------------------------------------------- */

	DEFINE_ABSTRACT_CLONE( HAlignandum )

	/** get the length of the active segment.
	 *
	 * */
	virtual Position getLength() const = 0;

	/** get the length of the full sequence.
	 *
	 */
	virtual Position getFullLength() const = 0;

	/** restrict the sequence to a segment.
	 *
	 * If no coordinates are given, the full sequence is used.
	 *
     *   @param from     where segment starts
     *   @param to       where segment ends
	 */
	virtual void useSegment( Position from = NO_POS, Position to = NO_POS) = 0;

	/** return the index of the first residue in active segment
	 */
	virtual Position getFrom() const = 0;

	/** return the index plus one of the last residue in active segment
	 */
	virtual Position getTo() const = 0;

	/** return true if object is prepared for alignment
	 *
	 * This function permits lazy evaluation of of some
	 * alignable types like profiles.
	 */
	virtual bool isPrepared() const = 0;

	/** get residue at position.
	 *
	 * @param pos	position
	 *
	 * Residues are numerical types and are mapped from alpha-
	 * numeric types through @ref Encoder objects.
	 */
	virtual Residue asResidue( Position pos ) const = 0;

	/** get character at position.
	 *
	 * @param pos	position
	 *
	 * This applies the @ref Encoder associated with
	 * this object to translate from the numeric residue
	 * represntation.
	 */
	virtual char asChar( Position pos ) const = 0;

	/** returns a string of the object.
	 *
	 * The string has exactly the same length as the object.
	 */
	virtual std::string asString() const = 0;

	/** mask positions in segment from from to to.
	 *
	 * @param from  first residue in segment.
	 * @param to 	last residue in segment + 1. If to is omitted, only
	 * 				position from is masked.
	 */
	virtual void mask( const Position & from, const Position & to = NO_POS) = 0;

	/** returns true if position pos is masked.
	 *
	 * @param pos 	position
	 */
	virtual bool isMasked( const Position & pos ) const = 0;

	/** shuffle object.
	 *
	 * @param num_iterations number of iterations to shuffle
	 * @param window_size	shuffle within windows of size window_size.
	 * 						If @param window_size is 0, the whole sequence is used
	 * 					    fo shuffling.
	 */
	virtual void shuffle(
			unsigned int num_iterations = 1,
			Position window_size = 0 ) = 0;

    /** swap two positions.
     *
     * @param x 	position to swap
     * @param y		position to swap
    */
    virtual void swap( const Position & x, const Position & y ) = 0;

	/* Mutators ------------------------------------------------------------------------------ */

	/** prepare object for alignment.
	*/
	virtual void prepare() const = 0;

	/** release memory need for alignment.
	*/
	virtual void release() const = 0;

	/** write human readable output to stream.
	 */
	virtual void write( std::ostream & output ) const = 0;

	/** save object to stream.
	 */
	virtual void save( std::ostream & input ) const = 0;

	/** set the storage type */
	virtual void setStorageType( const StorageType & storage_type ) = 0;

	/** get the storage type */
	virtual StorageType getStorageType( ) const = 0;

};

}
#endif /* ALIGNANDUM_H */

