/* 
   $Id: sulumodule.c,v 1.7 2003/11/05 20:25:28 pletzer Exp $

   A. Pletzer

   Py interface to SuperLU

   May 2 2001

   This module can be compiled as follows on Linux:

   gcc -Wall -shared -fPIC -I/usr/local-apletzer/include/python2.0/ -o sulumodule.so sulumodule.c  superlu.a /usr/local/lib/libblas.a

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

#include "dsp_defs.h"
#include "supermatrix.h"
#include "util.h"



static PyObject* sulu_solve(PyObject *self, PyObject *args){

  /**
   *   Solve: double version. Data must be in row compressed storage 
   */

  PyObject *sparse_data;
  PyObject *rhs_list;
  PyObject *element;
  PyObject *ij;

  int i, j, k;
  int nnz, n, nrhs, m;
  double *a;
  int *asub;
  int *xa;
  double *rhs;
  double *xact;
  int *perm_r;
  int *perm_c;
  SuperMatrix A, B;
  int ldx;
  char trans[1];
  int permc_spec;
  SuperMatrix L, U;      /* factor L & U*/
  int info;
  superlu_options_t options;
  SuperLUStat_t stat;
  PyObject *a_double;
  PyObject *result;

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
  if ( !(a = doubleMalloc(nnz)) ) ABORT("Malloc fails for a[].");
  if ( !(asub = intMalloc(nnz)) ) ABORT("Malloc fails for asub[].");
  if ( !(xa = intMalloc(n+1)) ) ABORT("Malloc fails for xa[].");
  if ( !(rhs = doubleMalloc(m*nrhs)) ) ABORT("Malloc fails for rhs[].");

  xact = doubleMalloc(n*nrhs);

  if ( !(perm_r = intMalloc(m)) ) ABORT("Malloc fails for perm_r[].");
  if ( !(perm_c = intMalloc(n)) ) ABORT("Malloc fails for perm_c[].");
    
  /* Convert to CCS and fill in */

  k = 0;
  for(i = 0; i < n; ++i){
    xa[i] = k;
    element = PySequence_Fast_GET_ITEM(rhs_list, i); /*PyList_GET_ITEM(rhs_list, i);*/
    rhs[i] = PyFloat_AsDouble(element);
    for(j = 0 ; j < n; ++j){
      ij = PyTuple_New(2); 
      PyTuple_SET_ITEM(ij, 0, PyInt_FromLong((long) j)); 
      PyTuple_SET_ITEM(ij, 1, PyInt_FromLong((long) i)); 
      element = PyDict_GetItem(sparse_data, ij);
      Py_DECREF(ij); /* --- */
      if(element){
	a[k] = PyFloat_AsDouble(element);
	asub[k] = j;
	k++;
      }
    }
  }
  xa[n] = k;



  dCreate_CompCol_Matrix(&A, m, n, nnz, a, asub, xa, SLU_NC, SLU_D, SLU_GE);
  dCreate_Dense_Matrix(&B, m, nrhs, rhs, m, SLU_DN, SLU_D, SLU_GE);

  ldx=n;
  dGenXtrue(n, nrhs, xact, ldx);
  *trans = 'N';

  /*
   * Get column permutation vector perm_c[], according to permc_spec:
   *   permc_spec = 0: natural ordering 
   *   permc_spec = 1: minimum degree on structure of A'*A
   *   permc_spec = 2: minimum degree on structure of A'+A
   *   permc_spec = 3: approximate minimum degree for unsymmetric matrices
   */   
 	
  if(permc_spec<0 || permc_spec>3) permc_spec=0;
  get_perm_c(permc_spec, &A, perm_c);

  set_default_options(&options);
  
  if(permc_spec==0) options.ColPerm = NATURAL;
  if(permc_spec==1) options.ColPerm = MMD_ATA;
  if(permc_spec==2) options.ColPerm = MMD_AT_PLUS_A;
  if(permc_spec==3) options.ColPerm = COLAMD;

  StatInit(&stat);

  /* int panel_size = sp_ienv(1); */


  /*  solution returned in B, which propagates back to rhs */
  /* dPrint_Dense_Matrix("B", &B); */
  dgssv(&options, &A, perm_c, perm_r, &L, &U, &B, &stat, &info);

  if(info!=0){
    printf("*** error after dgssv %d \n", info);
    if(info>0){
      printf("usually matrix is singular or not enough memory\n");
    } else {
      printf("wrong input data?\n");
    }
/*     dPrint_CompCol_Matrix("A", &A); */
/*     dPrint_Dense_Matrix("B", &B); */
    return NULL;
  } else {
    /*        dPrint_Dense_Matrix("B", &B); */
  }

  result = PyList_New(n); /* + */
  for(i=0; i<n; i++) {
    a_double = PyFloat_FromDouble( rhs[i] ); /* + */
    PyList_SetItem(result, i, a_double); /* steals a ref */
    /* Py_DECREF(a_double); */ /* - ** should decref here? */
  }
    

  /* clean up */

  /* no need to deallocate these  */
/*   if(a) SUPERLU_FREE (a);  */
/*   if(asub) SUPERLU_FREE (asub); */
/*   if(xa) SUPERLU_FREE (xa); */

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


static PyMethodDef sulu_methods[] = {
  {(char *)"solve", sulu_solve, METH_VARARGS, (char *)"solve(A, b, cperm) -- solve A*x = b where A is a sparse matrix (dict), b the right hand side vector (list), and cperm = 0, 1, 2 or 3 the choice of column permutations"},
  {NULL,NULL}
};

void initsulu(){
  Py_InitModule((char *)"sulu",sulu_methods);
}




