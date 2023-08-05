/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersAlignandum.h,v 1.2 2004/01/07 14:35:32 aheger Exp $

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

#ifndef HELPERS_ALIGNANDUM_H
#define HELPERS_ALIGNANDUM_H 1

#include "alignlib_fwd.h"

namespace alignlib
{

/**
 *
 * @defgroup FactoryAlignandum Factory functions for Alignandum objects.
 * @{
 *
 *
*/

/** load an @ref Alignandum object from stream.
 *
 * @param stream stream to read an @ref Alignandum object from.
 * @exception AlignlibException	no complete object in stream.
 * @return a new Alignandum object.
 */
HAlignandum loadAlignandum( std::istream & stream );

/** create a sequence.
 *
 * The default @ref Encoder object is used.
 *
 * @param sequence NULL terminated C-string.
 * @return a new @ref Alignandum object.
 */
HAlignandum makeSequence( const char * sequence );

/** create a sequence.
 *
 * The default @ref Encoder object is used.
 *
 * @param sequence string.
 * @return a new @ref Alignandum object.
 */
HAlignandum makeSequence( const std::string & sequence );

/** create a sequence from a fasta file
 *
 * @param input input stream
 * @param description string to store description in.
 * @param encoder @ref Encoder object to use.
 * @return a new @ref Alignandum object. Returns an empty pointer if no sequence has been read.
 */
HAlignandum makeSequenceFromFasta(
		std::istream & input,
		std::string & description );

/** mutate a sequence according to a substitution matrix
 *
 * Initializes random generator with seed, if seed > 0.
 * */
HAlignandum makeMutatedSequence(
		HAlignandum src,
		const HMutationMatrix & matrix,
		const long seed = 0);

/** create a new profile.
 *
 * The object is initialized with default objects.
 *
 * @return a new @ref Alignandum object. The profile is empty.
 */
HAlignandum makeProfile();

/** create a new profile of a given length.
 *
 * The object is initialized with default objects.
 * @param length	length of the profile.
 * @return a new @ref Alignandum object. The profile is empty, but has a set length.
 */
HAlignandum makeProfile( const Position & length );

/** create a new profile from a string of concatenated sequences.
 *
 * The object is initialized with default objects.
 *
 * @param sequences sequences for filling the profile.
 * @param nsequences number of concatenated sequences.
 * @return a new @ref Alignandum object filled with sequences.
 */

HAlignandum makeProfile(
		const std::string & sequences,
		int nsequences );

/** create a new profile from a @ref MultipleAlignment.
 *
 * The object is initialized with default objects.
 *
 * @param mali multiple alignment.
 * @return a new @ref Alignandum object filled from a multiple alignment.
 */

HAlignandum makeProfile(
		const HMultipleAlignment & mali );

/** create a new profile from two @ref Alignandum objects.
 *
 * @param seqa first sequence/profile
 * @param map_seqa2profile map of first sequence/profile to new profile
 * @param seqb first sequence/profile
 * @param map_seqb2profile map of first sequence/profile to new profile
 *
 * @return a new @ref Alignandum object filled from a multiple alignment.
 */
HAlignandum makeProfile(
		const HAlignandum & seqa,
		const HAlignment & map_seqa2profile,
		const HAlignandum & seqb,
		const HAlignment & map_seqb2profile );

/** create a new profile from several @ref Alignandum objects.
 *
 * @param @ref MultAlignment mapping the sequences to the multiple alignment
 * @param @ref vector of @ref Alignandum objects in the multiple alignment
 *
 * @return a new @ref Alignandum object filled from a multiple alignment.
 */
HAlignandum makeProfile(
		const HMultAlignment & mali,
		const HAlignandumVector & sequences );


/**
 * @}
 */



}

#endif	/* HELPERS_ALIGNANDUM_H */
