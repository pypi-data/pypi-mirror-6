#!/usr/bin/env python
#
# A. Pletzer, J. Mollis 8/1/2000

from math import pi
from ellipt2d import ellipt2d
from Ireg2tri import Ireg2tri
from DirichletBound import DirichletBound
import vector
import time, os
try:
    from geqdsk import geqdsk
except:
    raise "this demo requires geqdsk... (not supplied with ellipt2d)"
    
import superlu

class demo_RealisticIreg:
    """
    Unstructured mesh with realistic irregular geometryRe
    """
 
    def __init__(self):


        # 1. Equation definition--------------
        
	k = 2.*pi
	self.f_funct_str, self.g_funct_str, self.s_funct_str = '1', '%10.4f' % (-k**2), '0'
        

        # 2. Domain grid/boundary defintions----------------

        g = geqdsk("./g101544.00185")
        pps = g.getPlasmaGeometry()
        vacps = g.getLimiterGeometry()

        points = []
        seglist = []
        holelist = []
        regionlist = []

        dB = DirichletBound()

        for i in range(0,len(pps)-1):
            points.append(pps[i])
            dB[i] = 1.0

        for i in range(0,len(vacps)-2):
            points.append(vacps[i])
            dB[len(pps)-1 + i] = 0.0

        for j in range(0,len(pps)-2):
            seglist.append((j,j+1))
        seglist.append((0,len(pps)-2))
        pos = len(pps)-1   
        for j in range(pos,len(points)-1):
            seglist.append((j,j+1))
        seglist.append((pos,len(points)-1))

        holelist.append( (0.99,0.0) )
      
        ## Grid creation/boundary set up------------------

        initialAreaBound = 0.01
        meshgen = Ireg2tri(initialAreaBound)
        print 'points = ', points
        print 'seglist = ', seglist
        meshgen.setUpConvexHull(points,seglist,regionlist,holelist)

        meshgen.setUpDirichlet(dB)

        self.grid = meshgen.triangulate()
        self.grid = meshgen.refine(1)

        # update the boundary conditions
        meshgen.updateDirichlet(dB)
        dB.plot(self.grid)

        # 4. Set up the equation.

        equ = ellipt2d(self.grid, self.f_funct_str, self.g_funct_str, self.s_funct_str)
        
	# 5. Assemble stiffness matrix and compute source vector
	t = time.time()
        [amat, s] = equ.stiffnessMat()
	print 'Time to assemble stiffness matrix:',(time.time()-t),'Sec.'

	# 6. Apply Boundary conditions.

        equ.dirichletB(dB,amat,s)
        #equ.neumannB(nB,s)
        #equ.robinB(rB,amat,s)

        
        # 7. Solve linear system.

        to = time.time()
        v = superlu.solve(amat,s)
	print 'Time to solve Linear System:',(time.time()-to),'Sec.'

        # 8. Write DX and UCD formated files.

        equ.toUCD(v, 'ellipt2d.inp' )	 

	#9. Display results with OpenDX or AVS/Express.

	#os.system("dx -image ellipt2d.net")

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
        tkplot.tkplot(canvas, equ.grid, v, 0,0,1, WIDTH, HEIGHT) 
        root.mainloop() 

        


if __name__ == "__main__":

    a = demo_RealisticIreg()
    

