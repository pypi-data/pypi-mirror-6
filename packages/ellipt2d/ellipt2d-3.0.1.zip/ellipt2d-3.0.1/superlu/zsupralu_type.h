/* 

$Id: zsupralu_type.h,v 1.3 2003/12/23 19:54:52 pletzer Exp $ 

*/

/**
 * @file
 * @brief Supralu doublecomplex API
 * 
 * This file contains a list of procedures that create, manipulate, 
 * perform standard sparse matrix operations on dense vectors, and
 * destroy a Supralu object. The Superlu object's members are structs
 * defined in the zsp_defs.h header. The API has been written to allow 
 * easy interfacing to other languages, notably Fortran and Python. The
 * address of the object (**self) can be passed as an opaque handle to
 * other languages.
 *
 * In all routines below, the call is successful if the returned value 
 * of the last argument info is zero. The first argument is always the 
 * pointer to the object (**self).
 * 
 * @author A. Pletzer
 */

#ifndef _ZSUPRALU_TYPE
#define _ZSUPRALU_TYPE

#include "zsp_defs.h"

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

} zsupralu_sparse_type;

/* Fortran name mapping */

#if defined( __RS6000) || defined(__HP) || defined(__IBM__)
#define zsupralu_new_ zsupralu_new
#define zsupralu_del_ zsupralu_del
#define zsupralu_vector_dot_matrix_ zsupralu_vector_dot_matrix
#define zsupralu_conj_vector_dot_matrix_ zsupralu_conj_vector_dot_matrix
#define zsupralu_matrix_dot_vector_ zsupralu_matrix_dot_vector
#define zsupralu_vector_dot_matrix_dot_vector_ zsupralu_vector_dot_matrix_dot_vector
#define zsupralu_conj_vector_dot_matrix_dot_vector_ zsupralu_conj_vector_dot_matrix_dot_vector
#define zsupralu_determinant_ zsupralu_determinant
#define zsupralu_solve_ zsupralu_solve
#else
#if defined(__CRAY)
#define zsupralu_new_ ZSUPRALU_NEW
#define zsupralu_del_ ZSUPRALU_DEL
#define zsupralu_vector_dot_matrix_ ZSUPRALU_VECTOR_DOT_MATRIX
#define zsupralu_conj_vector_dot_matrix_ ZSUPRALU_CONJ_VECTOR_DOT_MATRIX
#define zsupralu_matrix_dot_vector_ ZSUPRALU_MATRIX_DOT_VECTOR
#define zsupralu_vector_dot_matrix_dot_vector_ ZSUPRALU_VECTOR_DOT_MATRIX_DOT_VECTOR
#define zsupralu_conj_vector_dot_matrix_dot_vector_ ZSUPRALU_CONJ_VECTOR_DOT_MATRIX_DOT_VECTOR
#define zsupralu_determinant_ ZSUPRALU_DETERMINANT
#define zsupralu_solve_ ZSUPRALU_SOLVE
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
 * @see zsupralu_del_
 */
void zsupralu_new_(zsupralu_sparse_type **self,
		   doublecomplex *vals,
		   int *row_ind, int *col_ptr,
		   int *nnz, int *n, int *info);


/**
 * Destructor. Clean-up and reclaim the memory. Every call to zsupralu_new_
 * should be matched by a call to zsupralu_del_.
 *
 * @param self object instance (inout).
 * @param info Error flag, info=0 means ok (out).
 *
 * @see zsupralu_new_
 */
void zsupralu_del_(zsupralu_sparse_type **self, int *info);

/**
 * Vector dot matrix multiplication. The array sizes must match the 
 * rank of the sparse matrix object.
 *
 * @param self object instance (inout).
 * @param vector Array (in).
 * @param res Result of vector dot matrix (out)
 * @param info Error flag, info=0 means ok (out).
 */
void zsupralu_vector_dot_matrix_(zsupralu_sparse_type **self, 
				doublecomplex *vector, doublecomplex *res,
				 int *info);

/**
 * Conjugate(vector) dot matrix multiplication. The array sizes must match the 
 * rank of the sparse matrix object.
 *
 * @param self object instance (inout).
 * @param vector Array (in).
 * @param res Result of conjugate(vector) dot matrix (out).
 * @param info Error flag, info=0 means ok (out).
 */
void zsupralu_conj_vector_dot_matrix_(zsupralu_sparse_type **self, 
				doublecomplex *vector, doublecomplex *res,
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
void zsupralu_matrix_dot_vector_(zsupralu_sparse_type **self,
				doublecomplex *vector, doublecomplex *res,
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
void zsupralu_vector_dot_matrix_dot_vector_(zsupralu_sparse_type **self, 
				doublecomplex *vector1, doublecomplex *vector2,
					    doublecomplex *res, int *info);

/**
 * Conjugate(vector) dot matrix dot vector multiplication. The array sizes must match the 
 * rank of the sparse matrix object.
 * 
 * @param self object instance (inout).
 * @param vector1 Array (in).
 * @param vector2 Array (in).
 * @param res Result of conjugate(vector1) dot matrix dot vector2 multiplication (out).
 * @param info Error flag, info=0 means ok (out).
 */
void zsupralu_conj_vector_dot_matrix_dot_vector_(zsupralu_sparse_type **self,
				doublecomplex *vector1, doublecomplex *vector2,
						 doublecomplex *res, int *info);

/**
 * Compute the column permutation vector. Invoke this prior to performing the 
 * LU decomposition when solving linear systems. For details on Column 
 * permutation specification, see http://crd.lbl.gov/~xiaoye/SuperLU/.
 *
 * @param self object instance (inout).
 * @param permc_spec Column permutation specification: 0=natural ordering, 1=A'*A, 2=A'+A, 3=minimum degree for unsymmetric matrices (in).
 * @info info Error flag, info=0 means ok (out).
 *
 * @see zsupralu_colperm_
 */
void zsupralu_colperm_(zsupralu_sparse_type **self, 
		       int *permc_spec, int *info);

/**
 * Perform the LU decomposition. Invoke this after zsupralu_colperm_ but 
 * before calling zsupralu_solve_ or zsupralu_determinant_. 
 *
 * @param self object instance (inout).
 * @param info Error flag, info=0 means ok (out).
 *
 * @see zsupralu_colperm_, zsupralu_solve_, zsupralu_determinant_
 */
void zsupralu_lu_(zsupralu_sparse_type **self, int *info);

/**
 * Compute the determinant. Invoke this after calling zsupralu_lu_.
 *
 * @param self object instance (inout).
 * @param res_mantissa Determinant is res_mantissa * 2^res_exponent (out).
 * @param res_exponent Exponent, see above (out).
 * @param info Error flag, info=0 means ok (out).
 *
 * @see zsupralu_lu_
 */
void zsupralu_determinant_(zsupralu_sparse_type **self,
			   doublecomplex *res_mantissa, int *res_exponent,
			   int *info);

/**
 * Solve linear system. Invoke this after calling zsupralu_lu_.
 *
 * @param self object instance (inout).
 * @param b Right-hand side vector of same rank as sparse matrix object, will be overwritten by the solution vector (inout)
 * @param info Error flag, info=0 means ok (out).
 *
 * @see zsupralu_lu_
 */
void zsupralu_solve_(zsupralu_sparse_type **self, 
		     doublecomplex *b, int *info);



#endif /* _ZSUPRALU_TYPE */
