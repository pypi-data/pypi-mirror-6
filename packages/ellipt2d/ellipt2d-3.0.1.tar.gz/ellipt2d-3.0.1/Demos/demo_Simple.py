#!/usr/bin/env python
#

import time, os
from math import sqrt

from ellipt2d import ellipt2d
from DirichletBound import DirichletBound
import vector, reg2tri

class demo_Simple:
    """
    This demo shows how simple it can be to solve
    uncomplicated problems with ellipt2d.
    """
 
    def __init__(self):

        # number of nodes
	N = 100

        # box size
	xmin = 0.0
	xmax = 1.0
	ymin = 0.0
	ymax = 1.0

        nx1 = int(sqrt(N))
        ny1 = int(sqrt(N))
        nx1 = max(3, nx1)
        ny1 = max(3, ny1)


        # Mesh generation.
	grid = reg2tri.rect2cross((xmin, ymin, xmax, ymax), nx1, ny1)

        # Create Dirichlet boundary condition object
	db = DirichletBound()

        # Set the boundary conditions 
	for i in range(0,nx1):
	    db[i] = 2.0

	for i in range( (ny1-1)*(nx1) , (ny1-1)*(nx1)+ nx1 ):
	    db[i] = 4.0
        
        # Create ellipt2d object.
        # Equation is -div f grad v + g v = s
        f='1.'; g='1.'; s='0.'
	equ = ellipt2d(grid, f, g, s)

        # Assemble the stiffness matrix
	[amat, rhs] = equ.stiffnessMat()

	# Apply the boundary conditions (modify amat and rhs
	equ.dirichletB(db,amat,rhs)

	v = amat.CGsolve(rhs,rhs,(1.0e-3)/(float(N)), 2*len(rhs) )

        # Plotting using builtin Tk methods
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
        tkplot.tkplot(canvas, grid, db, 0,0,1, WIDTH, HEIGHT) 
        root.mainloop() 

if __name__ == "__main__":

    a = demo_Simple()





