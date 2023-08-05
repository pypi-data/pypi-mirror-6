/*
  alignlib - a library for aligning protein sequences

  $Id: ImplProfile.h,v 1.3 2004/01/07 14:35:35 aheger Exp $

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


#ifndef IMPL_PROFILE_H
#define IMPL_PROFILE_H 1

#if HAVE_CONFIG_H
#include <config.h>
#endif

#include <iosfwd>
#include "alignlib_fwd.h"

#include "ImplAlignandum.h"
#include "Profile.h"
#include "Matrix.h"

namespace alignlib
{

/**
    Basic implementation for (sequence) profiles, i.e. position specific scoring matrices.
    A profile stores counts, frequencies, and profile-scores for a
    profile and uses different helper objects for the calculation
    of a profile.

    Masking for a profile means:
    1.  profile- value gets set to MASK_VALUE
    2.  counts and frequencies get set to 0

    @author Andreas Heger
    @version $Id: ImplProfile.h,v 1.3 2004/01/07 14:35:35 aheger Exp $
    @short base class for profiles
 */

class ImplProfile : public ImplAlignandum, public Profile
{

	friend HAlignandum  extractProfileBinaryCounts( std::istream & input,
			const Position length,
			const Regularizor *,
			const LogOddor *);

	friend HAlignandum  extractProfileBinaryCountsAsInt( std::istream & input,
			const Position length,
			int bytes,
			float scale_factor,
			const Regularizor *,
			const LogOddor *);

	friend HAlignandum addProfile2Profile( HAlignandum dest,
			const HAlignandum source,
			const HAlignment map_source2dest );

	friend HAlignandum addSequence2Profile( HAlignandum dest,
			const HAlignandum source,
			const HAlignment map_source2dest );

	friend HAlignandum substituteProfileWithProfile( HAlignandum dest,
			const HAlignandum source,
			const HAlignment map_source2dest );

	friend HAlignandum rescaleProfileCounts( HAlignandum dest, double scale_factor);

	friend HAlignandum normalizeProfileCounts( HAlignandum dest, WeightedCount total_weight );

	friend HAlignandum resetProfile( HAlignandum dest, Position length );

	friend HAlignandum makeProfile( const Position & length,
			const HEncoder &,
			const HRegularizor &,
			const HLogOddor &);

	// friend ProfileFrequencies * exportProfileFrequencies( HAlignandum dest );

public:
	/* constructors and desctructors------------------------------------------------------- */

	/** constructor */
	ImplProfile();

	ImplProfile( const HMultipleAlignment & src );

	ImplProfile( const Position & length );

	/** copy constructor */
	ImplProfile( const ImplProfile &);

	/** destructor */
	virtual ~ImplProfile();

    DEFINE_CLONE( HAlignandum );

	/** get internal representation of residue in position pos */
	virtual Residue asResidue( Position pos ) const;

	/* Mutators ------------------------------------------------------------------------------ */

	/** load data into cache, if cacheable type. In this implementation of profiles, this
	will also calculate the profile */
	virtual void prepare() const;

	/** discard cache, if cacheable type. In this implementation of profiles, this will
     delete the frequencies and profile-types. Only the counts are stored, so that the
     profile can be reconstituted. */
	virtual void release() const;

	/** write important member data in a minimally formated way to a stream. Important
	in this sense means data that the user is interested, not internal state variables,
	that would be needed to accurately reconstitute the object.
	Use different "factory" functions to format the output in a way, that you would
	like to have it (see writeSequenceFasta(...) for an example)
	 */
	virtual void write( std::ostream & output ) const;

	/** swap two positions in the profile */
	virtual void swap( const Position & x, const Position & y );

	/** mask a column */
	virtual void mask( const Position & pos);

	/** save state of object into stream
	 */
	virtual void load( std::istream & input ) ;

	/** export member data for Scorer and filler objects */
	virtual ScoreMatrix * exportScoreMatrix() const ;
	virtual FrequencyMatrix * exportFrequencyMatrix() const ;
	virtual WeightedCountMatrix * exportWeightedCountMatrix() const;

	/** return a copy of the score matrix for inspection.
	 * @return a score matrix.
	 * */
	virtual HScoreMatrix getScoreMatrix() const ;

	/** return a copy of the frequency matrix for inspection.
	 * @return a frequency matrix.
	 * */
	virtual HFrequencyMatrix getFrequencyMatrix() const ;

	/** return a copy of the counts matrix for inspection.
	 * @return a counts matrix.
	 * */
	virtual HWeightedCountMatrix getWeightedCountMatrix() const;

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
			const bool reverse_mapping = false );

	/** resize profile to new length - the old data is discarded.
	 *
	 * @param length new length of profile
	 */
	virtual void resize( Position length );

protected:

	/** allocate counts for a segment */
	template< class T>
	Matrix<T> * allocateSegment( Matrix<T> * data ) const;

	/** get row with maximum value per column */
	template <class T>
	Residue getMaximumPerColumn( const Matrix<T> * data, const Position & column ) const;

	/** mask a column */
	template<class T>
	void setColumnToValue( Matrix<T> * data,
			const Position & column,
			const T & value );

	/** write a part of a profile */
	template<class T>
	void writeSegment( std::ostream & output, const Matrix<T> * data ) const;

	/** save matrix in sparse format to stream */
	template<class T>
	void saveSparseMatrix( std::ostream & output, const Matrix<T> * data ) const;

	/** load matrix in sparse format to stream */
	template<class T>
	void loadSparseMatrix( std::istream & input, Matrix<T> * data );

	/** get residue with most counts in column */
	virtual Residue	getMaximumCount( Position column ) const ;

	/** get residue with highest positive profile score in column */
	virtual Residue	getMaximumScore( Position column ) const ;

	/** get residue with highest frequency in column */
	virtual Residue	getMaximumFrequency( Position column ) const ;

	/** allocate memory for counts
	 *
	 * Also sets the width of the profile.
	 * */
	virtual void allocateCounts() const;

	/** allocate memory for frequencies */
	virtual void allocateFrequencies() const;

	/** allocate memory for the profile */
	virtual void allocateScores() const;

	/** fill count matrix */
	virtual void fillCounts( const HMultipleAlignment & src );

	/** save state of object into stream
	 */
	virtual void __save( std::ostream & output, MagicNumberType type = MNNoType ) const;

	/** width of a profile column
	 *
	 * This width is set from the alphabet size of the translator and is set if
	 * allocateCounts() is called.
	 * */
	mutable Residue mProfileWidth;

	/** pointer to the location of the counts stored in memory */
	mutable WeightedCountMatrix * mWeightedCountMatrix;

	/** pointer to the location of the frequencies stored in memory */
	mutable FrequencyMatrix * mFrequencyMatrix;

	/** pointer to the location of the profile stored in memory */
	mutable ScoreMatrix * mScoreMatrix;

};

// handle definition for down-casting
typedef boost::shared_ptr<ImplProfile>HImplProfile;



}

#endif /* _PROFILE_H */

