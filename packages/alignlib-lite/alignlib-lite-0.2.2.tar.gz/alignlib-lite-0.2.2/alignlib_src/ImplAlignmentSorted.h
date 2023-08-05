/*
  alignlib - a library for aligning protein sequences

  $Id: ImplAlignmentSet.h,v 1.3 2004/03/19 18:23:40 aheger Exp $

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

#ifndef IMPL_ALIGNATA_SET_H
#define IMPL_ALIGNATA_SET_H 1

#include <iosfwd>
#include "alignlib_fwd.h"
#include "ImplAlignment.h"

namespace alignlib
{

/** 
    @short alignment, where residues are stored in a set using row.
    
    Residues are kept in a set indexed by row.
	
    @author Andreas Heger
    @version $Id: ImplAlignmentSet.h,v 1.3 2004/03/19 18:23:40 aheger Exp $
*/

 template< class T>
   class ImplAlignmentSorted : public ImplAlignment 
 {

  typedef typename T::const_iterator PairConstIterator;
  typedef typename T::iterator PairIterator;
  
 public:

    //------------------> constructors / destructors <---------------------------------------------------------
    /** constructor */
    ImplAlignmentSorted();

    /** copy constructor */
    ImplAlignmentSorted( const ImplAlignmentSorted &src );

    /** destructor */
    virtual ~ImplAlignmentSorted();

    //------------------------------------------------------------------------------------------------------------
    virtual HAlignment getNew() const;
    
    /** return an identical copy */
    virtual HAlignment getClone() const;

    //------------------------------------------------------------------------------------------------------------
    //------------------------------------------------------------------------------------------------------------
    /**
       @short Non-Const iterator over an alignment.
     */
    class ImplAlignmentSorted_Iterator : public Alignment::Iterator 
    {
    public:
        ImplAlignmentSorted_Iterator(PairIterator it) : 
        	mIterator( it ) 
        	{};
	
        ImplAlignmentSorted_Iterator( const ImplAlignmentSorted_Iterator & src ) : 
        	mIterator( src.mIterator) 
        	{};
	
        virtual ~ImplAlignmentSorted_Iterator() 
        	{};
	
        virtual ImplAlignmentSorted_Iterator * getClone() const
  		{
  			return new ImplAlignmentSorted_Iterator( mIterator);
  		}

        /** dereference operator
         * 
         * Const-ness is cast away. Do not mess with mRow or mCol with
         * the returned pair. However, it might be used to set the score.
         */
        virtual const ResiduePair & getReference() const 
        { 
        	return *mIterator;
        }

        /** for indirection
         * 
         * Const-ness is cast away. Do not mess with mRow or mCol with
         * the returned pair. However, it might be used to set the score.
         *  	    
         */
        virtual const ResiduePair * getPointer() const 
        { 
        	return &(*mIterator); 
        }	

        /** advance one position */
        virtual void next() { ++mIterator; }
	    
        /** step back one position */
        virtual void previous() { --mIterator;}
        
    private:
	PairIterator mIterator;
    };

    /** return const iterator */
    virtual AlignmentIterator begin() const ; 
    
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

    /** removes a row-region in an alignment */
    virtual void removeRowRegion( Position from, Position to );

    /** removes a row-region in an alignment */
    virtual void removeColRegion( Position from, Position to );

 protected:

	 /** update boundaries in case alignment length has changed */
	 virtual void updateBoundaries() const;
	 
 private:

    /** clear container */
    void clearContainer();
    
    /** container with residue pairs */
    T mPairs;
};

						  

}

#endif /* _ALIGNATA_H */

