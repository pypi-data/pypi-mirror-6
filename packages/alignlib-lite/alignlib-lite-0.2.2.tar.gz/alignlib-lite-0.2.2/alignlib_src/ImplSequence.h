/*
  alignlib - a library for aligning protein sequences

  $Id: ImplSequence.h,v 1.2 2004/01/07 14:35:36 aheger Exp $

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

#ifndef IMPL_SEQUENCE_H
#define IMPL_SEQUENCE_H 1

#if HAVE_CONFIG_H
#include <config.h>
#endif

#include "alignlib_fwd.h"
#include "Sequence.h"
#include "ImplAlignandum.h"
#include <iosfwd>

namespace alignlib
{

    /** A class for sequences, that are to be aligned. Instances of this
	class are created by factory functions. This class implements the
	part of the interface, that has not been implemented by IAlignandum

	ImplSequence inherits both from ImplAlignandum and Sequence

	@author Andreas Heger
	@version $Id: ImplSequence.h,v 1.2 2004/01/07 14:35:36 aheger Exp $
	@short Contains sequence, that are to be aligned
     */


class ImplSequence : public ImplAlignandum, public Sequence
{

    friend HAlignandum addSequence2Profile( HAlignandum dest,
    		const HAlignandum source,
    		const HAlignment map_source2dest );

 public:
    /*------------------------------------------------------------------------------------ */
	 /** constructor */
	 ImplSequence();

    /** create sequence from a string, given a translator object */
    ImplSequence( const std::string & src );

    /** the copy constructor */
    ImplSequence( const ImplSequence & );

    /** the destructor */
    virtual ~ImplSequence();

    /*------------------------------------------------------------------------------------ */
    DEFINE_CLONE( HAlignandum );

    /** get internal representation of residue in position pos */
    virtual Residue asResidue( Position pos ) const;

    /** mask column at position x */
    virtual void mask( const Position & x);

    /* Mutators ------------------------------------------------------------------------------ */

    /** load data into cache, if cacheable type */
    virtual void prepare() const;

    /** discard cache, if cacheable type */
    virtual void release() const;

    /** write human readable output to stream.
     */
    virtual void write( std::ostream & output ) const;

    /** save state of object into stream
     */
    virtual void load( std::istream & input ) ;

    /** export functions for Scorer objects */
    virtual const ResidueVector * getSequence() const ;

    /** swap two residues */
    virtual void swap( const Position & x, const Position & y);

 protected:

	 /** save state of object into stream
	  */
	 virtual void __save( std::ostream & output, MagicNumberType type = MNNoType ) const;

	 /** re-set the length of the object
	  *
	  * This method re-allocates memory and sets the sequence to all gap.
	  */
	 virtual void resize( Position length );

 private:

 public:

 protected:

    /** sequence */
    ResidueVector mSequence;
};

// handle definition for down-casting
typedef boost::shared_ptr<ImplSequence>HImplSequence;

}


#endif /* _SEQUENCE_H */

