/*
  alignlib - a library for aligning protein sequences

  $Id: Encoder.h,v 1.3 2004/03/19 18:23:41 aheger Exp $

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

#ifndef TRANSLATOR_H
#define TRANSLATOR_H 1

#include "alignlib_fwd.h"
#include "Macros.h"
#include "AlignlibBase.h"

namespace alignlib
{

/** @short Protocoll class for objects that translate alphanumeric alphabets to numeric codes.

    Encoders are responsible for translating between biological alphabets (ACGT, 20 amino acids)
	to the numeric representation used by alignment algorithms. Each characters is assigned
	a numeric number starting from 0.

	The alphabet can include characters for masking (e.g., X for protein sequences, N for nucleotide
	sequences) and these are part of the alphabet. While several characters might be defined as
	gap-characters, on encoding only a single code is used for all. On decoding, the default mask
	character will be returned.

	The encoders also record gap characters and assign a unique code for these, but
	these characters are not considered to be a part of the alphabet (and thus do not
	count towards the alphabet size.)

	Any character that is not recognized by an @ref Encoder will be substituted with
	a mask character.

	Encoders are in general case-insensitive, case information is lost on encoding/decoding.

   @author Andreas Heger
   @version $Id: Encoder.h,v 1.3 2004/03/19 18:23:41 aheger Exp $
*/
class Encoder : public virtual AlignlibBase
{
	friend std::ostream & operator<<(std::ostream &output, const Encoder &);

    // class member functions
 public:
    // constructors and destructors

    /** constructor */
    Encoder();

    /** copy constructor */
    Encoder(const Encoder &);

    /** destructor */
    virtual ~Encoder ();

    DEFINE_ABSTRACT_CLONE( HEncoder )

    /** decode a string of residues from internal to real-world representation.
     *
	 *
	 *	@param src		Vector of residues
	 *  @return a string of the decoded residues.
    */
    virtual std::string decode( const ResidueVector & src ) const = 0;

    /** translate a single residue from internal to real-world representation.
     */
    virtual char decode( const Residue src) const = 0;

    /** translate at string of residues from real word presentation to internal representation.

	@param  src		pointer to string of residues
	@param  length	length of string
	@return a handle to a vector of encoded characters.

    */
    virtual ResidueVector encode( const std::string & src ) const = 0;

    /** translate a single residue from real-world to internal representation.
     */
    virtual Residue encode( const char) const = 0;

   /** check, if the supplied character is in the alphabet.
    * @param c character to test.
    * */
    virtual bool isValidChar( const char c) const = 0;

    /** get code used for a masked character. */
    virtual Residue getMaskCode() const = 0;

    /** get internal code used for a gap. */
    virtual Residue getGapCode()  const = 0;

    /** get character used for a masked character. */
    virtual std::string getMaskChars() const = 0;

    /** get character used for a gap. */
    virtual std::string getGapChars()  const = 0;

    /** get character used for masked characters. */
    virtual char getMaskChar() const = 0;

    /** get character used for gaps. */
    virtual char getGapChar()  const = 0;

    /** returns a string with all letters in the alphabet sorted by their index */
    virtual std::string getAlphabet() const = 0;

    /** return the alphabet type */
    virtual AlphabetType getAlphabetType() const = 0;

    /** get the size of the alphabet. This includes
     * mask characters but excludes gap characters */
    virtual int getAlphabetSize() const = 0;

    /** build a map between two translators. Return a mapping of
     * every residue in the other translator to characters in this translator.
     *
     * All characters than can not be mapped will be mapped to the mask
     * character.
     *
     * This function will not map gap characters.
     */
    virtual HResidueVector map( const HEncoder & other ) const = 0;

    /** build a map for a list of characters.
	 *
     * All characters than can not be mapped will be mapped to the mask
     * character.
     *
     * @return residue code of each charater in alphabet.
     */
    virtual HResidueVector getMap( const std::string & alphabet ) const = 0;

    /** count characters in string.
     *
     * @param src 	string
     *
     * This method counts all characters in a string excluding
     * gap characters.
     */
    virtual Position countChars( const std::string & src ) const = 0;

    /** write translator to stream */
    virtual void write( std::ostream &) const = 0;

	/** save state of object into stream
	 */
	virtual void save( std::ostream & input ) const = 0;

};

}

#endif /* _TRANSLATOR_H */

