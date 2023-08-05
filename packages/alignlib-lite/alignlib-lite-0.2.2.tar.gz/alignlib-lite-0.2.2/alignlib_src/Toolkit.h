/*
  alignlib - a library for aligning protein sequences

  $Id: Toolkit.h,v 1.3 2004/03/19 18:23:41 aheger Exp $

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

#ifndef TOOLKIT_H
#define TOOLKIT_H 1

#include "alignlib_fwd.h"
#include "Macros.h"

namespace alignlib
{

#define DEFINE_FACTORY_ABSTRACT(handle,text,make,set,get) \
    /** provide a new text object cloned from the default object
     *
     * @return a new @ref text object
     * */ \
    virtual handle make () const = 0; \
    /** set the default text object
     *
     * @return the default the @ref text object
     */ \
    virtual void set ( const handle & ) = 0; \
    /** get the default text object
     *
     * @return the default the @ref text object
     */ \
    virtual handle get() const = 0;


/** @short Factor providing default objects
 *
 * A toolkit provides an environment that classes can draw
 * upon to request default implementations of alignments,
 * objects, etc.
 *
 */

class Toolkit
{
	friend std::ostream & operator<<(std::ostream &output, const Toolkit &);

    // class member functions
 public:
    // constructors and destructors

    /** constructor */
    Toolkit();

    /** copy constructor */
    Toolkit(const Toolkit &);

    /** destructor */
    virtual ~Toolkit ();

    /** write information of object to stream
     *
     * */
    virtual void write( std::ostream & output ) const = 0;

    DEFINE_ABSTRACT_CLONE( HToolkit )

    DEFINE_FACTORY_ABSTRACT( HAlignator, Alignator, makeAlignator, setAlignator, getAlignator)
    DEFINE_FACTORY_ABSTRACT( HFragmentor, Fragmentor, makeFragmentor, setFragmentor, getFragmentor)
    DEFINE_FACTORY_ABSTRACT( HAlignment, Alignment, makeAlignment, setAlignment, getAlignment)
    DEFINE_FACTORY_ABSTRACT( HMultAlignment, MultAlignment, makeMultAlignment, setMultAlignment, getMultAlignment)
    DEFINE_FACTORY_ABSTRACT( HMultipleAlignator, MultipleAlignator, makeMultipleAlignator, setMultipleAlignator, getMultipleAlignator)
    DEFINE_FACTORY_ABSTRACT( HDistor, Distor, makeDistor, setDistor, getDistor)
    DEFINE_FACTORY_ABSTRACT( HWeightor, Weightor, makeWeightor, setWeightor, getWeightor)
    DEFINE_FACTORY_ABSTRACT( HRegularizor, Regularizor, makeRegularizor, setRegularizor, getRegularizor)
    DEFINE_FACTORY_ABSTRACT( HLogOddor, LogOddor, makeLogOddor, setLogOddor, getLogOddor)
      DEFINE_FACTORY_ABSTRACT( HEncoder, Encoder, makeEncoder, setEncoder, getEncoder)
      DEFINE_FACTORY_ABSTRACT( HTreetor, Treetor, makeTreetor, setTreetor, getTreetor)
    DEFINE_FACTORY_ABSTRACT( HScorer, Scorer, makeScorer, setScorer, getScorer)
    DEFINE_FACTORY_ABSTRACT( HIterator2D, Iterator2D, makeIterator2D, setIterator2D, getIterator2D)
    DEFINE_FACTORY_ABSTRACT( HSubstitutionMatrix, SubstitutionMatrix, makeSubstitutionMatrix, setSubstitutionMatrix, getSubstitutionMatrix)

};

}

#endif /* _TOOLKIT_H */

