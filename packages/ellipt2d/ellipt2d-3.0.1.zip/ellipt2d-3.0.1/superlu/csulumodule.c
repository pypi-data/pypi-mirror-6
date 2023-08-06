/* 

   $Id: csulumodule.c,v 1.12 2003/11/05 20:25:27 pletzer Exp $

   A. Pletzer

   Py interface to SuperLU

   May 2 2001

   This module can be compiled as follows on Linux:

   gcc -Wall -shared -fPIC -I/usr/local-apletzer/include/python2.0/ -o csulumodule.so sulumodule.c  superlu.a /usr/local/lib/libblas.a

*/

#include <stdlib.h>
#include "Python.h"

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


#include "zsp_defs.h"
#include "supermatrix.h"
#include "util.h"

void to_CCS(int n, PyObject* sparse_data, PyObject* rhs_list, 
	    doublecomplex *a, int *asub, int *xa, 
	    doublecomplex *rhs){

  PyObject *element, *ij;
  int k = 0;
  int i, j;

 /* Convert to CCS and fill in */


  for(i = 0; i < n; ++i){
    xa[i] = k;
    element = PySequence_Fast_GET_ITEM(rhs_list, i); /*PyList_GET_ITEM(rhs_list, i);*/
    rhs[i].r = PyComplex_RealAsDouble(element);
    rhs[i].i = PyComplex_ImagAsDouble(element);
    for(j = 0 ; j < n; ++j){
      ij = PyTuple_New(2); 
      PyTuple_SET_ITEM(ij, 0, PyInt_FromLong((long) j)); 
      PyTuple_SET_ITEM(ij, 1, PyInt_FromLong((long) i)); 
      element = PyDict_GetItem(sparse_data, ij);
      Py_DECREF(ij); /* --- */
      if(element){
	a[k].r = PyComplex_RealAsDouble(element);
	a[k].i = PyComplex_ImagAsDouble(element);
	asub[k] = j;
	k++;
      }
    }
  }
  xa[n] = k;

}

static PyObject* csulu_solve(PyObject *self, PyObject *args){

  /* Solve: data in compressed column storage */

  PyObject *sparse_data;
  PyObject *rhs_list;

  int i, j, k;
  int nnz, n, nrhs, m;
  doublecomplex *a;
  int *asub;
  int *xa;
  doublecomplex *rhs;
  doublecomplex *xact;
  int *perm_r;
  int *perm_c;
  SuperMatrix A, B;
  int ldx;
  char trans[1];
  int permc_spec;
  SuperMatrix L, U;     /* factor L & U*/
  int info;
  PyObject *a_doublecomplex;
  PyObject *result;
  superlu_options_t options;
  SuperLUStat_t stat;

  COUNTREFS();

  if(!PyArg_ParseTuple(args,(char *)"OOi", 
		       &sparse_data, &rhs_list, &permc_spec)){ 
    return NULL; 
  } 
  if(!PyDict_Check(sparse_data)){
    PyErr_SetString(PyExc_TypeError,
		    "Wrong 1st argument! Dict required (sparse matrix).");
    return NULL;
  }
  if(!PyList_Check(rhs_list)){
    PyErr_SetString(PyExc_TypeError,
		    "Wrong 2nd argument! List required (rhs).");
    return NULL;
  }
    
  nnz = (int) PyDict_Size(sparse_data);
  n = (int) PyList_Size(rhs_list);
  nrhs = 1;
  m = n;

  /* allocations */
  if ( !(a = doublecomplexMalloc(nnz)) ) ABORT("Malloc fails for a[].");
  if ( !(asub = intMalloc(nnz)) ) ABORT("Malloc fails for asub[].");
  if ( !(xa = intMalloc(n+1)) ) ABORT("Malloc fails for xa[].");
  if ( !(rhs = doublecomplexMalloc(m*nrhs)) ) ABORT("Malloc fails for rhs[].");

  xact = doublecomplexMalloc(n * nrhs);

  if ( !(perm_r = intMalloc(m)) ) ABORT("Malloc fails for perm_r[].");
  if ( !(perm_c = intMalloc(n)) ) ABORT("Malloc fails for perm_c[].");
    

  /* convert to CCS format */
  to_CCS(n, sparse_data, rhs_list, a, asub, xa, rhs);

  zCreate_CompCol_Matrix(&A, m, n, nnz, a, asub, xa, SLU_NC, SLU_Z, SLU_GE);
  zCreate_Dense_Matrix(&B, m, nrhs, rhs, m, SLU_DN, SLU_Z, SLU_GE);

  /* zPrint_CompCol_Matrix("A", &A); */
  /* zPrint_Dense_Matrix("B", &B); */

  ldx=n;
  zGenXtrue(n, nrhs, xact, ldx);
  *trans = 'N';

  /*
   * Get column permutation vector perm_c[], according to permc_spec:
   *   permc_spec = 0: natural ordering 
   *   permc_spec = 1: minimum degree on structure of A'*A
   *   permc_spec = 2: minimum degree on structure of A'+A
   *   permc_spec = 3: approximate minimum degree for unsymmetric matrices
   */    

  set_default_options(&options);

  if(permc_spec<0 || permc_spec>3) permc_spec=0;
   if(permc_spec==0) options.ColPerm = NATURAL;
   if(permc_spec==1) options.ColPerm = MMD_ATA;
   if(permc_spec==2) options.ColPerm = MMD_AT_PLUS_A;
   if(permc_spec==3) options.ColPerm = COLAMD;

   StatInit(&stat);

  /* int panel_size = sp_ienv(1); */


  /* solution returned in B, which propagates back to rhs */
  /* zPrint_Dense_Matrix("B", &B); */
  zgssv(&options, &A, perm_c, perm_r, &L, &U, &B, &stat, &info);

  if(info!=0){
    printf("*** error after zgssv %d \n", info);
    if(info>0){
      printf("usually matrix is singular or not enough memory\n");
    } else {
      printf("wrong input data?\n");
    }
/*     zPrint_CompCol_Matrix("A", &A); */
/*     zPrint_Dense_Matrix("B", &B); */
    return NULL;
  }

  result = PyList_New(n); /* + */
  for(i=0; i<n; i++) {
    a_doublecomplex = PyComplex_FromDoubles( rhs[i].r, rhs[i].i ); /* + */
    PyList_SET_ITEM(result, i, a_doublecomplex); /* steals a ref */
  }
    

  /* clean up */

  /* no need to deallocate these */
/*    SUPERLU_FREE (a); */
/*    SUPERLU_FREE (asub); */
/*    SUPERLU_FREE (xa); */

  SUPERLU_FREE (rhs);
  SUPERLU_FREE (xact);
  SUPERLU_FREE (perm_r);
  SUPERLU_FREE (perm_c);
  Destroy_CompCol_Matrix(&A);
  Destroy_SuperMatrix_Store(&B);
  Destroy_SuperNode_Matrix(&L);
  Destroy_CompCol_Matrix(&U);
  StatFree(&stat);
    
  COUNTREFS();

  return result;
}




static PyMethodDef csulu_methods[] = {
  {(char *)"solve", csulu_solve, METH_VARARGS, (char *)"solve(A, b, cperm) -- solve A*x = b where A is a sparse matrix (dict), b the right hand side vector (list), and cperm = 0, 1, 2 or 3 the choice of column permutations"},
  {NULL,NULL}
};

void initcsulu(){
  Py_InitModule((char *)"csulu",csulu_methods);
}



