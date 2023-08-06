#!/usr/bin/env python
# Some methods involving integrals over cells which are 
# useful to construct the stiffness matrix
#
# A. Pletzer 13-Jan-2000
# $Id: triangle.py,v 1.7 2013/12/20 22:38:27 pletzer Exp $

"""
ellipt2d: node connectivity data structure
"""

import math

class triangle:
    """
    Compute all integrals over cells needed to build the stiffness matrix.
    
    The argument i, when present, denotes the offset node index which
    takes the value 0, 1, or 2. A value of i=0 indicates self coupling,
    1=coupling between the node and its 1st neighbour along the
    counterclockwise path, 2=coupling with the 2nd neighbour.
    """

    def __init__(self, grid, ia, ib, ic):
        """
        Create a triangular cell given a node object (grid) and 3
        node indices
        """
        self.ia, self.ib, self.ic = ia, ib, ic
        self.xa, self.ya = grid.x(ia), grid.y(ia)
        self.xb, self.yb = grid.x(ib), grid.y(ib)
        self.xc, self.yc = grid.x(ic), grid.y(ic)

        self.xba, self.yba = self.xb - self.xa, self.yb - self.ya
        self.xcb, self.ycb = self.xc - self.xb, self.yc - self.yb
        self.xac, self.yac = self.xa - self.xc, self.ya - self.yc

        self.area =  0.5*( -self.xba*self.yac + self.xac*(self.yb-self.ya) )
        self.area4 = 4.0*self.area

        self.int_dxdx = (self.ycb*self.ycb/self.area4, 
                         self.ycb*self.yac/self.area4,
                         self.ycb*self.yba/self.area4)

        self.int_dydy = (self.xcb*self.xcb/self.area4,
                         self.xcb*self.xac/self.area4,
                         self.xcb*self.xba/self.area4)

    def integral_dxdx(self, i):
        """
        Integral of d e_i/dx * d e_j/dx
        """
        return self.int_dxdx[i]

    def integral_dydy(self, i):
        """
        Integral of d e_i/dy * d e_j/dy
        """
        return self.int_dydy[i]

    def integral_dxdy(self, i):
        """
        Integral of d e_i/dx * d e_j/dy
        """
        if i==0:
            return -(self.yb-self.yc)*(self.xb-self.xc)/self.area4
        elif i==1:
            return -(self.yb-self.yc)*(self.xc-self.xa)/self.area4
        elif i==2:
            return -(self.yb-self.yc)*(self.xa-self.xb)/self.area4
        else:
            print('***error index i =',i,' > 2 in triangle::integral_dxdy')
            return 0.0

    def integral_dydx(self, i):
        """
        Integral of d e_i/dy * d e_j/dx
        """
        if i==0:
            return -(self.xc-self.xb)*(self.yc-self.yb)/self.area4
        elif i==1:
            return -(self.xc-self.xb)*(self.ya-self.yc)/self.area4
        elif i==2:
            return -(self.xc-self.xb)*self.yba/self.area4
        else:
            print('***error index i =',i,' > 2 in triangle::integral_dydx')
            return 0.0


    def integral_g(self, i, g):
        """
        Integral of e_i g e_j
        """
	area = abs(self.area)
	res = 0.0
	if i==0:
		res = g[0]/ 20.0 + g[1]/ 60.0 + g[2]/ 60.0
	elif i==1:
		res = g[0]/ 60.0 + g[1]/ 60.0 + g[2]/120.0
	elif i==2:
		res = g[0]/ 60.0 + g[1]/120.0 + g[2]/ 60.0
	else:
		print('***error index i =',i,' > 2 in triangle::integral_g')
	return res*2.0*area

    def integral_s(self, s):
        """
        Integral of e_i s
        """
	area = abs(self.area)
	return 2.0*area*( s[0]/12.0 + s[1]/24.0 + s[2]/24.0 )
