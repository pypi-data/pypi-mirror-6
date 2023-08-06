#!/usr/bin/env python
# $Id: attrib.py,v 1.5 2003/07/21 13:58:13 pletzer Exp $
"""
Test setAttributes/getAttributes
"""

import Ireg2tri
from math import cos, sin, pi, sqrt


nt = 16
dt = 2*pi/nt
area = 0.1
mesh = Ireg2tri.Ireg2tri(area)
a = 1.0
pts = [ ( a*cos(i*dt), a*sin(i*dt) ) for i in range(nt)]
mesh.setUpConvexHull(pts, nattr=5)

grid = mesh.triangulate()

# function to interpolate
attributes = [ [0.,0.,0.,0.,0.] for i in range(len(grid)) ]
for i in range(len(grid)):
	x, y = grid.x(i), grid.y(i)
	attributes[i] = [x, y, x**2, y**2, x*y]
mesh.setAttributes(attributes)
grid = mesh.refine(1)

# new attributes
a = mesh.getAttributes()
error = 0
for i in range(len(grid)):
	x, y = grid.x(i), grid.y(i)
	deviation = sqrt( (a[i][0]-x)**2 + \
			  (a[i][1]-y)**2 + \
			  (a[i][2]-x**2)**2 + \
			  (a[i][3]-y**2)**2 + \
			  (a[i][4]-x*y)**2)
	error += deviation
error /= len(grid)
print 'error=', error



from Tkinter import Tk, Canvas, Frame
from tkplot import tkplot
root = Tk()
frame = Frame(root) 
frame.pack() 
WIDTH, HEIGHT = 300, 300
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT)
canvas.pack()
tkplot(canvas, grid, [], 1, 1, 1, WIDTH, HEIGHT)
root.mainloop()
