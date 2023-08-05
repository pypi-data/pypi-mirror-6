/*
  alignlib - a library for aligning protein Profiles

  $Id: ImplProfile.h,v 1.2 2004/01/07 14:35:36 aheger Exp $

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

#ifndef PROFILE_H
#define PROFILE_H 1

#if HAVE_CONFIG_H
#include <config.h>
#endif

#include "alignlib_fwd.h"
#include "Alignandum.h"
#include <iosfwd>
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

    /** A class for profile, that are to be aligned.
     *
     * Instances of this class are created by factory functions. This class adds
     * functions that are specific to Profiles to the @ref Alignandum interface.
     *
     * This class is a protocol class and as such defines only the general interface.
     *
     * @author Andreas Heger
     * @version $Id$
     * @short A Profile
     */

class Profile : public virtual Alignandum
{

	/* friends ---------------------------------------------------------------------------- */
	friend  std::ostream & operator<<( std::ostream &, const Profile &);

public:
	/** empty constructor */
	Profile();

	/** copy constructor */
	Profile( const Profile &);

	/** destructor */
	virtual ~Profile();


	/** return a copy of the score matrix for inspection.
	 * @return a score matrix.
	 * */
	virtual HScoreMatrix getScoreMatrix() const = 0;

	/** return a copy of the frequency matrix for inspection.
	 * @return a frequency matrix.
	 * */
	virtual HFrequencyMatrix getFrequencyMatrix() const = 0;

	/** return a copy of the counts matrix for inspection.
	 * @return a counts matrix.
	 * */
	virtual HWeightedCountMatrix getWeightedCountMatrix() const = 0;

	/** add an @ref Alignandum object to the profile
	 *
	 * Note that this function will simply add the counts
	 * of the two profiles. A sequence is regarded as a
	 * profile with single counts in each column.
	 *
	 * @param src the object to be added.
	 * @param a mapping giving column correspondencies
	 * @param reverse_mapping - mapping is in reverse order
	 * */
	virtual void add(
			const HAlignandum & src,
			const HAlignment & map_src2dest,
			const bool reverse_mapping = false ) = 0;

	/** resize profile to new length - the old data is discarded.
	 *
	 * @param length new length of profile
	 */
	virtual void resize( Position length ) = 0;
};

/** @brief cast an @ref Alignandum object to a @ref Profile.
 *
 * If the conversion fails, the returned handle
 * will point to NULL.
 *
 * @param src the @ref Alignandum object to cast
 * @return the same object as sequence
 */
HProfile toProfile( HAlignandum & src );

/** @brief cast an @ref Alignandum object to a @ref Profile.
 *
 * If the conversion fails, the returned handle
 * will point to NULL.
 *
 * @param src the @ref Alignandum object to cast
 * @return the same object as sequence
 */
const HProfile toProfile( const HAlignandum & src );



}


#endif /* _Profile_H */

