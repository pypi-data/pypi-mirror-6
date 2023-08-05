/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignmentMatrix.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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

#ifndef IMPL_ALIGNATA_MATRIX_H
#define IMPL_ALIGNATA_MATRIX_H 1

#include <iosfwd>
#include <vector>
#include "alignlib_fwd.h"
#include "ImplAlignment.h"

namespace alignlib 
{

//----------------------------------------------------------------------------------------------------------------------
/** @brief calculate the diagonal for a residue pair.
 */
inline Diagonal calculateDiagonal( const ResiduePair & p) 
{ 
  return (p.mCol - p.mRow); 
}
//----------------------------------------------------------------------------------------------------------------------
/** @brief calculates the diagonal, so that (1,1) is (row_from, col_from)
 */
inline Diagonal calculateNormalizedDiagonal( const ResiduePair & p, 
						  Position row_from, 
						  Position col_from) { 
  return ( (p.mCol - col_from +1 ) - (p.mRow - row_from + 1)); 
}

/** @short base class for dotplots.

    Residues are kept in a list in memory. Note, that in this form of alignments,
    several column residues can be aligned to the same row residue and vice versa.
	
    Think of this Alignment as a dot-matrix. Actually, this is what it is used for
    in AlignatorDot. However, the full matrix is not stored memory, but as 
    a list of aligned residues (sorted first by row, then by column). The class provides
    and index for quick mapping of row to column (always the smallest col is returned).
    
    Note, that some of the functions meaningful in simple pairwise alignment object have
    a consistent but slightly different sense here. For example the alignment length
    returns the number of dots might therefore be longer than the sequences. 
    
    Also, mapRowToCol and mapColToRow give unpredictable results.
    
    Some implementation details:
    
    If the alignment is empty, mRowFrom is larger than mRowTo. This property is needed
    at some checks (for example in ImplAlignmentMatrix_iterator)
    
    @author Andreas Heger
    @version $Id: ImplAlignmentMatrix.h,v 1.3 2004/03/19 18:23:40 aheger Exp $
*/

class ImplAlignmentMatrix : public ImplAlignment 
{

    friend class ConstIterator;
    friend class ImplAlignatorDots;

 public:

    typedef std::vector<ResiduePair> PAIRVECTOR;
    typedef PAIRVECTOR::iterator PairIterator;
    typedef PAIRVECTOR::const_iterator PairConstIterator;

    //------------------> constructors / destructors <---------------------------------------------------------
    /** constructor */
    ImplAlignmentMatrix();
    
    /** copy constructor */
    ImplAlignmentMatrix( const ImplAlignmentMatrix &src );

    /** destructor */
    virtual ~ImplAlignmentMatrix();

    //------------------------------------------------------------------------------------------------------------

    class ImplAlignmentMatrix_Iterator : public Alignment::Iterator 
    {
    public:
	
      ImplAlignmentMatrix_Iterator( const PAIRVECTOR & pairs, 
				   Position index, 
				   Position max_index ) :
	mPairs( pairs ), mCurrentIndex(index), mMaximumIndex( max_index) {
	};
	
	ImplAlignmentMatrix_Iterator( const ImplAlignmentMatrix_Iterator & src ) : 
	  mPairs( src.mPairs ), mCurrentIndex( src.mCurrentIndex ), mMaximumIndex( src.mMaximumIndex ) {};
	
	 virtual ~ImplAlignmentMatrix_Iterator() {};
      
	virtual Iterator * getClone() const {return new ImplAlignmentMatrix_Iterator( *this );}
	
	/** dereference operator: runtime error, if out of bounds? */
	virtual const ResiduePair & getReference() const 
	{ 
		return (mPairs[mCurrentIndex]);
	}
 
	/** for indirection */
	virtual const ResiduePair * getPointer() const 
	{ 
		if (mCurrentIndex >= 0 && mCurrentIndex < mMaximumIndex)
			return &mPairs[mCurrentIndex]; 
		else 
			return NULL;
	}
      
	/** advance one position, until you find an aligned pair */
	virtual void next() { mCurrentIndex++; if (mCurrentIndex > mMaximumIndex) mCurrentIndex = mMaximumIndex; }
	
	/** step back one position, until you find an aligned pair */
	virtual void previous() { mCurrentIndex--; if (mCurrentIndex < -1) mCurrentIndex = -1; }
	
    private:
	const PAIRVECTOR & mPairs;
	Position mCurrentIndex;
	Position mMaximumIndex;
	
    };
    
    /** return const iterator */
    virtual AlignmentIterator begin() const; 
    
    /** return const iterator */
    virtual AlignmentIterator end() const; 

    //----------------> accessors <------------------------------------------------------------------------------

    /** returns the first aligned pair. Have to create a copy not a reference, because not all alignments will have
	a list of pairs ready */
    virtual ResiduePair front() const;
    
    /** returns the last aligned pair */
    virtual ResiduePair back() const;

    /** adds a pair of residue to the alignment */
    virtual void addPair( const ResiduePair & new_pair ); 

    /** removes a pair of residues from the alignment */
    virtual void removePair( const ResiduePair & old_pair );

    /** retrieves a pair of residues from the alignment */
    virtual ResiduePair getPair( const ResiduePair & p) const;

    /** clear the current alignemnt */
    virtual void clear();

 protected:

    /** build index */
    virtual void buildIndex() const = 0;

    /** sort Dots by row and col */
    virtual void sortDots() const = 0;

    /** calculate alignment length */
    virtual void calculateLength() const;

    /** allocate Memory for ndots dots */
    virtual void allocateIndex( unsigned long size ) const;
    
    /** eliminate duplicates entries in mPairs. This only works, if mPairs has
	been sorted previously.
    */
    virtual void eliminateDuplicates() const;
    
    /** sort dots in range from-to by row */
    void sortDotsByRow(Position from, Position to) const;

    /** sort dots in range from-to by col */
    void sortDotsByCol(Position from, Position to) const;

    /** sort dots in range from from to to by diagonal */
    void sortDotsByDiagonal(Position from, Position to) const;

    /** List of residue pairs, mutable, because they get sorted in-situ */
    mutable PAIRVECTOR mPairs;

    /** index of pairs for each row */
    mutable Dot * mIndex;

	/** update boundaries in case alignment length has changed */
	virtual void updateBoundaries() const;
    
 private:
    /* allocated size of size */
    mutable long mAllocatedIndexSize;

};

typedef boost::shared_ptr<ImplAlignmentMatrix> HImplAlignmentMatrix;
						  
}

#endif /* _ALIGNATA_H */

