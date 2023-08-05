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

#ifndef SEQUENCE_H
#define SEQUENCE_H 1

#if HAVE_CONFIG_H
#include <config.h>
#endif

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"
#include "Alignandum.h"
#include <iosfwd>

namespace alignlib
{

    /** A class for sequences, that are to be aligned.
     *
     * Instances of this class are created by factory functions. This class adds
     * functions that are specific to sequences to the @ref Alignandum interface.
     *
     * This class is a protocol class and as such defines only the general interface.
     *
     * @author Andreas Heger
     * @version $Id$
     * @short A sequence
     */

class Sequence : public virtual Alignandum
{

	/* friends ---------------------------------------------------------------------------- */
	friend  std::ostream & operator<<( std::ostream &, const Sequence &);

public:
	/** empty constructor */
	Sequence();

	/** copy constructor */
	Sequence( const Sequence &);

	/** destructor */
	virtual ~Sequence();
};

/** @brief cast an @ref Alignandum object to a @ref Sequence.
 *
 * If the conversion fails, the returned handle
 * will point to NULL.
 *
 * @param src the @ref Alignandum object to cast
 * @return the same object as sequence
 */
HSequence toSequence( HAlignandum & src );

/** @brief cast an @ref Alignandum object to a @ref Sequence.
 *
 * If the conversion fails, the returned handle
 * will point to NULL.
 *
 * @param src the @ref Alignandum object to cast
 * @return the same object as sequence
 */
const HSequence toSequence( const HAlignandum & src );

}


#endif /* _SEQUENCE_H */

