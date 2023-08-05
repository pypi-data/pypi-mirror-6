/*
  alignlib - a library for aligning protein sequences

  $Id: HelpersSequence.cpp,v 1.2 2004/01/07 14:35:32 aheger Exp $

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

#include <time.h>

#include <iostream>
#include <fstream>
#include <string>

#include "Matrix.h"

#include "HelpersAlignandum.h"
#include "AlignlibException.h"

#include "Encoder.h"
#include "HelpersEncoder.h"

#include "Alignandum.h"
#include "ImplSequence.h"
#include "Toolkit.h"
#include "HelpersToolkit.h"

#include <math.h>

using namespace std;

namespace alignlib
{

//---------------------------------< implementation of useful functions >--------------

//----------------------------------------------------------------------------------
/** create a sequence from a stream */
/*
HAlignandum extractSequence( std::istream & input, const HEncoder & translator )
{
	// TODO to be implemented
	return NULL;
}
*/

//----------------------------------------------------------------------------------
/** create a sequence from a stream, put description into field description.
 * Return False, if unsuccessfull, true if successful. */
HAlignandum makeSequenceFromFasta(
		std::istream & input,
		std::string & description )
{

#define MAX_CHUNK 10000

	const HEncoder & translator = getDefaultToolkit()->getEncoder();

	char * buffer = new char[MAX_CHUNK];

	while ( (input.peek() != '>') &&
			!input.eof() ) {
		input.getline( buffer, MAX_CHUNK);
	}

	if (input.eof())
		return HAlignandum();

	input.get();
	input.getline(buffer, MAX_CHUNK);

	description = buffer;
	// erase end of line
	description.erase(description.size(),1);

	std::string sequence("");

	// build the sequence character-wise
	while ( (input.peek() != '>') &&
			!input.eof() )
	{
		input.getline( buffer, MAX_CHUNK);

		for (unsigned int i = 0; i < strlen(buffer); i++)
			if (translator->isValidChar( buffer[i] ))
				sequence += buffer[i];
	}

	delete [] buffer;

	if (sequence.size() > 0)
		return makeSequence( sequence.c_str() );
	else
		return HAlignandum();
}

/* TODO: This routine should be replaced by something, that
     a. uses a different random generator
     b. is more efficient.
     c. is portable
*/

const double max_rand = pow(2.0,31) -1;

Residue sampleFromDistribution( const double * histogram, const int width )
{
	double x = random() / max_rand;
	double s = 0;
	Residue i = 0;
	for (i = 0; i < width; i++)
	{
		s+= histogram[i];
		if (x < s) return i;
	}
	return width - 1;
}

HAlignandum makeMutatedSequence(
		HAlignandum src,
		const HMutationMatrix & matrix,
		const long seed )
{
	assert( matrix->getNumRows() == matrix->getNumCols() );

	int width = matrix->getNumRows();

	// intialize random generator
	if (seed > 0)
		srandom(seed);

	char * buffer = new char[src->getLength() + 1];
	buffer[src->getLength()] = '\0';

	const HEncoder & translator = src->getToolkit()->getEncoder();

	for (Position i = 0; i < src->getLength(); ++i)
	{
		Residue residue = src->asResidue(i);
		Residue new_residue = sampleFromDistribution(
				matrix->getRow(residue),
				width );
		buffer[i] = translator->decode(new_residue);
	}

	HAlignandum sequence = makeSequence( buffer );
	sequence->setToolkit( src->getToolkit() );
	delete [] buffer;

	return sequence;

}


} // namespace alignlib















