#!/usr/bin/env python
# $Id: demo_dino.py,v 1.8 2013/12/20 17:17:07 pletzer Exp $
#
# J. Mollis 8/1/2000, A. P. 8/9/2000

from math import pi
from ellipt2d import ellipt2d
from DirichletBound import DirichletBound
import vector, time, os
import superlu, Ireg2tri


"""
Helmholtz equation in a dinosaur shaped domain
"""

# geometry setup

points =[(1.,1.),(1.,0.),(1.5,0.),(1.5,1.),(1.6,1.),(1.7,0.),(2.,0.),(2.,0.9),(3.5,1.),
         (3.6,0.),(4.,0.),(4.2,1.2),(5.,.5),(7.,0.2),(8.,0.1),(6.5,.6), (5.2,0.8), (4.5,2.),(4.8,3.5),
         (4.,2.9),(4.2,4.5),(3.3,3.2),(2.8,4.3),(2.3,3.1),(1.9,3.),(1.8,3.2),(1.3,5.),
         (1.2,5.5),(0.4,5.3),(0.8,5.0)]

# need to define segments if domain has concavities and/or
# inhomogeneous boundary conditions
seglist = []
for i in range(len(points)-1):
    seglist.append((i,i+1))
seglist.append((len(points)-1,0))

dB = DirichletBound()
for i in range(len(points)/2):
    dB[i] = 1.0
for i in range(len(points)/2, len(points)):
    dB[i] = 0.0

initialAreaBound = 0.02
t0 = time.time()
meshgen = Ireg2tri.Ireg2tri(initialAreaBound)
meshgen.setUpConvexHull(points,seglist)
meshgen.setUpDirichlet(dB)
grid = meshgen.triangulate()
grid = meshgen.refine(2)
print 'time to triangulate         %9.3f  ' % (time.time() - t0),' [s]'
#grid.plot()
#dB.plot(grid,1)


# Helmholtz equation

k = 2.*pi
f, g, s = '1', '%10.4f' % (-k**2), '0'

# Solve PDE

equ = ellipt2d(grid, f,g,s)
t0 = time.time()
[amat, s] = equ.stiffnessMat()
print 'time to build sparse matrix %9.3f  ' % (time.time() - t0),' [s]'

# apply boundary conditions

equ.dirichletB(dB,amat,s)

# solve linear system
    
t0 = time.time()
v = superlu.solve(amat,s)
print 'time to solve matrix system %9.3f  ' % (time.time() - t0),' [s]'

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
tkplot.tkplot(canvas, grid, v, 0,0,1, WIDTH, HEIGHT) 
root.mainloop() 





















