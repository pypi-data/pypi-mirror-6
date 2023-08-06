#!/usr/bin/env python
# $Id: gui.py,v 1.3 2013/12/20 17:17:07 pletzer Exp $
#
# A. Pletzer 8/1/2000

"""
Build sparse finite element matrix for Laplace operator
"""

from math import *
import reg2tri, vector
from sparse import dot
from DirichletBound import DirichletBound
from ellipt2dF import ellipt2d
import os, string, time, cell
import colormap
from Tkinter import *


class gui:
    """
    Tk interface for ELLIPT2D.
    """
    def __init__(self, parent, width_in=400, height_in=340):
        self.nsize = 21
        self.parent = parent
        self.width, self.height = width_in, height_in
        f = Frame(parent)
        
        self.canvas = Canvas(parent,
                                  height = height_in,
                                  width = width_in,
                                  relief = SUNKEN,
                                  borderwidth = 2)
        self.canvas.grid(row=0, column=0, columnspan=4, rowspan=8)


        quit = Button(parent,
                      text="QUIT", fg="red", command=f.quit)
	quit.grid(row=8, column=0, sticky=W)
        clear = Button(parent,
                       text = 'Clear',
                       command = self.clear)
	clear.grid(row=8, column=1)
        start = Button(parent,
                       text = 'Start', fg="green",
                       command = self.start)
	start.grid(row=8, column=2, sticky=E)
        
        text_eq = StringVar()
        text_eq.set(      "-div f(x,y) grad v  + g(x,y) v = s")
        l1 = Label(f, textvariable=text_eq)
	l1.grid(row=0, column=0,sticky=W, columnspan=3)

	text_f_funct = StringVar()
	text_f_funct.set("f(x,y)=>")
	lf = Label(f, textvariable=text_f_funct)
	lf.grid(row=1, column=0, sticky=W)
        self.f_funct = Entry(f,width=40)
	self.f_funct.insert(0,"1.0")
        self.f_funct.grid(row=1, column=1, sticky=W)
	

	text_g_funct = StringVar()
	text_g_funct.set("g(x,y)=>")
	lg = Label(f, textvariable=text_g_funct)
	lg.grid(row=2, column=0, sticky=W)
        self.g_funct = Entry(f,width=40)
	self.g_funct.insert(0,"0.0")
        self.g_funct.grid(row=2, column=1, sticky=W)
 
	text_s_funct = StringVar()
	text_s_funct.set("s(x,y)=>")
	ls = Label(f, textvariable=text_s_funct)
	ls.grid(row=3, column=0, sticky=W)
        self.s_funct = Entry(f,width=40)
	self.s_funct.insert(0,"0.0")
        self.s_funct.grid(row=3, column=1, sticky=W)

        self.text_number = StringVar()
        l2 = Label(f, textvariable=self.text_number)
        self.text_number.set("Grid size nx*ny ")
        self.number = Entry(f, width=3)
	self.number.insert(0, "100")
	l2.grid(row=4,column=0,sticky=E)
        self.number.grid(row=4, column=1)

        f.grid()

      
        
    def start(self):
        self.f_funct_str = self.f_funct.get()
        self.g_funct_str = self.g_funct.get()
        self.s_funct_str = self.s_funct.get()
        self.nsize = string.atoi(self.number.get())
        start = time.time()
        self.simulate()
        self.finish()
        print 'Time used ',time.time()-start,' [s]'

    def finish(self):
        self.text_number.set("Grid size nx*ny")

    def clear(self):
        # is there a better way to clear?
        self.canvas.create_polygon(0, 0, self.width, 0,
                                   self.width, self.height,
                                   0, self.height, 0, 0, fill='white' )

    def plot(self, f=[]):
		if f==[]: f = self.cells.node.nodes()

		cmax = max(f)
		cmin = min(f)
		offset =  0.05*min(self.width, self.height)
		xmin, ymin, xmax, ymax = self.xmin, self.ymin, self.xmax, self.ymax
		scale =  min(0.9*self.width/(xmax-xmin),
                             0.9*self.height/(ymax-ymin))


		for index in self.cells.data.keys():
			ia, ib, ic = self.cells.data[index]
			xa = offset+scale*             (self.cells.node.x(ia)-xmin)
                        ya = self.height -offset-scale*(self.cells.node.y(ia)-ymin)
			xb = offset+scale*             (self.cells.node.x(ib)-xmin)
                        yb = self.height -offset-scale*(self.cells.node.y(ib)-ymin)
			xc = offset+scale*             (self.cells.node.x(ic)-xmin)
                        yc = self.height -offset-scale*(self.cells.node.y(ic)-ymin)
			x0 = (xa+xb+xc)/3
			y0 = (ya+yb+yc)/3

			fabc = (f[ia] + f[ib] + f[ic])/3.0
			n = len(self.cells.node)
		      	color = colormap.strRgb(fabc, cmin, cmax)
			self.canvas.create_polygon(
                            xa, ya, xb, yb, xc, yc, fill=color) 
			self.canvas.create_line(xa, ya, xb, yb)
			self.canvas.create_line(xb, yb, xc, yc)
			self.canvas.create_line(xc, yc, xa, ya)
		# add min/max values
		max_flag=1
		min_flag=1
		for inode in self.cells.node.nodes():
			fnode = f[inode]
			xnode = offset+scale*(self.cells.node.x(inode)-xmin)
			ynode = self.height -offset-scale*(self.cells.node.y(inode)-ymin)
			if fnode==cmax:
			   col='blue'
			   self.canvas.create_polygon(xnode-5,ynode+5,xnode+5,ynode+5,xnode, ynode-5, fill=col)
			   if max_flag:
                               self.canvas.create_polygon(xnode-10,ynode-1,xnode+22,ynode-1,xnode+22, ynode-12, xnode-10, ynode-12, fill='yellow')
                               self.canvas.create_text(xnode+6,ynode-6, text=str('%4.1f' % fnode), fill=col) 
			   max_flag=0		
			if fnode==cmin:
			   col='yellow'
			   self.canvas.create_polygon(xnode-5,ynode-5,xnode+5,ynode-5,xnode, ynode+5, fill=col)
			   if min_flag:
                               self.canvas.create_polygon(xnode-10,ynode-1,xnode+22,ynode-1,xnode+22, ynode-12, xnode-10, ynode-12, fill='blue')
                               self.canvas.create_text(xnode+6,ynode-6, text=str('%4.1f' % fnode), fill=col)
			   min_flag=0		


    def simulate(self):
        # 1. Domain, mesh and equation creation

        self.nx1 = int(sqrt(self.nsize)/1.5)
        self.ny1 = int(sqrt(self.nsize)*1.5)
        self.nx1 = max(3, self.nx1)
        self.ny1 = max(3, self.ny1)

        # geometry
	pos = []
	for iy in range(self.ny1):
		pos.append([])
		for ix in range(self.nx1):
			rho, phi = 1.+ix/float(self.nx1-1), pi*iy/float(self.ny1-1)
			x, y = rho*cos(phi), rho*sin(phi)
			pos[iy].append((x, y))

        
        
        self.grid = reg2tri.criss(pos)
        
        (self.xmin, self.ymin, self.xmax, self.ymax) = self.grid.boxsize()

	self.cells = cell.cell(self.grid)
        equ = ellipt2d(self.grid, \
                       ((self.f_funct_str,'0'),('0',self.f_funct_str)), \
                       self.g_funct_str, self.s_funct_str)
##        or
##        equ = ellipt2d(self.grid, (self.f_funct_str,self.f_funct_str), \
##                       self.g_funct_str, self.s_funct_str)
##        or
##        equ = ellipt2d(self.grid, self.f_funct_str, \
##                       self.g_funct_str, self.s_funct_str)
        
	# 2. Assemble stiffness matrix and compute source vector
        
	[amat, s] = equ.stiffnessMat()

	# 3. Apply Dirichlet boundary conditions
        
	self.db = DirichletBound({})
        for iy in range(self.ny1):
            self.db[iy] = 0.0              
            self.db[(self.nx1-1)*self.ny1+iy] = 1.0 

	equ.dirichletB(self.db,amat,s)	
	
        # 4. Solve linear system

	v0 = s # initial guess
        tol = 1.0e-6
        niter_max = 2*len(s) # max number of CG iterations
	t0 = time.time()
        v = amat.CGsolve(v0, s, tol, niter_max )
	print 'time in CG ', time.time() - t0, ' [s]'
	t0 = time.time()
        # the following solver is ~ 10x more performant
        # but requires the C/fortran module umfpack 
	#v = umfsparse.solve(amat, s)
	#print 'time in umfsparse.solve ', time.time() - t0, ' [s]'
	print ' error = ', vector.sum(dot(amat, v)-s)

        self.plot(v)

	equ.toUCD(v, "ellipt2d.inp")

        print 'max(v)=', max(v)
        print 'min(v)=', min(v)

if __name__ == "__main__":

    root = Tk()
    app = gui(root)
    root.mainloop()







