/* 

$Id: dsupralu_type.h,v 1.3 2003/12/23 19:54:52 pletzer Exp $ 

*/

/**
 * @file
 * @brief Supralu double API
 * 
 * This file contains a list of procedures that create, manipulate, 
 * perform standard sparse matrix operations on dense vectors, and
 * destroy a Supralu object. The Superlu object's members are structs
 * defined in the dsp_defs.h header. The API has been written to allow 
 * easy interfacing to other languages, notably Fortran and Python. The
 * address of the object (**self) can be passed as an opaque handle to
 * other languages.
 *
 * In all routines below, the call is successful if the returned value 
 * of the last argument info is zero. The first argument is always the 
 * a pointer to the object (**self).
 * 
 * @author A. Pletzer
 */

#ifndef _DSUPRALU_TYPE
#define _DSUPRALU_TYPE

#include "dsp_defs.h"

typedef struct {

  SuperMatrix A, AC;
  SuperMatrix *L, *U;
  int *perm_r; /* row permutations from partial pivoting */
  int *perm_c; /* column permutation vector */
  int *etree; /* column elimination tree */
  superlu_options_t options;
  SuperLUStat_t stat;
  int colperm_is_computed;
  int LUfactorized;

} dsupralu_sparse_type;

/* Fortran name mapping */

#if defined( __RS6000) || defined(__HP) || defined(__IBM__)
#define dsupralu_new_ dsupralu_new
#define dsupralu_del_ dsupralu_del
#define dsupralu_vector_dot_matrix_ dsupralu_vector_dot_matrix
#define dsupralu_matrix_dot_vector_ dsupralu_matrix_dot_vector
#define dsupralu_vector_dot_matrix_dot_vector_ dsupralu_vector_dot_matrix_dot_vector
#define dsupralu_determinant_ dsupralu_determinant
#define dsupralu_solve_ dsupralu_solve
#else
#if defined(__CRAY)
#define dsupralu_new_ DSUPRALU_NEW
#define dsupralu_del_ DSUPRALU_DEL
#define dsupralu_vector_dot_matrix_ DSUPRALU_VECTOR_DOT_MATRIX
#define dsupralu_matrix_dot_vector_ DSUPRALU_MATRIX_DOT_VECTOR
#define dsupralu_vector_dot_matrix_dot_vector_ DSUPRALU_VECTOR_DOT_MATRIX_DOT_VECTOR
#define dsupralu_determinant_ DSUPRALU_DETERMINANT
#define dsupralu_solve_ DSUPRALU_SOLVE
#endif
#endif

/**
 * Constructor. Takes a sparse matrix in compressed column storage 
 * format (vals[], row_ind[], col_ptr[]) and return a pointer to a fresh 
 * object self. In the compressed column storage, the matrix elements 
 * are filled into the array vals by running down the columns. Each time
 * a column is started, the index of vals is added to jcol_ptr. By 
 * convention, the n-th+1 value of jcol_ptr is the number of non-zero
 * values nnz. 
 *
 * @param self object instance (inout).
 * @param vals Matrix elements (array size nnz: in).
 * @param row_ind Row indices of the matrix elements (array size nnz: in).
 * @param col_ptr The vals indices that start a new column (array size n+1: in).
 * @param nnz No. of non-zero elements (in).
 * @param n Rank of square matrix (in).
 * @param info Error flag, info=0 means ok (out).
 *
 * @see dsupralu_del_
 */
void dsupralu_new_(dsupralu_sparse_type **self,
		   double *vals,
		   int *row_ind, int *col_ptr,
		   int *nnz, int *n, int *info);

/**
 * Destructor. Clean-up and reclaim the memory. Every call to dsupralu_new_
 * should be matched by a call to dsupralu_del_.
 *
 * @param self object instance (inout).
 * @param info Error flag, info=0 means ok (out).
 *
 * @see dsupralu_new_
 */
void dsupralu_del_(dsupralu_sparse_type **self, int *info);

/**
 * Vector dot matrix multiplication. The array sizes must match the 
 * rank of the sparse matrix object.
 *
 * @param self object instance (inout).
 * @param vector Array (in).
 * @param res Result of vector dot matrix (out)
 * @param info Error flag, info=0 means ok (out).
 */
void dsupralu_vector_dot_matrix_(dsupralu_sparse_type **self, 
				double *vector, double *res,
				 int *info);

/** 
 * Matrix dot vector multiplication. The array sizes must match the 
 * rank of the sparse matrix object.
 *
 * @param self object instance (inout).
 * @param vector Array (in)
 * @param res Result of matrix dot vector multiplication (out).
 * @param info Error flag, info=0 means ok (out).
 */
void dsupralu_matrix_dot_vector_(dsupralu_sparse_type **self,
				double *vector, double *res,
				 int *info);

/**
 * Vector dot matrix dot vector multiplication. The array sizes must match the 
 * rank of the sparse matrix object.
 * 
 * @param self object instance (inout).
 * @param vector1 Array (in).
 * @param vector2 Array (in).
 * @param res Result of vector1 dot matrix dot vector2 multiplication (out).
 * @param info Error flag, info=0 means ok (out).
 */
void dsupralu_vector_dot_matrix_dot_vector_(dsupralu_sparse_type **self, 
				double *vector1, double *vector2,
					    double *res, int *info);

/**
 * Compute the column permutation vector. Invoke this prior to performing the 
 * LU decomposition when solving linear systems. For details on Column 
 * permutation specification, see http://crd.lbl.gov/~xiaoye/SuperLU/.
 *
 * @param self object instance (inout).
 * @param permc_spec Column permutation specification: 0=natural ordering, 1=A'*A, 2=A'+A, 3=minimum degree for unsymmetric matrices (in).
 * @info info Error flag, info=0 means ok (out).
 *
 * @see dsupralu_colperm_
 */
void dsupralu_colperm_(dsupralu_sparse_type **self, 
		       int *permc_spec, int *info);

/**
 * Perform the LU decomposition. Invoke this after dsupralu_colperm_ but 
 * before calling dsupralu_solve_ or dsupralu_determinant_. 
 *
 * @param self object instance (inout).
 * @param info Error flag, info=0 means ok (out).
 *
 * @see dsupralu_colperm_, dsupralu_solve_, dsupralu_determinant_
 */
void dsupralu_lu_(dsupralu_sparse_type **self, int *info);

/**
 * Compute the determinant. Invoke this after calling dsupralu_lu_.
 *
 * @param self object instance (inout).
 * @param res_mantissa Determinant is res_mantissa * 2^res_exponent (out).
 * @param res_exponent Exponent, see above (out).
 * @param info Error flag, info=0 means ok (out).
 *
 * @see dsupralu_lu_
 */
void dsupralu_determinant_(dsupralu_sparse_type **self,
			   double *res_mantissa, int *res_exponent,
			   int *info);

/**
 * Solve linear system. Invoke this after calling dsupralu_lu_.
 *
 * @param self object instance (inout).
 * @param b Right-hand side vector of same rank as sparse matrix object, will be overwritten by the solution vector (inout)
 * @param info Error flag, info=0 means ok (out).
 *
 * @see dsupralu_lu_
 */
void dsupralu_solve_(dsupralu_sparse_type **self, 
		     double *b, int *info);



#endif /* _DSUPRALU_TYPE */
