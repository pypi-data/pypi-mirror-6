#!/usr/bin/env python
# $Id: demo_RegRb.py,v 1.10 2013/12/20 17:17:07 pletzer Exp $
# A. Pletzer, J.Mollis 8/1/2000

"""
This demo uses a regular mesh and Robin BCs
"""

from ellipt2d import ellipt2d
import vector, reg2tri
import time
from math import sqrt
from RobinBound import RobinBound

class demo_RegRb:
 
    def __init__(self):
        
        self.nsize = 100
           
        # 1. Equation definition--------------

        self.f_funct_str = '1' 
        self.g_funct_str = '0'
        self.s_funct_str = '0'

        ### 2. Domain grid/boundary defintions----------------
        
        x0, y0 = 0.0, 0.0       
        xmax, ymax = 1.0, 1.0 

        self.nx1 = int(sqrt(self.nsize))
        self.ny1 = int(sqrt(self.nsize))
        self.nx1 = max(3, self.nx1)
        self.ny1 = max(3, self.ny1)

        ## Grid creation/boundary set up-------------------

        self.grid = reg2tri.rect2cross(
            (x0, y0, xmax, ymax), self.nx1, self.ny1)

        rB = RobinBound()

        for i in range(0,self.nx1-1):
            rB[(i,i+1)] = (10.0,10.0)
            self.grid.setBound(i)
        self.grid.setBound(self.nx1-1)
        
        for i in range( (self.ny1-1)*(self.nx1) , (self.ny1-1)*(self.nx1) + self.nx1-1):
            rB[(i,i+1)] = (2.0,7.0)
            self.grid.setBound(i)
        self.grid.setBound( (self.ny1-1)*(self.nx1) + self.nx1-1 )
        
        #self.grid.plot(0)
	#rB.plot(self.grid)

        # 4. Set up the equation.

        equ = ellipt2d(self.grid, self.f_funct_str, self.g_funct_str, self.s_funct_str)
        
	# 5. Assemble stiffness matrix and compute source vector

        [amat, s] = equ.stiffnessMat()

	# 6. Apply Boundary conditions.

        equ.robinB(rB,amat,s)

        # 7. Solve linear system.

        v = amat.CGsolve(s,s,(1.0e-3)/(float(self.nsize)))    

        # 8. Write DX and UCD formated files.

        equ.toUCD(v, 'ellipt2d.inp' )	 

        print 'max v = ', max(v)

        #10. Plotting using builtin Tk methods
        
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
        tkplot.tkplot(canvas, self.grid, v, 1,0,0, WIDTH, HEIGHT) 
        tkplot.tkplot(canvas, self.grid, rB, 0,0,0, WIDTH, HEIGHT) 
        root.mainloop() 
      

if __name__ == "__main__":

    
    a = demo_RegRb() 











