/* 

$Id: dsupralu_meth.c,v 1.3 2003/12/23 19:54:52 pletzer Exp $ 

Sparse matrix operations 

*/
#include <math.h>
#include "dsupralu_type.h"

void dGetDiagU(SuperMatrix *L, double *diagU);

void dsupralu_new_(dsupralu_sparse_type **self,
		   double *vals,
		   int *row_ind, int *col_ptr,
		   int *nnz, int *n, int *info){

  *info = 0;

  if ( !((*self) = SUPERLU_MALLOC(sizeof(dsupralu_sparse_type))) ){
       *info = -1;
       return;
  }
  (*self)->LUfactorized=0;
  (*self)->colperm_is_computed=0;

  (*self)->perm_r = NULL;
  (*self)->perm_c = NULL;
  (*self)->etree = NULL;
  (*self)->L = NULL;
  (*self)->U = NULL;

  dCreate_CompCol_Matrix(&((*self)->A), 
			 *n, 
			 *n, 
			 *nnz, 
			 vals, 
			 row_ind, 
			 col_ptr, 
			 SLU_NC, 
			 SLU_D, 
			 SLU_GE);


  set_default_options(&((*self)->options));
  (*self)->options.ColPerm = MMD_AT_PLUS_A; // works best?

  StatInit(&((*self)->stat));
}
		  
void dsupralu_del_(dsupralu_sparse_type **self, int *info){

  /* Destructor */

  *info = 0;

  if( (*self)->etree ) {
    SUPERLU_FREE ((*self)->etree);
    (*self)->etree = NULL;
  }
  if( (*self)->perm_r ) {
    SUPERLU_FREE ((*self)->perm_r);
    (*self)->perm_r = NULL;
  }
  if( (*self)->perm_c ) {
    SUPERLU_FREE ((*self)->perm_c);
    (*self)->perm_c = NULL;
  }
  if( (*self)->L )  {
    if( (*self)->LUfactorized ) 
      Destroy_SuperNode_Matrix((*self)->L);
    SUPERLU_FREE ((*self)->L);
    (*self)->L = NULL;
  }
  if( (*self)->U )  {
    if( (*self)->LUfactorized )
      Destroy_CompCol_Matrix((*self)->U);
    SUPERLU_FREE ((*self)->U);
    (*self)->U = NULL;
  }
  if( (*self)->colperm_is_computed )
    Destroy_CompCol_Permuted(&((*self)->AC));

  Destroy_SuperMatrix_Store(&((*self)->A));
  
  StatFree(&((*self)->stat));

  SUPERLU_FREE (*self);
}


void dsupralu_vector_dot_matrix_(dsupralu_sparse_type **self,
				double *vector, double *res,
				int *info){

  /* 

  vector . A -> res 

  n: matrix rank

  */

  int k, i, j, n;
  NCformat *Astore;
  double *val;

  *info = 0;

  Astore = ((*self)->A).Store;
  val = Astore->nzval;
  n = ((*self)->A).ncol;
  for(j=0; j<n; ++j){
    res[j] = 0.;
    for(k = Astore->colptr[j]; k < Astore->colptr[j+1]; ++k){
      i = Astore->rowind[k];
      res[j] += val[k] * vector[i];
    }
  }
}

void dsupralu_matrix_dot_vector_(dsupralu_sparse_type **self,
				double *vector, double *res,
				int *info){

  /* 

  A . vector -> res 

  n: matrix rank

  */

  int k, i, j, n;
  NCformat *Astore;
  double *val;

  *info = 0;

  Astore = ((*self)->A).Store;
  val = Astore->nzval;
  n = ((*self)->A).ncol;
  for(i=0; i<n; ++i){
    res[i] = 0.;
  }
  for(j=0; j<n; ++j){
    for(k = Astore->colptr[j]; k < Astore->colptr[j+1]; ++k){
      i = Astore->rowind[k];
      res[i] += val[k] * vector[j];
    }
  }
}


void dsupralu_vector_dot_matrix_dot_vector_(dsupralu_sparse_type **self,
				double *vector1, double *vector2,
				double *res, int *info){

  /* 

  vector1 . A . vector2 -> res 

  */

  int k, i, j, n;
  NCformat *Astore;
  double *val;
  double v1, v2;

  *info = 0;
  *res = 0.;

  Astore = ((*self)->A).Store;
  val = Astore->nzval;
  n = ((*self)->A).ncol;  
  for(j=0; j<n; ++j){
    v2 = vector2[j]; 
    for(k = Astore->colptr[j]; k < Astore->colptr[j+1]; ++k){
      i = Astore->rowind[k];
      v1 = vector1[i]; 
      *res += v1 * val[k] * v2;
    }
  }
}


void dsupralu_colperm_(dsupralu_sparse_type **self, int *permc_spec, int *info){

  /*
   * Get column permutation vector perm_c[], according to permc_spec:
   *   permc_spec = 0: natural ordering 
   *   permc_spec = 1: minimum degree on structure of A'*A
   *   permc_spec = 2: minimum degree on structure of A'+A
   *   permc_spec = 3: approximate minimum degree for unsymmetric matrices
   */    	
  
  int_t n;

  *info = 0;

  n = ((*self)->A).nrow;
  if ( !((*self)->perm_c = intMalloc(n)) ){ 
    *info = -1;
    return;
  }
  if ( !((*self)->etree = intMalloc(n)) ){
    *info = -3;
    return;
  }
  get_perm_c(*permc_spec, &((*self)->A), (*self)->perm_c);
  sp_preorder(&((*self)->options), &((*self)->A), (*self)->perm_c, (*self)->etree, &((*self)->AC));

  (*self)->colperm_is_computed = 1; 
}

void dsupralu_lu_(dsupralu_sparse_type **self, int *info){

  /* LU factorization */

  double drop_tol = 0.0;
  int  panel_size, relax;
  int_t n;

  n = ((*self)->A).nrow;
  
  *info = 0;

  if( ! (*self)->colperm_is_computed ){
    *info = -6;
    return;
  }

  /* ONLY PERFORM THE LU DECOMPOSITION */

  if ( !((*self)->perm_r = intMalloc(n)) ){
    *info = -2;
    return;
  }
  if ( ! ((*self)->L = (SuperMatrix *) SUPERLU_MALLOC( sizeof(SuperMatrix))) ){
    *info = -4;
    return;
  }
  if ( ! ((*self)->U = (SuperMatrix *) SUPERLU_MALLOC( sizeof(SuperMatrix) )) ){
    *info = -5;
    return;
  }
  
  panel_size = sp_ienv(1);
  relax = sp_ienv(2);

  dgstrf(&((*self)->options), &((*self)->AC), drop_tol, relax, panel_size, 
	 (*self)->etree, NULL, 0, (*self)->perm_c, (*self)->perm_r, 
	 (*self)->L, (*self)->U, &((*self)->stat), info);

  (*self)->LUfactorized = 1;
}


void dsupralu_determinant_(dsupralu_sparse_type **self,
			   double *res_mantissa, int *res_exponent, int *info){
  /* 

  Compute the determinant 

  The det of a triangular matrix is just the product of its diagonal elements. 
  However, we need to correct for the permutation matrices (which have 
  det = +/- 1).

  The returned value is:

  res_mantissa * 2^res_exponent

  */
  
  int_t n;
  double *diagU;
  int i;
  int exponent = 0;
  int iexp;

  *info = 0;

  if( ! (*self)->LUfactorized ){
    *info = -7;
    return;
  }
  n = ((*self)->A).nrow;
  if ( !(diagU = SUPERLU_MALLOC( n * sizeof(SuperMatrix) )) )
       ABORT("Malloc fails for diagU[].");
  
  dGetDiagU( (*self)->L, diagU );
  
  *res_mantissa = 1.;
  *res_exponent = 0;
  for(i=0; i<n; ++i){
    *res_mantissa *= frexp(diagU[i], &iexp);
    *res_exponent += iexp;
    /* normalize */
    *res_mantissa = frexp(*res_mantissa, &iexp);
    *res_exponent += iexp;
    exponent += (  abs((*self)->perm_r[i]-i) + abs((*self)->perm_c[i]-i)  );
  }
  exponent /= 2;
  exponent = exponent % 2;
  if(exponent)
    *res_mantissa *= -1.;
  
  SUPERLU_FREE(diagU);
  
}

void dsupralu_solve_(dsupralu_sparse_type **self, 
		     double *b, int *info){

  /* Solve (after LU factorization) */

  SuperMatrix B;
  int_t nrhs = 1;
  int_t n;
  trans_t  trans;
  trans = NOTRANS;

  *info = 0;

  if( ! (*self)->LUfactorized ){
    *info = -7;
    return;
  }
  n = ((*self)->A).nrow;

  dCreate_Dense_Matrix(&B, n, nrhs, b, n, SLU_DN, SLU_D, SLU_GE);

  /* Solve the system A*X=B, overwriting B with X. */
  dgstrs(trans, (*self)->L, (*self)->U, (*self)->perm_c, (*self)->perm_r, &B, &((*self)->stat), info);
  Destroy_SuperMatrix_Store(&B);
  
}

/* 
 * -- Auxiliary routine in SuperLU (version 2.0) --
 * Lawrence Berkeley National Lab, Univ. of California Berkeley.
 * Xiaoye S. Li
 * September 11, 2003
 *
 */


void dGetDiagU(SuperMatrix *L, double *diagU)
{
  /*
   * Purpose
   * =======
   *
   * GetDiagU extracts the main diagonal of matrix U of the LU factorization.
   *  
   * Arguments
   * =========
   *
   * L      (input) SuperMatrix*
   *        The factor L from the factorization Pr*A*Pc=L*U as computed by
   *        dgstrf(). Use compressed row subscripts storage for supernodes,
   *        i.e., L has types: Stype = SLU_SC, Dtype = SLU_D, Mtype = SLU_TRLU.
   *
   * diagU  (output) double*, dimension (n)
   *        The main diagonal of matrix U.
   *
   * Note
   * ====
   * The diagonal blocks of the L and U matrices are stored in the L
   * data structures.
   *
   */
    int_t i, k, nsupers;
    int_t fsupc, nsupr, nsupc, luptr;
    double *dblock, *Lval;
    SCformat *Lstore;

    Lstore = L->Store;
    Lval = Lstore->nzval;
    nsupers = Lstore->nsuper + 1;

    for (k = 0; k < nsupers; ++k) {
      fsupc = L_FST_SUPC(k);
      nsupc = L_FST_SUPC(k+1) - fsupc;
      nsupr = L_SUB_START(fsupc+1) - L_SUB_START(fsupc);
      luptr = L_NZ_START(fsupc);

      dblock = &diagU[fsupc];
      for (i = 0; i < nsupc; ++i) {
        dblock[i] = Lval[luptr];
        luptr += nsupr + 1;
      }
    }
}


#ifdef _MAIN
/*---------------------------------------------------------------------------*/
#define DEBUGlevel 1
/* 

test unit 
gcc -g -I/usr/local/superlu/include -Wall -D_MAIN dsupralu_meth.c -L/usr/local/superlu/lib -lsuperlu -lblas -lm

>> amat=[1.,3.,0;2.,4.,0.;0,0,5.];
>> b = [0 1. 2];
>> x = [1. 0. 3.];
>> b * amat

ans =

     2     4    10

>> amat * b'

ans =

     3
     4
    10

>> b * amat * x'


ans =

    32

>> det(amat)

ans =

   -10

>> amat\ b'

 ans =

    1.5000
   -0.5000
    0.4000
  
*/

int main(){
  dsupralu_sparse_type *self;
  int i;
#define NSIZE 3
  int n;
  int nnz=5;
  int permc_spec;
  double d;
  int iexp;
  int ier = 0;

  double vals[5]={1., 2., 3., 4., 5.};
  double b[NSIZE] = {0., 1., 2.};
  double x[NSIZE] = {1., 0., 3.};
  double y[NSIZE];
  double res;
  int row_ind[5] = {0, 1, 0, 1, 2};
  int col_ptr[NSIZE+1]={0, 2, 4, 5}; 

  
#if ( DEBUGlevel>=1 )
    CHECK_MALLOC("begin");
#endif
  n = NSIZE;
  dsupralu_new_(&self, vals, row_ind, col_ptr, &nnz, &n, &ier);
  permc_spec = 1;
  printf("dsupralu_new_: ier=%d\n", ier);

  dsupralu_vector_dot_matrix_(&self, b, y, &ier);
  printf("dsupralu_vector_dot_matrix_: ier=%d\n", ier);
  for(i=0; i<NSIZE; ++i) printf("y[%d]=%lf\n", i, y[i]);

  dsupralu_matrix_dot_vector_(&self, b, y, &ier);
  printf("dsupralu_matrix_dot_vector_: ier=%d\n", ier);
  for(i=0; i<NSIZE; ++i) printf("y[%d]=%lf\n", i, y[i]);

  dsupralu_vector_dot_matrix_dot_vector_(&self, b, x, &res, &ier);
  printf("dsupralu_vector_dot_matrix_dot_vector_: res=%lf ier=%d\n", 
	 res, ier);

  dsupralu_colperm_(&self, &permc_spec, &ier);
  printf("dsupralu_colperm_: ier=%d\n", ier);

  dsupralu_lu_(&self, &ier);
  printf("dsupralu_lu_: ier=%d\n" ,ier);

  dsupralu_determinant_(&self, &d, &iexp, &ier);
  printf("dsupralu_determinant_: ier=%d det(A)=%lf * 2^%d = %lf\n", 
	 ier, d, iexp, ldexp(d, iexp));
  
  for(i=0; i<NSIZE; ++i) x[i]=b[i];
  dsupralu_solve_(&self, x, &ier);
  printf("dsupralu_solve_: ier=%d\n", ier);
  for(i=0; i<n; ++i) printf("x[%i]=%f\n", i, x[i]);

  dsupralu_del_(&self, &ier);  
#if ( DEBUGlevel>=1 )
    CHECK_MALLOC("end");
#endif

  return 0;
  
}

#endif
