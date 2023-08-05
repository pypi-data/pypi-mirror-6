#!/usr/bin/env python
# Some methods involving integrals over cells which are 
# useful to construct the stiffness matrix
#
# A. Pletzer 13-Jan-2000
# $Id: triangle.py,v 1.4 2003/07/16 13:50:10 pletzer Exp $

"""
ellipt2d: node connectivity data structure
"""

from math import *


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
        self.xa = grid.x(ia)
        self.ya = grid.y(ia)
        self.xb = grid.x(ib)
        self.yb = grid.y(ib)
        self.xc = grid.x(ic)
        self.yc = grid.y(ic)
        self.area = 0.5*( (self.xb-self.xa)*(self.yc-self.ya) - (self.xc-self.xa)*(self.yb-self.ya) )

    def integral_dxdx(self, i):
        """
        Integral of d e_i/dx * d e_j/dx
        """
        if i==0:
            return (self.yb-self.yc)*(self.yb-self.yc)/(4.0*self.area)
        elif i==1:
            return (self.yb-self.yc)*(self.yc-self.ya)/(4.0*self.area)
        elif i==2:
            return (self.yb-self.yc)*(self.ya-self.yb)/(4.0*self.area)
        else:
            print '***error index i =',i,' > 2 in triangle::integral_dxdx'
            return 0.0

    def integral_dxdy(self, i):
        """
        Integral of d e_i/dx * d e_j/dy
        """
        if i==0:
            return -(self.yb-self.yc)*(self.xb-self.xc)/(4.0*self.area)
        elif i==1:
            return -(self.yb-self.yc)*(self.xc-self.xa)/(4.0*self.area)
        elif i==2:
            return -(self.yb-self.yc)*(self.xa-self.xb)/(4.0*self.area)
        else:
            print '***error index i =',i,' > 2 in triangle::integral_dxdy'
            return 0.0

    def integral_dydx(self, i):
        """
        Integral of d e_i/dy * d e_j/dx
        """
        if i==0:
            return -(self.xc-self.xb)*(self.yc-self.yb)/(4.0*self.area)
        elif i==1:
            return -(self.xc-self.xb)*(self.ya-self.yc)/(4.0*self.area)
        elif i==2:
            return -(self.xc-self.xb)*(self.yb-self.ya)/(4.0*self.area)
        else:
            print '***error index i =',i,' > 2 in triangle::integral_dydx'
            return 0.0

    def integral_dydy(self, i):
        """
        Integral of d e_i/dy * d e_j/dy
        """
        if i==0:
            return (self.xc-self.xb)*(self.xc-self.xb)/(4.0*self.area)
        elif i==1:
            return (self.xc-self.xb)*(self.xa-self.xc)/(4.0*self.area)
        elif i==2:
            return (self.xc-self.xb)*(self.xb-self.xa)/(4.0*self.area)
        else:
            print '***error index i =',i,' > 2 in triangle::integral_dydy'
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
		print '***error index i =',i,' > 2 in triangle::integral_g'
	return res*2.0*area

    def integral_s(self, s):
        """
        Integral of e_i s
        """
	area = abs(self.area)
	return 2.0*area*( s[0]/12.0 + s[1]/24.0 + s[2]/24.0 )
