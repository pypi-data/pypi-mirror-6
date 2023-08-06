#ifndef _MSC_VER
	#include <stdbool.h>
#else
	#define _Bool char
	#define bool _Bool
	#define true 1
	#define false 0
#endif

#ifndef _MSC_VER
	#define _finite isfinite
	#define _isnan	isnan
#endif

#include "earth/earth.c"


#ifndef _MSC_VER
	#undef _finite
	#undef _isnan
#endif

#include "Python.h"

void init_earth(void) {
	PyObject * mod;
	mod = Py_InitModule("_earth", NULL);
	if (mod == NULL) {
		return;
	}
}
