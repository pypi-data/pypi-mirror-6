#!/usr/bin/env python
# $Id: csparse.py,v 1.12 2013/12/20 22:51:14 pletzer Exp $
"""
A dictionary based sparse matrix representation (complex)
"""

import cvector
import math, types, operator

"""
A complex sparse matrix class based on a ditionary, supporting matrix (dot)
product and a conjugate gradient solver. Warning: the conjugate gradient
(or bi-conjugate gradient) solver is not guaranteed to converge if the
matrix is not Hermitian.

In this version, the csparse class inherits from the dictionary; this
requires Python 2.2 or later.
"""

class csparse(dict):
	"""
	A complex sparse matrix 
	A. Pletzer 5 Jan 00/12 April 2002

	Dictionary storage format { (i,j): value, ... }
	where (i,j) are the matrix indices
       	"""

	# no c'tor

	def size(self):
		" returns # of rows and columns "
		nrow = 0
		ncol = 0
		for key in list(self.keys()):
			nrow = max([nrow, key[0]+1])
			ncol = max([ncol, key[1]+1])
		return (nrow, ncol)

	def __setitem__(self, ij, val):
		# ensure that val is complex
		super(csparse, self).__setitem__(ij, complex(val))

	def __add__(self, other):
		res = csparse(self.copy())
		for ij in other:
			res[ij] = self.get(ij,0j) + other[ij]
		return res
		
	def __neg__(self):
		return csparse(list(zip(list(self.keys()), list(map(operator.neg, list(self.values()))))))

	def __sub__(self, other):
		res = csparse(self.copy())
		for ij in other:
			res[ij] = self.get(ij,0j) - other[ij]
		return res
		
	def __mul__(self, other):
		" element by element multiplication: other can be scalar or csparse "
		try:
			# other is sparse
			nval = len(other)
			res = csparse()
			if nval < len(self):
				for ij in other:
					res[ij] = self.get(ij,0j)*other[ij]
			else:
				for ij in self:
					res[ij] = self[ij]*other.get(ij,0j)
			return res
		except:
			# other is scalar
			return csparse(list(zip(list(self.keys()), [x*other for x in list(self.values())])))


	def __rmul__(self, other): return self.__mul__(other)

	def __div__(self, other):
		" element by element division self/other: other is scalar"
		return csparse(list(zip(list(self.keys()), [x/other for x in list(self.values())])))
		
	def __rdiv__(self, other):
		" element by element division other/self: other is scalar"
		return csparse(list(zip(list(self.keys()), [other/x for x in list(self.values())])))

	def abs(self):
		return csparse(list(zip(list(self.keys()), list(map(operator.abs, list(self.values()))))))

	def out(self):
		print('# (i, j) -- value')
		for k in list(self.keys()):
			print(k, self[k])

	def plot(self, width_in=400, height_in=400):

		import colormap
                try:
                        import tkinter 
                except:
                        import Tkinter as tkinter

		cmax = max(self.abs().values())
		cmin = min(self.abs().values())
		
		offset =  0.05*min(width_in, height_in)
		xmin, ymin, xmax, ymax = 0,0,self.size()[0], self.size()[1]
		scale =  min(0.9*width_in, 0.9*height_in)/max(xmax-xmin, ymax-ymin)

		root = tkinter.Tk()
		frame = tkinter.Frame(root)
		frame.pack()

		nr, nc = self.size()
		text = tkinter.Label(width=60, height=10,
				     text='nrow=%d ncol=%d\n%d non-zero elements'%\
				     (nr, nc, len(self)))
		text.pack()
		

		canvas = tkinter.Canvas(bg="black", width=width_in, height=height_in)
		canvas.pack()

		for index in list(self.keys()):
			ix, iy = index[0], ymax-index[1]-1
			ya, xa = offset+scale*(ix  ), height_in -offset-scale*(iy  )
			yb, xb = offset+scale*(ix+1), height_in -offset-scale*(iy  )
			yc, xc = offset+scale*(ix+1), height_in -offset-scale*(iy+1)
			yd, xd = offset+scale*(ix  ), height_in -offset-scale*(iy+1)
			color = colormap.strRgb(abs(self[index]), cmin, cmax)
			canvas.create_polygon(xa, ya, xb, yb, xc, yc, xd, yd, fill=color)
		
		root.mainloop()

	def CGsolve(self, x0, b, tol=1.0e-10, nmax = 1000):
		# solve self*x = b and return x using the conjugate gradient method
		if not cvector.isVector(b):
			raise TypeError(self.__class__).with_traceback(' in solve ')
		else:
			if self.size()[0] != len(b) or self.size()[1] != len(b):
				print('**Incompatible sizes in solve')
				print('**size()=', self.size()[0], self.size()[1])
				print('**len=', len(b))
			else:
				kvec = diag(self) # preconditionner
				n = len(b)
				x = x0 # initial guess
				r =  b - dot(self, x)
				w = r/kvec;
				p = cvector.zeros(n);
				beta = 0.0;
				rho = cvector.dot(r, w);
				err = cvector.norm(dot(self,x) - b);
				k = 0
				print(" conjugate gradient convergence (log error)")
				while abs(err) > tol and k < nmax:
					p = w + beta*p;
					z = dot(self, p);
					alpha = rho/cvector.dot(p, z);
					r = r - alpha*z;
					w = r/kvec;
					rhoold = rho;
					rho = cvector.dot(r, w);
					x = x + alpha*p;
					beta = rho/rhoold;
					err = cvector.norm(dot(self, x) - b);
					print(k,' %5.1f ' % math.log10(abs(err)))
					k = k+1
				return x
	    		
	def biCGsolve(self,x0, b, tol=1.0e-10, nmax = 1000):
		# solve self*x = b and return x using the bi-conjugate gradient method
		if not cvector.isVector(b):
			raise TypeError(self.__class__).with_traceback(' in solve ')
		else:
			if self.size()[0] != len(b) or self.size()[1] != len(b):
				print('**Incompatible sizes in solve')
				print('**size()=', self.size()[0], self.size()[1])
				print('**len=', len(b))
			else:
				kvec = diag(self) # preconditionner 
				n = len(b)
				x = x0 # initial guess
				r =  b - dot(self, x)
				rbar =  r
				w = r/kvec;
				wbar = rbar/kvec;
				p = cvector.zeros(n);
				pbar = cvector.zeros(n);
				beta = 0.0;
				rho = cvector.dot(rbar, w);
				err = cvector.norm(dot(self,x) - b);
				k = 0
				print(" bi-conjugate gradient convergence (log error)")
				while abs(err) > tol and k < nmax:
					p = w + beta*p;
					pbar = wbar + beta*pbar;
					z = dot(self, p);
					alpha = rho/cvector.dot(pbar, z);
					r = r - alpha*z;
					rbar = rbar - alpha* dot(pbar, self);
					w = r/kvec;
					wbar = rbar/kvec;
					rhoold = rho;
					rho = cvector.dot(rbar, w);
					x = x + alpha*p;
					beta = rho/rhoold;
					err = cvector.norm(dot(self, x) - b);
					try:
						print(k,' %5.1f ' % math.log10(abs(err)))
					except: print(k, abs(err))
					k = k+1
				return x

	def save(self, filename, OneBased=0):
		"""
		Save matrix in file <filaname> using format:
		OneBased, nrow, ncol, nnonzeros
		[ii, jj, data_re, data_im]

		"""
		m = n = 0
		nnz = len(self)
		for ij in list(self.keys()):
			m = max(ij[0], m)
			n = max(ij[1], n)

		f = open(filename,'w')
		f.write('%d %d %d %d\n' % (OneBased, m+1,n+1,nnz))
		for ij in list(self.keys()):
			i,j = ij
			try:
				are, aim = self[ij].real, self[ij].imag
			except: are, aim = self[ij], 0.
			f.write('%d %d %20.17f %20.17f \n'% \
				(i+OneBased,j+OneBased,are,aim))
		f.close()
				
###############################################################################

def isSparse(x):
    return hasattr(x,'__class__') and x.__class__ is csparse

def transp(a):
	" transpose "
	new = csparse({})
	for ij in a:
		new[(ij[1], ij[0])] = a[ij].conjugate()
	return new

def dotDot(y,a,x):
	" double dot product y^+ *A*x "
	res = 0j
	if cvector.isVector(y) and isSparse(a) and cvector.isVector(x):
		for ij in list(a.keys()):
			i,j = ij
			res += y[i].conjugate()*a[ij]*x[j]
	else:
		print('csparse::Error: dotDot takes cvector, csparse , cvector as args')
	return res

def dot(a, b):
	" vector-matrix, matrix-vector or matrix-matrix product "
	if isSparse(a) and cvector.isVector(b):
		new = cvector.zeros(a.size()[0])
		for ij in list(a.keys()):
			new[ij[0]] += a[ij]* b[ij[1]]
		return new
	elif cvector.isVector(a) and isSparse(b):
		new = cvector.zeros(b.size()[1])
		for ij in list(b.keys()):
			new[ij[1]] += a[ij[0]].conjugate()* b[ij]
		return new
	elif isSparse(a) and isSparse(b):
		if a.size()[1] != b.size()[0]:
			print('**Warning shapes do not match in dot(csparse, csparse)')
		new = csparse({})
		n = min([a.size()[1], b.size()[0]])
		for i in range(a.size()[0]):
			for j in range(b.size()[1]):
				sum = 0j
				for k in range(n):
					sum += a.get((i,k),0.)*b.get((k,j),0.)
				if sum != 0j:
					new[(i,j)] = sum
		return new
	else:
		raise TypeError('in dot')

def diag(b):
	# given a csparse matrix b return its diagonal
	res = cvector.zeros(b.size()[0])
	for i in range(b.size()[0]):
		res[i] = b.get((i,i), 0j)
	return res
		
def identity(n):
	if type(n) != int:
		raise TypeError(' in identity: # must be integer')
	else:
		new = csparse({})
		for i in range(n):
			new[(i,i)] = 1+0j
		return new

###############################################################################
if __name__ == "__main__":

	print('a = csparse()')
	a = csparse()

	print('a.__doc__=',a.__doc__)

	print('a[(0,0)] = 1.0')
	a[(0,0)] = 1.0
	a.out()

	print('a[(2,3)] = 3.0')
	a[(2,3)] = 3.0
	a.out()

	print('len(a)=',len(a))
	print('a.size()=', a.size())
			
	b = csparse({(0,0):2.0+0j,
		     (0,1):1.0+0j,
		     (1,0):1.0+0j,
		     (1,1):2.0+0j,
		     (1,2):1.0+0j,
		     (2,1):1.0+0j,
		     (2,2):2.0+0j})
	print('a=', a)
	print('b=', b)
	b.out()

	print('a+b')
	c = a + b
	c.out()

	print('-a')
	c = -a
	c.out()
	a.out()

	print('a-b')
	c = a - b
	c.out()

	print('a*1.2')
	c = a*1.2
	c.out()


	print('1.2*a')
	c = 1.2*a
	c.out()
	print('a=', a)

	print('dot(a, b)')
	print('a.size()[1]=',a.size()[1],' b.size()[0]=', b.size()[0])
	c = dot(a, b)
	c.out()

	print('dot(b, a)')
	print('b.size()[1]=',b.size()[1],' a.size()[0]=', a.size()[0])
	c = dot(b, a)
	c.out()

	print('dot(b, cvector.cvector([1,2,3]))')
	c = dot(b, cvector.cvector([1+0j,2+0j,3+0j]))
	c.out()
	
	print('dot(cvector.cvector([1,2,3]), b)')
	c = dot(cvector.cvector([1+0j,2+0j,3+0j]), b)
	c.out()

	print('a*b -> element by element product')
	print('a=',a)
	#print 'b[(2,3)]=',b[(2,3)]
	c = a*b
	c.out()

	print('b*a -> element by element product')
	c = b*a
	c.out()
	
	print('a/1.2')
	c = a/1.2
	c.out()

	print('c = identity(4)')
	c = identity(4)
	c.out()

	print('c = transp(a)')
	c = transp(a)
	c.out()

	print('b.size()=', b.size())
	s = cvector.cvector([1, 0, 0])
	print('s')
	s.out()

	b[(2,2)]=-10.0
	b[(2,0)]=10. +1j

	bsym = transp(b) + b
	x0 = s 
	print('x = bsym.biCGsolve(x0, s, 1.0e-10, 20)')
	x = bsym.biCGsolve(x0, s, 1.0e-10,  20)
	x.out()

	print('check validity of solve')
	c = dot(b, x) - s
	c.out()

	b.plot()

	print('del b[(2,2)]')
	del b[(2,2)]

	print('del a')
	del a
	#a.out()
