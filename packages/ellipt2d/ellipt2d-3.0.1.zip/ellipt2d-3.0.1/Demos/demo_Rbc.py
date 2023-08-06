#!/usr/bin/env python

from math import sqrt
from ellipt2d import ellipt2d
from DirichletBound import DirichletBound
from NeumannBound import NeumannBound
import reg2tri
import vector
import time, os

class demo_Simple:
    """
    This demo sets some interesting boundary conditions. Interior 
    Dirichlet BCs and and a few Neumann edges.
    """
 
    def __init__(self):

	N = 100

	f = '1'
	g = '1'
	s = '0'

	xmin = 0.0
	xmax = 1.0
	ymin = 0.0
	ymax = 1.0

        nx1 = int(sqrt(N))
        ny1 = int(sqrt(N))
        nx1 = max(3, nx1)
        ny1 = max(3, ny1)


	grid = reg2tri.rect2cross((xmin, ymin, xmax, ymax), nx1, ny1)

	db = DirichletBound()

	for i in range(0,nx1-3):
	    db[i] = 2.0
	db[nx1-3] = 5.0
	db[nx1-2] = 6.0
	db[nx1-1] = 7.0
	
	db[25] = 8.0         # inner Dirichlet BC's.    
	db[55] = 12.0

	for i in range( (ny1-1)*(nx1) , (ny1-1)*(nx1)+ nx1 ):
	    db[i] = 4.0
        
	nb = NeumannBound()  # Neumann boundary condition set on one segment.

	nb[(nx1,(2)*nx1)] = 3.0
	nb[(2*nx1,3*nx1)] = 3.0

	equ = ellipt2d(grid, f,g,s)

	[amat, s] = equ.stiffnessMat()
	
	equ.dirichletB(db,amat,s)
	equ.neumannB(nb,s)

	v = amat.CGsolve(s,s,(1.0e-3)/(float(N)), 2*len(s) )
	
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
        # plot solution Dirichlet boundary conditions
        tkplot.tkplot(canvas, grid, v, 0,0,1, WIDTH, HEIGHT) 
        tkplot.tkplot(canvas, grid, db, 0,0,1, WIDTH, HEIGHT) 
        tkplot.tkplot(canvas, grid, nb, 0,0,1, WIDTH, HEIGHT) 
        root.mainloop() 

if __name__ == "__main__":

    a = demo_Simple()








