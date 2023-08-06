#!/usr/bin/env python
# $Id: cvector.py,v 1.11 2013/12/20 22:51:14 pletzer Exp $ 
# a python vector class
# A. Pletzer 5 Jan 00/11 April 2002
#
"""
A list based vector representation (complex)
"""
import cmath, math, operator
from vector import vector
from functools import reduce

"""
A complex vector class that supports elementwise mathematical operations

In this version, the vector call inherits from list; this 
requires Python 2.2 or later.
"""

class cvector(list):
	"""
        A complex number vector class
	"""
	# no c'tor

	def __getslice__(self, i, j):
		try:
			# use the list __getslice__ method and convert
			# result to cvector
			return cvector(super(cvector, self).__getslice__(i,j))
		except:
			raise TypeError('cvector::FAILURE in __getslice__')
		
	def __add__(self, other):
		return cvector(list(map(operator.add, self, other)))

	def __neg__(self):
		return cvector(list(map(operator.neg, self)))
	
	def __sub__(self, other):
		return cvector(list(map(operator.sub, self, other)))

	def __mul__(self, other):
	    """
	    Element by element multiplication
	    """
	    try:
		    return cvector(list(map(operator.mul, self,other)))
	    except:
		    # other is a const
		    return cvector([x*other for x in self])


	def __rmul__(self, other):
		return (self*other)


	def __div__(self, other):
	    """
	    Element by element division.
	    """
	    try:
		    return cvector(list(map(operator.div, self, other)))
	    except:
		    return cvector([x/other for x in self])

	def __rdiv__(self, other):
	    """
	    The same as __div__
	    """
	    try:
		    return cvector(list(map(operator.div, other, self)))
	    except:
		    # other is a const
		    return cvector([other/x for x in self])

        def size(self): return len(self)

	def conjugate(self):
	    return cvector([x.conjugate() for x in self])

        def ReIm(self):
		"""
		Return the real and imaginary parts
		"""
		return [
			vector([x.real for x in self]),
			vector([x.imag for x in self]),
			]
	
        def AbsArg(self):
		"""
		Return modulus and phase parts
		"""
		return (vector(list(map(operator.abs, self))), \
			vector([math.atan2(x.imag,x.real) for x in self]))


	def out(self):
	    """
	    Prints out the cvector.
	    """
	    print(self)

###############################################################################


def isVector(x):
    """
    Determines if the argument is a cvector class object.
    """
    return hasattr(x,'__class__') and x.__class__ is cvector

def zeros(n):
    """
    Returns a zero cvector of length n.
    """
    return cvector([0j]*n)

def ones(n):
    """
    Returns a cvector of length n with all ones.
    """
    return cvector([1+0j]*n)

def random(n, lmin=0.0, lmax=1.0):
    """
    Returns a random cvector of length n.
    """
    import random as rand
    gen = rand.random()
    dl = lmax-lmin
    return cvector([dl*(rand.random() + 1j*rand.random()) for x in range(n)])
	
def dot(a, b):
    """
    dot product of two cvectors.
    """
    return reduce(operator.add, a.conjugate()*b, 0j)
	

def norm(a):
    """
    Computes the norm of cvector a.
    """
    return cmath.sqrt(abs(dot(a,a)))

def sum(a):
    """
    Returns the sum of the elements of a.
    """
    return reduce(operator.add, a, 0j)

# elementwise operations
	
def log10(a):
    """
    log10 of each element of a.
    """
    return cvector(list(map(cmath.log10, a)))

def log(a):
    """
    log of each element of a.
    """
    try:
	return cvector(list(map(cmath.log, a)))
    except:
	raise TypeError('cvector::FAILURE in log')
	    
def exp(a):
    """
    Elementwise exponential.
    """
    try:
	return cvector(list(map(cmath.exp, a)))
    except:
	raise TypeError('cvector::FAILURE in exp')

def sin(a):
    """
    Elementwise sine.
    """
    try:
	return cvector(list(map(cmath.sin, a)))
    except:
	raise TypeError('cvector::FAILURE in sin')
	    
def tan(a):
    """
    Elementwise tangent.
    """
    try:
	return cvector(list(map(cmath.tan, a)))
    except:
	raise TypeError('cvector::FAILURE in tan')
	    
def cos(a):
    """
    Elementwise cosine.
    """
    try:
	return cvector(list(map(cmath.cos, a)))
    except:
	raise TypeError('cvector::FAILURE in cos')

def asin(a):
    """
    Elementwise inverse sine.
    """
    try:
	return cvector(list(map(cmath.asin, a)))
    except:
	raise TypeError('cvector::FAILURE in asin')

def atan(a):
    """
    Elementwise inverse tangent.
    """	
    try:
	return cvector(list(map(cmath.atan, a)))
    except:
	raise TypeError('cvector::FAILURE in atan')

def acos(a):
    """
    Elementwise inverse cosine.
    """
    try:
	return cvector(list(map(cmath.acos, a)))
    except:
	raise TypeError('cvector::FAILURE in acos')

def sqrt(a):
    """
    Elementwise sqrt.
    """
    try:
	return cvector(list(map(cmath.sqrt, a)))
    except:
	raise TypeError('cvector::FAILURE in sqrt')

def sinh(a):
    """
    Elementwise hyperbolic sine.
    """
    try:
	return cvector(list(map(cmath.sinh, a)))
    except:
	raise TypeError('cvector::FAILURE in sinh')

def tanh(a):
    """
    Elementwise hyperbolic tangent.
    """
    try:
	return cvector(list(map(cmath.tanh, a)))
    except:
	raise TypeError('cvector::FAILURE in tanh')

def cosh(a):
    """
    Elementwise hyperbolic cosine.
    """
    try:
	return cvector(list(map(cmath.cosh, a)))
    except:
	raise TypeError('cvector::FAILURE in cosh')


def pow(a,b):
    """
    Takes the elements of a and raises them to the b-th power
    """
    try:
        return cvector([x**b for x in a])
    except:
	raise TypeError('cvector::FAILURE in pow')
	
	

###############################################################################
if __name__ == "__main__":

	print('a = zeros(4)')
	a = zeros(4)

	print('a.__doc__=',a.__doc__)

	print('a[0] = 1-5j')
	a[0] = 1-5j

	print('a[3] = 3+4j')
	a[3] = 3+4j

	print('a[0]=', a[0])
	print('a[1]=', a[1])

	print('len(a)=',len(a))
	print('a.size()=', a.size())
			
	b = cvector([1+0j, 4+0j, 1-2j, -3+1j])
	print('a=', a)
	print('b=', b)

	print('a+b')
	c = a + b
	c.out()

	print('a.conjugate()')
	c = a.conjugate()
	c.out()

	print('a.conjugate()*b')
	c = a.conjugate() * b
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

	print('dot(a,b) = ', dot(a,b))
	print('dot(b,a) = ', dot(b,a))

	print('a*b')
	c = a*b
	c.out()
	
	print('a/1.2')
	c = a/1.2
	c.out()

	print('a[0:2]')
	c = a[0:2]
	c.out()

	print('a[2:5] = [9.0, 4.0, 5.0]')
	a[2:5] = [9.0, 4.0, 5.0]
	a.out()

	print('sqrt(a)=',sqrt(a))
	print('cos(a)=', cos(a))
	print('1.2*cos(a)=',1.2*cos(a))
##	print 'pow(a, 2*ones(len(a)))=',pow(a, 2*ones(len(a)))
##	print 'pow(a, 2)=',pow(a, 2*ones(len(a)))

	print('ones(10)')
	c = ones(10)
	c.out()

	print('zeros(10)')
	c = zeros(10)
	c.out()

	print('del a')
	del a
	#a.out()

	
			

