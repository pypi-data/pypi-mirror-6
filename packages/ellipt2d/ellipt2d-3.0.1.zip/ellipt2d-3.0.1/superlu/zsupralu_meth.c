/* 

$Id: zsupralu_meth.c,v 1.3 2003/12/23 19:54:52 pletzer Exp $ 

Sparse matrix operations 

*/
#include <math.h>
#include "zsupralu_type.h"

void zGetDiagU(SuperMatrix *L, doublecomplex *diagU);

void zsupralu_new_(zsupralu_sparse_type **self,
		   doublecomplex *vals,
		   int *row_ind, int *col_ptr,
		   int *nnz, int *n, int *info){

  *info = 0;

  if ( !((*self) = SUPERLU_MALLOC(sizeof(zsupralu_sparse_type))) ){
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

  zCreate_CompCol_Matrix(&((*self)->A), 
			 *n, 
			 *n, 
			 *nnz, 
			 vals, 
			 row_ind, 
			 col_ptr, 
			 SLU_NC, 
			 SLU_Z, 
			 SLU_GE);


  set_default_options(&((*self)->options));
  (*self)->options.ColPerm = MMD_AT_PLUS_A; // works best?

  StatInit(&((*self)->stat));
}
		  
void zsupralu_del_(zsupralu_sparse_type **self, int *info){

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


void zsupralu_vector_dot_matrix_(zsupralu_sparse_type **self,
				doublecomplex *vector, doublecomplex *res,
				int *info){

  /* 

  vector . A -> res 

  n: matrix rank

  */

  int k, i, j, n;
  NCformat *Astore;
  doublecomplex *val;

  *info = 0;

  Astore = ((*self)->A).Store;
  val = Astore->nzval;
  n = ((*self)->A).ncol;
  for(j=0; j<n; ++j){
    res[j].r = 0.; res[j].i = 0.;
    for(k = Astore->colptr[j]; k < Astore->colptr[j+1]; ++k){
      i = Astore->rowind[k];
      res[j].r += val[k].r * vector[i].r - val[k].i * vector[i].i;
      res[j].i += val[k].i * vector[i].r + val[k].r * vector[i].i;
    }
  }
}


void zsupralu_conj_vector_dot_matrix_(zsupralu_sparse_type **self,
				doublecomplex *vector, doublecomplex *res,
				int *info){

  /* 

  (vector)^* . A -> res 

  n: matrix rank

  */

  int k, i, j, n;
  NCformat *Astore;
  doublecomplex *val;

  *info = 0;

  Astore = ((*self)->A).Store;
  val = Astore->nzval;
  n = ((*self)->A).ncol;
  for(j=0; j<n; ++j){
    res[j].r = 0.; res[j].i = 0.;
    for(k = Astore->colptr[j]; k < Astore->colptr[j+1]; ++k){
      i = Astore->rowind[k];
      res[j].r += val[k].r * vector[i].r + val[k].i * vector[i].i;
      res[j].i += val[k].i * vector[i].r - val[k].r * vector[i].i;
    }
  }
}


void zsupralu_matrix_dot_vector_(zsupralu_sparse_type **self,
				doublecomplex *vector, doublecomplex *res,
				int *info){

  /* 

  A . vector -> res 

  n: matrix rank

  */

  int k, i, j, n;
  NCformat *Astore;
  doublecomplex *val;

  *info = 0;

  Astore = ((*self)->A).Store;
  val = Astore->nzval;
  n = ((*self)->A).ncol;
  for(i=0; i<n; ++i){
    res[i].r = 0.; res[i].i = 0.;
  }
  for(j=0; j<n; ++j){
    for(k = Astore->colptr[j]; k < Astore->colptr[j+1]; ++k){
      i = Astore->rowind[k];
      res[i].r += val[k].r * vector[j].r - val[k].i * vector[j].i;
      res[i].i += val[k].i * vector[j].r + val[k].r * vector[j].i;      
    }
  }
}


void zsupralu_vector_dot_matrix_dot_vector_(zsupralu_sparse_type **self,
				doublecomplex *vector1, doublecomplex *vector2,
				doublecomplex *res, int *info){

  /* 

  vector1 . A . vector2 -> res 

  */

  int k, i, j, n;
  NCformat *Astore;
  doublecomplex *val;
  double ar, ai, v1r, v1i, v2r, v2i;

  *info = 0;
  res->r = 0.; res->i = 0.;

  Astore = ((*self)->A).Store;
  val = Astore->nzval;
  n = ((*self)->A).ncol;  
  for(j=0; j<n; ++j){
    v2r = vector2[j].r; 
    v2i = vector2[j].i;
    for(k = Astore->colptr[j]; k < Astore->colptr[j+1]; ++k){
      i = Astore->rowind[k];
      ar = val[k].r; 
      ai = val[k].i;
      v1r = vector1[i].r; 
      v1i = vector1[i].i;
      res->r += 
	+ v1r * ar * v2r
	- v1i * ai * v2r
	- v1i * ar * v2i
	- v1r * ai * v2i;
      res->i += 
	+ v1i * ar * v2r
	+ v1r * ai * v2r
	+ v1r * ar * v2i
	- v1i * ai * v2i;
    }
  }
}

void zsupralu_conj_vector_dot_matrix_dot_vector_(zsupralu_sparse_type **self,
				doublecomplex *vector1, doublecomplex *vector2,
				doublecomplex *res, int *info){

  /* 

  vector1 . A . vector2 -> res 

  */

  int k, i, j, n;
  NCformat *Astore;
  doublecomplex *val;
  double ar, ai, v1r, v1i, v2r, v2i;

  *info = 0;
  res->r = 0.; res->i = 0.;

  Astore = ((*self)->A).Store;
  val = Astore->nzval;
  n = ((*self)->A).ncol;  
  for(j=0; j<n; ++j){
    v2r = vector2[j].r; 
    v2i = vector2[j].i;
    for(k = Astore->colptr[j]; k < Astore->colptr[j+1]; ++k){
      i = Astore->rowind[k];
      ar = val[k].r; 
      ai = val[k].i;
      v1r =   vector1[i].r; 
      v1i = - vector1[i].i;
      res->r += 
	+ v1r * ar * v2r
	- v1i * ai * v2r
	- v1i * ar * v2i
	- v1r * ai * v2i;
      res->i += 
	+ v1i * ar * v2r
	+ v1r * ai * v2r
	+ v1r * ar * v2i
	- v1i * ai * v2i;
    }
  }
}

void zsupralu_colperm_(zsupralu_sparse_type **self, int *permc_spec, int *info){

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

void zsupralu_lu_(zsupralu_sparse_type **self, int *info){

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

  zgstrf(&((*self)->options), &((*self)->AC), drop_tol, relax, panel_size, 
	 (*self)->etree, NULL, 0, (*self)->perm_c, (*self)->perm_r, 
	 (*self)->L, (*self)->U, &((*self)->stat), info);

  (*self)->LUfactorized = 1;
}


void zsupralu_determinant_(zsupralu_sparse_type **self,
			   doublecomplex *res_mantissa, int *res_exponent,
			   int *info){
  /* 

  Compute the determinant 

  The det of a triangular metrix is just the product of its diagonal elements. 
  However, we need to correct for the permutation matrices (which have 
  det = +/- 1).

  The returned value is:

  res_mantissa * 2^res_exponent

  */
  
  int_t n;
  doublecomplex *diagU;
  int i;
  int exponent = 0;
  int iexp;
  double magnitude, phase;

  *info = 0;

  if( ! (*self)->LUfactorized ){
    *info = -7;
    return;
  }
  n = ((*self)->A).nrow;
  if ( !(diagU = SUPERLU_MALLOC( n * sizeof(SuperMatrix) )) )
       ABORT("Malloc fails for diagU[].");
  
  zGetDiagU( (*self)->L, diagU );
  
  magnitude = 1.;
  *res_exponent = 0;
  phase = 0.;
  for(i=0; i<n; ++i){
    magnitude *= frexp(sqrt(diagU[i].r*diagU[i].r + diagU[i].i*diagU[i].i), &iexp);
    *res_exponent += iexp;
    /* normalize */
    magnitude = frexp(magnitude, &iexp);
    *res_exponent += iexp;
    phase += atan2(diagU[i].i, diagU[i].r);
    exponent += (  abs((*self)->perm_r[i]-i) + abs((*self)->perm_c[i]-i)  );
  }

  exponent /= 2;
  exponent = exponent % 2;
  if(exponent){
    magnitude *= -1.;
  }
  res_mantissa->r = magnitude*cos(phase);
  res_mantissa->i = magnitude*sin(phase);
  
  
  SUPERLU_FREE(diagU);
  
}

void zsupralu_solve_(zsupralu_sparse_type **self, 
		     doublecomplex *b, int *info){

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

  zCreate_Dense_Matrix(&B, n, nrhs, b, n, SLU_DN, SLU_Z, SLU_GE);

  /* Solve the system A*X=B, overwriting B with X. */
  zgstrs(trans, (*self)->L, (*self)->U, (*self)->perm_c, (*self)->perm_r, &B, &((*self)->stat), info);
  Destroy_SuperMatrix_Store(&B);
  
}

/* 
 * -- Auxiliary routine in SuperLU (version 2.0) --
 * Lawrence Berkeley National Lab, Univ. of California Berkeley.
 * Xiaoye S. Li
 * September 11, 2003
 *
 */


void zGetDiagU(SuperMatrix *L, doublecomplex *diagU)
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
    doublecomplex *zblock, *Lval;
    SCformat *Lstore;

    Lstore = L->Store;
    Lval = Lstore->nzval;
    nsupers = Lstore->nsuper + 1;

    for (k = 0; k < nsupers; ++k) {
      fsupc = L_FST_SUPC(k);
      nsupc = L_FST_SUPC(k+1) - fsupc;
      nsupr = L_SUB_START(fsupc+1) - L_SUB_START(fsupc);
      luptr = L_NZ_START(fsupc);

      zblock = &diagU[fsupc];
      for (i = 0; i < nsupc; ++i) {
        zblock[i] = Lval[luptr];
        luptr += nsupr + 1;
      }
    }
}


#ifdef _MAIN
/*---------------------------------------------------------------------------*/
#define DEBUGlevel 1
/* 

test unit 
gcc -g -I/usr/local/superlu/include -Wall -D_MAIN zsupralu_meth.c -L/usr/local/superlu/lib -lsuperlu -lblas -lm

>> amat=[1.+i,3.,0;2.,4.,0.;0,0,5.];
>> b = [0 1. 2*i];
>> x = [1. 0. i];
>> conj(b) * amat

ans =

   2.0000             4.0000                  0 -10.0000i

>> b * amat

ans =

   2.0000             4.0000                  0 +10.0000i

>> amat * conj(b')

ans =

   3.0000          
   4.0000          
        0 +10.0000i

>> b * amat * conj(x')

ans =

    -8

>> conj(b) * amat * conj(x')

ans =

    12


>> det(amat)

ans =

 -10.0000 +20.0000i

>> amat\ conj(b')

ans =

   0.3000 + 0.6000i
   0.1000 - 0.3000i
        0 + 0.4000i

   
*/

int main(){
  zsupralu_sparse_type *self;
  int i;
#define NSIZE 3
  int n;
  int nnz=5;
  int permc_spec;
  doublecomplex z_mantissa;
  int z_exponent;
  int ier = 0;

  doublecomplex vals[5]={ {1.,1.},{2.,0.},{3.,0.}, {4.,0.}, {5.,0.} };
  doublecomplex b[NSIZE] = { {0.,0.}, {1.,0.}, {0., 2.} };
  doublecomplex x[NSIZE] = { {1.,0.}, {0.,0.}, {0., 1.} };
  doublecomplex y[NSIZE];
  doublecomplex res;
  int row_ind[5] = {0, 1, 0, 1, 2};
  int col_ptr[NSIZE+1]={0, 2, 4, 5}; 

  
#if ( DEBUGlevel>=1 )
    CHECK_MALLOC("begin");
#endif
  n = NSIZE;
  zsupralu_new_(&self, vals, row_ind, col_ptr, &nnz, &n, &ier);
  permc_spec = 1;
  printf("zsupralu_new_: ier=%d\n", ier);

  zsupralu_conj_vector_dot_matrix_(&self, b, y, &ier);
  printf("zsupralu_conj_vector_dot_matrix_: ier=%d\n", ier);
  for(i=0; i<NSIZE; ++i) printf("y[%d]=%lf +i* %lf\n", i, y[i].r, y[i].i);

  zsupralu_vector_dot_matrix_(&self, b, y, &ier);
  printf("zsupralu_vector_dot_matrix_: ier=%d\n", ier);
  for(i=0; i<NSIZE; ++i) printf("y[%d]=%lf +i* %lf\n", i, y[i].r, y[i].i);

  zsupralu_matrix_dot_vector_(&self, b, y, &ier);
  printf("zsupralu_matrix_dot_vector_: ier=%d\n", ier);
  for(i=0; i<NSIZE; ++i) printf("y[%d]=%lf +i* %lf\n", i, y[i].r, y[i].i);

  zsupralu_vector_dot_matrix_dot_vector_(&self, b, x, &res, &ier);
  printf("zsupralu_vector_dot_matrix_dot_vector_: res=%lf +i* %lf ier=%d\n", 
	 res.r, res.i, ier);

  zsupralu_conj_vector_dot_matrix_dot_vector_(&self, b, x, &res, &ier);
  printf("zsupralu_conj_vector_dot_matrix_dot_vector_: res=%lf +i* %lf ier=%d\n", 
	 res.r, res.i, ier);

  zsupralu_colperm_(&self, &permc_spec, &ier);
  printf("zsupralu_colperm_: ier=%d\n", ier);

  zsupralu_lu_(&self, &ier);
  printf("zsupralu_lu_: ier=%d\n" ,ier);

  zsupralu_determinant_(&self, &z_mantissa, &z_exponent, &ier);
  printf("zsupralu_determinant_: ier=%d det(A)=(%lf +i*%lf)*2^%d = %lf +i*%lf\n",
	 ier, z_mantissa.r, z_mantissa.i, z_exponent, 
	 z_mantissa.r*pow(2., z_exponent), z_mantissa.i*pow(2., z_exponent));
  
  for(i=0; i<NSIZE; ++i) x[i]=b[i];
  zsupralu_solve_(&self, x, &ier);
  printf("zsupralu_solve_: ier=%d\n", ier);
  for(i=0; i<n; ++i) printf("x[%i]=%f +i%f\n", i, x[i].r, x[i].i);

  zsupralu_del_(&self, &ier);  
#if ( DEBUGlevel>=1 )
    CHECK_MALLOC("end");
#endif

  return 0;
  
}

#endif
