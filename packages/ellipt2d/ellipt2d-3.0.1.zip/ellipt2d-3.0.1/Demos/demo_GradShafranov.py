#!/usr/bin/env python
# $Id: demo_GradShafranov.py,v 1.6 2013/12/20 17:17:07 pletzer Exp $
# J. Mollis 8/1/2000, A. P. 8/9/2000

from ellipt2d import ellipt2d
from DirichletBound import DirichletBound
import vector
import time
import os
import superlu, Ireg2tri


"""
Grad Shafranov equation with external current.
"""

# geometry setup


points =[(0.2,-2.),(0.2,1.2),(0.5,1.2), (0.7,1.17),
         (1.,1.),(1.29,0.5),(1.3,0.5), (1.3,-1.6),
         (1.1,-2.), (0.1,-2.)]

# need to define segments if domain has concavities and/or
# inhomogeneous boundary conditions
seglist = []
for i in range(len(points)-1):
    seglist.append((i,i+1))
seglist.append((len(points)-1,0))

dB = DirichletBound()

# 0.0 on boundary
for i in range(len(points)):
    dB[i] = 0.0


initialAreaBound = 0.03
t0 = time.time()
meshgen = Ireg2tri.Ireg2tri(initialAreaBound)
meshgen.setUpConvexHull(points, seglist)
meshgen.setUpDirichlet(dB)
grid = meshgen.triangulate()
grid = meshgen.refine(3)

# update BCs (BC values interpolated on Steiner points)
meshgen.updateDirichlet(dB)

print 'time to triangulate         %9.3f  ' % (time.time() - t0),' [s]'


# Grad-Shafranov equation with source term -x**2 p0 - f0 + a current source term
# (p0, f0 are constants)

# mhd current
p0, f0 = 4.5, 2.0
f, g = '1./x', '0'
s = '- %10.4f *x - %10.4f/x' % (p0, f0)

# add Gaussian ext current
Ispot, xs, ys, spotSize = 1.0, 0.8, -1.5, 0.2
s = s + '+%f*exp(-((x-%f)**2 + (y-%f)**2)/%f)/x' % (Ispot/spotSize**2,xs,ys,spotSize**2)

# Solve PDE

t0 = time.time()
equ1 = ellipt2d(grid, f,g,s)
[amat, s] = equ1.stiffnessMat()
print 'Time to build stiffness matrix ', time.time()-t0,' [s]'

# apply boundary conditions

equ1.dirichletB(dB,amat,s)

# solve linear system
    
t0 = time.time()
v = superlu.solve(amat,s)
print 'Time to solve matrix system', time.time()-t0,' [s]'

print 'min v = ', min(v)
print 'max v = ', max(v)

# plot result

from Tkinter import Tk, Canvas, BOTTOM
import tkplot
root = Tk() 
WIDTH, HEIGHT = 200, 350 
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack()
tkplot.tkplot(canvas, grid, v, 1,0,1, WIDTH, HEIGHT) 
root.mainloop() 





















