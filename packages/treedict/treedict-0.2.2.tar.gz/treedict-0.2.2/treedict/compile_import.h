#ifndef _DEBUG_IMPORT_H_
#define _DEBUG_IMPORT_H_

#ifdef NDEBUG
#define DEBUG_MODE 0
#else
#define DEBUG_MODE 1
#endif

#ifdef PYTHON3
#define IS_PYTHON2 0
#else
#define IS_PYTHON2 1
#endif

#endif /* _DEBUG_IMPORT_H_ */
