#!/usr/bin/env python
# $Id: csuperlu.py,v 1.13 2013/12/20 22:58:30 pletzer Exp $
"""
Solver based on SuperLU (Complex)

A. Pletzer May 4 2001
"""

def toCCS(amat):
	"""
	Conversion to Column Compressed Storage (CCS). Return 3 arrays:
	[values, row_indices, col_ptr]
	
	Assume indexing is zero based!
	"""

	import time
	tic = time.time()
	[m, n] = amat.size()
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
	print(('time to iterate ', time.time()-tic))
	return [values, row_indices, col_ptr]

def CCS_yDotA(y, values, row_indices, col_ptr):
	
	""" Y^+ . A where A is in CCS """
	
	n = len(y)
	res = cvector.zeros(n)
	for col in range(n):
		for i in range(col_ptr[col], col_ptr[col+1]):
			print(('col=%d i=%d:%d-1'%(col,col_ptr[col], col_ptr[col+1]))) 
			res[col] += y[row_indices[i]].conjugate() * values[i]
	return res
		

def solve(amat, rhs):
	"""
	Solve the linear system Amat * x = rhs.

	amat: the sparse matrix {(i,j):val, ...}
	rhs: the right hand side vector, a list of values [val0, val1,...]

	A solution to the linear system is returned as a vector
	"""

	import zsupralu, cvector
	[m, n] = amat.size()
	handle = zsupralu.new(amat, n)
	# column permutation
	# 0 natural ordering
	# 1 minimum degree on structure of A'*A
	# 2 minimum degree on structure of A'+A
	# 3 approximate minimum degree for unsymmetric matrices
	cperm = 2
	zsupralu.colperm(handle[0], cperm)
	zsupralu.lu(handle[0])
	return cvector.cvector(zsupralu.solve(handle[0], rhs))
	

def eigen(amat, bmat, lambd0, v0, tol=1.e-10, nmax=1000, verbose=0):
	"""
	solve eigenproblem amat*v = lambd bmat*v
	tol: max tolerance |amat*v - lambd bmat*v|
	nmax: max no of iterations
	"""

	try:
		import zsupralu
		import csparse, cvector
	except:
		print('Cannot import csparse or cvector')

	if amat.size()[0] != bmat.size()[0] or \
	   amat.size()[1] != bmat.size()[1] or \
	   len(v0) != amat.size()[1]:
		print('incompatible sizes in eigen')
		print((amat.size()[0], bmat.size()[0]))
		print((amat.size()[1], bmat.size()[1], len(v0)))
		return None

	lambd = lambd0
	v     = v0
	BmatH = zsupralu.new(bmat, bmat.size()[1])

	for i in range(nmax):
		cmat = amat - lambd*bmat
		residue = abs(cvector.norm(csparse.dot(cmat, v)))

		print(('-'*20))
		try:
			print(('iteration %d lambd=(%f,%f) residue=%10.2e' % \
			      (i, lambd.real, lambd.imag, residue)))
		except:
			print(('iteration %d lambd=(%f,0.) residue=%10.2e' % \
			      (i, lambd, residue)))

		if residue < tol: break

		##rhs = csparse.dot(bmat,v)
		rhs = zsupralu.matrix_dot_vector(BmatH[0], v)
		newv = solve(cmat, rhs)
		newv_b_v    = cvector.dot(newv, rhs)
		##newv_b_newv = cvector.dot(newv, csparse.dot(bmat, newv))
		newv_b_newv = zsupralu.vector_dot_matrix_dot_vector(\
			BmatH[0], newv, newv)
							       
		lambd = lambd + newv_b_v/newv_b_newv
		#lambd = lambd + cvector.dot(v, csparse.dot(bmat, v))/cvector.dot(v,csparse.dot(bmat, newv)) 
		v = newv/cvector.norm(newv)
		#v = newv/math.sqrt(abs(newv_b_newv))

	return [lambd, v, residue, i]


#.........................................................................

if __name__=='__main__':
	
	import csparse, cvector, zsupralu

	for i in range(1):
	    amat = csparse.csparse({
		(0,0):1+1j,
		(1,0):2+0j,
		(0,1):3+0j,
		(1,1):4+0j,
		(2,2):5+0j,
		    })
	    amat.out()
	    [m,n] = amat.size()
	    print('calling zsupralu.new')
	    h1, h2 = zsupralu.new(amat, n)
	    print(('h1=', h1, ' h2=', h2))
	    b = [0j, 1+0j, 2j]
	    x = [1+0j, 0j, 1j]
	    print(('zsupralu.vector_dot_matrix(h1, b)=', \
		  zsupralu.vector_dot_matrix(h1, b)))
	    print(('zsupralu.vector_dot_matrix(h1, b, "T")=', \
		  zsupralu.vector_dot_matrix(h1, b, "T")))
	    print(('zsupralu.matrix_dot_vector(h1, b)=', \
		  zsupralu.matrix_dot_vector(h1, b)))
	    print(('zsupralu.vector_dot_matrix_dot_vector(h1, b, x)=', \
		  zsupralu.vector_dot_matrix_dot_vector(h1, b, x)))
	    print(('zsupralu.vector_dot_matrix_dot_vector(h1, b, x, "T")=', \
		  zsupralu.vector_dot_matrix_dot_vector(h1, b, x, "T")))
	    cperm = 2
	    print('calling zsupralu.colperm')
	    zsupralu.colperm(h1, cperm)
	    print('calling zsupralu.lu')
	    zsupralu.lu(h1)
	    print(('zsupralu.det(h1)=', zsupralu.det(h1)))
	    rhs=[0+0j, 1+0j, 0+0j]
	    print('calling zsupralu.solve')
	    v = zsupralu.solve(h1, rhs)
	    print(('v=', v))
	    print('checking...')
	    v = zsupralu.matrix_dot_vector(h1, v)
	    print(('error = ', cvector.norm(cvector.cvector(v) - rhs)))
	    print('calling zsupralu.SOLVE')
	    zsupralu.SOLVE(h1, rhs)
	    print(('rhs=', rhs))
	
	
