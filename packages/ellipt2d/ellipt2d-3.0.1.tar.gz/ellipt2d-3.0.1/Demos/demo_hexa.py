#!/usr/bin/env python
# $Id: demo_hexa.py,v 1.8 2013/12/20 17:17:07 pletzer Exp $
# A. P. 8/11/2000

from math import pi, cos, sin, sqrt
from DirichletBound import DirichletBound
from ellipt2d import ellipt2d
import vector
import time, os, sys
import superlu
import Ireg2tri

"""
Solve Helmholtz's equation on a hexagonal shaped domain to recover
Christopherson's well known pattern cell solutions.
(D G Christopherson, Quart. J. of Math., 11, 63-65 (1941)).
"""

nEdges = 6
points = []
for i in range(nEdges):
    t = i* 2.*pi/nEdges
    x, y = cos(t), sin(t)
    points.append((x,y))
print points

# need to define segments if domain has concavities and/or
# inhomogeneous boundary conditions
seglist = []
for i in range(len(points)-1):
    seglist.append((i,i+1))
seglist.append((len(points)-1,0))

# now add 1 internal node with Dirichlet BC
dB = DirichletBound()

points.append((0.,0.))
dB[len(points)-1] = 1.0

# triangulate domain
initialAreaBound = 0.1
t0 = time.time()
meshgen = Ireg2tri.Ireg2tri(initialAreaBound)
meshgen.setUpConvexHull(points,seglist)
meshgen.setUpDirichlet(dB)
grid = meshgen.triangulate()
grid = meshgen.refine(5)

# Helmholtz equation

f = '1'
s = '0'


v0   = vector.zeros(len(grid))
diff0= 0.0

k0 = 32.*pi/(3.*sqrt(3.)) # resonant k
n = 1
g  = '%10.4f' % (-(k0*float(n))**2)

print 'Equation=> -div '+f+' grad '+g+' = ',s
equ= ellipt2d(grid, f, g, s)
[amat, rhs] = equ.stiffnessMat()

# apply Dirichlet BCs
equ.dirichletB(dB,amat,rhs)

# default homogeneous Neumann BCs
v = superlu.solve(amat,rhs)
diff = max(v) - min(v)


# plot

from Tkinter import Tk, Frame, Button, Canvas, BOTTOM
import tkplot
root = Tk() 
frame = Frame(root) 
frame.pack() 
WIDTH, HEIGHT = 500, 450 
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack()
tkplot.tkplot(canvas, grid, v, 1,0,0, WIDTH, HEIGHT) 
root.mainloop() 
