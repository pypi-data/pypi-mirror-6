/*
  alignlib - a library for aligning protein sequences

  $Id: ImplEncoder.h,v 1.3 2004/03/19 18:23:41 aheger Exp $

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

#ifndef IMPL_TRANSLATOR_H
#define IMPL_TRANSLATOR_H 1

#include <string>
#include "alignlib_fwd.h"
#include "Encoder.h"
#include "Macros.h"
#include "ImplAlignlibBase.h"

namespace alignlib
{

/** @short Basic and complete implementation of translators.

    This implementation constructs a translation table from
    an alphabet supplied to the constructor.

    This implementation ignores case, but does not permit
    ambiguous characters, for example both T and U mapping to
    the same index.

    @author Andreas Heger
    @version $Id: ImplEncoder.h,v 1.3 2004/03/19 18:23:41 aheger Exp $
*/
class ImplEncoder : public Encoder, public ImplAlignlibBase
{

	// class member functions
 public:
    /** constructor */
    ImplEncoder();

     /** create a translator with two pointers to the translation tables
	@param alphabet_type	the alphabet type (used to identify user alphabets
	@param alphabet			the letters in the alphabet
	@param gap_chars		permitted mask characters. These will all be mapped to a unique code.
	@param mask_chars		permitted gap characters. These will all be mapped to a unique code.
    */
    ImplEncoder( const AlphabetType & alphabet_type,
    		const std::string & alphabet,
    		const std::string & gap_chars,
    		const std::string & mask_chars );

    /** copy constructor */
    ImplEncoder(const ImplEncoder &);

    /** destructor */
    virtual ~ImplEncoder ();

    DEFINE_CLONE( HEncoder );

    /** mapping functions */
    virtual char operator[]( const Residue & residue ) const;

    virtual Residue operator[]( const char & c ) const;

    /** translate a string of residues from internal to real world representation
	@param src		pointer to string of residues
	@param length	length of string
    */
    virtual std::string decode( const ResidueVector & src ) const;

    /** translate a single residue from internal to real world representation.
     */
    virtual char decode( const Residue src) const;

    /** translate at string of residues from real word presentation to internal representation.
	@param src		pointer to string of residues
	@param length	length of string
    */
    virtual ResidueVector encode( const std::string & src) const;

    /** translate a single residue from real world to internal representation.
     */
    virtual Residue encode( const char) const;

   /** check, if the supplied character is in the alphabet. */
    virtual bool isValidChar( const char ) const;

    /** get code used for a masked character. */
    virtual Residue getMaskCode() const;

    /** get internal code used for a gap. */
    virtual Residue getGapCode()  const;

    /** get character used for masked characters. */
    virtual char getMaskChar() const;

    /** get character used for gaps. */
    virtual char getGapChar()  const;

    /** get character used for a masked character. */
    virtual std::string getMaskChars() const;

    /** get character allowed for gaps. */
    virtual std::string getGapChars()  const;

    /** get the size of the alphabet - including gap but
     * excluding mask characters */
    virtual int getAlphabetSize() const;

    /** returns a string with all letters in the alphabet sorted by their index */
    virtual std::string getAlphabet() const;

    /** return the alphabet type */
    virtual AlphabetType getAlphabetType() const;

    /** write translator to stream in human readable format */
    virtual void write( std::ostream &) const;

    /** save state of object into stream
     */
    virtual void save( std::ostream & output ) const;

    /** build a map between two translators. Return a mapping of
     * every residue in the other translator to characters in this translators.
     *
     * All characters than can not be mapped will be mapped to the mask
     * character.
     *
     * This function does not map gap characters.
     */
    virtual HResidueVector map( const HEncoder & other ) const;

    /** build a map for a list of characters.
	 *
     * All characters than can not be mapped will be mapped to the mask
     * character.
     *
     * @return residue code of each charater in alphabet.
     */
    virtual HResidueVector getMap( const std::string & alphabet ) const ;

    /** count characters in string.
     *
     * @param src 	string
     *
     * This method counts all characters in a string excluding
     * gap characters.
     */
    virtual Position countChars( const std::string & src ) const;

 private:

	/** necessary to distinguish between built-in and custom alphabets */
	AlphabetType mAlphabetType;

	 /** the alphabet */
	std::string mAlphabet;

    /** gap characters */
    std::string mGapChars;

    /** mask characters */
    std::string mMaskChars;

    /** code signifying a gap */
    Residue mGapCode;

    /** code signifying a masked character */
    Residue mMaskCode;

    /** the table size */
    int mTableSize;

    /** the encoding table */
    Residue * mEncodingTable;

    /** the decoding table */
    char * mDecodingTable;

    /** size of alphabet : characters + mask code */
    int mAlphabetSize;
};




}

#endif /* IMPL_TRANSLATOR_H */

