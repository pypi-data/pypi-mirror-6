#!/usr/bin/env python

# $Id: ring.py,v 1.2 2005/11/10 15:34:16 pletzer Exp $

"""
Solve Laplace's equation in the geometry of a ring using
an unstructured mesh. The boundary conditions are zero Neumann
on the outside and inhomogeneous Neumann on the inside. 
"""

from math import cos, sin, pi, sqrt
from ellipt2d import ellipt2d
from DirichletBound import DirichletBound
from NeumannBound import NeumannBound
from Triangulate import Triangulate
import Tkinter
import tkplot
import superlu

class ring:

	def __init__(self, R=1.0, rp=0.5, area=0.01):

		"""
		R: large radius
		rp: small readius
		area: max area constrint in triangulation
		"""
		

		# ode operator
		f = '1.'
		g = '0.'
		s = '0.'

		# estimates for the nmber of boundary points
		n2 = int(2*pi*R/sqrt(area))
		dt2 = 2*pi/n2
		n1 = int(n2*rp/R)
		dt1 = 2*pi/n1

		# outer circle
		listofpts = [(R*cos(i*dt2), R*sin(i*dt2)) for i in range(n2)]
		# inner circle
		newlistofpts = [(rp*cos(i*dt1), rp*sin(i*dt1)) for i in range(n1)]
		listofpts += newlistofpts

		# outer segments
		seglist =[(i,i+1) for i in range(n2-1)] + [(n2-1,0)]
		# interior segments
		seglist +=[(n2+i,n2+i+1)  for i in range(n1-1)] + [(n1+n2-1,n2)]
		regionlist = []
		holelistofpts = [(0., 0.)]

		# Trick: the triangulation allows one to
		# add Steiner points on the boundary. These
		# additional points will also require boundary conditions
		# to be applied. We will use the Dirichlet boundary condition
		# mechanism to update the boundary values on these points. The
		# Neumann boundary conditions will be computed by averaging the
		# the values between to adjacent nodes.

		db = [(0.,0.) for i in range(len(listofpts))]  # pseudo-Neumann in fact
			
		nb = NeumannBound(start={})

		# We could apply zero Neumman on the outer circle,
		# but that is not really necessary as zero Neumann are the
		# default BCs
##		for i in range(n2-1):
##			nb[(i,i+1)] = 0
##		nb[(n2-1,0)] = 0 

		# apply pseudo-Neumann
		for i in range(len(newlistofpts)):
			db[n2+i] = (cos(i*2*pi/len(newlistofpts)), 1.0)
		 
		tri = Triangulate()
		tri.set_points(listofpts)
		tri.set_segments(seglist)
		tri.set_holes(holelistofpts)

		print 'set attributes...'
		tri.set_attributes(db)
		print 'done....'

		tri.triangulate(area=area)
		mesh  = tri.get_nodes()
		print mesh

		db = tri.get_attributes()
		
		# convert the pseudo-Neumann BCs into segment-based Neumann BCs
		xc, yc = holelistofpts[0]
		for i in range(len(db)):
			connected = mesh[i]
			#if connected[2] == 1:
			for j in connected[1]:
				if mesh.isBound(j) == 1 and db[i][1]==1.0:
					# 
					xi, yi = mesh.x(i)-xc, mesh.y(i)-yc
					xj, yj = mesh.x(j)-xc, mesh.y(j)-yc
					surf = xi*yj - xj*yi
					value = (db[i][0]+db[j][0])/2
					# normal points inwards for the inner boundary
					ij = (i,j)
					if surf < 0.: ij = (j,i)
					if ij not in nb.data:
						nb[ij] = -value
						
		equ = ellipt2d(mesh,f,g,s)

		[amat, s] = equ.stiffnessMat()

		# now apply Neumann BCs
		equ.neumannB(nb,s)

		# applying only Neumann BCs makes the system singular (solution
		# is defined up to a global constant), so we freeze one node (0), setting
		# it to zero. This is achieved by setting the (0,0) diagonal element to a very
		# number.
		amat[(0,0)] = 1.23434556e10


		# solve system
		v = superlu.solve(amat,s)
		
		print 'field at node 0: ',v[0]
		print 'min/max values: %g %g '%(min(v), max(v))
		
		WIDTH = 600
		HEIGHT = 600
		root = Tkinter.Tk()
		frame = Tkinter.Frame(root)
		frame.pack()
		canvas = Tkinter.Canvas(bg="White",width=WIDTH,height=HEIGHT)
		canvas.pack()
		tkplot.tkplot(canvas,mesh,v,0,0,1,WIDTH,HEIGHT)
                tkplot.tkplot(canvas,mesh,nb,1,0,1,WIDTH,HEIGHT)
		root.mainloop()

a = ring()
