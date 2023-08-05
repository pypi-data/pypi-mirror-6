//--------------------------------------------------------------------------------
// Project LibAlign
//
// Copyright (C) 2000 Andreas Heger All rights reserved
//
// Author: Andreas Heger <heger@ebi.ac.uk>
//
// $Id$
//--------------------------------------------------------------------------------


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef IMPL_TOOLKIT_H
#define IMPL_TOOLKIT_H 1

#include "alignlib_fwd.h"
#include "alignlib_interfaces.h"
#include "Toolkit.h"
#include "alignlib.h"
#include "AlignlibDebug.h"

/**
	Basic implementation of toolkit.

   @author Andreas Heger
   @version $Id$: ImplDistor.h,v 1.1.1.1 2002/07/08 21:20:17 heger Exp $
   @short base class of a toolkit
*/


namespace alignlib
{

#define DEFINE_FACTORY(handle,text,make,set,get) \
	public: \
    /** provide a new text object cloned from the default object
     *
     * @return a new @ref text object
     * */ \
    virtual handle make () const { return text->getClone(); } ; \
    /** set the default text object
     */ \
    virtual void set ( const handle & x ) { text = x; }; \
    /** get the default text object
     *
     * @return the default the @ref text object
     */ \
    virtual handle get() const { return text; } ; \
    protected: \
    handle text;


#define OUTPUT(prefix, text) \
	output << prefix << " " << text << std::endl;

class ImplToolkit: public Toolkit
{
	friend std::ostream & operator<<(std::ostream &output, const Toolkit &);

    // class member functions
 public:
    // constructors and destructors

    /** constructor */
    ImplToolkit() : Toolkit(),
		Alignator( makeAlignatorDPFull( ALIGNMENT_LOCAL, -10, -2) ),
		Fragmentor( alignlib::makeFragmentorDiagonals( Alignator, -10, -2 ) ),
		Alignment( alignlib::makeAlignmentVector() ),
		MultAlignment( alignlib::makeMultAlignment() ),
		MultipleAlignator( alignlib::makeMultipleAlignatorSimple( Alignator ) ),
		Distor( alignlib::makeDistorKimura() ),
		Weightor( alignlib::makeWeightor() ),
		Regularizor( alignlib::makeRegularizor() ),
		LogOddor( alignlib::makeLogOddor()),
		Encoder( alignlib::makeEncoder( Protein20 ) ),
		Treetor( alignlib::makeTreetorDistanceLinkage() ),
		Scorer( alignlib::makeScorer() ),
		Iterator2D( alignlib::makeIterator2DFull() ),
		SubstitutionMatrix( alignlib::makeSubstitutionMatrixBlosum62( Encoder ) )
    {
    	debug_func_cerr(5);
    };

    /** copy constructor */
    ImplToolkit(const ImplToolkit & src) : Toolkit(src),
    	Alignator(src.Alignator->getClone()),
    	Fragmentor(src.Fragmentor->getClone()),
    	Alignment(src.Alignment->getClone()),
    	MultAlignment(src.MultAlignment->getClone()),
    	MultipleAlignator(src.MultipleAlignator->getClone()),
    	Distor( src.Distor->getClone()),
    	Weightor( src.Weightor->getClone()),
    	Regularizor( src.Regularizor->getClone()),
    	LogOddor( src.LogOddor->getClone()),
    	Encoder( src.Encoder->getClone()),
    	Treetor( src.Treetor->getClone()),
    	Scorer( src.Scorer->getClone()),
    	Iterator2D( src.Iterator2D->getClone()),
    	SubstitutionMatrix( src.SubstitutionMatrix->getClone())
    	{
    	debug_func_cerr(5);
    	};

    /** destructor */
    virtual ~ImplToolkit ()
    {
    	debug_func_cerr(5);
    };

	//------------------------------------------------------------------------------------------------------------
	/** returns a new Toolkit
	 */
	virtual HToolkit getNew() const
	{
		debug_func_cerr(5);
		return HToolkit(new ImplToolkit) ;
	};

	/** returns an identical Toolkit
	 */
	virtual HToolkit getClone() const
	{
    	debug_func_cerr(5);
    	return HToolkit( new ImplToolkit( *this) ) ;
	};

    DEFINE_FACTORY( HAlignator, Alignator, makeAlignator, setAlignator, getAlignator);
    DEFINE_FACTORY( HFragmentor, Fragmentor, makeFragmentor, setFragmentor, getFragmentor);
    DEFINE_FACTORY( HAlignment, Alignment, makeAlignment, setAlignment, getAlignment);
    DEFINE_FACTORY( HMultAlignment, MultAlignment, makeMultAlignment, setMultAlignment, getMultAlignment);
    DEFINE_FACTORY( HMultipleAlignator, MultipleAlignator, makeMultipleAlignator, setMultipleAlignator, getMultipleAlignator);
    DEFINE_FACTORY( HDistor, Distor, makeDistor, setDistor, getDistor);
    DEFINE_FACTORY( HWeightor, Weightor, makeWeightor, setWeightor, getWeightor);
    DEFINE_FACTORY( HRegularizor, Regularizor, makeRegularizor, setRegularizor, getRegularizor);
    DEFINE_FACTORY( HLogOddor, LogOddor, makeLogOddor, setLogOddor, getLogOddor);
    DEFINE_FACTORY( HEncoder, Encoder, makeEncoder, setEncoder, getEncoder);
    DEFINE_FACTORY( HTreetor, Treetor, makeTreetor, setTreetor, getTreetor);
    DEFINE_FACTORY( HScorer, Scorer, makeScorer, setScorer, getScorer);
    DEFINE_FACTORY( HIterator2D, Iterator2D, makeIterator2D, setIterator2D, getIterator2D);

    // need to check matrix
    DEFINE_FACTORY( HSubstitutionMatrix, SubstitutionMatrix, makeSubstitutionMatrix, setSubstitutionMatrix, getSubstitutionMatrix);

    virtual void write( std::ostream & output ) const
    {
    	output << "toolkit contents" << std::endl;
        OUTPUT( "Alignator", Alignator );
        OUTPUT( "Fragmentor", Fragmentor );
        OUTPUT( "Alignment", Alignment );
        OUTPUT( "MultAlignment", MultAlignment );
        OUTPUT( "MultipleAlignator", MultipleAlignator );
        OUTPUT( "Distor", Distor );
        OUTPUT( "Weightor", Weightor );
        OUTPUT( "Regularizor", Regularizor );
        OUTPUT( "LogOddor", LogOddor );
        OUTPUT( "Encoder", Encoder );
        OUTPUT( "Treetor", Treetor );
        OUTPUT( "Scorer",  Scorer);
        OUTPUT( "Iterator2D", Iterator2D );
    }
};

/** initialize and create the default toolkit
 * The default objects point back to the default toolkit,
 * which is impossible to achieve in the constructor.
 */
#define BOOTSTRAP(fn) tk->fn()->setToolkit( tk );
HToolkit bootstrapToolkit()
{
	debug_func_cerr(5);
	HToolkit tk( new ImplToolkit() );
	BOOTSTRAP(getAlignator);
	BOOTSTRAP(getFragmentor);
	BOOTSTRAP(getAlignment);
	BOOTSTRAP(getMultAlignment);
	BOOTSTRAP(getMultipleAlignator);
	BOOTSTRAP(getDistor);
	BOOTSTRAP(getWeightor);
	BOOTSTRAP(getRegularizor);
	BOOTSTRAP(getLogOddor);
	BOOTSTRAP(getEncoder);
	BOOTSTRAP(getTreetor);
	BOOTSTRAP(getScorer);
	BOOTSTRAP(getIterator2D);
	BOOTSTRAP(getSubstitutionMatrix);
	return tk;
}

HToolkit makeToolkit( const ToolkitType & type )
{
	debug_func_cerr(5);
	switch ( type )
	{
	case ProteinAlignment: return HToolkit( new ImplToolkit() ); break;
	case DNAAlignment: return HToolkit( new ImplToolkit() ); break;
	case Genomics: return HToolkit( new ImplToolkit() ); break;
	}
}

IMPLEMENT_STATIC_DEFAULT( HToolkit, bootstrapToolkit(), getDefaultToolkit, setDefaultToolkit, default_toolkit );

// default objects without dependencies
IMPLEMENT_DEFAULT( HIterator2D, getDefaultIterator2D, setDefaultIterator2D, getIterator2D, setIterator2D );
IMPLEMENT_DEFAULT( HLogOddor, getDefaultLogOddor, setDefaultLogOddor,  getLogOddor, setLogOddor );
IMPLEMENT_DEFAULT( HRegularizor, getDefaultRegularizor, setDefaultRegularizor, getRegularizor, setRegularizor );
IMPLEMENT_DEFAULT( HWeightor, getDefaultWeightor, setDefaultWeightor, getWeightor, setWeightor );
IMPLEMENT_DEFAULT( HScorer, getDefaultScorer, setDefaultScorer,  getScorer, setScorer )
IMPLEMENT_DEFAULT( HDistor, getDefaultDistor, setDefaultDistor, getDistor, setDistor );
IMPLEMENT_DEFAULT( HEncoder, getDefaultEncoder, setDefaultEncoder, getEncoder, setEncoder );
IMPLEMENT_DEFAULT( HSubstitutionMatrix, getDefaultSubstitutionMatrix, setDefaultSubstitutionMatrix, getSubstitutionMatrix, setSubstitutionMatrix );
IMPLEMENT_DEFAULT( HTreetor, getDefaultTreetor, setDefaultTreetor, getTreetor, setTreetor );
IMPLEMENT_STATIC_DEFAULT( HPalette, makePalette(), getDefaultPalette, setDefaultPalette, default_palette );

}

#endif /* IMPL_TOOLKIT_H */

