#include "f2c.h"

integer icamax_(integer *n, complex *cx, integer *incx)
{
    /* System generated locals */
    integer ret_val, i__1, i__2;
    real r__1, r__2;
    /* Builtin functions */
    double r_imag(complex *);
    /* Local variables */
    static real smax;
    static integer i, ix;
/*     finds the index of element having max. absolute value.   
       jack dongarra, linpack, 3/11/78.   
       modified 3/93 to return if incx .le. 0.   
       modified 12/3/93, array(1) declarations changed to array(*)   
    
   Parameter adjustments   
       Function Body */
#define CX(I) cx[(I)-1]
    ret_val = 0;
    if (*n < 1 || *incx <= 0) {
	return ret_val;
    }
    ret_val = 1;
    if (*n == 1) {
	return ret_val;
    }
    if (*incx == 1) {
	goto L20;
    }
/*        code for increment not equal to 1 */
    ix = 1;
    smax = (r__1 = CX(1).r, dabs(r__1)) + (r__2 = r_imag(&CX(1)), dabs(r__2));
    ix += *incx;
    i__1 = *n;
    for (i = 2; i <= *n; ++i) {
	i__2 = ix;
	if ((r__1 = CX(ix).r, dabs(r__1)) + (r__2 = r_imag(&CX(ix)), dabs(
		r__2)) <= smax) {
	    goto L5;
	}
	ret_val = i;
	i__2 = ix;
	smax = (r__1 = CX(ix).r, dabs(r__1)) + (r__2 = r_imag(&CX(ix)), 
		dabs(r__2));
L5:
	ix += *incx;
/* L10: */
    }
    return ret_val;
/*        code for increment equal to 1 */
L20:
    smax = (r__1 = CX(1).r, dabs(r__1)) + (r__2 = r_imag(&CX(1)), dabs(r__2));
    i__1 = *n;
    for (i = 2; i <= *n; ++i) {
	i__2 = i;
	if ((r__1 = CX(i).r, dabs(r__1)) + (r__2 = r_imag(&CX(i)), dabs(
		r__2)) <= smax) {
	    goto L30;
	}
	ret_val = i;
	i__2 = i;
	smax = (r__1 = CX(i).r, dabs(r__1)) + (r__2 = r_imag(&CX(i)), dabs(
		r__2));
L30:
	;
    }
    return ret_val;
} /* icamax_ */



/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

integer idamax_(integer *n, doublereal *dx, integer *incx)
{


    /* System generated locals */
    integer ret_val, i__1;
    doublereal d__1;

    /* Local variables */
    static doublereal dmax__;
    static integer i, ix;


/*     finds the index of element having max. absolute value.   
       jack dongarra, linpack, 3/11/78.   
       modified 3/93 to return if incx .le. 0.   
       modified 12/3/93, array(1) declarations changed to array(*)   


    
   Parameter adjustments   
       Function Body */
#define DX(I) dx[(I)-1]


    ret_val = 0;
    if (*n < 1 || *incx <= 0) {
	return ret_val;
    }
    ret_val = 1;
    if (*n == 1) {
	return ret_val;
    }
    if (*incx == 1) {
	goto L20;
    }

/*        code for increment not equal to 1 */

    ix = 1;
    dmax__ = abs(DX(1));
    ix += *incx;
    i__1 = *n;
    for (i = 2; i <= *n; ++i) {
	if ((d__1 = DX(ix), abs(d__1)) <= dmax__) {
	    goto L5;
	}
	ret_val = i;
	dmax__ = (d__1 = DX(ix), abs(d__1));
L5:
	ix += *incx;
/* L10: */
    }
    return ret_val;

/*        code for increment equal to 1 */

L20:
    dmax__ = abs(DX(1));
    i__1 = *n;
    for (i = 2; i <= *n; ++i) {
	if ((d__1 = DX(i), abs(d__1)) <= dmax__) {
	    goto L30;
	}
	ret_val = i;
	dmax__ = (d__1 = DX(i), abs(d__1));
L30:
	;
    }
    return ret_val;
} /* idamax_ */


/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

integer isamax_(integer *n, real *sx, integer *incx)
{


    /* System generated locals */
    integer ret_val, i__1;
    real r__1;

    /* Local variables */
    static real smax;
    static integer i, ix;


/*     finds the index of element having max. absolute value.   
       jack dongarra, linpack, 3/11/78.   
       modified 3/93 to return if incx .le. 0.   
       modified 12/3/93, array(1) declarations changed to array(*)   


    
   Parameter adjustments   
       Function Body */
#define SX(I) sx[(I)-1]


    ret_val = 0;
    if (*n < 1 || *incx <= 0) {
	return ret_val;
    }
    ret_val = 1;
    if (*n == 1) {
	return ret_val;
    }
    if (*incx == 1) {
	goto L20;
    }

/*        code for increment not equal to 1 */

    ix = 1;
    smax = dabs(SX(1));
    ix += *incx;
    i__1 = *n;
    for (i = 2; i <= *n; ++i) {
	if ((r__1 = SX(ix), dabs(r__1)) <= smax) {
	    goto L5;
	}
	ret_val = i;
	smax = (r__1 = SX(ix), dabs(r__1));
L5:
	ix += *incx;
/* L10: */
    }
    return ret_val;

/*        code for increment equal to 1 */

L20:
    smax = dabs(SX(1));
    i__1 = *n;
    for (i = 2; i <= *n; ++i) {
	if ((r__1 = SX(i), dabs(r__1)) <= smax) {
	    goto L30;
	}
	ret_val = i;
	smax = (r__1 = SX(i), dabs(r__1));
L30:
	;
    }
    return ret_val;
} /* isamax_ */


/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

integer izamax_(integer *n, doublecomplex *zx, integer *incx)
{


    /* System generated locals */
    integer ret_val, i__1;

    /* Local variables */
    static doublereal smax;
    static integer i;
    extern doublereal dcabs1_(doublecomplex *);
    static integer ix;


/*     finds the index of element having max. absolute value.   
       jack dongarra, 1/15/85.   
       modified 3/93 to return if incx .le. 0.   
       modified 12/3/93, array(1) declarations changed to array(*)   


    
   Parameter adjustments   
       Function Body */
#define ZX(I) zx[(I)-1]


    ret_val = 0;
    if (*n < 1 || *incx <= 0) {
	return ret_val;
    }
    ret_val = 1;
    if (*n == 1) {
	return ret_val;
    }
    if (*incx == 1) {
	goto L20;
    }

/*        code for increment not equal to 1 */

    ix = 1;
    smax = dcabs1_(&ZX(1));
    ix += *incx;
    i__1 = *n;
    for (i = 2; i <= *n; ++i) {
	if (dcabs1_(&ZX(ix)) <= smax) {
	    goto L5;
	}
	ret_val = i;
	smax = dcabs1_(&ZX(ix));
L5:
	ix += *incx;
/* L10: */
    }
    return ret_val;

/*        code for increment equal to 1 */

L20:
    smax = dcabs1_(&ZX(1));
    i__1 = *n;
    for (i = 2; i <= *n; ++i) {
	if (dcabs1_(&ZX(i)) <= smax) {
	    goto L30;
	}
	ret_val = i;
	smax = dcabs1_(&ZX(i));
L30:
	;
    }
    return ret_val;
} /* izamax_ */


/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

/* Subroutine */ int zaxpy_(integer *n, doublecomplex *za, doublecomplex *zx, 
	integer *incx, doublecomplex *zy, integer *incy)
{


    /* System generated locals */
    integer i__1, i__2, i__3, i__4;
    doublecomplex z__1, z__2;

    /* Local variables */
    static integer i;
    extern doublereal dcabs1_(doublecomplex *);
    static integer ix, iy;


/*     constant times a vector plus a vector.   
       jack dongarra, 3/11/78.   
       modified 12/3/93, array(1) declarations changed to array(*)   

    
   Parameter adjustments   
       Function Body */
#define ZY(I) zy[(I)-1]
#define ZX(I) zx[(I)-1]


    if (*n <= 0) {
	return 0;
    }
    if (dcabs1_(za) == 0.) {
	return 0;
    }
    if (*incx == 1 && *incy == 1) {
	goto L20;
    }

/*        code for unequal increments or equal increments   
            not equal to 1 */

    ix = 1;
    iy = 1;
    if (*incx < 0) {
	ix = (-(*n) + 1) * *incx + 1;
    }
    if (*incy < 0) {
	iy = (-(*n) + 1) * *incy + 1;
    }
    i__1 = *n;
    for (i = 1; i <= *n; ++i) {
	i__2 = iy;
	i__3 = iy;
	i__4 = ix;
	z__2.r = za->r * ZX(ix).r - za->i * ZX(ix).i, z__2.i = za->r * ZX(
		ix).i + za->i * ZX(ix).r;
	z__1.r = ZY(iy).r + z__2.r, z__1.i = ZY(iy).i + z__2.i;
	ZY(iy).r = z__1.r, ZY(iy).i = z__1.i;
	ix += *incx;
	iy += *incy;
/* L10: */
    }
    return 0;

/*        code for both increments equal to 1 */

L20:
    i__1 = *n;
    for (i = 1; i <= *n; ++i) {
	i__2 = i;
	i__3 = i;
	i__4 = i;
	z__2.r = za->r * ZX(i).r - za->i * ZX(i).i, z__2.i = za->r * ZX(
		i).i + za->i * ZX(i).r;
	z__1.r = ZY(i).r + z__2.r, z__1.i = ZY(i).i + z__2.i;
	ZY(i).r = z__1.r, ZY(i).i = z__1.i;
/* L30: */
    }
    return 0;
} /* zaxpy_ */


/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

/* Subroutine */ int zcopy_(integer *n, doublecomplex *zx, integer *incx, 
	doublecomplex *zy, integer *incy)
{


    /* System generated locals */
    integer i__1, i__2, i__3;

    /* Local variables */
    static integer i, ix, iy;


/*     copies a vector, x, to a vector, y.   
       jack dongarra, linpack, 4/11/78.   
       modified 12/3/93, array(1) declarations changed to array(*)   


    
   Parameter adjustments   
       Function Body */
#define ZY(I) zy[(I)-1]
#define ZX(I) zx[(I)-1]


    if (*n <= 0) {
	return 0;
    }
    if (*incx == 1 && *incy == 1) {
	goto L20;
    }

/*        code for unequal increments or equal increments   
            not equal to 1 */

    ix = 1;
    iy = 1;
    if (*incx < 0) {
	ix = (-(*n) + 1) * *incx + 1;
    }
    if (*incy < 0) {
	iy = (-(*n) + 1) * *incy + 1;
    }
    i__1 = *n;
    for (i = 1; i <= *n; ++i) {
	i__2 = iy;
	i__3 = ix;
	ZY(iy).r = ZX(ix).r, ZY(iy).i = ZX(ix).i;
	ix += *incx;
	iy += *incy;
/* L10: */
    }
    return 0;

/*        code for both increments equal to 1 */

L20:
    i__1 = *n;
    for (i = 1; i <= *n; ++i) {
	i__2 = i;
	i__3 = i;
	ZY(i).r = ZX(i).r, ZY(i).i = ZX(i).i;
/* L30: */
    }
    return 0;
} /* zcopy_ */

/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

/* Double Complex */ VOID zdotc_(doublecomplex * ret_val, integer *n, 
	doublecomplex *zx, integer *incx, doublecomplex *zy, integer *incy)
{
    /* System generated locals */
    integer i__1, i__2;
    doublecomplex z__1, z__2, z__3;

    /* Builtin functions */
    void d_cnjg(doublecomplex *, doublecomplex *);

    /* Local variables */
    static integer i;
    static doublecomplex ztemp;
    static integer ix, iy;


/*     forms the dot product of a vector.   
       jack dongarra, 3/11/78.   
       modified 12/3/93, array(1) declarations changed to array(*)   

    
   Parameter adjustments */
    --zy;
    --zx;

    /* Function Body */
    ztemp.r = 0., ztemp.i = 0.;
     ret_val->r = 0.,  ret_val->i = 0.;
    if (*n <= 0) {
	return ;
    }
    if (*incx == 1 && *incy == 1) {
	goto L20;
    }

/*        code for unequal increments or equal increments   
            not equal to 1 */

    ix = 1;
    iy = 1;
    if (*incx < 0) {
	ix = (-(*n) + 1) * *incx + 1;
    }
    if (*incy < 0) {
	iy = (-(*n) + 1) * *incy + 1;
    }
    i__1 = *n;
    for (i = 1; i <= *n; ++i) {
	d_cnjg(&z__3, &zx[ix]);
	i__2 = iy;
	z__2.r = z__3.r * zy[iy].r - z__3.i * zy[iy].i, z__2.i = z__3.r * 
		zy[iy].i + z__3.i * zy[iy].r;
	z__1.r = ztemp.r + z__2.r, z__1.i = ztemp.i + z__2.i;
	ztemp.r = z__1.r, ztemp.i = z__1.i;
	ix += *incx;
	iy += *incy;
/* L10: */
    }
     ret_val->r = ztemp.r,  ret_val->i = ztemp.i;
    return ;

/*        code for both increments equal to 1 */

L20:
    i__1 = *n;
    for (i = 1; i <= *n; ++i) {
	d_cnjg(&z__3, &zx[i]);
	i__2 = i;
	z__2.r = z__3.r * zy[i].r - z__3.i * zy[i].i, z__2.i = z__3.r * 
		zy[i].i + z__3.i * zy[i].r;
	z__1.r = ztemp.r + z__2.r, z__1.i = ztemp.i + z__2.i;
	ztemp.r = z__1.r, ztemp.i = z__1.i;
/* L30: */
    }
     ret_val->r = ztemp.r,  ret_val->i = ztemp.i;
    return ;
} /* zdotc_ */


/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

/* Subroutine */ int zgemv_(char *trans, integer *m, integer *n, 
	doublecomplex *alpha, doublecomplex *a, integer *lda, doublecomplex *
	x, integer *incx, doublecomplex *beta, doublecomplex *y, integer *
	incy)
{


    /* System generated locals */
    integer a_dim1, a_offset, i__1, i__2, i__3, i__4, i__5;
    doublecomplex z__1, z__2, z__3;

    /* Builtin functions */
    void d_cnjg(doublecomplex *, doublecomplex *);

    /* Local variables */
    static integer info;
    static doublecomplex temp;
    static integer lenx, leny, i, j;
    extern logical lsame_(char *, char *);
    static integer ix, iy, jx, jy, kx, ky;
    extern /* Subroutine */ int xerbla_(char *, integer *);
    static logical noconj;


/*  Purpose   
    =======   

    ZGEMV  performs one of the matrix-vector operations   

       y := alpha*A*x + beta*y,   or   y := alpha*A'*x + beta*y,   or   

       y := alpha*conjg( A' )*x + beta*y,   

    where alpha and beta are scalars, x and y are vectors and A is an   
    m by n matrix.   

    Parameters   
    ==========   

    TRANS  - CHARACTER*1.   
             On entry, TRANS specifies the operation to be performed as   
             follows:   

                TRANS = 'N' or 'n'   y := alpha*A*x + beta*y.   

                TRANS = 'T' or 't'   y := alpha*A'*x + beta*y.   

                TRANS = 'C' or 'c'   y := alpha*conjg( A' )*x + beta*y.   

             Unchanged on exit.   

    M      - INTEGER.   
             On entry, M specifies the number of rows of the matrix A.   
             M must be at least zero.   
             Unchanged on exit.   

    N      - INTEGER.   
             On entry, N specifies the number of columns of the matrix A. 
  
             N must be at least zero.   
             Unchanged on exit.   

    ALPHA  - COMPLEX*16      .   
             On entry, ALPHA specifies the scalar alpha.   
             Unchanged on exit.   

    A      - COMPLEX*16       array of DIMENSION ( LDA, n ).   
             Before entry, the leading m by n part of the array A must   
             contain the matrix of coefficients.   
             Unchanged on exit.   

    LDA    - INTEGER.   
             On entry, LDA specifies the first dimension of A as declared 
  
             in the calling (sub) program. LDA must be at least   
             max( 1, m ).   
             Unchanged on exit.   

    X      - COMPLEX*16       array of DIMENSION at least   
             ( 1 + ( n - 1 )*abs( INCX ) ) when TRANS = 'N' or 'n'   
             and at least   
             ( 1 + ( m - 1 )*abs( INCX ) ) otherwise.   
             Before entry, the incremented array X must contain the   
             vector x.   
             Unchanged on exit.   

    INCX   - INTEGER.   
             On entry, INCX specifies the increment for the elements of   
             X. INCX must not be zero.   
             Unchanged on exit.   

    BETA   - COMPLEX*16      .   
             On entry, BETA specifies the scalar beta. When BETA is   
             supplied as zero then Y need not be set on input.   
             Unchanged on exit.   

    Y      - COMPLEX*16       array of DIMENSION at least   
             ( 1 + ( m - 1 )*abs( INCY ) ) when TRANS = 'N' or 'n'   
             and at least   
             ( 1 + ( n - 1 )*abs( INCY ) ) otherwise.   
             Before entry with BETA non-zero, the incremented array Y   
             must contain the vector y. On exit, Y is overwritten by the 
  
             updated vector y.   

    INCY   - INTEGER.   
             On entry, INCY specifies the increment for the elements of   
             Y. INCY must not be zero.   
             Unchanged on exit.   


    Level 2 Blas routine.   

    -- Written on 22-October-1986.   
       Jack Dongarra, Argonne National Lab.   
       Jeremy Du Croz, Nag Central Office.   
       Sven Hammarling, Nag Central Office.   
       Richard Hanson, Sandia National Labs.   



       Test the input parameters.   

    
   Parameter adjustments   
       Function Body */
#define X(I) x[(I)-1]
#define Y(I) y[(I)-1]

#define A(I,J) a[(I)-1 + ((J)-1)* ( *lda)]

    info = 0;
    if (! lsame_(trans, "N") && ! lsame_(trans, "T") && ! 
	    lsame_(trans, "C")) {
	info = 1;
    } else if (*m < 0) {
	info = 2;
    } else if (*n < 0) {
	info = 3;
    } else if (*lda < max(1,*m)) {
	info = 6;
    } else if (*incx == 0) {
	info = 8;
    } else if (*incy == 0) {
	info = 11;
    }
    if (info != 0) {
	xerbla_("ZGEMV ", &info);
	return 0;
    }

/*     Quick return if possible. */

    if (*m == 0 || *n == 0 || alpha->r == 0. && alpha->i == 0. && (beta->r == 
	    1. && beta->i == 0.)) {
	return 0;
    }

    noconj = lsame_(trans, "T");

/*     Set  LENX  and  LENY, the lengths of the vectors x and y, and set 
  
       up the start points in  X  and  Y. */

    if (lsame_(trans, "N")) {
	lenx = *n;
	leny = *m;
    } else {
	lenx = *m;
	leny = *n;
    }
    if (*incx > 0) {
	kx = 1;
    } else {
	kx = 1 - (lenx - 1) * *incx;
    }
    if (*incy > 0) {
	ky = 1;
    } else {
	ky = 1 - (leny - 1) * *incy;
    }

/*     Start the operations. In this version the elements of A are   
       accessed sequentially with one pass through A.   

       First form  y := beta*y. */

    if (beta->r != 1. || beta->i != 0.) {
	if (*incy == 1) {
	    if (beta->r == 0. && beta->i == 0.) {
		i__1 = leny;
		for (i = 1; i <= leny; ++i) {
		    i__2 = i;
		    Y(i).r = 0., Y(i).i = 0.;
/* L10: */
		}
	    } else {
		i__1 = leny;
		for (i = 1; i <= leny; ++i) {
		    i__2 = i;
		    i__3 = i;
		    z__1.r = beta->r * Y(i).r - beta->i * Y(i).i, 
			    z__1.i = beta->r * Y(i).i + beta->i * Y(i)
			    .r;
		    Y(i).r = z__1.r, Y(i).i = z__1.i;
/* L20: */
		}
	    }
	} else {
	    iy = ky;
	    if (beta->r == 0. && beta->i == 0.) {
		i__1 = leny;
		for (i = 1; i <= leny; ++i) {
		    i__2 = iy;
		    Y(iy).r = 0., Y(iy).i = 0.;
		    iy += *incy;
/* L30: */
		}
	    } else {
		i__1 = leny;
		for (i = 1; i <= leny; ++i) {
		    i__2 = iy;
		    i__3 = iy;
		    z__1.r = beta->r * Y(iy).r - beta->i * Y(iy).i, 
			    z__1.i = beta->r * Y(iy).i + beta->i * Y(iy)
			    .r;
		    Y(iy).r = z__1.r, Y(iy).i = z__1.i;
		    iy += *incy;
/* L40: */
		}
	    }
	}
    }
    if (alpha->r == 0. && alpha->i == 0.) {
	return 0;
    }
    if (lsame_(trans, "N")) {

/*        Form  y := alpha*A*x + y. */

	jx = kx;
	if (*incy == 1) {
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		i__2 = jx;
		if (X(jx).r != 0. || X(jx).i != 0.) {
		    i__2 = jx;
		    z__1.r = alpha->r * X(jx).r - alpha->i * X(jx).i, 
			    z__1.i = alpha->r * X(jx).i + alpha->i * X(jx)
			    .r;
		    temp.r = z__1.r, temp.i = z__1.i;
		    i__2 = *m;
		    for (i = 1; i <= *m; ++i) {
			i__3 = i;
			i__4 = i;
			i__5 = i + j * a_dim1;
			z__2.r = temp.r * A(i,j).r - temp.i * A(i,j).i, 
				z__2.i = temp.r * A(i,j).i + temp.i * A(i,j)
				.r;
			z__1.r = Y(i).r + z__2.r, z__1.i = Y(i).i + 
				z__2.i;
			Y(i).r = z__1.r, Y(i).i = z__1.i;
/* L50: */
		    }
		}
		jx += *incx;
/* L60: */
	    }
	} else {
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		i__2 = jx;
		if (X(jx).r != 0. || X(jx).i != 0.) {
		    i__2 = jx;
		    z__1.r = alpha->r * X(jx).r - alpha->i * X(jx).i, 
			    z__1.i = alpha->r * X(jx).i + alpha->i * X(jx)
			    .r;
		    temp.r = z__1.r, temp.i = z__1.i;
		    iy = ky;
		    i__2 = *m;
		    for (i = 1; i <= *m; ++i) {
			i__3 = iy;
			i__4 = iy;
			i__5 = i + j * a_dim1;
			z__2.r = temp.r * A(i,j).r - temp.i * A(i,j).i, 
				z__2.i = temp.r * A(i,j).i + temp.i * A(i,j)
				.r;
			z__1.r = Y(iy).r + z__2.r, z__1.i = Y(iy).i + 
				z__2.i;
			Y(iy).r = z__1.r, Y(iy).i = z__1.i;
			iy += *incy;
/* L70: */
		    }
		}
		jx += *incx;
/* L80: */
	    }
	}
    } else {

/*        Form  y := alpha*A'*x + y  or  y := alpha*conjg( A' )*x + y.
 */

	jy = ky;
	if (*incx == 1) {
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		temp.r = 0., temp.i = 0.;
		if (noconj) {
		    i__2 = *m;
		    for (i = 1; i <= *m; ++i) {
			i__3 = i + j * a_dim1;
			i__4 = i;
			z__2.r = A(i,j).r * X(i).r - A(i,j).i * X(i)
				.i, z__2.i = A(i,j).r * X(i).i + A(i,j)
				.i * X(i).r;
			z__1.r = temp.r + z__2.r, z__1.i = temp.i + z__2.i;
			temp.r = z__1.r, temp.i = z__1.i;
/* L90: */
		    }
		} else {
		    i__2 = *m;
		    for (i = 1; i <= *m; ++i) {
			d_cnjg(&z__3, &A(i,j));
			i__3 = i;
			z__2.r = z__3.r * X(i).r - z__3.i * X(i).i, 
				z__2.i = z__3.r * X(i).i + z__3.i * X(i)
				.r;
			z__1.r = temp.r + z__2.r, z__1.i = temp.i + z__2.i;
			temp.r = z__1.r, temp.i = z__1.i;
/* L100: */
		    }
		}
		i__2 = jy;
		i__3 = jy;
		z__2.r = alpha->r * temp.r - alpha->i * temp.i, z__2.i = 
			alpha->r * temp.i + alpha->i * temp.r;
		z__1.r = Y(jy).r + z__2.r, z__1.i = Y(jy).i + z__2.i;
		Y(jy).r = z__1.r, Y(jy).i = z__1.i;
		jy += *incy;
/* L110: */
	    }
	} else {
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		temp.r = 0., temp.i = 0.;
		ix = kx;
		if (noconj) {
		    i__2 = *m;
		    for (i = 1; i <= *m; ++i) {
			i__3 = i + j * a_dim1;
			i__4 = ix;
			z__2.r = A(i,j).r * X(ix).r - A(i,j).i * X(ix)
				.i, z__2.i = A(i,j).r * X(ix).i + A(i,j)
				.i * X(ix).r;
			z__1.r = temp.r + z__2.r, z__1.i = temp.i + z__2.i;
			temp.r = z__1.r, temp.i = z__1.i;
			ix += *incx;
/* L120: */
		    }
		} else {
		    i__2 = *m;
		    for (i = 1; i <= *m; ++i) {
			d_cnjg(&z__3, &A(i,j));
			i__3 = ix;
			z__2.r = z__3.r * X(ix).r - z__3.i * X(ix).i, 
				z__2.i = z__3.r * X(ix).i + z__3.i * X(ix)
				.r;
			z__1.r = temp.r + z__2.r, z__1.i = temp.i + z__2.i;
			temp.r = z__1.r, temp.i = z__1.i;
			ix += *incx;
/* L130: */
		    }
		}
		i__2 = jy;
		i__3 = jy;
		z__2.r = alpha->r * temp.r - alpha->i * temp.i, z__2.i = 
			alpha->r * temp.i + alpha->i * temp.r;
		z__1.r = Y(jy).r + z__2.r, z__1.i = Y(jy).i + z__2.i;
		Y(jy).r = z__1.r, Y(jy).i = z__1.i;
		jy += *incy;
/* L140: */
	    }
	}
    }

    return 0;

/*     End of ZGEMV . */

} /* zgemv_ */


/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

/* Subroutine */ int zgerc_(integer *m, integer *n, doublecomplex *alpha, 
	doublecomplex *x, integer *incx, doublecomplex *y, integer *incy, 
	doublecomplex *a, integer *lda)
{


    /* System generated locals */
    integer a_dim1, a_offset, i__1, i__2, i__3, i__4, i__5;
    doublecomplex z__1, z__2;

    /* Builtin functions */
    void d_cnjg(doublecomplex *, doublecomplex *);

    /* Local variables */
    static integer info;
    static doublecomplex temp;
    static integer i, j, ix, jy, kx;
    extern /* Subroutine */ int xerbla_(char *, integer *);


/*  Purpose   
    =======   

    ZGERC  performs the rank 1 operation   

       A := alpha*x*conjg( y' ) + A,   

    where alpha is a scalar, x is an m element vector, y is an n element 
  
    vector and A is an m by n matrix.   

    Parameters   
    ==========   

    M      - INTEGER.   
             On entry, M specifies the number of rows of the matrix A.   
             M must be at least zero.   
             Unchanged on exit.   

    N      - INTEGER.   
             On entry, N specifies the number of columns of the matrix A. 
  
             N must be at least zero.   
             Unchanged on exit.   

    ALPHA  - COMPLEX*16      .   
             On entry, ALPHA specifies the scalar alpha.   
             Unchanged on exit.   

    X      - COMPLEX*16       array of dimension at least   
             ( 1 + ( m - 1 )*abs( INCX ) ).   
             Before entry, the incremented array X must contain the m   
             element vector x.   
             Unchanged on exit.   

    INCX   - INTEGER.   
             On entry, INCX specifies the increment for the elements of   
             X. INCX must not be zero.   
             Unchanged on exit.   

    Y      - COMPLEX*16       array of dimension at least   
             ( 1 + ( n - 1 )*abs( INCY ) ).   
             Before entry, the incremented array Y must contain the n   
             element vector y.   
             Unchanged on exit.   

    INCY   - INTEGER.   
             On entry, INCY specifies the increment for the elements of   
             Y. INCY must not be zero.   
             Unchanged on exit.   

    A      - COMPLEX*16       array of DIMENSION ( LDA, n ).   
             Before entry, the leading m by n part of the array A must   
             contain the matrix of coefficients. On exit, A is   
             overwritten by the updated matrix.   

    LDA    - INTEGER.   
             On entry, LDA specifies the first dimension of A as declared 
  
             in the calling (sub) program. LDA must be at least   
             max( 1, m ).   
             Unchanged on exit.   


    Level 2 Blas routine.   

    -- Written on 22-October-1986.   
       Jack Dongarra, Argonne National Lab.   
       Jeremy Du Croz, Nag Central Office.   
       Sven Hammarling, Nag Central Office.   
       Richard Hanson, Sandia National Labs.   



       Test the input parameters.   

    
   Parameter adjustments   
       Function Body */
#define X(I) x[(I)-1]
#define Y(I) y[(I)-1]

#define A(I,J) a[(I)-1 + ((J)-1)* ( *lda)]

    info = 0;
    if (*m < 0) {
	info = 1;
    } else if (*n < 0) {
	info = 2;
    } else if (*incx == 0) {
	info = 5;
    } else if (*incy == 0) {
	info = 7;
    } else if (*lda < max(1,*m)) {
	info = 9;
    }
    if (info != 0) {
	xerbla_("ZGERC ", &info);
	return 0;
    }

/*     Quick return if possible. */

    if (*m == 0 || *n == 0 || alpha->r == 0. && alpha->i == 0.) {
	return 0;
    }

/*     Start the operations. In this version the elements of A are   
       accessed sequentially with one pass through A. */

    if (*incy > 0) {
	jy = 1;
    } else {
	jy = 1 - (*n - 1) * *incy;
    }
    if (*incx == 1) {
	i__1 = *n;
	for (j = 1; j <= *n; ++j) {
	    i__2 = jy;
	    if (Y(jy).r != 0. || Y(jy).i != 0.) {
		d_cnjg(&z__2, &Y(jy));
		z__1.r = alpha->r * z__2.r - alpha->i * z__2.i, z__1.i = 
			alpha->r * z__2.i + alpha->i * z__2.r;
		temp.r = z__1.r, temp.i = z__1.i;
		i__2 = *m;
		for (i = 1; i <= *m; ++i) {
		    i__3 = i + j * a_dim1;
		    i__4 = i + j * a_dim1;
		    i__5 = i;
		    z__2.r = X(i).r * temp.r - X(i).i * temp.i, z__2.i =
			     X(i).r * temp.i + X(i).i * temp.r;
		    z__1.r = A(i,j).r + z__2.r, z__1.i = A(i,j).i + z__2.i;
		    A(i,j).r = z__1.r, A(i,j).i = z__1.i;
/* L10: */
		}
	    }
	    jy += *incy;
/* L20: */
	}
    } else {
	if (*incx > 0) {
	    kx = 1;
	} else {
	    kx = 1 - (*m - 1) * *incx;
	}
	i__1 = *n;
	for (j = 1; j <= *n; ++j) {
	    i__2 = jy;
	    if (Y(jy).r != 0. || Y(jy).i != 0.) {
		d_cnjg(&z__2, &Y(jy));
		z__1.r = alpha->r * z__2.r - alpha->i * z__2.i, z__1.i = 
			alpha->r * z__2.i + alpha->i * z__2.r;
		temp.r = z__1.r, temp.i = z__1.i;
		ix = kx;
		i__2 = *m;
		for (i = 1; i <= *m; ++i) {
		    i__3 = i + j * a_dim1;
		    i__4 = i + j * a_dim1;
		    i__5 = ix;
		    z__2.r = X(ix).r * temp.r - X(ix).i * temp.i, z__2.i =
			     X(ix).r * temp.i + X(ix).i * temp.r;
		    z__1.r = A(i,j).r + z__2.r, z__1.i = A(i,j).i + z__2.i;
		    A(i,j).r = z__1.r, A(i,j).i = z__1.i;
		    ix += *incx;
/* L30: */
		}
	    }
	    jy += *incy;
/* L40: */
	}
    }

    return 0;

/*     End of ZGERC . */

} /* zgerc_ */


/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

/* Subroutine */ int zhemv_(char *uplo, integer *n, doublecomplex *alpha, 
	doublecomplex *a, integer *lda, doublecomplex *x, integer *incx, 
	doublecomplex *beta, doublecomplex *y, integer *incy)
{


    /* System generated locals */
    integer a_dim1, a_offset, i__1, i__2, i__3, i__4, i__5;
    doublereal d__1;
    doublecomplex z__1, z__2, z__3, z__4;

    /* Builtin functions */
    void d_cnjg(doublecomplex *, doublecomplex *);

    /* Local variables */
    static integer info;
    static doublecomplex temp1, temp2;
    static integer i, j;
    extern logical lsame_(char *, char *);
    static integer ix, iy, jx, jy, kx, ky;
    extern /* Subroutine */ int xerbla_(char *, integer *);


/*  Purpose   
    =======   

    ZHEMV  performs the matrix-vector  operation   

       y := alpha*A*x + beta*y,   

    where alpha and beta are scalars, x and y are n element vectors and   
    A is an n by n hermitian matrix.   

    Parameters   
    ==========   

    UPLO   - CHARACTER*1.   
             On entry, UPLO specifies whether the upper or lower   
             triangular part of the array A is to be referenced as   
             follows:   

                UPLO = 'U' or 'u'   Only the upper triangular part of A   
                                    is to be referenced.   

                UPLO = 'L' or 'l'   Only the lower triangular part of A   
                                    is to be referenced.   

             Unchanged on exit.   

    N      - INTEGER.   
             On entry, N specifies the order of the matrix A.   
             N must be at least zero.   
             Unchanged on exit.   

    ALPHA  - COMPLEX*16      .   
             On entry, ALPHA specifies the scalar alpha.   
             Unchanged on exit.   

    A      - COMPLEX*16       array of DIMENSION ( LDA, n ).   
             Before entry with  UPLO = 'U' or 'u', the leading n by n   
             upper triangular part of the array A must contain the upper 
  
             triangular part of the hermitian matrix and the strictly   
             lower triangular part of A is not referenced.   
             Before entry with UPLO = 'L' or 'l', the leading n by n   
             lower triangular part of the array A must contain the lower 
  
             triangular part of the hermitian matrix and the strictly   
             upper triangular part of A is not referenced.   
             Note that the imaginary parts of the diagonal elements need 
  
             not be set and are assumed to be zero.   
             Unchanged on exit.   

    LDA    - INTEGER.   
             On entry, LDA specifies the first dimension of A as declared 
  
             in the calling (sub) program. LDA must be at least   
             max( 1, n ).   
             Unchanged on exit.   

    X      - COMPLEX*16       array of dimension at least   
             ( 1 + ( n - 1 )*abs( INCX ) ).   
             Before entry, the incremented array X must contain the n   
             element vector x.   
             Unchanged on exit.   

    INCX   - INTEGER.   
             On entry, INCX specifies the increment for the elements of   
             X. INCX must not be zero.   
             Unchanged on exit.   

    BETA   - COMPLEX*16      .   
             On entry, BETA specifies the scalar beta. When BETA is   
             supplied as zero then Y need not be set on input.   
             Unchanged on exit.   

    Y      - COMPLEX*16       array of dimension at least   
             ( 1 + ( n - 1 )*abs( INCY ) ).   
             Before entry, the incremented array Y must contain the n   
             element vector y. On exit, Y is overwritten by the updated   
             vector y.   

    INCY   - INTEGER.   
             On entry, INCY specifies the increment for the elements of   
             Y. INCY must not be zero.   
             Unchanged on exit.   


    Level 2 Blas routine.   

    -- Written on 22-October-1986.   
       Jack Dongarra, Argonne National Lab.   
       Jeremy Du Croz, Nag Central Office.   
       Sven Hammarling, Nag Central Office.   
       Richard Hanson, Sandia National Labs.   



       Test the input parameters.   

    
   Parameter adjustments   
       Function Body */
#define X(I) x[(I)-1]
#define Y(I) y[(I)-1]

#define A(I,J) a[(I)-1 + ((J)-1)* ( *lda)]

    info = 0;
    if (! lsame_(uplo, "U") && ! lsame_(uplo, "L")) {
	info = 1;
    } else if (*n < 0) {
	info = 2;
    } else if (*lda < max(1,*n)) {
	info = 5;
    } else if (*incx == 0) {
	info = 7;
    } else if (*incy == 0) {
	info = 10;
    }
    if (info != 0) {
	xerbla_("ZHEMV ", &info);
	return 0;
    }

/*     Quick return if possible. */

    if (*n == 0 || alpha->r == 0. && alpha->i == 0. && (beta->r == 1. && 
	    beta->i == 0.)) {
	return 0;
    }

/*     Set up the start points in  X  and  Y. */

    if (*incx > 0) {
	kx = 1;
    } else {
	kx = 1 - (*n - 1) * *incx;
    }
    if (*incy > 0) {
	ky = 1;
    } else {
	ky = 1 - (*n - 1) * *incy;
    }

/*     Start the operations. In this version the elements of A are   
       accessed sequentially with one pass through the triangular part   
       of A.   

       First form  y := beta*y. */

    if (beta->r != 1. || beta->i != 0.) {
	if (*incy == 1) {
	    if (beta->r == 0. && beta->i == 0.) {
		i__1 = *n;
		for (i = 1; i <= *n; ++i) {
		    i__2 = i;
		    Y(i).r = 0., Y(i).i = 0.;
/* L10: */
		}
	    } else {
		i__1 = *n;
		for (i = 1; i <= *n; ++i) {
		    i__2 = i;
		    i__3 = i;
		    z__1.r = beta->r * Y(i).r - beta->i * Y(i).i, 
			    z__1.i = beta->r * Y(i).i + beta->i * Y(i)
			    .r;
		    Y(i).r = z__1.r, Y(i).i = z__1.i;
/* L20: */
		}
	    }
	} else {
	    iy = ky;
	    if (beta->r == 0. && beta->i == 0.) {
		i__1 = *n;
		for (i = 1; i <= *n; ++i) {
		    i__2 = iy;
		    Y(iy).r = 0., Y(iy).i = 0.;
		    iy += *incy;
/* L30: */
		}
	    } else {
		i__1 = *n;
		for (i = 1; i <= *n; ++i) {
		    i__2 = iy;
		    i__3 = iy;
		    z__1.r = beta->r * Y(iy).r - beta->i * Y(iy).i, 
			    z__1.i = beta->r * Y(iy).i + beta->i * Y(iy)
			    .r;
		    Y(iy).r = z__1.r, Y(iy).i = z__1.i;
		    iy += *incy;
/* L40: */
		}
	    }
	}
    }
    if (alpha->r == 0. && alpha->i == 0.) {
	return 0;
    }
    if (lsame_(uplo, "U")) {

/*        Form  y  when A is stored in upper triangle. */

	if (*incx == 1 && *incy == 1) {
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		i__2 = j;
		z__1.r = alpha->r * X(j).r - alpha->i * X(j).i, z__1.i =
			 alpha->r * X(j).i + alpha->i * X(j).r;
		temp1.r = z__1.r, temp1.i = z__1.i;
		temp2.r = 0., temp2.i = 0.;
		i__2 = j - 1;
		for (i = 1; i <= j-1; ++i) {
		    i__3 = i;
		    i__4 = i;
		    i__5 = i + j * a_dim1;
		    z__2.r = temp1.r * A(i,j).r - temp1.i * A(i,j).i, 
			    z__2.i = temp1.r * A(i,j).i + temp1.i * A(i,j)
			    .r;
		    z__1.r = Y(i).r + z__2.r, z__1.i = Y(i).i + z__2.i;
		    Y(i).r = z__1.r, Y(i).i = z__1.i;
		    d_cnjg(&z__3, &A(i,j));
		    i__3 = i;
		    z__2.r = z__3.r * X(i).r - z__3.i * X(i).i, z__2.i =
			     z__3.r * X(i).i + z__3.i * X(i).r;
		    z__1.r = temp2.r + z__2.r, z__1.i = temp2.i + z__2.i;
		    temp2.r = z__1.r, temp2.i = z__1.i;
/* L50: */
		}
		i__2 = j;
		i__3 = j;
		i__4 = j + j * a_dim1;
		d__1 = A(j,j).r;
		z__3.r = d__1 * temp1.r, z__3.i = d__1 * temp1.i;
		z__2.r = Y(j).r + z__3.r, z__2.i = Y(j).i + z__3.i;
		z__4.r = alpha->r * temp2.r - alpha->i * temp2.i, z__4.i = 
			alpha->r * temp2.i + alpha->i * temp2.r;
		z__1.r = z__2.r + z__4.r, z__1.i = z__2.i + z__4.i;
		Y(j).r = z__1.r, Y(j).i = z__1.i;
/* L60: */
	    }
	} else {
	    jx = kx;
	    jy = ky;
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		i__2 = jx;
		z__1.r = alpha->r * X(jx).r - alpha->i * X(jx).i, z__1.i =
			 alpha->r * X(jx).i + alpha->i * X(jx).r;
		temp1.r = z__1.r, temp1.i = z__1.i;
		temp2.r = 0., temp2.i = 0.;
		ix = kx;
		iy = ky;
		i__2 = j - 1;
		for (i = 1; i <= j-1; ++i) {
		    i__3 = iy;
		    i__4 = iy;
		    i__5 = i + j * a_dim1;
		    z__2.r = temp1.r * A(i,j).r - temp1.i * A(i,j).i, 
			    z__2.i = temp1.r * A(i,j).i + temp1.i * A(i,j)
			    .r;
		    z__1.r = Y(iy).r + z__2.r, z__1.i = Y(iy).i + z__2.i;
		    Y(iy).r = z__1.r, Y(iy).i = z__1.i;
		    d_cnjg(&z__3, &A(i,j));
		    i__3 = ix;
		    z__2.r = z__3.r * X(ix).r - z__3.i * X(ix).i, z__2.i =
			     z__3.r * X(ix).i + z__3.i * X(ix).r;
		    z__1.r = temp2.r + z__2.r, z__1.i = temp2.i + z__2.i;
		    temp2.r = z__1.r, temp2.i = z__1.i;
		    ix += *incx;
		    iy += *incy;
/* L70: */
		}
		i__2 = jy;
		i__3 = jy;
		i__4 = j + j * a_dim1;
		d__1 = A(j,j).r;
		z__3.r = d__1 * temp1.r, z__3.i = d__1 * temp1.i;
		z__2.r = Y(jy).r + z__3.r, z__2.i = Y(jy).i + z__3.i;
		z__4.r = alpha->r * temp2.r - alpha->i * temp2.i, z__4.i = 
			alpha->r * temp2.i + alpha->i * temp2.r;
		z__1.r = z__2.r + z__4.r, z__1.i = z__2.i + z__4.i;
		Y(jy).r = z__1.r, Y(jy).i = z__1.i;
		jx += *incx;
		jy += *incy;
/* L80: */
	    }
	}
    } else {

/*        Form  y  when A is stored in lower triangle. */

	if (*incx == 1 && *incy == 1) {
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		i__2 = j;
		z__1.r = alpha->r * X(j).r - alpha->i * X(j).i, z__1.i =
			 alpha->r * X(j).i + alpha->i * X(j).r;
		temp1.r = z__1.r, temp1.i = z__1.i;
		temp2.r = 0., temp2.i = 0.;
		i__2 = j;
		i__3 = j;
		i__4 = j + j * a_dim1;
		d__1 = A(j,j).r;
		z__2.r = d__1 * temp1.r, z__2.i = d__1 * temp1.i;
		z__1.r = Y(j).r + z__2.r, z__1.i = Y(j).i + z__2.i;
		Y(j).r = z__1.r, Y(j).i = z__1.i;
		i__2 = *n;
		for (i = j + 1; i <= *n; ++i) {
		    i__3 = i;
		    i__4 = i;
		    i__5 = i + j * a_dim1;
		    z__2.r = temp1.r * A(i,j).r - temp1.i * A(i,j).i, 
			    z__2.i = temp1.r * A(i,j).i + temp1.i * A(i,j)
			    .r;
		    z__1.r = Y(i).r + z__2.r, z__1.i = Y(i).i + z__2.i;
		    Y(i).r = z__1.r, Y(i).i = z__1.i;
		    d_cnjg(&z__3, &A(i,j));
		    i__3 = i;
		    z__2.r = z__3.r * X(i).r - z__3.i * X(i).i, z__2.i =
			     z__3.r * X(i).i + z__3.i * X(i).r;
		    z__1.r = temp2.r + z__2.r, z__1.i = temp2.i + z__2.i;
		    temp2.r = z__1.r, temp2.i = z__1.i;
/* L90: */
		}
		i__2 = j;
		i__3 = j;
		z__2.r = alpha->r * temp2.r - alpha->i * temp2.i, z__2.i = 
			alpha->r * temp2.i + alpha->i * temp2.r;
		z__1.r = Y(j).r + z__2.r, z__1.i = Y(j).i + z__2.i;
		Y(j).r = z__1.r, Y(j).i = z__1.i;
/* L100: */
	    }
	} else {
	    jx = kx;
	    jy = ky;
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		i__2 = jx;
		z__1.r = alpha->r * X(jx).r - alpha->i * X(jx).i, z__1.i =
			 alpha->r * X(jx).i + alpha->i * X(jx).r;
		temp1.r = z__1.r, temp1.i = z__1.i;
		temp2.r = 0., temp2.i = 0.;
		i__2 = jy;
		i__3 = jy;
		i__4 = j + j * a_dim1;
		d__1 = A(j,j).r;
		z__2.r = d__1 * temp1.r, z__2.i = d__1 * temp1.i;
		z__1.r = Y(jy).r + z__2.r, z__1.i = Y(jy).i + z__2.i;
		Y(jy).r = z__1.r, Y(jy).i = z__1.i;
		ix = jx;
		iy = jy;
		i__2 = *n;
		for (i = j + 1; i <= *n; ++i) {
		    ix += *incx;
		    iy += *incy;
		    i__3 = iy;
		    i__4 = iy;
		    i__5 = i + j * a_dim1;
		    z__2.r = temp1.r * A(i,j).r - temp1.i * A(i,j).i, 
			    z__2.i = temp1.r * A(i,j).i + temp1.i * A(i,j)
			    .r;
		    z__1.r = Y(iy).r + z__2.r, z__1.i = Y(iy).i + z__2.i;
		    Y(iy).r = z__1.r, Y(iy).i = z__1.i;
		    d_cnjg(&z__3, &A(i,j));
		    i__3 = ix;
		    z__2.r = z__3.r * X(ix).r - z__3.i * X(ix).i, z__2.i =
			     z__3.r * X(ix).i + z__3.i * X(ix).r;
		    z__1.r = temp2.r + z__2.r, z__1.i = temp2.i + z__2.i;
		    temp2.r = z__1.r, temp2.i = z__1.i;
/* L110: */
		}
		i__2 = jy;
		i__3 = jy;
		z__2.r = alpha->r * temp2.r - alpha->i * temp2.i, z__2.i = 
			alpha->r * temp2.i + alpha->i * temp2.r;
		z__1.r = Y(jy).r + z__2.r, z__1.i = Y(jy).i + z__2.i;
		Y(jy).r = z__1.r, Y(jy).i = z__1.i;
		jx += *incx;
		jy += *incy;
/* L120: */
	    }
	}
    }

    return 0;

/*     End of ZHEMV . */

} /* zhemv_ */


/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

/* Subroutine */ int zher2_(char *uplo, integer *n, doublecomplex *alpha, 
	doublecomplex *x, integer *incx, doublecomplex *y, integer *incy, 
	doublecomplex *a, integer *lda)
{


    /* System generated locals */
    integer a_dim1, a_offset, i__1, i__2, i__3, i__4, i__5, i__6;
    doublereal d__1;
    doublecomplex z__1, z__2, z__3, z__4;

    /* Builtin functions */
    void d_cnjg(doublecomplex *, doublecomplex *);

    /* Local variables */
    static integer info;
    static doublecomplex temp1, temp2;
    static integer i, j;
    extern logical lsame_(char *, char *);
    static integer ix, iy, jx, jy, kx, ky;
    extern /* Subroutine */ int xerbla_(char *, integer *);


/*  Purpose   
    =======   

    ZHER2  performs the hermitian rank 2 operation   

       A := alpha*x*conjg( y' ) + conjg( alpha )*y*conjg( x' ) + A,   

    where alpha is a scalar, x and y are n element vectors and A is an n 
  
    by n hermitian matrix.   

    Parameters   
    ==========   

    UPLO   - CHARACTER*1.   
             On entry, UPLO specifies whether the upper or lower   
             triangular part of the array A is to be referenced as   
             follows:   

                UPLO = 'U' or 'u'   Only the upper triangular part of A   
                                    is to be referenced.   

                UPLO = 'L' or 'l'   Only the lower triangular part of A   
                                    is to be referenced.   

             Unchanged on exit.   

    N      - INTEGER.   
             On entry, N specifies the order of the matrix A.   
             N must be at least zero.   
             Unchanged on exit.   

    ALPHA  - COMPLEX*16      .   
             On entry, ALPHA specifies the scalar alpha.   
             Unchanged on exit.   

    X      - COMPLEX*16       array of dimension at least   
             ( 1 + ( n - 1 )*abs( INCX ) ).   
             Before entry, the incremented array X must contain the n   
             element vector x.   
             Unchanged on exit.   

    INCX   - INTEGER.   
             On entry, INCX specifies the increment for the elements of   
             X. INCX must not be zero.   
             Unchanged on exit.   

    Y      - COMPLEX*16       array of dimension at least   
             ( 1 + ( n - 1 )*abs( INCY ) ).   
             Before entry, the incremented array Y must contain the n   
             element vector y.   
             Unchanged on exit.   

    INCY   - INTEGER.   
             On entry, INCY specifies the increment for the elements of   
             Y. INCY must not be zero.   
             Unchanged on exit.   

    A      - COMPLEX*16       array of DIMENSION ( LDA, n ).   
             Before entry with  UPLO = 'U' or 'u', the leading n by n   
             upper triangular part of the array A must contain the upper 
  
             triangular part of the hermitian matrix and the strictly   
             lower triangular part of A is not referenced. On exit, the   
             upper triangular part of the array A is overwritten by the   
             upper triangular part of the updated matrix.   
             Before entry with UPLO = 'L' or 'l', the leading n by n   
             lower triangular part of the array A must contain the lower 
  
             triangular part of the hermitian matrix and the strictly   
             upper triangular part of A is not referenced. On exit, the   
             lower triangular part of the array A is overwritten by the   
             lower triangular part of the updated matrix.   
             Note that the imaginary parts of the diagonal elements need 
  
             not be set, they are assumed to be zero, and on exit they   
             are set to zero.   

    LDA    - INTEGER.   
             On entry, LDA specifies the first dimension of A as declared 
  
             in the calling (sub) program. LDA must be at least   
             max( 1, n ).   
             Unchanged on exit.   


    Level 2 Blas routine.   

    -- Written on 22-October-1986.   
       Jack Dongarra, Argonne National Lab.   
       Jeremy Du Croz, Nag Central Office.   
       Sven Hammarling, Nag Central Office.   
       Richard Hanson, Sandia National Labs.   



       Test the input parameters.   

    
   Parameter adjustments   
       Function Body */
#define X(I) x[(I)-1]
#define Y(I) y[(I)-1]

#define A(I,J) a[(I)-1 + ((J)-1)* ( *lda)]

    info = 0;
    if (! lsame_(uplo, "U") && ! lsame_(uplo, "L")) {
	info = 1;
    } else if (*n < 0) {
	info = 2;
    } else if (*incx == 0) {
	info = 5;
    } else if (*incy == 0) {
	info = 7;
    } else if (*lda < max(1,*n)) {
	info = 9;
    }
    if (info != 0) {
	xerbla_("ZHER2 ", &info);
	return 0;
    }

/*     Quick return if possible. */

    if (*n == 0 || alpha->r == 0. && alpha->i == 0.) {
	return 0;
    }

/*     Set up the start points in X and Y if the increments are not both 
  
       unity. */

    if (*incx != 1 || *incy != 1) {
	if (*incx > 0) {
	    kx = 1;
	} else {
	    kx = 1 - (*n - 1) * *incx;
	}
	if (*incy > 0) {
	    ky = 1;
	} else {
	    ky = 1 - (*n - 1) * *incy;
	}
	jx = kx;
	jy = ky;
    }

/*     Start the operations. In this version the elements of A are   
       accessed sequentially with one pass through the triangular part   
       of A. */

    if (lsame_(uplo, "U")) {

/*        Form  A  when A is stored in the upper triangle. */

	if (*incx == 1 && *incy == 1) {
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		i__2 = j;
		i__3 = j;
		if (X(j).r != 0. || X(j).i != 0. || (Y(j).r != 0. || 
			Y(j).i != 0.)) {
		    d_cnjg(&z__2, &Y(j));
		    z__1.r = alpha->r * z__2.r - alpha->i * z__2.i, z__1.i = 
			    alpha->r * z__2.i + alpha->i * z__2.r;
		    temp1.r = z__1.r, temp1.i = z__1.i;
		    i__2 = j;
		    z__2.r = alpha->r * X(j).r - alpha->i * X(j).i, 
			    z__2.i = alpha->r * X(j).i + alpha->i * X(j)
			    .r;
		    d_cnjg(&z__1, &z__2);
		    temp2.r = z__1.r, temp2.i = z__1.i;
		    i__2 = j - 1;
		    for (i = 1; i <= j-1; ++i) {
			i__3 = i + j * a_dim1;
			i__4 = i + j * a_dim1;
			i__5 = i;
			z__3.r = X(i).r * temp1.r - X(i).i * temp1.i, 
				z__3.i = X(i).r * temp1.i + X(i).i * 
				temp1.r;
			z__2.r = A(i,j).r + z__3.r, z__2.i = A(i,j).i + 
				z__3.i;
			i__6 = i;
			z__4.r = Y(i).r * temp2.r - Y(i).i * temp2.i, 
				z__4.i = Y(i).r * temp2.i + Y(i).i * 
				temp2.r;
			z__1.r = z__2.r + z__4.r, z__1.i = z__2.i + z__4.i;
			A(i,j).r = z__1.r, A(i,j).i = z__1.i;
/* L10: */
		    }
		    i__2 = j + j * a_dim1;
		    i__3 = j + j * a_dim1;
		    i__4 = j;
		    z__2.r = X(j).r * temp1.r - X(j).i * temp1.i, 
			    z__2.i = X(j).r * temp1.i + X(j).i * 
			    temp1.r;
		    i__5 = j;
		    z__3.r = Y(j).r * temp2.r - Y(j).i * temp2.i, 
			    z__3.i = Y(j).r * temp2.i + Y(j).i * 
			    temp2.r;
		    z__1.r = z__2.r + z__3.r, z__1.i = z__2.i + z__3.i;
		    d__1 = A(j,j).r + z__1.r;
		    A(j,j).r = d__1, A(j,j).i = 0.;
		} else {
		    i__2 = j + j * a_dim1;
		    i__3 = j + j * a_dim1;
		    d__1 = A(j,j).r;
		    A(j,j).r = d__1, A(j,j).i = 0.;
		}
/* L20: */
	    }
	} else {
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		i__2 = jx;
		i__3 = jy;
		if (X(jx).r != 0. || X(jx).i != 0. || (Y(jy).r != 0. || 
			Y(jy).i != 0.)) {
		    d_cnjg(&z__2, &Y(jy));
		    z__1.r = alpha->r * z__2.r - alpha->i * z__2.i, z__1.i = 
			    alpha->r * z__2.i + alpha->i * z__2.r;
		    temp1.r = z__1.r, temp1.i = z__1.i;
		    i__2 = jx;
		    z__2.r = alpha->r * X(jx).r - alpha->i * X(jx).i, 
			    z__2.i = alpha->r * X(jx).i + alpha->i * X(jx)
			    .r;
		    d_cnjg(&z__1, &z__2);
		    temp2.r = z__1.r, temp2.i = z__1.i;
		    ix = kx;
		    iy = ky;
		    i__2 = j - 1;
		    for (i = 1; i <= j-1; ++i) {
			i__3 = i + j * a_dim1;
			i__4 = i + j * a_dim1;
			i__5 = ix;
			z__3.r = X(ix).r * temp1.r - X(ix).i * temp1.i, 
				z__3.i = X(ix).r * temp1.i + X(ix).i * 
				temp1.r;
			z__2.r = A(i,j).r + z__3.r, z__2.i = A(i,j).i + 
				z__3.i;
			i__6 = iy;
			z__4.r = Y(iy).r * temp2.r - Y(iy).i * temp2.i, 
				z__4.i = Y(iy).r * temp2.i + Y(iy).i * 
				temp2.r;
			z__1.r = z__2.r + z__4.r, z__1.i = z__2.i + z__4.i;
			A(i,j).r = z__1.r, A(i,j).i = z__1.i;
			ix += *incx;
			iy += *incy;
/* L30: */
		    }
		    i__2 = j + j * a_dim1;
		    i__3 = j + j * a_dim1;
		    i__4 = jx;
		    z__2.r = X(jx).r * temp1.r - X(jx).i * temp1.i, 
			    z__2.i = X(jx).r * temp1.i + X(jx).i * 
			    temp1.r;
		    i__5 = jy;
		    z__3.r = Y(jy).r * temp2.r - Y(jy).i * temp2.i, 
			    z__3.i = Y(jy).r * temp2.i + Y(jy).i * 
			    temp2.r;
		    z__1.r = z__2.r + z__3.r, z__1.i = z__2.i + z__3.i;
		    d__1 = A(j,j).r + z__1.r;
		    A(j,j).r = d__1, A(j,j).i = 0.;
		} else {
		    i__2 = j + j * a_dim1;
		    i__3 = j + j * a_dim1;
		    d__1 = A(j,j).r;
		    A(j,j).r = d__1, A(j,j).i = 0.;
		}
		jx += *incx;
		jy += *incy;
/* L40: */
	    }
	}
    } else {

/*        Form  A  when A is stored in the lower triangle. */

	if (*incx == 1 && *incy == 1) {
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		i__2 = j;
		i__3 = j;
		if (X(j).r != 0. || X(j).i != 0. || (Y(j).r != 0. || 
			Y(j).i != 0.)) {
		    d_cnjg(&z__2, &Y(j));
		    z__1.r = alpha->r * z__2.r - alpha->i * z__2.i, z__1.i = 
			    alpha->r * z__2.i + alpha->i * z__2.r;
		    temp1.r = z__1.r, temp1.i = z__1.i;
		    i__2 = j;
		    z__2.r = alpha->r * X(j).r - alpha->i * X(j).i, 
			    z__2.i = alpha->r * X(j).i + alpha->i * X(j)
			    .r;
		    d_cnjg(&z__1, &z__2);
		    temp2.r = z__1.r, temp2.i = z__1.i;
		    i__2 = j + j * a_dim1;
		    i__3 = j + j * a_dim1;
		    i__4 = j;
		    z__2.r = X(j).r * temp1.r - X(j).i * temp1.i, 
			    z__2.i = X(j).r * temp1.i + X(j).i * 
			    temp1.r;
		    i__5 = j;
		    z__3.r = Y(j).r * temp2.r - Y(j).i * temp2.i, 
			    z__3.i = Y(j).r * temp2.i + Y(j).i * 
			    temp2.r;
		    z__1.r = z__2.r + z__3.r, z__1.i = z__2.i + z__3.i;
		    d__1 = A(j,j).r + z__1.r;
		    A(j,j).r = d__1, A(j,j).i = 0.;
		    i__2 = *n;
		    for (i = j + 1; i <= *n; ++i) {
			i__3 = i + j * a_dim1;
			i__4 = i + j * a_dim1;
			i__5 = i;
			z__3.r = X(i).r * temp1.r - X(i).i * temp1.i, 
				z__3.i = X(i).r * temp1.i + X(i).i * 
				temp1.r;
			z__2.r = A(i,j).r + z__3.r, z__2.i = A(i,j).i + 
				z__3.i;
			i__6 = i;
			z__4.r = Y(i).r * temp2.r - Y(i).i * temp2.i, 
				z__4.i = Y(i).r * temp2.i + Y(i).i * 
				temp2.r;
			z__1.r = z__2.r + z__4.r, z__1.i = z__2.i + z__4.i;
			A(i,j).r = z__1.r, A(i,j).i = z__1.i;
/* L50: */
		    }
		} else {
		    i__2 = j + j * a_dim1;
		    i__3 = j + j * a_dim1;
		    d__1 = A(j,j).r;
		    A(j,j).r = d__1, A(j,j).i = 0.;
		}
/* L60: */
	    }
	} else {
	    i__1 = *n;
	    for (j = 1; j <= *n; ++j) {
		i__2 = jx;
		i__3 = jy;
		if (X(jx).r != 0. || X(jx).i != 0. || (Y(jy).r != 0. || 
			Y(jy).i != 0.)) {
		    d_cnjg(&z__2, &Y(jy));
		    z__1.r = alpha->r * z__2.r - alpha->i * z__2.i, z__1.i = 
			    alpha->r * z__2.i + alpha->i * z__2.r;
		    temp1.r = z__1.r, temp1.i = z__1.i;
		    i__2 = jx;
		    z__2.r = alpha->r * X(jx).r - alpha->i * X(jx).i, 
			    z__2.i = alpha->r * X(jx).i + alpha->i * X(jx)
			    .r;
		    d_cnjg(&z__1, &z__2);
		    temp2.r = z__1.r, temp2.i = z__1.i;
		    i__2 = j + j * a_dim1;
		    i__3 = j + j * a_dim1;
		    i__4 = jx;
		    z__2.r = X(jx).r * temp1.r - X(jx).i * temp1.i, 
			    z__2.i = X(jx).r * temp1.i + X(jx).i * 
			    temp1.r;
		    i__5 = jy;
		    z__3.r = Y(jy).r * temp2.r - Y(jy).i * temp2.i, 
			    z__3.i = Y(jy).r * temp2.i + Y(jy).i * 
			    temp2.r;
		    z__1.r = z__2.r + z__3.r, z__1.i = z__2.i + z__3.i;
		    d__1 = A(j,j).r + z__1.r;
		    A(j,j).r = d__1, A(j,j).i = 0.;
		    ix = jx;
		    iy = jy;
		    i__2 = *n;
		    for (i = j + 1; i <= *n; ++i) {
			ix += *incx;
			iy += *incy;
			i__3 = i + j * a_dim1;
			i__4 = i + j * a_dim1;
			i__5 = ix;
			z__3.r = X(ix).r * temp1.r - X(ix).i * temp1.i, 
				z__3.i = X(ix).r * temp1.i + X(ix).i * 
				temp1.r;
			z__2.r = A(i,j).r + z__3.r, z__2.i = A(i,j).i + 
				z__3.i;
			i__6 = iy;
			z__4.r = Y(iy).r * temp2.r - Y(iy).i * temp2.i, 
				z__4.i = Y(iy).r * temp2.i + Y(iy).i * 
				temp2.r;
			z__1.r = z__2.r + z__4.r, z__1.i = z__2.i + z__4.i;
			A(i,j).r = z__1.r, A(i,j).i = z__1.i;
/* L70: */
		    }
		} else {
		    i__2 = j + j * a_dim1;
		    i__3 = j + j * a_dim1;
		    d__1 = A(j,j).r;
		    A(j,j).r = d__1, A(j,j).i = 0.;
		}
		jx += *incx;
		jy += *incy;
/* L80: */
	    }
	}
    }

    return 0;

/*     End of ZHER2 . */

} /* zher2_ */



/*
 * -- SuperLU routine (version 2.0) --
 * Univ. of California Berkeley, Xerox Palo Alto Research Center,
 * and Lawrence Berkeley National Lab.
 * November 15, 1997
 *
 */
/*
 * File name:		zmyblas2.c
 * Purpose:
 *     Level 2 BLAS operations: solves and matvec, written in C.
 * Note:
 *     This is only used when the system lacks an efficient BLAS library.
 */
#include "dcomplex.h"

/*
 * Solves a dense UNIT lower triangular system. The unit lower 
 * triangular matrix is stored in a 2D array M(1:nrow,1:ncol). 
 * The solution will be returned in the rhs vector.
 */
void zlsolve ( int ldm, int ncol, doublecomplex *M, doublecomplex *rhs )
{
    int k;
    doublecomplex x0, x1, x2, x3, temp;
    doublecomplex *M0;
    doublecomplex *Mki0, *Mki1, *Mki2, *Mki3;
    register int firstcol = 0;

    M0 = &M[0];


    while ( firstcol < ncol - 3 ) { /* Do 4 columns */
      	Mki0 = M0 + 1;
      	Mki1 = Mki0 + ldm + 1;
      	Mki2 = Mki1 + ldm + 1;
      	Mki3 = Mki2 + ldm + 1;

      	x0 = rhs[firstcol];
      	zz_mult(&temp, &x0, Mki0); Mki0++;
      	z_sub(&x1, &rhs[firstcol+1], &temp);
      	zz_mult(&temp, &x0, Mki0); Mki0++;
	z_sub(&x2, &rhs[firstcol+2], &temp);
	zz_mult(&temp, &x1, Mki1); Mki1++;
	z_sub(&x2, &x2, &temp);
      	zz_mult(&temp, &x0, Mki0); Mki0++;
	z_sub(&x3, &rhs[firstcol+3], &temp);
	zz_mult(&temp, &x1, Mki1); Mki1++;
	z_sub(&x3, &x3, &temp);
	zz_mult(&temp, &x2, Mki2); Mki2++;
	z_sub(&x3, &x3, &temp);

 	rhs[++firstcol] = x1;
      	rhs[++firstcol] = x2;
      	rhs[++firstcol] = x3;
      	++firstcol;
    
      	for (k = firstcol; k < ncol; k++) {
	    zz_mult(&temp, &x0, Mki0); Mki0++;
	    z_sub(&rhs[k], &rhs[k], &temp);
	    zz_mult(&temp, &x1, Mki1); Mki1++;
	    z_sub(&rhs[k], &rhs[k], &temp);
	    zz_mult(&temp, &x2, Mki2); Mki2++;
	    z_sub(&rhs[k], &rhs[k], &temp);
	    zz_mult(&temp, &x3, Mki3); Mki3++;
	    z_sub(&rhs[k], &rhs[k], &temp);
	}

        M0 += 4 * ldm + 4;
    }

    if ( firstcol < ncol - 1 ) { /* Do 2 columns */
        Mki0 = M0 + 1;
        Mki1 = Mki0 + ldm + 1;

        x0 = rhs[firstcol];
	zz_mult(&temp, &x0, Mki0); Mki0++;
	z_sub(&x1, &rhs[firstcol+1], &temp);

      	rhs[++firstcol] = x1;
      	++firstcol;
    
      	for (k = firstcol; k < ncol; k++) {
	    zz_mult(&temp, &x0, Mki0); Mki0++;
	    z_sub(&rhs[k], &rhs[k], &temp);
	    zz_mult(&temp, &x1, Mki1); Mki1++;
	    z_sub(&rhs[k], &rhs[k], &temp);
	} 
    }
    
}

/*
 * Solves a dense upper triangular system. The upper triangular matrix is
 * stored in a 2-dim array M(1:ldm,1:ncol). The solution will be returned
 * in the rhs vector.
 */
void
zusolve ( ldm, ncol, M, rhs )
int ldm;	/* in */
int ncol;	/* in */
doublecomplex *M;	/* in */
doublecomplex *rhs;	/* modified */
{
    doublecomplex xj, temp;
    int jcol, j, irow;

    jcol = ncol - 1;

    for (j = 0; j < ncol; j++) {

	z_div(&xj, &rhs[jcol], &M[jcol + jcol*ldm]); /* M(jcol, jcol) */
	rhs[jcol] = xj;
	
	for (irow = 0; irow < jcol; irow++) {
	    zz_mult(&temp, &xj, &M[irow+jcol*ldm]); /* M(irow, jcol) */
	    z_sub(&rhs[irow], &rhs[irow], &temp);
	}

	jcol--;

    }
}


/*
 * Performs a dense matrix-vector multiply: Mxvec = Mxvec + M * vec.
 * The input matrix is M(1:nrow,1:ncol); The product is returned in Mxvec[].
 */
void zmatvec ( ldm, nrow, ncol, M, vec, Mxvec )
int ldm;	/* in -- leading dimension of M */
int nrow;	/* in */ 
int ncol;	/* in */
doublecomplex *M;	/* in */
doublecomplex *vec;	/* in */
doublecomplex *Mxvec;	/* in/out */
{
    doublecomplex vi0, vi1, vi2, vi3;
    doublecomplex *M0, temp;
    doublecomplex *Mki0, *Mki1, *Mki2, *Mki3;
    register int firstcol = 0;
    int k;

    M0 = &M[0];

    while ( firstcol < ncol - 3 ) {	/* Do 4 columns */
	Mki0 = M0;
	Mki1 = Mki0 + ldm;
	Mki2 = Mki1 + ldm;
	Mki3 = Mki2 + ldm;

	vi0 = vec[firstcol++];
	vi1 = vec[firstcol++];
	vi2 = vec[firstcol++];
	vi3 = vec[firstcol++];	
	for (k = 0; k < nrow; k++) {
	    zz_mult(&temp, &vi0, Mki0); Mki0++;
	    z_add(&Mxvec[k], &Mxvec[k], &temp);
	    zz_mult(&temp, &vi1, Mki1); Mki1++;
	    z_add(&Mxvec[k], &Mxvec[k], &temp);
	    zz_mult(&temp, &vi2, Mki2); Mki2++;
	    z_add(&Mxvec[k], &Mxvec[k], &temp);
	    zz_mult(&temp, &vi3, Mki3); Mki3++;
	    z_add(&Mxvec[k], &Mxvec[k], &temp);
	}

	M0 += 4 * ldm;
    }

    while ( firstcol < ncol ) {		/* Do 1 column */
 	Mki0 = M0;
	vi0 = vec[firstcol++];
	for (k = 0; k < nrow; k++) {
	    zz_mult(&temp, &vi0, Mki0); Mki0++;
	    z_add(&Mxvec[k], &Mxvec[k], &temp);
	}
	M0 += ldm;
    }
	
}


/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

/* Subroutine */ int zscal_(integer *n, doublecomplex *za, doublecomplex *zx, 
	integer *incx)
{


    /* System generated locals */
    integer i__1, i__2, i__3;
    doublecomplex z__1;

    /* Local variables */
    static integer i, ix;


/*     scales a vector by a constant.   
       jack dongarra, 3/11/78.   
       modified 3/93 to return if incx .le. 0.   
       modified 12/3/93, array(1) declarations changed to array(*)   


    
   Parameter adjustments   
       Function Body */
#define ZX(I) zx[(I)-1]


    if (*n <= 0 || *incx <= 0) {
	return 0;
    }
    if (*incx == 1) {
	goto L20;
    }

/*        code for increment not equal to 1 */

    ix = 1;
    i__1 = *n;
    for (i = 1; i <= *n; ++i) {
	i__2 = ix;
	i__3 = ix;
	z__1.r = za->r * ZX(ix).r - za->i * ZX(ix).i, z__1.i = za->r * ZX(
		ix).i + za->i * ZX(ix).r;
	ZX(ix).r = z__1.r, ZX(ix).i = z__1.i;
	ix += *incx;
/* L10: */
    }
    return 0;

/*        code for increment equal to 1 */

L20:
    i__1 = *n;
    for (i = 1; i <= *n; ++i) {
	i__2 = i;
	i__3 = i;
	z__1.r = za->r * ZX(i).r - za->i * ZX(i).i, z__1.i = za->r * ZX(
		i).i + za->i * ZX(i).r;
	ZX(i).r = z__1.r, ZX(i).i = z__1.i;
/* L30: */
    }
    return 0;
} /* zscal_ */


/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

/* Subroutine */ int ztrsv_(char *uplo, char *trans, char *diag, integer *n, 
	doublecomplex *a, integer *lda, doublecomplex *x, integer *incx)
{


    /* System generated locals */
    integer a_dim1, a_offset, i__1, i__2, i__3, i__4, i__5;
    doublecomplex z__1, z__2, z__3;

    /* Builtin functions */
    void z_div(doublecomplex *, doublecomplex *, doublecomplex *), d_cnjg(
	    doublecomplex *, doublecomplex *);

    /* Local variables */
    static integer info;
    static doublecomplex temp;
    static integer i, j;
    extern logical lsame_(char *, char *);
    static integer ix, jx, kx;
    extern /* Subroutine */ int xerbla_(char *, integer *);
    static logical noconj, nounit;


/*  Purpose   
    =======   

    ZTRSV  solves one of the systems of equations   

       A*x = b,   or   A'*x = b,   or   conjg( A' )*x = b,   

    where b and x are n element vectors and A is an n by n unit, or   
    non-unit, upper or lower triangular matrix.   

    No test for singularity or near-singularity is included in this   
    routine. Such tests must be performed before calling this routine.   

    Parameters   
    ==========   

    UPLO   - CHARACTER*1.   
             On entry, UPLO specifies whether the matrix is an upper or   
             lower triangular matrix as follows:   

                UPLO = 'U' or 'u'   A is an upper triangular matrix.   

                UPLO = 'L' or 'l'   A is a lower triangular matrix.   

             Unchanged on exit.   

    TRANS  - CHARACTER*1.   
             On entry, TRANS specifies the equations to be solved as   
             follows:   

                TRANS = 'N' or 'n'   A*x = b.   

                TRANS = 'T' or 't'   A'*x = b.   

                TRANS = 'C' or 'c'   conjg( A' )*x = b.   

             Unchanged on exit.   

    DIAG   - CHARACTER*1.   
             On entry, DIAG specifies whether or not A is unit   
             triangular as follows:   

                DIAG = 'U' or 'u'   A is assumed to be unit triangular.   

                DIAG = 'N' or 'n'   A is not assumed to be unit   
                                    triangular.   

             Unchanged on exit.   

    N      - INTEGER.   
             On entry, N specifies the order of the matrix A.   
             N must be at least zero.   
             Unchanged on exit.   

    A      - COMPLEX*16       array of DIMENSION ( LDA, n ).   
             Before entry with  UPLO = 'U' or 'u', the leading n by n   
             upper triangular part of the array A must contain the upper 
  
             triangular matrix and the strictly lower triangular part of 
  
             A is not referenced.   
             Before entry with UPLO = 'L' or 'l', the leading n by n   
             lower triangular part of the array A must contain the lower 
  
             triangular matrix and the strictly upper triangular part of 
  
             A is not referenced.   
             Note that when  DIAG = 'U' or 'u', the diagonal elements of 
  
             A are not referenced either, but are assumed to be unity.   
             Unchanged on exit.   

    LDA    - INTEGER.   
             On entry, LDA specifies the first dimension of A as declared 
  
             in the calling (sub) program. LDA must be at least   
             max( 1, n ).   
             Unchanged on exit.   

    X      - COMPLEX*16       array of dimension at least   
             ( 1 + ( n - 1 )*abs( INCX ) ).   
             Before entry, the incremented array X must contain the n   
             element right-hand side vector b. On exit, X is overwritten 
  
             with the solution vector x.   

    INCX   - INTEGER.   
             On entry, INCX specifies the increment for the elements of   
             X. INCX must not be zero.   
             Unchanged on exit.   


    Level 2 Blas routine.   

    -- Written on 22-October-1986.   
       Jack Dongarra, Argonne National Lab.   
       Jeremy Du Croz, Nag Central Office.   
       Sven Hammarling, Nag Central Office.   
       Richard Hanson, Sandia National Labs.   



       Test the input parameters.   

    
   Parameter adjustments   
       Function Body */
#define X(I) x[(I)-1]

#define A(I,J) a[(I)-1 + ((J)-1)* ( *lda)]

    info = 0;
    if (! lsame_(uplo, "U") && ! lsame_(uplo, "L")) {
	info = 1;
    } else if (! lsame_(trans, "N") && ! lsame_(trans, "T") &&
	     ! lsame_(trans, "C")) {
	info = 2;
    } else if (! lsame_(diag, "U") && ! lsame_(diag, "N")) {
	info = 3;
    } else if (*n < 0) {
	info = 4;
    } else if (*lda < max(1,*n)) {
	info = 6;
    } else if (*incx == 0) {
	info = 8;
    }
    if (info != 0) {
	xerbla_("ZTRSV ", &info);
	return 0;
    }

/*     Quick return if possible. */

    if (*n == 0) {
	return 0;
    }

    noconj = lsame_(trans, "T");
    nounit = lsame_(diag, "N");

/*     Set up the start point in X if the increment is not unity. This   
       will be  ( N - 1 )*INCX  too small for descending loops. */

    if (*incx <= 0) {
	kx = 1 - (*n - 1) * *incx;
    } else if (*incx != 1) {
	kx = 1;
    }

/*     Start the operations. In this version the elements of A are   
       accessed sequentially with one pass through A. */

    if (lsame_(trans, "N")) {

/*        Form  x := inv( A )*x. */

	if (lsame_(uplo, "U")) {
	    if (*incx == 1) {
		for (j = *n; j >= 1; --j) {
		    i__1 = j;
		    if (X(j).r != 0. || X(j).i != 0.) {
			if (nounit) {
			    i__1 = j;
			    z_div(&z__1, &X(j), &A(j,j));
			    X(j).r = z__1.r, X(j).i = z__1.i;
			}
			i__1 = j;
			temp.r = X(j).r, temp.i = X(j).i;
			for (i = j - 1; i >= 1; --i) {
			    i__1 = i;
			    i__2 = i;
			    i__3 = i + j * a_dim1;
			    z__2.r = temp.r * A(i,j).r - temp.i * A(i,j).i, 
				    z__2.i = temp.r * A(i,j).i + temp.i * A(i,j).r;
			    z__1.r = X(i).r - z__2.r, z__1.i = X(i).i - 
				    z__2.i;
			    X(i).r = z__1.r, X(i).i = z__1.i;
/* L10: */
			}
		    }
/* L20: */
		}
	    } else {
		jx = kx + (*n - 1) * *incx;
		for (j = *n; j >= 1; --j) {
		    i__1 = jx;
		    if (X(jx).r != 0. || X(jx).i != 0.) {
			if (nounit) {
			    i__1 = jx;
			    z_div(&z__1, &X(jx), &A(j,j));
			    X(jx).r = z__1.r, X(jx).i = z__1.i;
			}
			i__1 = jx;
			temp.r = X(jx).r, temp.i = X(jx).i;
			ix = jx;
			for (i = j - 1; i >= 1; --i) {
			    ix -= *incx;
			    i__1 = ix;
			    i__2 = ix;
			    i__3 = i + j * a_dim1;
			    z__2.r = temp.r * A(i,j).r - temp.i * A(i,j).i, 
				    z__2.i = temp.r * A(i,j).i + temp.i * A(i,j).r;
			    z__1.r = X(ix).r - z__2.r, z__1.i = X(ix).i - 
				    z__2.i;
			    X(ix).r = z__1.r, X(ix).i = z__1.i;
/* L30: */
			}
		    }
		    jx -= *incx;
/* L40: */
		}
	    }
	} else {
	    if (*incx == 1) {
		i__1 = *n;
		for (j = 1; j <= *n; ++j) {
		    i__2 = j;
		    if (X(j).r != 0. || X(j).i != 0.) {
			if (nounit) {
			    i__2 = j;
			    z_div(&z__1, &X(j), &A(j,j));
			    X(j).r = z__1.r, X(j).i = z__1.i;
			}
			i__2 = j;
			temp.r = X(j).r, temp.i = X(j).i;
			i__2 = *n;
			for (i = j + 1; i <= *n; ++i) {
			    i__3 = i;
			    i__4 = i;
			    i__5 = i + j * a_dim1;
			    z__2.r = temp.r * A(i,j).r - temp.i * A(i,j).i, 
				    z__2.i = temp.r * A(i,j).i + temp.i * A(i,j).r;
			    z__1.r = X(i).r - z__2.r, z__1.i = X(i).i - 
				    z__2.i;
			    X(i).r = z__1.r, X(i).i = z__1.i;
/* L50: */
			}
		    }
/* L60: */
		}
	    } else {
		jx = kx;
		i__1 = *n;
		for (j = 1; j <= *n; ++j) {
		    i__2 = jx;
		    if (X(jx).r != 0. || X(jx).i != 0.) {
			if (nounit) {
			    i__2 = jx;
			    z_div(&z__1, &X(jx), &A(j,j));
			    X(jx).r = z__1.r, X(jx).i = z__1.i;
			}
			i__2 = jx;
			temp.r = X(jx).r, temp.i = X(jx).i;
			ix = jx;
			i__2 = *n;
			for (i = j + 1; i <= *n; ++i) {
			    ix += *incx;
			    i__3 = ix;
			    i__4 = ix;
			    i__5 = i + j * a_dim1;
			    z__2.r = temp.r * A(i,j).r - temp.i * A(i,j).i, 
				    z__2.i = temp.r * A(i,j).i + temp.i * A(i,j).r;
			    z__1.r = X(ix).r - z__2.r, z__1.i = X(ix).i - 
				    z__2.i;
			    X(ix).r = z__1.r, X(ix).i = z__1.i;
/* L70: */
			}
		    }
		    jx += *incx;
/* L80: */
		}
	    }
	}
    } else {

/*        Form  x := inv( A' )*x  or  x := inv( conjg( A' ) )*x. */

	if (lsame_(uplo, "U")) {
	    if (*incx == 1) {
		i__1 = *n;
		for (j = 1; j <= *n; ++j) {
		    i__2 = j;
		    temp.r = X(j).r, temp.i = X(j).i;
		    if (noconj) {
			i__2 = j - 1;
			for (i = 1; i <= j-1; ++i) {
			    i__3 = i + j * a_dim1;
			    i__4 = i;
			    z__2.r = A(i,j).r * X(i).r - A(i,j).i * X(
				    i).i, z__2.i = A(i,j).r * X(i).i + 
				    A(i,j).i * X(i).r;
			    z__1.r = temp.r - z__2.r, z__1.i = temp.i - 
				    z__2.i;
			    temp.r = z__1.r, temp.i = z__1.i;
/* L90: */
			}
			if (nounit) {
			    z_div(&z__1, &temp, &A(j,j));
			    temp.r = z__1.r, temp.i = z__1.i;
			}
		    } else {
			i__2 = j - 1;
			for (i = 1; i <= j-1; ++i) {
			    d_cnjg(&z__3, &A(i,j));
			    i__3 = i;
			    z__2.r = z__3.r * X(i).r - z__3.i * X(i).i, 
				    z__2.i = z__3.r * X(i).i + z__3.i * X(
				    i).r;
			    z__1.r = temp.r - z__2.r, z__1.i = temp.i - 
				    z__2.i;
			    temp.r = z__1.r, temp.i = z__1.i;
/* L100: */
			}
			if (nounit) {
			    d_cnjg(&z__2, &A(j,j));
			    z_div(&z__1, &temp, &z__2);
			    temp.r = z__1.r, temp.i = z__1.i;
			}
		    }
		    i__2 = j;
		    X(j).r = temp.r, X(j).i = temp.i;
/* L110: */
		}
	    } else {
		jx = kx;
		i__1 = *n;
		for (j = 1; j <= *n; ++j) {
		    ix = kx;
		    i__2 = jx;
		    temp.r = X(jx).r, temp.i = X(jx).i;
		    if (noconj) {
			i__2 = j - 1;
			for (i = 1; i <= j-1; ++i) {
			    i__3 = i + j * a_dim1;
			    i__4 = ix;
			    z__2.r = A(i,j).r * X(ix).r - A(i,j).i * X(
				    ix).i, z__2.i = A(i,j).r * X(ix).i + 
				    A(i,j).i * X(ix).r;
			    z__1.r = temp.r - z__2.r, z__1.i = temp.i - 
				    z__2.i;
			    temp.r = z__1.r, temp.i = z__1.i;
			    ix += *incx;
/* L120: */
			}
			if (nounit) {
			    z_div(&z__1, &temp, &A(j,j));
			    temp.r = z__1.r, temp.i = z__1.i;
			}
		    } else {
			i__2 = j - 1;
			for (i = 1; i <= j-1; ++i) {
			    d_cnjg(&z__3, &A(i,j));
			    i__3 = ix;
			    z__2.r = z__3.r * X(ix).r - z__3.i * X(ix).i, 
				    z__2.i = z__3.r * X(ix).i + z__3.i * X(
				    ix).r;
			    z__1.r = temp.r - z__2.r, z__1.i = temp.i - 
				    z__2.i;
			    temp.r = z__1.r, temp.i = z__1.i;
			    ix += *incx;
/* L130: */
			}
			if (nounit) {
			    d_cnjg(&z__2, &A(j,j));
			    z_div(&z__1, &temp, &z__2);
			    temp.r = z__1.r, temp.i = z__1.i;
			}
		    }
		    i__2 = jx;
		    X(jx).r = temp.r, X(jx).i = temp.i;
		    jx += *incx;
/* L140: */
		}
	    }
	} else {
	    if (*incx == 1) {
		for (j = *n; j >= 1; --j) {
		    i__1 = j;
		    temp.r = X(j).r, temp.i = X(j).i;
		    if (noconj) {
			i__1 = j + 1;
			for (i = *n; i >= j+1; --i) {
			    i__2 = i + j * a_dim1;
			    i__3 = i;
			    z__2.r = A(i,j).r * X(i).r - A(i,j).i * X(
				    i).i, z__2.i = A(i,j).r * X(i).i + 
				    A(i,j).i * X(i).r;
			    z__1.r = temp.r - z__2.r, z__1.i = temp.i - 
				    z__2.i;
			    temp.r = z__1.r, temp.i = z__1.i;
/* L150: */
			}
			if (nounit) {
			    z_div(&z__1, &temp, &A(j,j));
			    temp.r = z__1.r, temp.i = z__1.i;
			}
		    } else {
			i__1 = j + 1;
			for (i = *n; i >= j+1; --i) {
			    d_cnjg(&z__3, &A(i,j));
			    i__2 = i;
			    z__2.r = z__3.r * X(i).r - z__3.i * X(i).i, 
				    z__2.i = z__3.r * X(i).i + z__3.i * X(
				    i).r;
			    z__1.r = temp.r - z__2.r, z__1.i = temp.i - 
				    z__2.i;
			    temp.r = z__1.r, temp.i = z__1.i;
/* L160: */
			}
			if (nounit) {
			    d_cnjg(&z__2, &A(j,j));
			    z_div(&z__1, &temp, &z__2);
			    temp.r = z__1.r, temp.i = z__1.i;
			}
		    }
		    i__1 = j;
		    X(j).r = temp.r, X(j).i = temp.i;
/* L170: */
		}
	    } else {
		kx += (*n - 1) * *incx;
		jx = kx;
		for (j = *n; j >= 1; --j) {
		    ix = kx;
		    i__1 = jx;
		    temp.r = X(jx).r, temp.i = X(jx).i;
		    if (noconj) {
			i__1 = j + 1;
			for (i = *n; i >= j+1; --i) {
			    i__2 = i + j * a_dim1;
			    i__3 = ix;
			    z__2.r = A(i,j).r * X(ix).r - A(i,j).i * X(
				    ix).i, z__2.i = A(i,j).r * X(ix).i + 
				    A(i,j).i * X(ix).r;
			    z__1.r = temp.r - z__2.r, z__1.i = temp.i - 
				    z__2.i;
			    temp.r = z__1.r, temp.i = z__1.i;
			    ix -= *incx;
/* L180: */
			}
			if (nounit) {
			    z_div(&z__1, &temp, &A(j,j));
			    temp.r = z__1.r, temp.i = z__1.i;
			}
		    } else {
			i__1 = j + 1;
			for (i = *n; i >= j+1; --i) {
			    d_cnjg(&z__3, &A(i,j));
			    i__2 = ix;
			    z__2.r = z__3.r * X(ix).r - z__3.i * X(ix).i, 
				    z__2.i = z__3.r * X(ix).i + z__3.i * X(
				    ix).r;
			    z__1.r = temp.r - z__2.r, z__1.i = temp.i - 
				    z__2.i;
			    temp.r = z__1.r, temp.i = z__1.i;
			    ix -= *incx;
/* L190: */
			}
			if (nounit) {
			    d_cnjg(&z__2, &A(j,j));
			    z_div(&z__1, &temp, &z__2);
			    temp.r = z__1.r, temp.i = z__1.i;
			}
		    }
		    i__1 = jx;
		    X(jx).r = temp.r, X(jx).i = temp.i;
		    jx -= *incx;
/* L200: */
		}
	    }
	}
    }

    return 0;

/*     End of ZTRSV . */

} /* ztrsv_ */

/*  -- translated by f2c (version 19940927).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

doublereal dcabs1_(doublecomplex *z)
{
/* >>Start of File<<   

       System generated locals */
    doublereal ret_val;
    static doublecomplex equiv_0[1];

    /* Local variables */
#define t ((doublereal *)equiv_0)
#define zz (equiv_0)

    zz->r = z->r, zz->i = z->i;
    ret_val = abs(t[0]) + abs(t[1]);
    return ret_val;
} /* dcabs1_ */

#undef zz
#undef t


