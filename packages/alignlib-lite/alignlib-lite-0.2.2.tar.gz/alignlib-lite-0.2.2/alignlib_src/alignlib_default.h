// define MACROS for creating default objects

#ifndef ALIGNLIB_DEFAULT_H_
#define ALIGNLIB_DEFAULT_H_

/** macro do define get/set default by querying default toolkit object
 * @param handle: the handle class
 * @param set: the name of the set function
 * @param get: the name of the get function
 */
#define IMPLEMENT_DEFAULT(handle,get,set,gget,sset) \
	handle get () { return getDefaultToolkit()->gget(); } \
	void set ( const handle & v ) { getDefaultToolkit()->sset(v); }

/** macro do define get/set default
 * @param h: the handle class
 * @param set: the name of the set function
 * @param get: the name of the get function
 */
#define DEFINE_DEFAULT(handle,get,set) \
	handle get(); \
	void set( const handle &)

/** macro do define get/set default
 * @param handle: the handle class
 * @param init: the initialization function
 * @param set: the name of the set function
 * @param get: the name of the get function
 */
#define IMPLEMENT_STATIC_DEFAULT(handle,init,get,set,df) \
		static handle df( init ); \
        handle get () { return df; } \
        void set ( const handle & v ) { df = v; }

#endif /*ALIGNLIB_DEFAULT_H_*/
