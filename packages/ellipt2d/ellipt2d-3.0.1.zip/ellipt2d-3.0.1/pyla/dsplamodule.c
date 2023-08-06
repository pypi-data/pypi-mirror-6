/******************************************************************************
   $Id: dsplamodule.c,v 1.10 2002/06/11 13:07:38 pletzer Exp $

   Sparse matrix algebra module: real numbers (doubles).
******************************************************************************/

#include <stdlib.h>
#include "Python.h"

static PyObject* dspla_dict2VIJ(PyObject *self, PyObject *args){

  /**
   * Convert sparse matrix dictionary to (vals, i, j) format
   */

  int nvals;
  PyObject *sparse_data;
  PyObject *values;
  PyObject *row_indices;
  PyObject *col_indices;
  PyObject *ij, *datum;
  int pos, count;

  if(!PyArg_ParseTuple(args,(char *)"O", 
		       &sparse_data)){ 
    return NULL; 
  } 
  if(!PyDict_Check(sparse_data)){
    PyErr_SetString(PyExc_TypeError,
		    "dict2VIJ::Wrong 1st argument! sparse matrix dictionary required.");
    return NULL;
  }
    
  nvals = PyDict_Size(sparse_data);

  values = PyTuple_New(nvals); /* rew_ref (must destroy in delete method) */
  row_indices = PyTuple_New(nvals); /* new_ref (must destroy in delete method) */
  col_indices = PyTuple_New(nvals); /* new_ref (must destroy in delete method) */
  
  pos = 0;
  count = 0;
  while(PyDict_Next(sparse_data, &pos, &ij, &datum)){
    PyTuple_SET_ITEM(values, count, datum);
    PyTuple_SET_ITEM(row_indices, count, 
		     PyTuple_GET_ITEM(ij, 0)); /* borr_ref */
    PyTuple_SET_ITEM(col_indices, count, 
		     PyTuple_GET_ITEM(ij, 1)); /* borr_ref */
    count++;
  }
  
  return Py_BuildValue((char *)"(OOO)", values, row_indices, col_indices);
}

static PyObject* dspla_PlusCTimesY(PyObject *self, PyObject *args){
  
  /* X += c*Y */
  
  PyObject *vector1;
  PyObject *constant;
  PyObject *vector2;
  int n, i;
  if(!PyArg_ParseTuple(args,(char *)"OOO", 
		       &vector1, &constant, &vector2)){ 
    return NULL; 
  } 
  if(!PyList_Check(vector1)){
    PyErr_SetString(PyExc_TypeError,
	 "PlusCTimesY::Wrong 1st argument! List required (vector1).");
    return NULL;
  }
  if(!PyFloat_Check(constant) && !PyComplex_Check(constant)){
    PyErr_SetString(PyExc_TypeError,
	 "PlusCTimesY::Wrong 2nd argument! Float or Complex required (constant).");
    return NULL;
  }
  if(!PyList_Check(vector2)){
    PyErr_SetString(PyExc_TypeError,
	 "PlusCTimesY::Wrong 3rd argument! List required (vector2).");
    return NULL;
  }
  n = PyList_Size(vector1);
  if(PyList_Size(vector2) != n){
    PyErr_Format(PyExc_RuntimeError,
		    "PlusCTimesY::Size mismatch between vectors! %d %d ",
		 n, PyList_Size(vector2));
    return NULL;
  }
  for(i=0; i<n; ++i){
    PyList_SET_ITEM(vector1, i,
		    PyNumber_InPlaceAdd(
					PyList_GET_ITEM(vector1,i),
					PyNumber_Multiply(
							  constant,
							  PyList_GET_ITEM(vector2,i)
							  )
					)
		    );
  }
  
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* dspla_TimesCPlusY(PyObject *self, PyObject *args){
  
  /* X *=c; X+=Y */
  
  PyObject *vector1;
  PyObject *constant;
  PyObject *vector2;
  int n, i;
  if(!PyArg_ParseTuple(args,(char *)"OOO", 
		       &vector1, &constant, &vector2)){ 
    return NULL; 
  } 
  if(!PyList_Check(vector1)){
    PyErr_SetString(PyExc_TypeError,
	 "TimesCPlusY::Wrong 1st argument! List required (vector1).");
    return NULL;
  }
  if(!PyFloat_Check(constant) && !PyComplex_Check(constant)){
    PyErr_SetString(PyExc_TypeError,
	 "TimesCPlusY::Wrong 2nd argument! Float or Complex required (constant).");
    return NULL;
  }
  if(!PyList_Check(vector2)){
    PyErr_SetString(PyExc_TypeError,
	 "TimesCPlusY::Wrong 3rd argument! List required (vector2).");
    return NULL;
  }
  n = PyList_Size(vector1);
  if(PyList_Size(vector2) != n){
    PyErr_Format(PyExc_RuntimeError,
		    "TimesCPlusY::Size mismatch between vectors! %d %d",
		 n, PyList_Size(vector2));
    return NULL;
  }
  for(i=0; i<n; ++i){
    PyList_SET_ITEM(vector1, i, 
		      PyNumber_InPlaceMultiply(
				       PyList_GET_ITEM(vector1,i), 
				       constant
				       )
		     );
    PyList_SET_ITEM(vector1, i, 
		     PyNumber_InPlaceAdd(
				       PyList_GET_ITEM(vector1,i), 
				       PyList_GET_ITEM(vector2,i)
				       )
		     );
  }
  
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* dspla_YDotX(PyObject *self, PyObject *args){
  
  /* vector multiplication */

  PyObject *vector1;
  PyObject *vector2;
  int n, i;
  PyObject *result;

  if(!PyArg_ParseTuple(args,(char *)"OO", 
		       &vector1, &vector2)){ 
    return NULL; 
  } 
  if(!PyList_Check(vector1)){
    PyErr_SetString(PyExc_TypeError,
	 "YDotX::Wrong 1st argument! List required (vector1).");
    return NULL;
  }
  if(!PyList_Check(vector2)){
    PyErr_SetString(PyExc_TypeError,
	 "YDotX::Wrong 2nd argument! List required (vector2).");
    return NULL;
  }

  n = PyList_Size(vector1);
  if(PyList_Size(vector2) != n){
    PyErr_Format(PyExc_RuntimeError,
		    "YDotX::Size mismatch between vectors! %d %d ",
		 n, PyList_Size(vector2));
    return NULL;
  }
  
  result = PyFloat_FromDouble((double) 0.);
  for(i=0; i<n; ++i){
    result = PyNumber_InPlaceAdd(result, 
				  PyNumber_Multiply(
						    PyList_GET_ITEM(vector1,i),
						    PyList_GET_ITEM(vector2,i)
						    )
				  );
  }
  
  return result;
}

static PyObject* dspla_YStarDotX(PyObject *self, PyObject *args){
  
  /* vector multiplication */

  PyObject *vector1;
  PyObject *vector2;
  PyObject *val;
  double re, im;
  int n, i;
  PyObject *result;
  

  if(!PyArg_ParseTuple(args,(char *)"OO", 
		       &vector1, &vector2)){ 
    return NULL; 
  } 
  if(!PyList_Check(vector1)){
    PyErr_SetString(PyExc_TypeError,
	 "YStarDotX::Wrong 1st argument! List required (vector1).");
    return NULL;
  }
  if(!PyList_Check(vector2)){
    PyErr_SetString(PyExc_TypeError,
	 "YStarDotX::Wrong 2nd argument! List required (vector2).");
    return NULL;
  }

  n = PyList_Size(vector1);
  if(PyList_Size(vector2) != n){
    PyErr_Format(PyExc_RuntimeError,
		    "YStarDotX::Size mismatch between vectors! %d %d ",
		 n, PyList_Size(vector2));
    return NULL;
  }
  
  result = PyComplex_FromDoubles((double) 0.0, (double) 0.0) ;
  for(i=0; i<n; ++i){
    val = PyList_GET_ITEM(vector1,i);
    re = PyComplex_RealAsDouble(val);
    im = PyComplex_ImagAsDouble(val);
    result = PyNumber_InPlaceAdd(result, 
				  PyNumber_Multiply(
						    PyComplex_FromDoubles(re, -im),
						    PyList_GET_ITEM(vector2,i)
						    )
				  );
  }
  
  return result;
}

static PyObject* dspla_ADotX(PyObject *self, PyObject *args){

  /* A . x matrix multiplication */

  PyObject *vij;
  PyObject *vector;
  PyObject *new_vector;
  PyObject *datum_o;
  PyObject *avals, *arows, *acols;
  int nvals, i, n;
  long row, col;

  if(!PyArg_ParseTuple(args,(char *)"OO", 
		       &vij, &vector)){ 
    return NULL; 
  } 
  if(!PyTuple_Check(vij)){
    PyErr_SetString(PyExc_TypeError,
	 "ADotX::Wrong 1st argument! Tuple required ((vals),(rows),(cols)).");
    return NULL;
  }
  if(!PyList_Check(vector)){
    PyErr_SetString(PyExc_TypeError,
	  "ADotX::Wrong 2nd argument! List required (vector).");
    return NULL;
  }

  n = PyList_Size(vector);
  new_vector = PyList_New(n); /* rew_ref */
  /* initialize */
  for(i = 0; i < n; ++i){
    datum_o = PyFloat_FromDouble((double)0.); /* new ref */
    PyList_SetItem(new_vector, i, datum_o);
    ///Py_DECREF(datum_o); /* - */
  }
  
  avals = PyTuple_GET_ITEM(vij, 0);
  if(!PyTuple_Check(avals)){
    PyErr_SetString(PyExc_TypeError,
		    "ADotX::Item 0 of vij should be a tuple (avals)!");
    return NULL;
  }
  arows = PyTuple_GET_ITEM(vij, 1);
  if(!PyTuple_Check(arows)){
    PyErr_SetString(PyExc_TypeError,
		    "ADotX::Item 1 of vij should be a tuple (arows)!");
    return NULL;
  }
  acols = PyTuple_GET_ITEM(vij, 2);
  if(!PyTuple_Check(acols)){
    PyErr_SetString(PyExc_TypeError,
		    "ADotX::Item 2 of vij should be a tuple (acols)!");
    return NULL;
  }

  nvals = PyTuple_Size(avals);

  for(i = 0; i < nvals; ++i){
    row = PyInt_AS_LONG(PyTuple_GET_ITEM(arows, i));
    col = PyInt_AS_LONG(PyTuple_GET_ITEM(acols, i));
    
    datum_o = PyList_GET_ITEM(new_vector, (int)row); /* borrowed ref */
    /* wi += aij * vj */
    datum_o = PyNumber_InPlaceAdd(datum_o, 
				  PyNumber_Multiply(
						    PyTuple_GET_ITEM(avals,i),
						    PyList_GET_ITEM(vector, col)
						    )
				  );
    PyList_SET_ITEM(new_vector, row, datum_o);
    ///Py_DECREF(datum_o); /* - */
  }  
  return new_vector;
}

static PyObject* dspla_XStarDotA(PyObject *self, PyObject *args){

  /* A . x matrix multiplication */

  PyObject *vij;
  PyObject *vector;
  PyObject *new_vector;
  PyObject *datum_o;
  PyObject *avals, *arows, *acols;
  int nvals, i, n;
  long row, col;
  PyObject *val;
  double re, im;

  if(!PyArg_ParseTuple(args,(char *)"OO", 
		       &vector, &vij)){ 
    return NULL; 
  } 
  if(!PyList_Check(vector)){
    PyErr_SetString(PyExc_TypeError,
	  "XStarDotA::Wrong 1st argument! List required (vector).");
    return NULL;
  }
  if(!PyTuple_Check(vij)){
    PyErr_SetString(PyExc_TypeError,
	 "XStarDotA::Wrong 2nd argument! Tuple required ((vals),(rows),(cols)).");
    return NULL;
  }

  n = PyList_Size(vector);
  new_vector = PyList_New(n); /* rew_ref */
  /* initialize */
  for(i = 0; i < n; ++i){
    datum_o = PyComplex_FromDoubles((double)0., (double) 0.); /* new ref */
    PyList_SetItem(new_vector, i, datum_o);
    ///Py_DECREF(datum_o); /* - */
  }
  
  avals = PyTuple_GET_ITEM(vij, 0);
  if(!PyTuple_Check(avals)){
    PyErr_SetString(PyExc_TypeError,
		    "XStarDotA::Item 0 of vij should be a tuple (avals)!");
    return NULL;
  }
  arows = PyTuple_GET_ITEM(vij, 1);
  if(!PyTuple_Check(arows)){
    PyErr_SetString(PyExc_TypeError,
		    "XStarDotA::Item 1 of vij should be a tuple (arows)!");
    return NULL;
  }
  acols = PyTuple_GET_ITEM(vij, 2);
  if(!PyTuple_Check(acols)){
    PyErr_SetString(PyExc_TypeError,
		    "XStarDotA::Item 2 of vij should be a tuple (acols)!");
    return NULL;
  }

  nvals = PyTuple_Size(avals);

  for(i = 0; i < nvals; ++i){
    row = PyInt_AS_LONG(PyTuple_GET_ITEM(arows, i));
    col = PyInt_AS_LONG(PyTuple_GET_ITEM(acols, i));
    
    datum_o = PyList_GET_ITEM(new_vector, col); /* borrowed ref */
    /* wi += vj^* * aji * */
    val = PyList_GET_ITEM(vector, row);
    re = PyComplex_RealAsDouble(val);
    im = PyComplex_ImagAsDouble(val);
    datum_o = PyNumber_InPlaceAdd(datum_o, 
				  PyNumber_Multiply(
						    PyComplex_FromDoubles(re, -im),
						    PyTuple_GET_ITEM(avals,i)
						    )
				  );
    PyList_SET_ITEM(new_vector, col, datum_o);
    ///Py_DECREF(datum_o); /* - */
  }  
  return new_vector;
}

static PyObject* dspla_XDivideY(PyObject *self, PyObject *args){

  /* x/y elementwise division */

  PyObject *vector1;
  PyObject *vector2;
  PyObject *new_vector;
  int i, n;

  if(!PyArg_ParseTuple(args,(char *)"OO", 
		       &vector1, &vector2)){ 
    return NULL; 
  } 
  if(!PyList_Check(vector1)){
    PyErr_SetString(PyExc_TypeError,
		    "XDivideY::Wrong 1st argument! List required (vector1).");
    return NULL;
  }
  if(!PyList_Check(vector2)){
    PyErr_SetString(PyExc_TypeError,
		    "XDivideY::Wrong 2nd argument! List required (vector2).");
    return NULL;
  }

  n = PyList_Size(vector1);
  if(n != PyList_Size(vector2)){
    PyErr_Format(PyExc_RuntimeError,
		    "XDivideY::Vector size mismatch! %d %d", n, PyList_Size(vector2));
    return NULL;    
  }
  new_vector = PyList_New(n); /* rew_ref */

  for(i = 0; i < n; ++i){
    PyList_SetItem(new_vector, i, 
		   PyNumber_Divide(
                          PyList_GET_ITEM(vector1, i),
			  PyList_GET_ITEM(vector2, i)
			  )
		   );
  }
  
  return new_vector;
}


static PyObject* dspla_deleteVIJ(PyObject *self, PyObject *args){

  /* Delete: (vals, i, j) data */

  PyObject *vij;
  PyObject *avals;
  PyObject *acols;
  PyObject *arows;
  int n, i;

  if(!PyArg_ParseTuple(args,(char *)"O", 
		       &vij)){ 
    return NULL; 
  } 
  if(!PyTuple_Check(vij)){
    PyErr_SetString(PyExc_TypeError,
		    "deleteVIJ::Wrong 1st argument! Tuple required ((vals, rows, cols)).");
    return NULL;
  }

  avals = PyTuple_GET_ITEM(vij, 0);
  if(!PyTuple_Check(avals)){
    PyErr_SetString(PyExc_TypeError,
		    "deleteVIJ::Item 0 of vij should be a tuple (avals)!");
    return NULL;
  }
  arows = PyTuple_GET_ITEM(vij, 1);
  if(!PyTuple_Check(arows)){
    PyErr_SetString(PyExc_TypeError,
		    "deleteVIJ::Item 1 of vij should be a tuple (arows)!");
    return NULL;
  }
  acols = PyTuple_GET_ITEM(vij, 2);
  if(!PyTuple_Check(acols)){
    PyErr_SetString(PyExc_TypeError,
		    "deleteVIJ::Item 2 of vij should be a tuple (acols)!");
    return NULL;
  }


  n = PyTuple_Size(avals);
  for(i=0; i<n ; ++i) {
    Py_DECREF(PyTuple_GET_ITEM(avals, i));
    Py_DECREF(PyTuple_GET_ITEM(arows, i));
    Py_DECREF(PyTuple_GET_ITEM(acols, i));
  }
  Py_DECREF(avals);
  Py_DECREF(acols);
  Py_DECREF(arows);

  Py_INCREF(Py_None);
  return Py_None;
}


static PyMethodDef dspla_methods[] = {
  {(char *)"toVIJ", dspla_dict2VIJ, 1, (char *)"dict2VIJ(A) -- Return the (vals, rows, cols) representation of a sparse matrix dictionary A"},
  {(char *)"ADotX", dspla_ADotX, 1, (char *)"Sparse matrix (vals, rows, cols) dot vector X"},
  {(char *)"XStarDotA", dspla_XStarDotA, 1, (char *)"Vector X^* dot Sparse matrix (vals, rows, cols)"},
  {(char *)"YDotX", dspla_YDotX, 1, (char *)"Vector Y dot vector X"},
  {(char *)"YStarDotX", dspla_YStarDotX, 1, (char *)"Vector Y^* dot vector X"},
  {(char *)"PlusCTimesY", dspla_PlusCTimesY, 1, (char *)"PlusCTimesY(X,c,Y): Vector X -> X + c*Y"},
  {(char *)"TimesCPlusY", dspla_TimesCPlusY, 1, (char *)"TimesCPlusY(X,c,Y): Vector X -> c*X + Y"},
  {(char *)"XDivideY", dspla_XDivideY, 1, (char *)"XDivideY(X,Y): Elementwise divison X/Y"},
  {(char *)"deleteVIJ", dspla_deleteVIJ, 1, (char *)"Destroy sparse matrix vij."},
  {NULL,NULL}
};

void initdspla(){
  (void) Py_InitModule((char *)"dspla",dspla_methods);
}
