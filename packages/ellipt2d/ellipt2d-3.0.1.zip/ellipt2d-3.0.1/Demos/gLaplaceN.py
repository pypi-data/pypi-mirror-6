#!/usr/bin/env python

"""
Module to compute some Green functions and their derivative in
cylindrical geometry
$Id: gLaplaceN.py,v 1.1 2010/01/28 20:28:20 pletzer Exp $
"""

import scipy.special
from math import sqrt, pi

class Green:

    def __init__(self, nTor):
        """
        Ctor
        @param nTor toroidal mode
        """
        self.nTor = float(nTor)
        self.lam = None
        self.s = None
        self.s2m1 = None
        self.p = None

    def set(self, x1, y1, x2, y2):
        """
        Set positions
        @param x1 observer-x
        @param y1 observer-y
        @param x2 source-x
        @param y2 source-y
        """
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        
        self.lam = 1.0 + ( (x1-x2)**2 + (y1-y2)**2 )/(2.0*x1*x2)
        self.s = self.lam/sqrt(self.lam**2 - 1.0)
        self.s2m1 = self.s**2 - 1.0
        p = (self.s - 1.0)/(self.s + 1.0)

        n = self.nTor
        gammaNHalf = scipy.special.gamma(n + 0.5)
        gammaN1 = scipy.special.gamma(n + 1.0)
        hyp2f1 = scipy.special.hyp2f1(n + 0.5, 0.5, n+1.0, p)
        self.g = sqrt(1./(pi*x1*x2)) * gammaNHalf * p**(n/2. + 0.25) * hyp2f1 / gammaN1

        n = self.nTor + 1.0
        gammaNHalf = scipy.special.gamma(n + 0.5)
        gammaN1 = scipy.special.gamma(n + 1.0)
        hyp2f1 = scipy.special.hyp2f1(n + 0.5, 0.5, n+1.0, p)
        self.g1 = sqrt(1./(pi*x1*x2)) * gammaNHalf * p**(n/2. + 0.25) * hyp2f1 / gammaN1

        self.dgnds = (self.nTor+0.5)*(self.s*self.g/sqrt(self.s2m1) - self.g1)/sqrt(self.s2m1)
        
    def get(self):
        """
        @return Green function value
        """
        return self.g

    def getDx1(self):
        """
        @return derivative with respect to x1
        """
        return -self.g/(2.0*self.x1) + \
               (self.lam*self.x2 - self.x1)*self.s2m1**(3./2.) * \
               self.dgnds / (self.x1*self.x2)

    def getDy1(self):
        """
        @return derivative with respect to y1
        """
        return (self.y2 - self.y1)*self.s2m1**(3./2.) * \
               self.dgnds / (self.x1*self.x2)

########################################################################
def main():
    g = Green(nTor=2)
    g.set(x1=1.5, y1=0.1, x2=1.0, y2=0.0)
    print 'value = ', g.get()
    print 'd/x1  = ', g.getDx1()
    print 'd/y1  = ', g.getDy1()

if __name__ == '__main__': main()
