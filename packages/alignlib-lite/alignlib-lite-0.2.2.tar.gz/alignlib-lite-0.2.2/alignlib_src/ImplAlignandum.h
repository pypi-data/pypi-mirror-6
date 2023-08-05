/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignandum.h,v 1.2 2004/01/07 14:35:33 aheger Exp $

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

#ifndef IMPL_ALIGNANDUM_H
#define IMPL_ALIGNANDUM_H 1

#include <iosfwd>
#include <vector>
#include "alignlib_fwd.h"
#include "Alignandum.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{

/**
    Base class for objects that are to be aligned. This class implements a subset of the interface,
    namely some basic behaviour for using segments and communicating its state (prepared/not prepared),
    that is common to all its derived classes.

    Encoder: There is one translator-object in the whole class library. If an object needs a different
    translator, then the default translator has to be changed. See Encoder for more information.

    @author Andreas Heger
    @version $Id: ImplAlignandum.h,v 1.2 2004/01/07 14:35:33 aheger Exp $
    @short protocol class of alignable objects
*/

class ImplAlignandum : public virtual Alignandum, public ImplAlignlibBase
{
    /* friends ---------------------------------------------------------------------------- */
    friend  std::ostream & operator<<( std::ostream &, const ImplAlignandum &);

 public:
    /* constructors and desctructors------------------------------------------------------- */

	 /** constructor */
	 ImplAlignandum();

	 /** constructor */
	 ImplAlignandum( const HEncoder & translator );

    /** copy constructor */
    ImplAlignandum( const ImplAlignandum &);

    /** desctructor */
    virtual ~ImplAlignandum();

    /** accessors ------------------------------------------------------------------------- */
    /** get length of window */
    virtual Position getLength() const;

    /** use a segment for exporting and set segment to from and to
	@param from	where segment starts
	@param to	where segment ends
    */
    virtual void useSegment( Position from = NO_POS, Position to = NO_POS);

    /** return true if object is prepared for alignment (for cacheable types ) */
    virtual bool isPrepared() const;

    /** get internal representation of residue in position pos */
    virtual char asChar( Position pos ) const;

    /** returns a string representation of the object */
    virtual std::string asString() const;

    /** mask column in a segment */
    virtual void mask( const Position & from, const Position & to);

    /** mask column in a segment */
    virtual void mask( const Position & column);

    /** check if a position is masked */
    virtual bool isMasked( const Position & column) const ;

    /** return first residue number in segment */
    virtual Position getFrom() const;

    /** return last residue number in segment */
    virtual Position getTo() const;

    /** shuffle the object */
    virtual void shuffle( unsigned int num_iterations,
    		Position window_size );

    /** save state of object into stream
     */
    virtual void save( std::ostream & output ) const;

    /** save state of object into stream
     */
    virtual void load( std::istream & input ) ;

	/** set the storage type */
	virtual void setStorageType( const StorageType & storage_type );

	/** get the storage type */
	virtual StorageType getStorageType( ) const;

 protected:
    /** the member functions below are protected, because they have to be only accessible for
	derived classes. They should know, what they are doing. */

    /** re-set the length of this object.
     *
     * This results in erasing the current contents of the object
     * and allocates memory.
     *
     * Calling this method resets the segment coordinates. */
    virtual void resize(Position length);

    /** get true length*/
    virtual Position getFullLength() const;

    /** set prepared flag */
    virtual void setPrepared( bool flag ) const;

    /** save state of object into stream
     */
    virtual void __save( std::ostream & output, MagicNumberType type = MNNoType ) const;

    /** bitvector keeping track of masked positions */
    std::vector< bool > mMasked;

	/** The storage type of this object when writing to stream */
	StorageType mStorageType;

 private:
    /** first residue of segment used for aligning */
    mutable Position mFrom;

    /** last residue of segment used for aligning */
    mutable Position mTo;

    /** true length of sequence */
    mutable Position mLength;

    /** flag, whether object is ready for alignment */
    mutable bool mIsPrepared;

};


}

#endif /* ALIGNANDUM_H */

