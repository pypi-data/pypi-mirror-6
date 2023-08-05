/*
  $Id: interpmodule.c,v 1.10 2006/06/16 17:16:55 el_boho Exp $

  Linear interpolation
*/
#include <stdlib.h>
#include "Python.h"

/* #define DEBUG */
#if defined(Py_DEBUG) || defined(DEBUG)
extern void _Py_CountReferences(FILE*);
#define CURIOUS(x) { fprintf(stderr, __FILE__ ":%d ", __LINE__); x; }
#else
#define CURIOUS(x)
#endif
#define MARKER()        CURIOUS(fprintf(stderr, "\n"))
#define DESCRIBE(x)     CURIOUS(fprintf(stderr, "  " #x "=%d\n", x))
#define DESCRIBE_HEX(x) CURIOUS(fprintf(stderr, "  " #x "=%08x\n", x))
#define COUNTREFS()     CURIOUS(_Py_CountReferences(stderr))

#define NEWINTERP

static int _Interp(PyObject *node_data, PyObject *value, PyObject *fnodes, double xi, double yi,
		   double *retval, double *xsi, double *eta){
  PyObject *ia, *ib, *ic;
  double xa, xb, xc;
  double ya, yb, yc;
  double fa, fb, fc;
  double two_area; 
    ia = PyList_GET_ITEM(value, 0); /* borrowed */
    ib = PyList_GET_ITEM(value, 1);
    ic = PyList_GET_ITEM(value, 2);
    xa = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ia), 
							   0), 
					   0));
    ya = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ia), 
							   0), 
					   1));
    xb = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ib), 
							   0), 
					   0));
    yb = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ib), 
							   0), 
					   1));
    xc = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ic), 
							   0), 
					   0));
    yc = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ic), 
							   0), 
					   1));
    two_area = (xb-xa)*(yc-ya) - (xc-xa)*(yb-ya);
    *xsi = ( (yc-ya)*(xi-xa)-(xc-xa)*(yi-ya) )/two_area;
    if(*xsi >= 0.0 && *xsi <= 1.0){
      *eta = (-(yb-ya)*(xi-xa)+(xb-xa)*(yi-ya) )/two_area;
      if(*eta >= 0.0 && *eta <= 1.0-(*xsi)){
	fa = PyFloat_AsDouble(PyList_GET_ITEM(fnodes, (int)PyInt_AS_LONG(ia)));
	fb = PyFloat_AsDouble(PyList_GET_ITEM(fnodes, (int)PyInt_AS_LONG(ib)));
	fc = PyFloat_AsDouble(PyList_GET_ITEM(fnodes, (int)PyInt_AS_LONG(ic)));
	*retval = fa + (*xsi)*(fb-fa) + (*eta)*(fc-fa);
	return 1;
      }	       
    }
    return 0;
}

static PyObject* interpolate_1pt_ex(PyObject *self, PyObject *args){

  PyObject *cell_data;  /* cell connectivity */
  PyObject *node_data; /* node positions and connectivity */
  PyObject *fnodes;  /* function to interpolate defined on nodes */
  PyObject *outside; /* value returned if point is outside domain */
  PyObject *guess;  /* list of indices to check first before exhaustive search */
  PyObject *retlist;
  int nnodes;
  PyObject *key, *value;
  double xi, yi, xsi, eta, retval;
  int pos, gi;

  COUNTREFS();
  
  if(!PyArg_ParseTuple(args,(char *)"OOOddOO", 
		       &cell_data, &node_data, &fnodes, &xi, &yi, &outside, &guess)){ 
    return NULL; 
  } 
  if(!PyDict_Check(cell_data)){
    PyErr_SetString(PyExc_TypeError,
		    "Wrong 1st argument! Dict required (type cell.data).");
    return NULL;
  }
  if(!PyDict_Check(node_data)){
    PyErr_SetString(PyExc_TypeError,
		    "Wrong 2nd argument! Dict required (type node.data).");
    return NULL;
  }
  PyList_Check(fnodes);
  if(!PyList_Check(fnodes)){
    PyErr_SetString(PyExc_TypeError,
		    "Wrong 3rd argument! List required (fnodes).");
    return NULL;
  }

  PyList_Check(guess);
  if(!PyList_Check(guess)){
    PyErr_SetString(PyExc_TypeError,
		    "Wrong 7th argument! List required (guess).");
    return NULL;
  }

  nnodes = PyList_Size(fnodes);
  if(nnodes != PyDict_Size(node_data)){
    PyErr_SetString(PyExc_TypeError,
		    "Incompatible sizes! len(fnodes)!=len(node.data).");
    return NULL;
  }


  pos = 0;
  for(gi=0; gi<PyList_Size(guess); ++gi){ /* check the list of guesses before traversing the full dictionary */
    key=PyList_GetItem(guess, gi);
    value=PyDict_GetItem(cell_data, key);
    if(value){
      if(_Interp(node_data, value, fnodes, xi, yi, &retval, &xsi, &eta)){
	retlist=PyList_New(4);
        PyList_SET_ITEM(retlist, 0, PyFloat_FromDouble(retval));
        Py_INCREF(key);
        PyList_SET_ITEM(retlist, 1, key);
        PyList_SET_ITEM(retlist, 2, PyFloat_FromDouble(xsi));
        PyList_SET_ITEM(retlist, 3, PyFloat_FromDouble(eta));
        return retlist;
      }
    }
  }
  while (PyDict_Next(cell_data, &pos, &key, &value)) {
    if(_Interp(node_data, value, fnodes, xi, yi, &retval, &xsi, &eta)){
      retlist=PyList_New(4);
      PyList_SET_ITEM(retlist, 0, PyFloat_FromDouble(retval));
      Py_INCREF(key);
      PyList_SET_ITEM(retlist, 1, key);
      PyList_SET_ITEM(retlist, 2, PyFloat_FromDouble(xsi));
      PyList_SET_ITEM(retlist, 3, PyFloat_FromDouble(eta));
      return retlist;
    }
  }
  COUNTREFS();
  Py_INCREF(outside);
  return outside;
      
}

static PyObject* interpolate_1pt(PyObject *self, PyObject *args){

  PyObject *cell_data;  /* cell connectivity */
  PyObject *node_data; /* node positions and connectivity */
  PyObject *fnodes;  /* function to interpolate defined on nodes */
  PyObject *outside; /* value returned if point is outside domain */

  int nnodes;
  double xi, yi;
#ifndef NEWINTERP
  PyObject *ia, *ib, *ic;
  double xa, xb, xc;
  double ya, yb, yc;
  double fa, fb, fc;
  double two_area;
#endif
  double xsi, eta, retval;
  PyObject *key, *value;
  int pos;

  COUNTREFS();
  
  if(!PyArg_ParseTuple(args,(char *)"OOOddO", 
		       &cell_data, &node_data, &fnodes, &xi, &yi, &outside)){ 
    return NULL; 
  } 
  if(!PyDict_Check(cell_data)){
    PyErr_SetString(PyExc_TypeError,
		    "Wrong 1st argument! Dict required (type cell.data).");
    return NULL;
  }
  if(!PyDict_Check(node_data)){
    PyErr_SetString(PyExc_TypeError,
		    "Wrong 2nd argument! Dict required (type node.data).");
    return NULL;
  }
  PyList_Check(fnodes);
  if(!PyList_Check(fnodes)){
    PyErr_SetString(PyExc_TypeError,
		    "Wrong 3rd argument! List required (fnodes).");
    return NULL;
  }
  nnodes = PyList_Size(fnodes);
  if(nnodes != PyDict_Size(node_data)){
    PyErr_SetString(PyExc_TypeError,
		    "Incompatible sizes! len(fnodes)!=len(node.data).");
    return NULL;
  }


  pos = 0;
  while (PyDict_Next(cell_data, &pos, &key, &value)) {
    #ifdef NEWINTERP
    if(_Interp(node_data, value, fnodes, xi, yi, &retval, &xsi, &eta)){
      return PyFloat_FromDouble(retval);
    }
    #else /*OLD INTERP */
    ia = PyList_GET_ITEM(value, 0); /* borrowed */
    ib = PyList_GET_ITEM(value, 1);
    ic = PyList_GET_ITEM(value, 2);
    xa = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ia), 
							   0), 
					   0));
    ya = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ia), 
							   0), 
					   1));
    xb = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ib), 
							   0), 
					   0));
    yb = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ib), 
							   0), 
					   1));
    xc = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ic), 
							   0), 
					   0));
    yc = PyFloat_AsDouble(PyTuple_GET_ITEM(
					   PyList_GET_ITEM(
							   PyDict_GetItem(node_data, ic), 
							   0), 
					   1));
    two_area = (xb-xa)*(yc-ya) - (xc-xa)*(yb-ya);
    xsi = ( (yc-ya)*(xi-xa)-(xc-xa)*(yi-ya) )/two_area;
    if(xsi >= 0.0 && xsi <= 1.0){
      eta = (-(yb-ya)*(xi-xa)+(xb-xa)*(yi-ya) )/two_area;
      if(eta >= 0.0 && eta <= 1.0-xsi){
	fa = PyFloat_AsDouble(PyList_GET_ITEM(fnodes, (int)PyInt_AS_LONG(ia)));
	fb = PyFloat_AsDouble(PyList_GET_ITEM(fnodes, (int)PyInt_AS_LONG(ib)));
	fc = PyFloat_AsDouble(PyList_GET_ITEM(fnodes, (int)PyInt_AS_LONG(ic)));
	return PyFloat_FromDouble(fa + xsi*(fb-fa) + eta*(fc-fa));
      }	       
    }
    #endif
  }
  COUNTREFS();
  Py_INCREF(outside);
  return outside;
      
}

static PyMethodDef interp_methods[] = {
  {(char *)"interp_ex", interpolate_1pt_ex, METH_VARARGS, (char *)"interp(cell.data, node.data, fnodes, xi, yi) -- return the linear interpolation of fnodes at xi, yi"}, 
  {(char *)"interp", interpolate_1pt, METH_VARARGS, (char *)"interp(cell.data, node.data, fnodes, xi, yi) -- return the linear interpolation of fnodes at xi, yi"}, 
  {NULL,NULL}
};

void initinterp(){
  Py_InitModule((char *)"interp", interp_methods);
}
