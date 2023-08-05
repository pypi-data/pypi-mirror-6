#include <string>
#include <iosfwd>

#include "alignlib_fwd.h"

namespace alignlib
{

  // The following I could not work out, so doing it without templates.
  // which is very cumbersome.
  
    /* template<class T>  */
    /* std::string _repr(T const &x) */
    /* { */
    /*   std::ostringstream s; */
    /*   s << *x; */
    /*   return s.str(); */
    /* } */

    /* // explicit instantiation */
    /* template std::string _repr<HAlignment>(HAlignment const & x); */
    /* //    #_repr<Alignment> Alignment2Repr = _repr<Alignment> */
    /* // typedef _repr<HAlignment>Alignment2Repr; */

  std::string Alignment2String( HAlignment const &x ) 
    {
      std::ostringstream s; 
      s << *x;
      return s.str();
    }

  std::string AlignmentFormat2String( AlignmentFormat const *x ) 
    {
      std::ostringstream s; 
      s << *x;
      return s.str();
    }

  
  
}



  


