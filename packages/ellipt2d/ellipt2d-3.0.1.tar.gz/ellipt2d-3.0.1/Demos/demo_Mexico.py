#!/usr/bin/env python
# $Id: demo_Mexico.py,v 1.7 2013/12/20 17:17:07 pletzer Exp $
# J. Mollis 8/1/2000, A. Pletzer 8/9/2000

"""
Helmholtz equation in a Mexico shaped domain
"""

from math import pi
from ellipt2d import ellipt2d
from DirichletBound import DirichletBound
import vector
import time, os
import superlu, Ireg2tri


# geometry setup

points =[(1.558, -5.828), (1.356, -5.873), (1.123, -5.752), (1.12, -5.471),(1.132, -5.482),
         (1.262, -5.42), (1.297, -5.227), (1.109, -5.298),(1.069, -5.348), (1.069, -5.459),
         (0.966, -5.426), (0.964, -5.504),(0.905, -5.567), (0.873, -5.535),
         (0.986, -5.692),(0.958, -5.867), (1.1, -6.209), (1.195, -6.327), (1.352, -6.343),
         (1.538, -6.564), (1.738, -6.73), (1.874, -6.785), (1.917, -6.902),(1.697, -6.772),
         (1.388, -6.571), (1.484, -6.726), (1.664, -6.901), (1.711, -6.844), (1.952, -7.027),
         (1.963, -6.883), (1.88, -6.543), (1.907, -6.391), (1.76, -6.243), (1.757, -6.05),
         (1.584, -5.945), (1.558, -5.828)]


# need to define segements if domain has concavities

seglist = []
for i in range(len(points)-1):
    seglist.append((i,i+1))
seglist.append((len(points)-1,0))


dB = DirichletBound()
for i in range(len(points)/2):
    dB[i] = 1.0
for i in range(len(points)/2, len(points)):
    dB[i] = 0.0

initialAreaBound = 0.1
meshgen = Ireg2tri.Ireg2tri(initialAreaBound)
meshgen.setUpConvexHull(points,seglist)
meshgen.setUpDirichlet(dB)
grid = meshgen.triangulate()
#grid = meshgen.refine(1)
#grid.plot()
#dB.plot(grid,1)


# Helmholtz equation

k = 2.*pi
f, g, s = '1', '%10.4f' % (-k**2), '0'

# Solve PDE

equ = ellipt2d(grid, f,g,s)
[amat, s] = equ.stiffnessMat()

# apply boundary conditions

equ.dirichletB(dB,amat,s)

# solve linear system

print "Solving linear system..."
v = superlu.solve(amat,s)

print 'min v = ', min(v)
print 'max v = ', max(v)

# plot result

from Tkinter import Tk, Frame, Button, Canvas, BOTTOM
import tkplot
root = Tk() 
frame = Frame(root) 
frame.pack() 
WIDTH, HEIGHT = 500, 450 
button = Button(frame, text="OK", fg="red", command=frame.quit) 
button.pack(side=BOTTOM) 
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack()
tkplot.tkplot(canvas, grid, v, draw_mesh=1, node_no=0, add_minmax=11,
              WIDTH=WIDTH, HEIGHT=HEIGHT) 
root.mainloop() 





















