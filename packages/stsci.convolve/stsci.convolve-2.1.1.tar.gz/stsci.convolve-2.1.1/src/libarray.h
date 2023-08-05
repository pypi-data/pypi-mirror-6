/* Compatibility with numarray, modified for use with convolve only
 */
#ifndef LIBARRAY_H
#define LIBARRAY_H

#include <numpy/arrayobject.h>
#include "arraybase.h"
#include "nummacro.h"


  /* This section is used when compiling libarray */
int NA_NumArrayCheck(PyObject *obj);

NAType NA_NAType(PyObject *);

PyObject*  NA_ReturnOutput  (PyObject*,PyArrayObject*);

PyArrayObject*  NA_InputArray  (PyObject*,NAType,int);

PyArrayObject*  NA_OutputArray  (PyObject*,NAType,int);

PyArrayObject*  NA_OptionalOutputArray  (PyObject*,NAType,int,PyArrayObject*);


#endif