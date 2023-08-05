/*
  alignlib - a library for aligning protein sequences

  $Id: ImplProfile.cpp,v 1.3 2004/01/07 14:35:35 aheger Exp $

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
#include <limits>
#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "ImplProfile.h"
#include "Encoder.h"
#include "HelpersEncoder.h"
#include "LogOddor.h"
#include "Weightor.h"
#include "Regularizor.h"
#include "MultipleAlignment.h"
#include "Alignment.h"
#include "AlignmentIterator.h"
#include "HelpersAlignandum.h"
#include "HelpersLogOddor.h"
#include "HelpersRegularizor.h"
#include "HelpersMultipleAlignment.h"
#include "HelpersWeightor.h"
#include "HelpersToolkit.h"
#include "MultAlignment.h"

/** default objects */

using namespace std;

namespace alignlib
{

//---------------------------------< implementation of factory functions >--------------

//------------------------------------------------------------------------------------------
/** create empty profile
 * */
HAlignandum makeProfile()
{
	return makeProfile();
}

//------------------------------------------------------------------------------------------
/** create empty profile with given length */
HAlignandum makeProfile(
		const Position & length )
{
	return HAlignandum( new ImplProfile( length ) );
}

//------------------------------------------------------------------------------------------
/** create profile from a string of sequences */
HAlignandum makeProfile( const std::string & src, int nsequences)
{
    HMultipleAlignment m( makeMultipleAlignment() );
    fillMultipleAlignment(
                    m,
                    src,
                    nsequences );

    return HAlignandum (new ImplProfile(m ) );
}

//------------------------------------------------------------------------------------------
/** create a default profile from a multiple alignment */
HAlignandum makeProfile(
		const HMultipleAlignment & mali )
{
	return HAlignandum( new ImplProfile( mali ) );
}

//---------------------------------------------------------------
HAlignandum makeProfile(
		const HAlignandum & seqa,
		const HAlignment & map_seqa2profile,
		const HAlignandum & seqb,
		const HAlignment & map_seqb2profile )
{
	debug_func_cerr(5);
	HProfile profile = toProfile(makeProfile(
			std::max( map_seqa2profile->getColTo(),
						map_seqb2profile->getColTo() )));
	profile->add( seqa, map_seqa2profile );
	profile->add( seqb, map_seqb2profile );
	return profile;
}

//---------------------------------------------------------------
HAlignandum makeProfile(
		const HMultAlignment & mali,
		const HAlignandumVector & sequences )
{
	debug_func_cerr(5);
	if (sequences->size() != mali->getNumSequences())
		throw AlignlibException( "ImplProfile.cpp: number of sequences given does not match number of sequences in MultAlignment");

	HProfile profile = toProfile(makeProfile( mali->getLength() ));

	for (int x = 0; x < mali->getNumSequences(); ++x)
		profile->add( (*sequences)[x], (*mali)[x], true );

	return profile;
}


//---------------------------------------> constructors and destructors <--------------------------------------
// The constructor is potentially empty, so that this object can be read from file.
ImplProfile::ImplProfile() :
		ImplAlignandum(),
		mWeightedCountMatrix(NULL),
		mFrequencyMatrix(NULL),
		mScoreMatrix(NULL),
		mProfileWidth(0)
{
	debug_func_cerr(5);
}


ImplProfile::ImplProfile( const Position & length ) :
			ImplAlignandum(),
			mWeightedCountMatrix(NULL),
			mFrequencyMatrix(NULL),
			mScoreMatrix(NULL),
			mProfileWidth(0)
{
	debug_func_cerr(5);
	resize( length );
}


ImplProfile::ImplProfile( const HMultipleAlignment & src ) :
		ImplAlignandum(),
		mWeightedCountMatrix(NULL),
		mFrequencyMatrix(NULL),
		mScoreMatrix(NULL),
		mProfileWidth(0)
{
	debug_func_cerr(5);
	resize( src->getLength() );
	fillCounts( src );
}

//---------------------------------------------------------------------------------------------------------------
ImplProfile::ImplProfile(const ImplProfile & src ) : ImplAlignandum( src ),
	mWeightedCountMatrix(NULL),
	mFrequencyMatrix(NULL),
	mScoreMatrix(NULL),
	mProfileWidth(src.mProfileWidth)
{
	debug_func_cerr(5);

	if (src.mWeightedCountMatrix != NULL)
		mWeightedCountMatrix = new WeightedCountMatrix( *src.mWeightedCountMatrix );

	if (src.mFrequencyMatrix != NULL)
		mFrequencyMatrix = new FrequencyMatrix( *src.mFrequencyMatrix );

	if (src.mScoreMatrix != NULL)
		mScoreMatrix = new ScoreMatrix( *src.mScoreMatrix );
}

//---------------------------------------------------------------------------------------------------------------
ImplProfile::~ImplProfile()
{
	debug_func_cerr(5);

	if (mWeightedCountMatrix != NULL)
		{ delete mWeightedCountMatrix; mWeightedCountMatrix = NULL; }
	if (mFrequencyMatrix != NULL)
		{ delete mFrequencyMatrix; mFrequencyMatrix = NULL; }
	if (mScoreMatrix != NULL)
		{ delete mScoreMatrix; mScoreMatrix = NULL; }
}

IMPLEMENT_CLONE( HAlignandum, ImplProfile );

//--------------------------------------------------------------------------------------
WeightedCountMatrix * ImplProfile::exportWeightedCountMatrix() const
{
	return mWeightedCountMatrix;
}

//--------------------------------------------------------------------------------------
FrequencyMatrix * ImplProfile::exportFrequencyMatrix() const
{
	return mFrequencyMatrix;
}

//--------------------------------------------------------------------------------------
ScoreMatrix * ImplProfile::exportScoreMatrix() const
{
	return mScoreMatrix;
}

//--------------------------------------------------------------------------------------
HWeightedCountMatrix ImplProfile::getWeightedCountMatrix() const
{
	return HWeightedCountMatrix( new WeightedCountMatrix(*mWeightedCountMatrix));
}

//--------------------------------------------------------------------------------------
HFrequencyMatrix ImplProfile::getFrequencyMatrix() const
{
	return HFrequencyMatrix( new FrequencyMatrix(*mFrequencyMatrix));
}

//--------------------------------------------------------------------------------------
HScoreMatrix ImplProfile::getScoreMatrix() const
{
	return HScoreMatrix( new ScoreMatrix( *mScoreMatrix ));
}


//--------------------------------------------------------------------------------------
void ImplProfile::resize( Position length )
{
	ImplAlignandum::resize( length );
	allocateCounts();
}

//---------------------------------------------------------------------------------------------------------------
void ImplProfile::fillCounts( const HMultipleAlignment &  src )
{
	debug_func_cerr(5);

	resize( src->getLength() );
	getToolkit()->getWeightor()->fillCounts( *mWeightedCountMatrix, src, getToolkit()->getEncoder());

	setPrepared( false );
}

//---------------------------------------------------------------------------------------------------------------
template< class T>
Matrix<T> * ImplProfile::allocateSegment( Matrix<T> * data ) const
{
	debug_func_cerr(5);

	if (data != NULL) delete data;
	data = new Matrix<T>( getFullLength(), mProfileWidth, 0 );

	return data;
}

//---------------------------------------------------------------------------------------------------------------
void ImplProfile::allocateCounts() const
{
	debug_func_cerr(5);

	mProfileWidth = getToolkit()->getEncoder()->getAlphabetSize();

	debug_cerr( 3, "allocating counts for a profile of size " << getFullLength() << " x " << (int)mProfileWidth );

	mWeightedCountMatrix = allocateSegment<WeightedCount>( mWeightedCountMatrix );
}

//---------------------------------------------------------------------------------------------------------------
void ImplProfile::allocateScores() const
{
	debug_func_cerr(5);
	mScoreMatrix = allocateSegment<Score>( mScoreMatrix );
}

//---------------------------------------------------------------------------------------------------------------
void ImplProfile::allocateFrequencies() const
{
	debug_func_cerr(5);
	mFrequencyMatrix = allocateSegment<Frequency>( mFrequencyMatrix );
}

//---------------------------------------------------------------------------------------------------------------
template<class T>
Residue ImplProfile::getMaximumPerColumn( const Matrix<T> * data,
										  const Position & column ) const
{
	assert( data != NULL );

	T max = std::numeric_limits<T>::min();
	Residue max_i = 0;

	T * col = data->getRow( column );
	for (Residue i = 0; i < mProfileWidth; ++i)
	{
		if (col[i] > max)
		{
			max = col[i];
			max_i = i;
		}
	}

	// if no counts, return gap code
	if (max == 0)
		return getToolkit()->getEncoder()->getGapCode();

	return max_i;
}

//---------------------------------------------------------------------------------------------------------------
Residue ImplProfile::getMaximumCount( const Position column ) const
{
	debug_func_cerr(6);
	return getMaximumPerColumn<WeightedCount>( mWeightedCountMatrix, column );
}

//---------------------------------------------------------------------------------------------------------------
Residue ImplProfile::getMaximumFrequency( const Position column ) const
{
	debug_func_cerr(5);
	return getMaximumPerColumn<Frequency>( mFrequencyMatrix, column );
}

//---------------------------------------------------------------------------------------------------------------
Residue ImplProfile::getMaximumScore( const Position column ) const
{
	debug_func_cerr(5);
	return getMaximumPerColumn<Score>( mScoreMatrix, column );
}

//---------------------------------------------------------------------------------------------------------------
template<class T>
void ImplProfile::setColumnToValue( Matrix<T> * data,
		const Position & column,
		const T & value )
{
	if (data == NULL) return;

	T * col = data->getRow( column );
	for (int i = 0; i < mProfileWidth; i++)
		col[i] = 0;
}

//---------------------------------------------------------------------------------------------------------------
void ImplProfile::mask( const Position & column)
{
	ImplAlignandum::mask( column );
	setColumnToValue<WeightedCount>( mWeightedCountMatrix, column, 0);
	setColumnToValue<Frequency>( mFrequencyMatrix, column, 0);
	setColumnToValue<Score>( mScoreMatrix, column, 0 );
}

//---------------------------------------------------------------------------------------------------------------
Residue ImplProfile::asResidue( const Position column ) const
{
	if (isMasked(column))
		return getToolkit()->getEncoder()->getMaskCode();
	return getMaximumCount( column );
}

//--------------------------------------------------------------------------------------
void ImplProfile::prepare() const
{
	debug_func_cerr(5);

	// do nothing, when a profile and frequencies already exist.
	if (mFrequencyMatrix == NULL)
	{
		allocateFrequencies();
		getToolkit()->getRegularizor()->fillFrequencies( *mFrequencyMatrix, *mWeightedCountMatrix, getToolkit()->getEncoder() );
	}

	if (!mScoreMatrix)
	{
		allocateScores();
		getToolkit()->getLogOddor()->fillProfile( *mScoreMatrix, *mFrequencyMatrix, getToolkit()->getEncoder());
	}
	setPrepared( true );
}

//--------------------------------------------------------------------------------------
void ImplProfile::release() const
{
	debug_func_cerr(5);

	if (mFrequencyMatrix != NULL)
	{
		delete mFrequencyMatrix;
		mFrequencyMatrix = NULL;
	}
	if (mScoreMatrix != NULL)
	{
		delete mScoreMatrix;
		mScoreMatrix = NULL;
	}
	setPrepared(false);
}

//--------------------------------------------------------------------------------------
void ImplProfile::swap( const Position & x, const Position & y )
{
	mWeightedCountMatrix->swapRows( x, y );
	if (mFrequencyMatrix != NULL)
		mFrequencyMatrix->swapRows( x, y );
	if (mWeightedCountMatrix != NULL)
		mWeightedCountMatrix->swapRows( x, y );
}

//--------------------------------------------------------------------------------------
template<class T>
void ImplProfile::writeSegment( std::ostream & output, const Matrix<T> * data ) const
{
	if (data == NULL) return;

	const Encoder & encoder(*(getToolkit()->getEncoder()));

	output << setw(4) << "#" << "  " << " ";
	for (Residue j = 0; j < mProfileWidth; j++)
		output << setw(6) << encoder.decode( j );
	output << std::endl;
	for (int i = 0; i < getLength(); i++)
	{
		output << setw(5) << i << " " << asChar(i) << " ";
		const T * column = data->getRow( i );
		for (Residue j = 0; j < mProfileWidth; j++)
			output << setw(6) << setprecision(2) << column[j];
		output << endl;
	}
}

//--------------------------------------> I/O <------------------------------------------------------------
void ImplProfile::write( std::ostream & output ) const
{

	output.setf( ios::fixed );

	if (mWeightedCountMatrix)
	{
		output << "----------->counts<----------------------------------------" << endl;
		writeSegment<WeightedCount>( output, mWeightedCountMatrix );
	}
	else
	{
		output << "----------->no counts available<---------------------------" << endl;
	}

	if (mFrequencyMatrix)
	{
		output << "----------->frequencies<-----------------------------------" << endl;
		writeSegment<Frequency>( output, mFrequencyMatrix );
	}
	else
	{
		output << "----------->no frequencies available<----------------------" << endl;
	}

	if (mScoreMatrix)
	{
		output << "----------->profile<---------------------------------------" << endl;
		writeSegment<Score>( output, mScoreMatrix );
	}
	else
	{
		output << "----------->no profile available<--------------------------" << endl;
	}
}

//--------------------------------------------------------------------------------------
template<class T>
void ImplProfile::saveSparseMatrix( std::ostream & output, const Matrix<T> * data ) const
{
	debug_func_cerr(5);
	assert (data != NULL);

	Residue eol = NO_RESIDUE;
	for (Position i = 0; i < getLength(); ++i)
	{
		const T * column = data->getRow( i );
		for (Residue j = 0; j < mProfileWidth; ++j)
		{
			T v = column[j];
			if ( v != 0)
			{
				output.write( (char*)&j, sizeof(Residue) );
				output.write( (char*)&v, sizeof( T ) );
			}
		}
		output.write( (char*)&eol, sizeof( Residue) );
	}
}

//--------------------------------------------------------------------------------------
template<class T>
void ImplProfile::loadSparseMatrix( std::istream & input, Matrix<T> * data )
{
	debug_func_cerr(5);
	assert (data != NULL);

	for (Position i = 0; i < getLength(); i++)
	{
		Residue j = NO_RESIDUE;
		T v = 0;

		while( true )
		{
			input.read( (char*)&j, sizeof( Residue ) );
			if ( j == NO_RESIDUE ) break;
			input.read( (char*)&v, sizeof( T ) );
			data->setValue( i, j, v);
		}
	}
}


//--------------------------------------------------------------------------------------
void ImplProfile::__save( std::ostream & output, MagicNumberType type ) const
{
	debug_func_cerr(5);
	if (type == MNNoType )
	{
		type = MNImplProfile;
		output.write( (char*)&type, sizeof(MagicNumberType ) );
	}
	ImplAlignandum::__save( output, type );

	output.write( (char*)&mProfileWidth, sizeof(Residue) );

	size_t size = getFullLength() * mProfileWidth;

	if ( mStorageType == Full )
	{
		output.write( (char*)mWeightedCountMatrix->getData(), sizeof(WeightedCount) * size);
		if (isPrepared() )
		{
			output.write( (char*)mFrequencyMatrix->getData(), sizeof(Frequency) * size);
			output.write( (char*)mScoreMatrix->getData(), sizeof(Score) * size );
		}
	}
	else if ( mStorageType == Sparse )
	{
		saveSparseMatrix<WeightedCount>( output, mWeightedCountMatrix );

		if (isPrepared() )
		{
			saveSparseMatrix<Frequency>( output, mFrequencyMatrix );
			// can only compress counts and frequencies
			output.write( (char*)mScoreMatrix->getData(), sizeof(Score) * size );
		}
	}
}

//--------------------------------------------------------------------------------------
void ImplProfile::load( std::istream & input)
{
	debug_func_cerr(5);
	ImplAlignandum::load( input );

	input.read( (char*)&mProfileWidth, sizeof( Residue ) );

	size_t size = getFullLength() * mProfileWidth;

	if ( mStorageType == Full )
	{
		allocateCounts();
		input.read( (char*)mWeightedCountMatrix->getData(),
					sizeof( WeightedCount) * size );

		if (input.fail() )
			throw AlignlibException( "incomplete profile in stream.");

		if (isPrepared() )
		{
			allocateFrequencies();
			input.read( (char*)mFrequencyMatrix->getData(),
						sizeof( Frequency) * size );
			allocateScores();
			input.read( (char*)mScoreMatrix->getData(),
						sizeof(Score) * size );
		}
	}
	else if ( mStorageType == Sparse )
	{
		allocateCounts();
		loadSparseMatrix<WeightedCount>( input, mWeightedCountMatrix );

		if (input.fail() )
			throw AlignlibException( "incomplete profile in stream.");

		if (isPrepared() )
		{
			allocateFrequencies();
			loadSparseMatrix<Frequency>( input, mFrequencyMatrix );
			allocateScores();
			input.read( (char*)mScoreMatrix->getData(),
					sizeof(Score) * size );
		}

	}


}

//------------------------------------------------------------------------------------------
void ImplProfile::add(
		const HAlignandum & source,
		const HAlignment & map_source2dest,
		bool is_reverse )
{
	debug_func_cerr(5);

	debug_cerr( 3, "adding to profile: is_reverse=" << is_reverse
			<< " this=" << map_source2dest->getRowFrom() << "-" << map_source2dest->getRowTo()
			<< " len=" << getFullLength()
			<< " other=" << map_source2dest->getColFrom() << "-" << map_source2dest->getColTo()
			<< " len=" << source->getFullLength() );

	assert( source->getToolkit()->getEncoder()->getAlphabetSize() == getToolkit()->getEncoder()->getAlphabetSize());

	if (is_reverse)
	{
		assert (map_source2dest->getColTo() <= source->getFullLength() );
		assert (map_source2dest->getRowTo() <= getFullLength() );
	}
	else
	{
		assert (map_source2dest->getRowTo() <= source->getFullLength() );
		assert (map_source2dest->getColTo() <= getFullLength() );
	}
	const HSequence sequence(toSequence( source ));
	if (sequence)
	{
		AlignmentIterator it(map_source2dest->begin());
		AlignmentIterator it_end(map_source2dest->end());

		if (is_reverse)
		{
			for (; it != it_end; ++it)
			{
				Position row = it->mCol;
				Position col = it->mRow;
				Residue i = sequence->asResidue(row);
				mWeightedCountMatrix->addValue(col,i,1);
			}
		}
		else
		{
			for (; it != it_end; ++it)
			{
				Position row = it->mRow;
				Position col = it->mCol;
				Residue i = sequence->asResidue(row);
				mWeightedCountMatrix->addValue(col,i,1);
			}
		}
	}
	else
	{
		const HProfile profile(toProfile(source));
		if (profile)
		{
			AlignmentIterator it(map_source2dest->begin());
			AlignmentIterator it_end(map_source2dest->end());

			HWeightedCountMatrix m(profile->getWeightedCountMatrix());
			if (is_reverse)
			{
				for (; it != it_end; ++it)
				{
					Position row = it->mCol;
					Position col = it->mRow;
					for (Residue i = 0; i < mProfileWidth; i++)
						mWeightedCountMatrix->addValue(col,i,(*m)[row][i]);
				}
			}
			else
			{
				for (; it != it_end; ++it)
				{
					Position row = it->mRow;
					Position col = it->mCol;
					for (Residue i = 0; i < mProfileWidth; i++)
						mWeightedCountMatrix->addValue(col,i,(*m)[row][i]);
				}
			}
		}
		else
			throw AlignlibException( "can not guess type of src - neither profile nor sequence");
	}

	if (isPrepared())
	{
		release();	// first release, otherwise it won't calculate anew
		prepare();
	}
}

} // namespace alignlib
