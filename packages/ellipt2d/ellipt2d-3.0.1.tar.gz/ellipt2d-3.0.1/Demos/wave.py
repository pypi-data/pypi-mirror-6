#!/usr/bin/python

# $Id: wave.py,v 1.2 2006/01/17 21:28:05 pletzer Exp $

"""
Free surface water wave
"""

import ellipt2d
import Triangulate
import superlu
import copy
import operator

LARGE = 1.254354e+8

def total_amount(xy):
    return reduce( operator.add, \
                          [ (xy[i+1][0]-xy[i][0])*(xy[i+1][1]+xy[i][1])/2.0 \
                            for i in range(len(xy)-1) ] )

class wave:

    def __init__(self,
                 boxsize=(1., 2.),
                 dt=0.1,
                 gravity=9.81,
                 ):


        self.xmax, self.ymax = boxsize
        self.dt      = dt
        self.gravity = gravity

        self.xy_surf = []
        self.vl_surf = []
        self.ph_surf = []

    def setFreeSurfaceCoordinates(self, xy):

        n = len(xy)
        self.xy_surf = xy
        # compute eq water level
        self.ewl = total_amount(xy)/(self.xmax)

    def getFreeSurfaceCoordinates(self):

        return self.xy_surf

    def getFreeSurfaceVelocity(self):

        return self.vl_surf

    def setFreeSurfacePotential(self, phis):

        n = len(phis)
        self.ph_surf = phis

    def solveLaplace(self):

        # 1. triangulate
        
        t = Triangulate.Triangulate()
        i_surf = range(len(self.xy_surf))
        pts = [self.xy_surf[i] for i in i_surf] + \
              [(self.xmax, 0.), (0.0, 0.0)]
        n   = len(pts)
        seg = [(i,i+1) for i in range(n-1)] + [(n-1,0)]
        att = [(1., self.ph_surf[i],) for i in i_surf] + \
               [(0., 0.0,), (0., 0.0,)]

        t.set_points(pts)
        t.set_segments(seg)  # are these segments correct?
        t.set_attributes(att)

        t.triangulate(area=0.005, mode='pzq27eQ')

        # 2. assemble stiffness matrix

        grid = t.get_nodes()
        #grid.plot()
        
        self.eq = ellipt2d.ellipt2d(grid, '1.', None, None)
        [amat, rhs] = self.eq.stiffnessMat()

        # 3. apply BCs
        
        att  = t.get_attributes()
        for i in range(len(grid)):
            is_surf, ph = att[i]
            if is_surf==1.0: # on surf
                amat[i,i] = LARGE
                rhs[i]    = LARGE*ph
        
        # 4. solve
        
        self.phi = superlu.solve(amat, rhs)

        # 5. grad phi at the surface (=velocity)

        self.vl_surf = [[0.,0.,] for i in i_surf]

        for ij, m in t.get_edges():
            i, j = ij
            if att[i] and i in i_surf:
##                if i not in i_surf:
##                    raise 'Error: i=%d i_surf=%s' \
##                          % (i, str(i_sruf))
                # free surface
                xi, yi = grid[i][0]
                nis    = grid[i][1] # neighbors to node i
                xj, yj = grid[j][0]
                njs    = grid[j][1]
                k = None
                # find the 3rd node k that closes the triangle
                for el in nis:
                    if el != j and el in njs:
                        k = el
                        break
                if k==None: raise 'Error: could not find opposite node: i,j='\
                   % (i,j)
                xk, yk = grid[k][0]

                dx1 = xj - xi
                dx2 = xk - xi
                dy1 = yj - yi
                dy2 = yk - yi

                dp1 = self.phi[j] - self.phi[i]
                dp2 = self.phi[k] - self.phi[i]

                jac = dx1*dy2 - dx2*dy1

                # half the contribution coming from each edge
                gx = (dp1*dy2 - dp2*dy1)/jac
                gy = (dp2*dx1 - dp1*dx2)/jac
                
                self.vl_surf[i][0] += gx*0.5
                self.vl_surf[i][1] += gy*0.5
##                self.vl_surf[j][0] += gx
##                self.vl_surf[j][1] += gy
                

    def updateFreeSurface(self):

        xy = copy.deepcopy(self.xy_surf)
        ph = copy.deepcopy(self.ph_surf)
        i_surf = range(len(self.xy_surf))

        # runge kutta 4

        # k1
        self.solveLaplace()
        grad_phi = self.vl_surf
        coef = 0.5
        k1_x = [self.dt*grad_phi[i][0] for i in i_surf]
        k1_x[0] = 0.0; k1_x[-1] = 0.0 # d phi/dn = 0 at edges
        k1_y = [self.dt*grad_phi[i][1] for i in i_surf]
        k1_p = [-self.dt*( \
            self.gravity*(self.xy_surf[i][1]-self.ewl) + \
            0.5*(grad_phi[i][0]**2+grad_phi[i][1]**2) ) \
                for i in i_surf]
        self.xy_surf = [ (xy[i][0] + coef*k1_x[i], xy[i][1] + coef*k1_y[i] ) \
                         for i in i_surf ]
        self.ph_surf = [ ph[i] + coef*k1_p[i] for i in i_surf ]

        # k2
        self.solveLaplace()
        grad_phi = self.vl_surf
        coef = 0.5
        k2_x = [self.dt*grad_phi[i][0] for i in i_surf]
        k2_x[0] = 0.0; k2_x[-1] = 0.0 # d phi/dn = 0 at edges
        k2_y = [self.dt*grad_phi[i][1] for i in i_surf]
        k2_p = [-self.dt*( \
            self.gravity*(self.xy_surf[i][1]-self.ewl) + \
            0.5*(grad_phi[i][0]**2+grad_phi[i][1]**2) ) \
                for i in i_surf]
        self.xy_surf = [ (xy[i][0] + coef*k2_x[i], xy[i][1] + coef*k2_y[i] ) \
                         for i in i_surf ]
        self.ph_surf = [ ph[i] + coef*k2_p[i] for i in i_surf ]

        # k3
        self.solveLaplace()
        grad_phi = self.vl_surf
        coef = 1.0
        k3_x = [self.dt*grad_phi[i][0] for i in i_surf]
        k3_x[0] = 0.0; k3_x[-1] = 0.0 # d phi/dn = 0 at edges
        k3_y = [self.dt*grad_phi[i][1] for i in i_surf]
        k3_p = [-self.dt*( \
            self.gravity*(self.xy_surf[i][1]-self.ewl) + \
            0.5*(grad_phi[i][0]**2+grad_phi[i][1]**2) ) \
                for i in i_surf]
        self.xy_surf = [ (xy[i][0] + coef*k3_x[i], xy[i][1] + coef*k3_y[i] ) \
                         for i in i_surf ]
        self.ph_surf = [ ph[i] + coef*k3_p[i] for i in i_surf ]

        # k4
        self.solveLaplace()
        grad_phi = self.vl_surf
        coef = 0.5
        k4_x = [self.dt*grad_phi[i][0] for i in i_surf]
        k4_x[0] = 0.0; k4_x[-1] = 0.0 # d phi/dn = 0 at edges
        k4_y = [self.dt*grad_phi[i][1] for i in i_surf]
        k4_p = [-self.dt*( \
            self.gravity*(self.xy_surf[i][1]-self.ewl) + \
            0.5*(grad_phi[i][0]**2+grad_phi[i][1]**2) ) \
                for i in i_surf]

        # update positions + potential
        self.xy_surf = [  (  xy[i][0] + \
                          k1_x[i]/6. + k2_x[i]/3. + k3_x[i]/3. + k4_x[i]/6. , \
                           xy[i][1] + \
                          k1_y[i]/6. + k2_y[i]/3. + k3_y[i]/3. + k4_y[i]/6. ) \
                         for i in i_surf ]
        
        self.ph_surf = [ ph[i] + \
                         k1_p[i]/6. + k2_p[i]/3. + k3_p[i]/3. + k4_p[i]/6. \
                         for i in i_surf ]

    def water_amount_error(self):
        return (total_amount(self.xy_surf) - self.ewl*self.xmax)/(self.ewl*self.xmax)

    def plot(self, canvas, color='black', width=300, height=300):

        scale = min(width/self.xmax, height/self.ymax)
        n = len(self.xy_surf)
        canvas.create_line( \
            [ (scale*self.xy_surf[i][0], height-scale*self.xy_surf[i][1]) \
            for i in range(n) ],
            fill=color)


#############################################################################

def main():

    from math import sin, cos, pi, sqrt
    import Tkinter
    import tkplot

    width, height = 1200, 600
    root = Tkinter.Tk()
    canvas = Tkinter.Canvas(bg="white", width=width, height=height)
    canvas.pack()

    xmax, ymax = 2.0, 1.0
    w = wave(boxsize=(xmax, ymax), dt=0.1)
    nx = 11
    dx = xmax/float(nx-1)
    wl = 0.5
    xy = [ (i*dx, wl*(1.+0.2*cos(pi*i*dx/xmax)),) for i in range(nx)]
    w.setFreeSurfaceCoordinates(xy)
    phis = [ 0.0 for i in range(nx)]
    w.setFreeSurfacePotential(phis)
    w.plot(canvas, color='red', width=width, height=height)

    nt = 10
    for i in range(nt):
        w.updateFreeSurface()
        xy = w.getFreeSurfaceCoordinates()
        print 'iteration %d error %g ' % (i, w.water_amount_error())
        w.plot(canvas, color='green', width=width, height=height)

    w.plot(canvas, color='blue', width=width, height=height)
##    tkplot.tkplot(canvas, w.eq.grid, w.phi, node_no=1,
##                      WIDTH=width, HEIGHT=height)

    root.mainloop()
    
if __name__=='__main__': main()
        
    

    

    
        
