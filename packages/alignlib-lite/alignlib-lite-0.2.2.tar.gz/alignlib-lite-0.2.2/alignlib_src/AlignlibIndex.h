#ifndef ALIGNLIBINDEX_H_
#define ALIGNLIBINDEX_H_

/*
  alignlib - a library for aligning protein sequences

  $Id: alignlibMethods.h,v 1.2 2004/01/07 14:35:31 aheger Exp $

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

#include <cstdio>
#include <map>
#include <sstream>
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "alignlib_fwd.h"

namespace alignlib
{
	/** @brief An indexed file
	 * 
	 * Objects of this class allow simple memory based
	 * indexing of files.
	 * 
	 * The class works with 
	 */
	template< typename T, class Recorder>
	class Index 
	{
		
	public:

	        typedef fpos_t FileIndex;
		typedef std::map<T, FileIndex> MapToken2Index;
		typedef typename std::map<T, FileIndex>::iterator MapToken2IndexIterator;

		/** open an index
		 * */
		Index();

		/** create an index from data
		 * @param data FILE handle to data file 
		 * */
		Index( std::FILE * data );
		
		/** create an index from pre-built index
		 * @param index FILE handle to index file 
		 * @param data FILE handle to data file 
		 */			
		Index( std::FILE * index, std::FILE * data );
	
		/** copy constructor
		 * */
		Index( const Index<T,Recorder> & src);
		
		/** destructor */
		~Index();
		
		/** @brief build the index from file 
		 * 
		 * */
		void create();

		/** @brief save the index to file 
		 * 
		 * @param file File handle to file for saving.
		 */
		void save( std::FILE * dest );

		/** @brief load the index from file 
		 * 
		 * @param file File handle of file with index.
		 */
		void load( std::FILE * index );

		/** @brief go to Position in file.
		 * 
		 * @param token Token to look up.
		 */		
		void goTo( const T & token ) const;

		/** @brief return True if token is in index
		 * 
		 * @param token Token to look up
		 */		
		bool hasToken( const T & token ) const;

		/** @brief return the size (number of entries) in the index
		 */
		long size() const;
		
		/** assign index to data
		 */
		void setData( FILE * data);

		/** return iterator over tokens */
		MapToken2IndexIterator begin() const;

		/** return iterator over tokens */
		MapToken2IndexIterator end() const;
		
		
	private:
		/** handle to DATA file */
		FILE * mData;
		
		/** index */
		mutable MapToken2Index mIndex;
		
	};

	/** Recorder class for table-formatted data
	 * 
	 * This class uses C++ streams to extract correctly
	 * typed data from a line.
	 */
	template< class T, int Column = 0>
	struct RecorderTable
	{
		RecorderTable( FILE * file, std::size_t max_line_length = 100000 ) : 
			mFile(file), mMaxLineLength( max_line_length), mBuffer(NULL)
		{
			mBuffer = new char[mMaxLineLength];
		}
		
		~RecorderTable()
		{
			delete [] mBuffer;
		}
		
		int operator()( T * result ) 
		{
			
			char * x = std::fgets( mBuffer, mMaxLineLength, mFile );
			
			if (x == NULL)
				return 0;
			
			std::istringstream istream( mBuffer );
			
			std::string s;
			for( int c = 0; c < Column; ++ c)
				istream >> s;				

			istream >> *result;
			return 1;
		}
		
	private:
		FILE * mFile;
		size_t mMaxLineLength;
		char * mBuffer;
	};

	FILE * openFileForRead( const std::string & filename );
	FILE * openFileForWrite( const std::string & filename );

	#define REPORT_STEP 10000

	template< class T, class Recorder> Index<T, Recorder>::Index() :
		mData(NULL)
	{
		debug_func_cerr(5);
	}

	template< class T, class Recorder> Index<T, Recorder>::Index(std::FILE * data) :
		mData(data)
	{
		debug_func_cerr(5);
		create();
	}

	template< class T, class Recorder> Index<T, Recorder>::Index(std::FILE * index,
			std::FILE * data) :
		mData(data)
	{
		debug_func_cerr(5);
		load(index);
	}

	template< class T, class Recorder> Index<T, Recorder>::Index( const Index<T,Recorder> & src) :
		mData(src.mData), mIndex( src.mIndex )
	{
		debug_func_cerr(5);
	}

	template< class T, class Recorder> Index<T, Recorder>::~Index()
	{
	}

	template< class T, class Recorder> void Index<T, Recorder>::create()
	{
		debug_func_cerr(5);

		if (mData == NULL)
			throw AlignlibException( "Index::create() called on undefined index - no file given" );
		
		long iteration = 0;

		FileIndex index;

		Recorder recorder(mData);

		rewind(mData);

		// TODO: find a way to set this to a generic default value
		T last = 0;
		T token = 0;
		while (!feof(mData))
		{
			++iteration;

			fgetpos(mData, &index);
			
			if (recorder( &token ) == 0)
				break;

			if (!(iteration % REPORT_STEP))
			{
				debug_cerr(5, "line=" << iteration << " nid=" << token << " last=" << last );
			}

			if (last == token) continue;
			
			MapToken2IndexIterator it(mIndex.find(token));
			if (it == mIndex.end())
			{
				mIndex[token] = index;
			}
			else
			{
				debug_cerr(5, "line=" << iteration << " token=" << token << " last=" << last);
				throw AlignlibException( "indexing error: duplicate tokens" );
			}
			
			last = token;
		}
	}

	template< class T, class Recorder> void Index<T, Recorder>::save(
			std::FILE * dest)
	{
		debug_func_cerr(5);

		if (mData == NULL)
			throw AlignlibException( "Index::save() called on undefined index - no file given" );

		MapToken2IndexIterator it(mIndex.begin()), end(mIndex.end());

		for (; it != end; ++it)
		{
			{
				int r = fwrite( &it->first, sizeof(T), 1, dest);
				if (r != 1)
					throw AlignlibException( "indexing error: could not write to file" );
			}
			{
				int r = fwrite( &it->second, sizeof(FileIndex), 1, dest);
				if (r != 1)
					throw AlignlibException( "indexing error: could not write to file" );
			}
		}
	}

	template< class T, class Recorder> void Index<T, Recorder>::load(
			std::FILE * infile)
	{
		debug_func_cerr(5);
		if (mData == NULL)
		  throw AlignlibException( "Index::load() called on undefined index - no file given");

		while(!feof(infile)) 
		  {
		    T nid;
		    FileIndex pos;
		    fread(&nid,sizeof(T), 1, infile);
		    if (feof(infile)) break;
		    fread(&pos, sizeof(FileIndex), 1, infile);
		    mIndex[nid] = pos;
		  }
	}

	template< class T, class Recorder> void Index<T, Recorder>::setData(
			std::FILE * data)
	{
		debug_func_cerr(5);
		mIndex.clear();
		mData = data;
	}

	template< class T, class Recorder> 
	long Index<T, Recorder>::size() const
	{
		debug_func_cerr(5);		
		return mIndex.size();
	}
			

	template< class T, class Recorder> bool Index<T, Recorder>::hasToken( const T & token ) const
	{
		return mIndex.find(token) != mIndex.end();
	}
	
	template< class T, class Recorder> void Index<T, Recorder>::goTo(const T & token) const
	{
		debug_func_cerr(5);
		std::vector<T> a(10);

		MapToken2IndexIterator it(mIndex.find(token));

		if (it != mIndex.end())
			fsetpos(mData, &(it->second));
		else
		{
			debug_cerr( 5, "could not find " << token)
			throw AlignlibException( "index lookup error.");
		}
	}

	template< class T, class Recorder>
	  typename Index<T, Recorder>::MapToken2IndexIterator Index<T, Recorder>::begin() const
	  {
	    return mIndex.begin();
	  }

	template< class T, class Recorder>
	  typename Index<T, Recorder>::MapToken2IndexIterator Index<T, Recorder>::end() const
	  {
	    return mIndex.end();
	  }
	
}

#endif /*ALIGNLIBINDEX_H_*/
