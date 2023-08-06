#!/usr/bin/env python

"""
Solve the Cartesian Helmholtz equation in a circular geometry with
circular cavities. Outward propagating waves are assumed on the
external boundary
"""

import cvector, cmath
from math import cos, sin, pi, sqrt, atan2, exp, sqrt

def Xcircle(x0, radius, t): return (x0 + radius*cos(t))
def Ycircle(y0, radius, t): return (y0 + radius*sin(t))


# g function = - n(x)**2
def gFunction(grid, ng, nh, Rring, Wring, N):
    res = [0.0 for i in range(len(grid))]
    height = ng - nh
    w2 = Wring**2
    for i in grid.data.keys():
        x, y = grid.data[i][0]
        t = atan2(y, x)
        r2 = min(10.0, ( (x-Rring*cos(t))**2 + (y-Rring*sin(t))**2 )/w2 )
        n = ng - height* exp(-r2)*(1.0 - cos(N*t/2)**10)
        res[i] = ng**2 - n**2
    return res


        

class bubble:

    def __init__(self, neff):
        """
        set default parameters

        dimensionas are in units of lambda_free_space, the wavelength
        of a plane wave in vacuum. 
        """

        self.neff = neff+0j # effective refractive index guess 
        
        # geometry
        self.Rclad = 4.0               # >> 1
        self.Rring = 1.5
        self.Wring = 0.5
        self.nBubbles = 3

        self.ng = 1.45 # refractive index of glass
        self.nh = 1.0 # air

        # resolution
        self.rN = 80 #int(2.*pi*self.Rring/self.Wring) #self.nBubbles * 16
        self.area = 0.05 # make smaller to increase resolution
        self.nRefine = 0
        

    def setGeometry(self):

        import Ireg2tri

        # external boundary, a large circle
        dt = 2.*pi/self.rN
        x0, y0 = 0., 0.
        xy = [(Xcircle(x0, self.Rclad, dt*i),
               Ycircle(y0, self.Rclad, dt*i))
              for i in range(self.rN)]
        self.extseglist = [(i,i+1) for i in range(self.rN-1)]
        self.extseglist.append( (self.rN-1, 0) )
        regionlist = []
        holelist = []

        # centre
        self.centreNode = len(xy)
        xy.append( (x0, y0) )
        
        # outer ring
        radius = self.Rring + self.Wring/2.
        xy += [(Xcircle(x0, radius, dt*i),
                Ycircle(y0, radius, dt*i)) for i in range(self.rN)]

        # middle ring
        radius = self.Rring
        xy += [(Xcircle(x0, radius, dt*i),
                Ycircle(y0, radius, dt*i)) for i in range(self.rN)]

        # inner ring
        radius = self.Rring - self.Wring/2.
        xy += [(Xcircle(x0, radius, dt*i),
                Ycircle(y0, radius, dt*i)) for i in range(self.rN)]

        # add points around centre
        nr = min(10, self.rN/3)
        dr = (self.Rring - self.Wring/2.)/(nr+1)
        nt = 4
        dt = 2.*pi/nt
        for j in range(nt):
            t = j*dt
            dr_cost, dr_sint = dr*cos(t), dr*sin(t)
            xy += [(x0+i*dr_cost, y0+i*dr_sint) for i in range(1, nr)]
            
        mesh = Ireg2tri.Ireg2tri(self.area)
        mesh.setUpConvexHull(xy, self.extseglist,
                             regionlist, holelist)
        mesh.triangulate()
        
        self.grid = mesh.refine(self.nRefine)
        
        #self.grid.plot()

    def assemble(self):

        import cellipt2d, RobinBound

        rB = RobinBound.RobinBound()
        A = 2*pi * cmath.sqrt(self.ng**2 - self.neff**2) * 1j
        for seg in self.extseglist:
            # use large Rclad approximation for escaping wave
            i, j = seg
            xi, yi = self.grid.x(i), self.grid.y(i)
            xj, yj = self.grid.x(j), self.grid.y(j)
            # average radius
            r0 = 0.5* sqrt( (xi + xj)**2 +  (yi + yj)**2 ) 
            rB[seg] = (0j, -A + 0.5/r0)
            self.grid.setBound( i )
            self.grid.setBound( j )

        #rB.plot(self.grid)
        

        # build system A x = lambda B x
        height = self.ng**2 -self.nh**2

        self.gvec = gFunction(self.grid,
                              self.ng, self.nh,
                              self.Rring, self.Wring,
                              self.nBubbles)

        #print min(self.gvec), max(self.gvec)
                              
        self.equ = cellipt2d.ellipt2d(grid=self.grid,
                                      f_funct='%f' % (1./(4*pi**2)),
                                      g_funct=self.gvec,
                                      s_funct='0.')
        
        [self.amat, rhs] = self.equ.stiffnessMat()

        identity = cellipt2d.ellipt2d(grid=self.grid,
                                      f_funct='0.',
                                      g_funct='1.',
                                      s_funct='0.')
        [self.bmat, rhs] = identity.stiffnessMat()

        # apply BCs on external boundary...
        self.equ.robinB(rB, self.amat, rhs)



    def solve(self, v, tol=1.e-6, niter=10):
        """
        Solve eigensystem:
        lambda0 = inital eigenvalue guess
        tol     = tolerance in eigenvalue
        niter   = max number of inverse iterations
        """

        import csuperlu
        
        lambda0 = self.ng**2 - self.neff**2 #- self.neff**2
        [self.lambd, self.v, residue, iter] = csuperlu.eigen(\
            self.amat, self.bmat, lambda0, v, tol, niter)

    def tkplot(self):
        
        from Tkinter import Tk, Frame, Button, Canvas, BOTTOM, LEFT
        import ctkplot, tkplot
        root = Tk() 
        frame = Frame(root) 
        frame.pack() 
        WIDTH, HEIGHT = 500, 450 
##        button = Button(frame, text="OK", fg="red", command=frame.quit) 
##        button.pack(side=BOTTOM) 
        canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
        canvas.pack(side=LEFT)
        canvas2 = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
        canvas2.pack(side=LEFT)
        tkplot.tkplot(canvas, self.grid, self.gvec, 0,0,1, WIDTH, HEIGHT) 
        ctkplot.ctkplot(canvas2, self.grid, self.v, 0,0,1, WIDTH, HEIGHT) 
        root.mainloop() 

###############################################################################
# main program
if __name__=='__main__':
    import sys, cmath
    try: 
        equ = bubble(neff = float(sys.argv[1]))
    except:
        equ = bubble(neff = 1.3)
    equ.setGeometry()
    count = 0
    diff = 999.
    # initial guess
    equ.v = cvector.zeros(len(equ.grid))
    equ.v[equ.centreNode] = 1.+0j
    while count < 10 and diff > 1.e-6:
        neff_old = equ.neff
        equ.assemble()
        equ.solve(equ.v)
        equ.neff = cmath.sqrt(equ.ng**2 - equ.lambd) #cmath.sqrt(-equ.lambd)
        print ' --> neff = ', equ.neff
        diff = abs(equ.neff - neff_old)/abs(neff_old)
        count += 1 
        
    equ.tkplot()
