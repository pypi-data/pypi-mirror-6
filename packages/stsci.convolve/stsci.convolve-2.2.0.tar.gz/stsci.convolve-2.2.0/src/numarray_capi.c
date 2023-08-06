/*
* This is a replacement for the numarray compatibility functions that
* are missing from later versions of numpy.
*
* If you have a C extension that is contained in a single source file:
*   in your module init function:
*       import_array()
*   at the end of your source file:
*       #include "numarray_capi.c"
*
* If you have a C extension that is contained in multiple source files:
*   see http://docs.scipy.org/doc/numpy/reference/c-api.array.html#importing-the-api
*/
#include <Python.h>

#include "numpy/npy_3kcompat.h"

#include <float.h>
#include "libarray.h"

#if (defined(__unix__) || defined(unix)) && !defined(USG)
#include <sys/param.h>
#endif

#if defined(__GLIBC__) || defined(__APPLE__) || defined(__MINGW32__) || (defined(__FreeBSD__) && (__FreeBSD_version >= 502114))
#include <fenv.h>
#elif defined(__CYGWIN__)
#include "numpy/fenv/fenv.h"
#include "numpy/fenv/fenv.c"
#endif

/**********************************************************************/
/*  Numarray Supporting Functions                                     */
/**********************************************************************/
static PyObject *_Error;

int
NA_NumArrayCheck(PyObject *obj) {
    return PyArray_Check(obj);
}

/* satisfies ensures that 'a' meets a set of requirements and matches
   the specified type.
   */
static int
satisfies(PyArrayObject *a, int requirements, NAType t)
{
    int type_ok = (PyArray_DESCR(a)->type_num == t) || (t == tAny);

    if (PyArray_ISCARRAY(a))
        return type_ok;
    if (PyArray_ISBYTESWAPPED(a) && (requirements & NUM_NOTSWAPPED))
        return 0;
    if (!PyArray_ISALIGNED(a) && (requirements & NUM_ALIGNED))
        return 0;
    if (!PyArray_ISCONTIGUOUS(a) && (requirements & NUM_CONTIGUOUS))
        return 0;
    if (!PyArray_ISWRITABLE(a) && (requirements & NUM_WRITABLE))
        return 0;
    if (requirements & NUM_COPY)
        return 0;
    return type_ok;
}



enum {
    BOOL_SCALAR,
    INT_SCALAR,
    LONG_SCALAR,
    FLOAT_SCALAR,
    COMPLEX_SCALAR
};

static int
_NA_maxType(PyObject *seq, int limit)
{
    if (limit > MAXDIM) {
        PyErr_Format( PyExc_ValueError,
                "NA_maxType: sequence nested too deep." );
        return -1;
    }
    if (NA_NumArrayCheck(seq)) {
        switch(PyArray_DESCR(PyArray(seq))->type_num) {
        case tBool:
            return BOOL_SCALAR;
        case tInt8:
        case tUInt8:
        case tInt16:
        case tUInt16:
        case tInt32:
        case tUInt32:
            return INT_SCALAR;
        case tInt64:
        case tUInt64:
            return LONG_SCALAR;
        case tFloat32:
        case tFloat64:
            return FLOAT_SCALAR;
        case tComplex32:
        case tComplex64:
            return COMPLEX_SCALAR;
        default:
            PyErr_Format(PyExc_TypeError,
                    "Expecting a python numeric type, got something else.");
            return -1;
        }
    } else if (PySequence_Check(seq) && !PyBytes_Check(seq)) {
        long i, maxtype=BOOL_SCALAR, slen;

        slen = PySequence_Length(seq);
        if (slen < 0) return -1;

        if (slen == 0) return INT_SCALAR;

        for(i=0; i<slen; i++) {
            long newmax;
            PyObject *o = PySequence_GetItem(seq, i);
            if (!o) return -1;
            newmax = _NA_maxType(o, limit+1);
            if (newmax  < 0)
                return -1;
            else if (newmax > maxtype) {
                maxtype = newmax;
            }
            Py_DECREF(o);
        }
        return maxtype;
    } else {
#if PY_VERSION_HEX >= 0x02030000
        if (PyBool_Check(seq))
            return BOOL_SCALAR;
        else
#endif
#if defined(NPY_PY3K)
            if (PyInt_Check(seq))
                return INT_SCALAR;
            else if (PyLong_Check(seq))
#else
            if (PyLong_Check(seq))
#endif
                return LONG_SCALAR;
            else if (PyFloat_Check(seq))
                return FLOAT_SCALAR;
            else if (PyComplex_Check(seq))
                return COMPLEX_SCALAR;
            else {
                PyErr_Format(PyExc_TypeError,
                        "Expecting a python numeric type, got something else.");
                return -1;
            }
    }
}

static int
NA_maxType(PyObject *seq)
{
    int rval;
    rval = _NA_maxType(seq, 0);
    return rval;
}

NA_NAType(PyObject *seq)
{
    int maxtype = NA_maxType(seq);
    int rval;
    switch(maxtype) {
    case BOOL_SCALAR:
        rval = tBool;
        goto _exit;
    case INT_SCALAR:
    case LONG_SCALAR:
        rval = tLong; /* tLong corresponds to C long int,
                         not Python long int */
        goto _exit;
    case FLOAT_SCALAR:
        rval = tFloat64;
        goto _exit;
    case COMPLEX_SCALAR:
        rval = tComplex64;
        goto _exit;
    default:
        PyErr_Format(PyExc_TypeError,
                "expecting Python numeric scalar value; got something else.");
        rval = -1;
    }
_exit:
    return rval;
}


/**********************************************************************/
/*  Numarray Interface Functions                                      */
/**********************************************************************/

PyArrayObject*
NA_InputArray(PyObject *a, NAType t, int requires)
{
    PyArray_Descr *descr;
    if (t == tAny) descr = NULL;
    else descr = PyArray_DescrFromType(t);
    return (PyArrayObject *)                                    \
        PyArray_CheckFromAny(a, descr, 0, 0, requires, NULL);
}

PyArrayObject *
NA_OutputArray(PyObject *a, NAType t, int requires)
{
    PyArray_Descr *dtype;
    PyArrayObject *ret;

    if (!PyArray_Check(a) || !PyArray_ISWRITEABLE(a)) {
        PyErr_Format(PyExc_TypeError,
                "NA_OutputArray: only writeable arrays work for output.");
        return NULL;
    }

    if (satisfies((PyArrayObject *)a, requires, t)) {
        Py_INCREF(a);
        return (PyArrayObject *)a;
    }
    if (t == tAny) {
        dtype = PyArray_DESCR(a);
        Py_INCREF(dtype);
    }
    else {
        dtype = PyArray_DescrFromType(t);
    }
    ret = (PyArrayObject *)PyArray_Empty(PyArray_NDIM(a), PyArray_DIMS(a),
            dtype, 0);
    ret->flags |= NPY_UPDATEIFCOPY;
    ret->base = a;
    PyArray_FLAGS(a) &= ~NPY_WRITEABLE;
    Py_INCREF(a);
    return ret;
}

/* NA_OptionalOutputArray works like NA_OutputArray, but handles the case
   where the output array 'optional' is omitted entirely at the python level,
   resulting in 'optional'==Py_None.  When 'optional' is Py_None, the return
   value is cloned (but with NAType 't') from 'master', typically an input
   array with the same shape as the output array.
   */
PyArrayObject *
NA_OptionalOutputArray(PyObject *optional, NAType t, int requires,
        PyArrayObject *master)
{
    if ((optional == Py_None) || (optional == NULL)) {
        PyObject *rval;
        PyArray_Descr *descr;
        if (t == tAny) descr=NULL;
        else descr = PyArray_DescrFromType(t);
        rval = PyArray_FromArray(
                master, descr, NUM_C_ARRAY | NUM_COPY | NUM_WRITABLE);
        return (PyArrayObject *)rval;
    } else {
        return NA_OutputArray(optional, t, requires);
    }
}

PyObject*
NA_ReturnOutput(PyObject *out, PyArrayObject *shadow)
{
    if ((out == Py_None) || (out == NULL)) {
        /* default behavior: return shadow array as the result */
        return (PyObject *) shadow;
    } else {
        PyObject *rval;
        /* specified output behavior: return None */
        /* del(shadow) --> out.copyFrom(shadow) */
        Py_DECREF(shadow);
        Py_INCREF(Py_None);
        rval = Py_None;
        return rval;
    }
}
