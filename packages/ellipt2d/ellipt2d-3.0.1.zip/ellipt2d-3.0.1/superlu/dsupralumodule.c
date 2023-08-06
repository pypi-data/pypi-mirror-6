/*

$Id: dsupralumodule.c,v 1.6 2005/12/01 21:44:12 pletzer Exp $

Python interface module to double version of SuperLU

*/

#include <stdlib.h>
#include "Python.h"

#include "dsupralu_type.h"

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

typedef void (*destr)(void *);

typedef struct {
 double *vals;
 int *row_ind;
 int *col_ptr;
 int n;
 int nnz;
} dccs_type;

void destroy_dccs(dccs_type *ptr){
#if defined(Py_DEBUG) || defined(DEBUG)
 printf("now destroying dccs_type\n");
#endif
 SUPERLU_FREE(ptr->vals);
 SUPERLU_FREE(ptr->row_ind);
 SUPERLU_FREE(ptr->col_ptr);
 SUPERLU_FREE(ptr);
}

void destroy_dsupralu_type(dsupralu_sparse_type *ptr){
 int info;
#if defined(Py_DEBUG) || defined(DEBUG)
 printf("now destroying dsupralu_sparse_type\n");
#endif
 dsupralu_del_(&ptr, &info);
 if(info !=0 ){
   PyErr_Format(PyExc_TypeError,
         "dsupralu_del_ returned INFO=%d.", info);
 }
}

int compare_ij(const int ija[], const int ijb[]){
  int ia, ja, ib, jb;
  ia = ija[0];
  ja = ija[1];
  ib = ijb[0];
  jb = ijb[1];
  if(ja < jb) return -1;
  if(ja > jb) return +1;
  /* ja == jb */
  if(ia < ib) return -1;
  return +1;
}

void d2CCS(int n, PyObject *amat,
  double *vals, int *row_ind, int *col_ptr){

 /*
    Convert Dict type to Compressed column storage format.
 */

  PyObject *element, *ij;
  int k = 0, j_last;
  int i, j, nnz;
  int *ij_array;

  PyObject *keys = PyDict_Keys(amat);

  if(keys){
   
    nnz = PyList_Size(keys);
   
    ij_array = (int *) malloc(sizeof(int)*nnz*2);

    for(k = 0; k < nnz; ++k){
      ij = PyList_GET_ITEM(keys, k);
      i = (int) PyInt_AS_LONG(PyTuple_GET_ITEM(ij, 0));
      j = (int) PyInt_AS_LONG(PyTuple_GET_ITEM(ij, 1));
      ij_array[2*k  ] = i;
      ij_array[2*k+1] = j;
    }

    qsort(ij_array, nnz, sizeof(int)*2, &compare_ij);

    j_last = -1;
    for(k = 0; k < nnz; ++k){
      i = ij_array[2*k  ];
      j = ij_array[2*k+1];
      row_ind[k] = i;
      ij = Py_BuildValue("(i,i)", i, j);
      element = PyDict_GetItem(amat, ij);
      Py_DECREF(ij);
      vals[k] = PyFloat_AsDouble(element);
      if(j > j_last){
	col_ptr[j] = k;
	j_last = j;
      }
    }
    col_ptr[n] = k;

    Py_DECREF(keys);
    free(ij_array);
  }
}

static PyObject *
dsupralu_NEW(PyObject *self, PyObject *args){

 /*
   Constructor. Returns two opaque handles:
   (1) supralu structure
   (2) Compressed Column Storage based sparse matrix
 */

 PyObject *address, *dccs_add, *result;
 dsupralu_sparse_type *object;
 dccs_type *dccs_obj;
 PyObject *amat_dict;
 int nnz, n, info;

 COUNTREFS();
 if(!PyArg_ParseTuple(args,(char *)"Oi",
               &amat_dict, &n)){
   return NULL;
 }
 if(!PyDict_Check(amat_dict)){
   PyErr_SetString(PyExc_TypeError,
            "Wrong 1st argument! Dict required (sparse matrix).");
   return NULL;
 }  
 nnz = PyDict_Size(amat_dict);
 if ( !(dccs_obj = SUPERLU_MALLOC(sizeof(dccs_type))) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for dccs_obj.");
   return NULL;
 }
 dccs_obj->n = n;
 dccs_obj->nnz = nnz;  
 if ( !(dccs_obj->vals = doubleMalloc(nnz)) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for vals[].");
   return NULL;
 }
 if ( !(dccs_obj->row_ind = intMalloc(nnz)) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for row_ind[].");
   return NULL;
 }
 /* create compressed column storage object hand hold on to it */
 if ( !(dccs_obj->col_ptr = intMalloc(n+1)) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for col_ptr[].");
   return NULL;
 }

 /* convert to compressed column storage */
 d2CCS(n, amat_dict, dccs_obj->vals, dccs_obj->row_ind, dccs_obj->col_ptr);
 //printf("c2\n");
 dsupralu_new_(&object,
        dccs_obj->vals, dccs_obj->row_ind, dccs_obj->col_ptr,
        &nnz, &n, &info);
 if(info !=0 ){
   PyErr_Format(PyExc_TypeError,
         "dsupralu_new_ returned INFO=%d.", info);
   return NULL;
 }
 
 /* Return 2 opaque handles */
 address = PyCObject_FromVoidPtr(object, (destr) destroy_dsupralu_type);
 dccs_add = PyCObject_FromVoidPtr(dccs_obj, (destr) destroy_dccs);
 result = Py_BuildValue("(OO)", address, dccs_add);
 Py_DECREF(dccs_add);
 Py_DECREF(address);
 return result;
}

static PyObject *
dsupralu_VECTOR_DOT_MATRIX(PyObject *self, PyObject *args){

 /*
    vector . matrix

 */

 PyObject *address;
 PyObject *vector_list, *result, *element;
 double *vector, *res;
 PyObject *a_double;
 dsupralu_sparse_type *object;
 int n, i, info;
 
 if(!PyArg_ParseTuple(args,(char *)"OO",
               &address, &vector_list)){
   return NULL;
 }
 if(!PyCObject_Check(address)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 1st argument! CObject required (dsupralu_sparse_type handle).");
   return NULL;
 }  
 if(!PyList_Check(vector_list)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 2nd argument! List required (vector_list).");
   return NULL;
 }
 
 n = PySequence_Length(vector_list);
 if( !(vector = doubleMalloc(n)) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for vector[].");
   return NULL;
 }
 if( !(res = doubleMalloc(n)) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for res[].");
   return NULL;
 }
 for(i=0; i<n; ++i) {
   element = PySequence_Fast_GET_ITEM(vector_list, i); /* borrows a ref */
   vector[i] = PyFloat_AsDouble(element);
 }

 object = PyCObject_AsVoidPtr(address);
 dsupralu_vector_dot_matrix_(&object, vector, res, &info);
 if(info !=0 ){
   PyErr_Format(PyExc_TypeError,
         "dsupralu_vector_dot_matrix_ returned INFO=%d.", info);
   return NULL;
 }

 result = PyList_New(n);
 for(i=0; i<n; ++i) {
   a_double = PyFloat_FromDouble( res[i] ); /* + */
   PyList_SET_ITEM(result, i, a_double); /* steals a ref */
 }
 
 SUPERLU_FREE(vector);
 SUPERLU_FREE(res);

 return result;  
}


static PyObject *
dsupralu_MATRIX_DOT_VECTOR(PyObject *self, PyObject *args){

 /*
    matrix . vector

 */

 PyObject *address;
 PyObject *vector_list, *result, *element;
 double *vector, *res;
 PyObject *a_double;
 dsupralu_sparse_type *object;
 int n, i, info;
 
 if(!PyArg_ParseTuple(args,(char *)"OO",
               &address, &vector_list)){
   return NULL;
 }
 if(!PyCObject_Check(address)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 1st argument! CObject required (dsupralu_sparse_type handle).");
   return NULL;
 }  
 if(!PyList_Check(vector_list)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 2nd argument! List required (vector_list).");
   return NULL;
 }
 
 n = PySequence_Length(vector_list);
 if( !(vector = doubleMalloc(n)) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for vector[].");
   return NULL;
 }
 if( !(res = doubleMalloc(n)) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for res[].");
   return NULL;
 }
 for(i=0; i<n; ++i) {
   element = PySequence_Fast_GET_ITEM(vector_list, i); /* borrows a ref */
   vector[i] = PyFloat_AsDouble(element);
 }

 object = PyCObject_AsVoidPtr(address);
 dsupralu_matrix_dot_vector_(&object, vector, res, &info);
 if(info !=0 ){
   PyErr_Format(PyExc_TypeError,
         "dsupralu_matrix_dot_vector_ returned INFO=%d.", info);
   return NULL;
 }

 result = PyList_New(n);
 for(i=0; i<n; ++i) {
   a_double = PyFloat_FromDouble( res[i] ); /* + */
   PyList_SET_ITEM(result, i, a_double); /* steals a ref */
 }
 
 SUPERLU_FREE(vector);
 SUPERLU_FREE(res);

 return result;  
}

static PyObject *
dsupralu_VECTOR_DOT_MATRIX_DOT_VECTOR(PyObject *self, PyObject *args){

 /*
    vector1 . matrix . vector2

 */

 PyObject *address;
 PyObject *vector1_list, *vector2_list, *element;
 double *vector1, *vector2;
 double res;
 dsupralu_sparse_type *object;
 int n1, n2, i, info;
 
 if(!PyArg_ParseTuple(args,(char *)"OOO",
               &address, &vector1_list, &vector2_list)){
   return NULL;
 }
 if(!PyCObject_Check(address)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 1st argument! CObject required (dsupralu_sparse_type handle).");
   return NULL;
 }  
 if(!PyList_Check(vector1_list)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 2nd argument! List required (vector1_list).");
   return NULL;
 }
 if(!PyList_Check(vector2_list)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 3rd argument! List required (vector2_list).");
   return NULL;
 }
 
 n1 = PySequence_Length(vector1_list);
 n2 = PySequence_Length(vector2_list);
 if( !(vector1 = doubleMalloc(n1)) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for vector1[].");
   return NULL;
 }
 if( !(vector2 = doubleMalloc(n2)) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for vector2[].");
   return NULL;
 }

 for(i=0; i<n1; ++i) {
   element = PySequence_Fast_GET_ITEM(vector1_list, i); /* borrows a ref */
   vector1[i] = PyFloat_AsDouble(element);
 }
 for(i=0; i<n2; ++i) {
   element = PySequence_Fast_GET_ITEM(vector2_list, i); /* borrows a ref */
   vector2[i] = PyFloat_AsDouble(element);
 }

 object = PyCObject_AsVoidPtr(address);
 dsupralu_vector_dot_matrix_dot_vector_(&object, vector1, vector2, &res, &info);
 if(info !=0 ){
   PyErr_Format(PyExc_TypeError,
         "dsupralu_vector_dot_matrix_dot_vector_ returned INFO=%d.", info);
   return NULL;
 }

 SUPERLU_FREE(vector1);
 SUPERLU_FREE(vector2);

 return PyFloat_FromDouble(res);
}

static PyObject *
dsupralu_COLPERM(PyObject *self, PyObject *args){

 /*
    Compute column permutation vector. Takes the
    supralu structure handle as input. Call this
    routine prior to performing the LU decomposition.
 */

 PyObject *address;
 int permc_spec, info;
 dsupralu_sparse_type *object;

 if(!PyArg_ParseTuple(args,(char *)"Oi",
               &address, &permc_spec)){
   return NULL;
 }
 if(!PyCObject_Check(address)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 1st argument! CObject required (dsupralu_sparse_type handle).");
   return NULL;
 }  
 /*
   permc_spec=0 natural ordering
   permc_spec=1 minimum degree on structure of A'*A
   permc_spec=2 minimum degree on structure of A'+A
   permc_spec=3 approximate minimum degree for unsymmetric matrices
 */    
 permc_spec = ( permc_spec > 0 ? permc_spec: 2 );
 permc_spec = ( permc_spec <=3 ? permc_spec: 2 );
 object = PyCObject_AsVoidPtr(address);
 dsupralu_colperm_(&object, &permc_spec, &info);
 if(info !=0 ){
   PyErr_Format(PyExc_TypeError,
         "dsupralu_colperm_ returned INFO=%d.", info);
   return NULL;
 }

 return Py_BuildValue("");
}

static PyObject *
dsupralu_LU(PyObject *self, PyObject *args){

 /*
   Perform the LU decomposition. Call this after
   dsupralu_COLPERM. Takes the supralu structure
   handle as input.
 */

 PyObject *address;
 int info;

 dsupralu_sparse_type *object;
 if(!PyArg_ParseTuple(args,(char *)"O",
               &address)){
   return NULL;
 }
 if(!PyCObject_Check(address)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 1st argument! CObject required (dsupralu_sparse_type handle).");
   return NULL;
 }  
 object = PyCObject_AsVoidPtr(address);
 dsupralu_lu_(&object, &info);
 if(info !=0 ){
   PyErr_Format(PyExc_TypeError,
         "dsupralu_lu_ returned INFO=%d.", info);
   return NULL;
 }

 return Py_BuildValue("");
}

static PyObject *
dsupralu_DET(PyObject *self, PyObject *args){
 
 /* Return the determinant as res_mantissa * 2^res_exponent */

 PyObject *address;
 dsupralu_sparse_type *object;
 double res_mantissa;
 int res_exponent;
 int info;

 if(!PyArg_ParseTuple(args,(char *)"O",
               &address)){
   return NULL;
 }
 if(!PyCObject_Check(address)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 1st argument! CObject required (dsupralu_sparse_type handle).");
   return NULL;
 }  

 object = PyCObject_AsVoidPtr(address);
 dsupralu_determinant_(&object, &res_mantissa, &res_exponent, &info);

 return Py_BuildValue("(di)", res_mantissa, res_exponent);
}

static PyObject *
dsupralu_SOLVE(PyObject *self, PyObject *args){

 /*
    Solve the linear system. Invoke this after calling
    dsupralu_COLPERM and dsupralu_LU. Takes the
    supralu structure handle as input.
 */

 PyObject *address;
 PyObject *rhs_list;
 PyObject *element;
 double *rhs;
 PyObject *result;
 PyObject *a_double;
 dsupralu_sparse_type *object;
 int info;
 int i, n;

 if(!PyArg_ParseTuple(args,(char *)"OO",
               &address, &rhs_list)){
   return NULL;
 }
 if(!PyCObject_Check(address)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 1st argument! CObject required (dsupralu_sparse_type handle).");
   return NULL;
 }  
 if(!PySequence_Check(rhs_list)){
   PyErr_SetString(PyExc_TypeError,
            "Wrong 2nd argument! Sequence required (rhs_list).");
   return NULL;
 }  
 n = PySequence_Length(rhs_list);
 if( !(rhs = doubleMalloc(n)) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for rhs[].");
   return NULL;
 }
 for(i=0; i<n; ++i){
   element = PySequence_Fast_GET_ITEM(rhs_list, i);
   rhs[i] = PyFloat_AsDouble(element);
 }
 object = PyCObject_AsVoidPtr(address);
 dsupralu_solve_(&object, rhs, &info);
 if(info !=0 ){
   PyErr_Format(PyExc_TypeError,
         "dsupralu_solve_ returned INFO=%d.", info);
   return NULL;
 }
 result = PyList_New(n);
 for(i=0; i<n; ++i) {
   a_double = PyFloat_FromDouble( rhs[i] ); /* + */
   PyList_SET_ITEM(result, i, a_double); /* steals a ref */
 }
 SUPERLU_FREE(rhs);

 return result;
}

static PyObject *
dsupralu_SOLVE_INPLACE(PyObject *self, PyObject *args){

 /*
    Solve the linear system. Invoke this after calling
    dsupralu_COLPERM and dsupralu_LU. Takes the
    supralu structure handle as input.

    The solution is returned in rhs_list.
 */

 PyObject *address;
 PyObject *rhs_list;
 PyObject *element;
 double *rhs;
 PyObject *a_double;
 dsupralu_sparse_type *object;
 int info;
 int i, n;

 if(!PyArg_ParseTuple(args,(char *)"OO",
               &address, &rhs_list)){
   return NULL;
 }
 if(!PyCObject_Check(address)){
   PyErr_SetString(PyExc_TypeError,
     "Wrong 1st argument! CObject required (dsupralu_sparse_type handle).");
   return NULL;
 }  
 if(!PySequence_Check(rhs_list)){
   PyErr_SetString(PyExc_TypeError,
            "Wrong 2nd argument! Sequence required (rhs_list).");
   return NULL;
 }  
 n = PySequence_Length(rhs_list);
 if( !(rhs = doubleMalloc(n)) ){
   PyErr_SetString(PyExc_TypeError,
            "Malloc fails for rhs[].");
   return NULL;
 }
 for(i=0; i<n; ++i){
   element = PySequence_Fast_GET_ITEM(rhs_list, i);
   rhs[i] = PyFloat_AsDouble(element);
 }
 object = PyCObject_AsVoidPtr(address);
 dsupralu_solve_(&object, rhs, &info);
 if(info !=0 ){
   PyErr_Format(PyExc_TypeError,
         "dsupralu_solve_ returned INFO=%d.", info);
   return NULL;
 }
 for(i=0; i<n; ++i) {
   a_double = PyFloat_FromDouble( rhs[i] ); /* + */
   PySequence_SetItem(rhs_list, i, a_double);
   Py_DECREF(a_double);
 }
 SUPERLU_FREE (rhs);

 return  Py_BuildValue("");
}

static PyMethodDef dsupralu_methods[] = {
 {"new", dsupralu_NEW, METH_VARARGS, "Store matrix in CCS format and return 2 handles to SUPRALU structure"},
 {"vector_dot_matrix", dsupralu_VECTOR_DOT_MATRIX, METH_VARARGS, "(vector)^* . matrix multiplication. Set the 3rd arg to 'T' if complex conjugate of vector should NOT be taken."},
 {"matrix_dot_vector", dsupralu_MATRIX_DOT_VECTOR, METH_VARARGS, "matrix . vector multiplication."},
 {"vector_dot_matrix_dot_vector", dsupralu_VECTOR_DOT_MATRIX_DOT_VECTOR, METH_VARARGS, "(vector1)^* . matrix . vector2 multiplication. Set the 3rd arg to 'T' if complex conjugate of vector should NOT be taken."},
 {"colperm", dsupralu_COLPERM, METH_VARARGS, "Compute column permutation vector"},
 {"lu", dsupralu_LU, METH_VARARGS, "Perform LU fatorization"},
 {"det", dsupralu_DET, METH_VARARGS, "Return (dm, de) with the determinant expressed as dm * 2**de"},
 {"solve", dsupralu_SOLVE, METH_VARARGS, "Solve linear system"},
 {"SOLVE", dsupralu_SOLVE_INPLACE, METH_VARARGS,
  "Solve linear system, replacing the right hand side array with the solution"},
 {NULL, NULL, 0, NULL}
};

void initdsupralu(){
 Py_InitModule( "dsupralu", dsupralu_methods);
}

/*
Example: this is how this module could be used:

#!/usr/bin/env python

import sparse, dsupralu

for i in range(1):
   amat = sparse.sparse({
       (0,0):1.,
       (1,0):2.,
       (0,1):3.,
       (1,1):4.,
       (2,2):5.,
           })
   amat.out()
   [m,n] = amat.size()
   print 'calling dsupralu.new'
   h1, h2 = dsupralu.new(amat, n)
   print 'h1=', h1, ' h2=', h2
   b = [0., 1., 2.]
   x = [1., 0., 1.]
   print 'dsupralu.vector_dot_matrix(h1, b)=', \
         dsupralu.vector_dot_matrix(h1, b)
   print 'dsupralu.matrix_dot_vector(h1, b)=', \
         dsupralu.matrix_dot_vector(h1, b)
   print 'dsupralu.vector_dot_matrix_dot_vector(h1, b, x)=', \
         dsupralu.vector_dot_matrix_dot_vector(h1, b, x)
   cperm = 2
   print 'calling dsupralu.colperm'
   dsupralu.colperm(h1, cperm)
   print 'calling dsupralu.lu'
   dsupralu.lu(h1)
   det = dsupralu.det(h1)
   print 'dsupralu.det(h1)=', det[0],' *2**', det[1],' = ', det[0]*2**det[1]
   rhs=[0., 1., 0.]
   print 'calling dsupralu.solve'
   v = dsupralu.solve(h1, rhs)
   print 'v=', v
   print 'calling dsupralu.SOLVE'
   dsupralu.SOLVE(h1, rhs)
   print 'rhs=', rhs

*/

