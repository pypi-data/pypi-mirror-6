#!/usr/bin/env python
# $Id: superlu.py,v 1.9 2013/12/20 22:58:30 pletzer Exp $

"""
Solver based on SuperLU (Real)

A. Pletzer May 4 2001
"""

import dsupralu, sparse, vector

def toCCS(amat):
	"""
	Conversion to Column Compressed Storage (CCS). Return 3 arrays:
	[values, row_indices, col_ptr]
	
	Assume indexing is zero based!
	"""

	import time
	tic = time.time()
	[m, n] = amat.size()
	print('time to get the matrix size ', time.time()-tic)
	print(n)
	values=[]
	row_indices=[]
	col_ptr=[]
	tic = time.time()
	for i in range(m):
		col_ptr.append(len(values))
		for j in range(n):
			if (j,i) in amat:
				values.append(amat[(j,i)])
				row_indices.append(j)
	col_ptr.append(len(values))
	print('time to iterate ', time.time()-tic)
	return [values, row_indices, col_ptr]

def solve(amat, rhs):
	"""
	Solve the linear system Amat * x = rhs.

	amat: the sparse matrix {(i,j):val, ...}
	rhs: the right hand side vector, a list of values [val0, val1,...]

	A solution to the linear system is returned as a vector
	"""

	[m, n] = amat.size()
	handle = dsupralu.new(amat, n)
	# column permutation
	# 0 natural ordering
	# 1 minimum degree on structure of A'*A
	# 2 minimum degree on structure of A'+A
	# 3 approximate minimum degree for unsymmetric matrices
	cperm = 2
	dsupralu.colperm(handle[0], cperm)
	dsupralu.lu(handle[0])
	return vector.vector(dsupralu.solve(handle[0], rhs))


#.........................................................................

if __name__=='__main__':
	
	import sparse, vector, dsupralu

	for i in range(11):

		amat = sparse.sparse({
		(0,0):1.,
		(1,0):2.,
		(0,1):3.,
		(1,1):4.,
		(2,2):5.,
		    })
		amat.out()
		[m,n] = amat.size()
		print('calling dsupralu.new')
		h1, h2 = dsupralu.new(amat, n)
		print('h1=', h1, ' h2=', h2)
		b = [0., 1., 2.]
		x = [1., 0., 1.]
		print('dsupralu.vector_dot_matrix(h1, b)=', \
		  dsupralu.vector_dot_matrix(h1, b))
		print('dsupralu.matrix_dot_vector(h1, b)=', \
		  dsupralu.matrix_dot_vector(h1, b))
		print('dsupralu.vector_dot_matrix_dot_vector(h1, b, x)=', \
		  dsupralu.vector_dot_matrix_dot_vector(h1, b, x))
		cperm = 2
		print('calling dsupralu.colperm')
		dsupralu.colperm(h1, cperm)
		print('calling dsupralu.lu')
		dsupralu.lu(h1)
		print('dsupralu.det(h1)=', dsupralu.det(h1))
		rhs=vector.vector([0., 1., 0.])
		print('calling dsupralu.solve')
		v = dsupralu.solve(h1, rhs)
		print('v=', v)
		print('checking...')
		v = dsupralu.matrix_dot_vector(h1, v)
		print('error = ', vector.norm(vector.vector(v) - rhs))
		print('calling dsupralu.SOLVE')
		dsupralu.SOLVE(h1, rhs)
		print('rhs=', rhs)

