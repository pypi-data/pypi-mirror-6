#!/usr/bin/env python

VERSION = "$Id: grTests.py,v 1.5 2009/06/26 17:53:18 pletzer Exp $"

"""
Test grin code
"""

def test0(R0=1.0, a=0.3, b=0.36, nTor=1, kappa=1.7, delta=0.3,
          nt1=64):

    """
    Laplace equation in toroidal geometry
    """
    
    from grMesh import Mesh
    from Tkinter import Tk, Frame, Canvas
    from grResponseMatrix import ResponseMatrix
    from math import pi, cos, sin, sqrt, atan2
    import numpy

    rm = ResponseMatrix()
    
    # contour 1
    dt1 = 2*pi/float(nt1)
    pts1 = [ (R0 + a*cos(i*dt1 + delta*sin(i*dt1)), kappa*a*sin(i*dt1)) for i in range(nt1) ]
    
    # contour 2
    nt2 = int(b * nt1/a + 0.5)
    dt2 = 2*pi/float(nt2)
    pts2 = [ (R0 + b*cos(i*dt2 + delta*sin(i*dt2)), kappa*b*sin(i*dt2)) for i in range(nt2) ]

    tri = Mesh()
    tri.generate(pts1, pts2)
    #tri.show()
    rm.setTriangulation( tri )

    # Operators
    assert(nTor > 0)
    rm.setOperators(f='x', g='%d/x' % nTor**2)

    n1 = len(tri.getContour1())
    n2 = len(tri.getContour2())
    nodes1 = tri.getNodes1()
    nodes2 = tri.getNodes2()

    # Dirichlet response matrices to inhomogenous Neumann
    A11 = numpy.zeros( (n1,n1), numpy.float64 )
    A12 = numpy.zeros( (n1,n2), numpy.float64 )
    A21 = numpy.zeros( (n2,n1), numpy.float64 )
    A22 = numpy.zeros( (n2,n2), numpy.float64 )

    segments1 = tri.getSegments1()
    for seg in segments1:
        rhs = rm.setUnitNormalDerivative(seg)
        A11[:,seg[0]] = rm.getResponse(nodes1, rhs)
        A21[:,seg[0]] = rm.getResponse(nodes2, rhs)
        
    
    segments2 = tri.getSegments2()
    for seg in segments2:
        rhs = rm.setUnitNormalDerivative(seg)
        A12[:,seg[0]-n1] = rm.getResponse(nodes1, rhs)
        A22[:,seg[0]-n1] = rm.getResponse(nodes2, rhs)
        
##     print 'A11\n'
##     print A11
##     print 'A12\n'
##     print A12
##     print 'A21\n'
##     print A21
##     print 'A22\n'
##     print A22

    print 'Response to unit Neumann on (1) and zero Dirichlet on (2):'

    dChi1Dn = - numpy.ones( (n1,), numpy.float64 )
    A22Inv = numpy.linalg.inv(A22)
    chi1 = numpy.dot( (A11 - numpy.dot(A12, numpy.dot(A22Inv, A21))), dChi1Dn)
    print chi1
    print 'Min/Max: %10.8g %10.8g' % (min(chi1), max(chi1))


def test1():

    # n=0 test
    
    from grMesh import Mesh
    from Triangulate import Triangulate
    from ellipt2d import ellipt2d
    from tkplot import tkplot
    import dsupralu
    from Tkinter import Tk, Frame, Canvas
    from grResponseMatrix import ResponseMatrix
    from math import pi, cos, sin, sqrt
    import numpy

    rm = ResponseMatrix()
    a = 1.0
    b = 2.0
    # contour 1
    nt1 = 8
    dt1 = 2*pi/float(nt1)
    pts1 = [ (a*cos(i*dt1), a*sin(i*dt1)) for i in range(nt1) ]
    # contour 2
    nt2 = int(b * nt1 / a + 0.5)
    dt2 = 2*pi/float(nt2)
    pts2 = [ (b*cos(i*dt2), b*sin(i*dt2)) for i in range(nt2) ]

    tri = Mesh()
    tri.generate(pts1, pts2)
    #tri.show()
    rm.setTriangulation( tri )

    # Cartesian
    rm.setOperators(f='1.0', g=0.0)

    n1 = len(tri.getContour1())
    n2 = len(tri.getContour2())
    nodes1 = tri.getNodes1()
    nodes2 = tri.getNodes2()
    A11 = numpy.zeros( (n1,n1), numpy.float64 )
    A12 = numpy.zeros( (n1,n2), numpy.float64 )
    A21 = numpy.zeros( (n2,n1), numpy.float64 )
    A22 = numpy.zeros( (n2,n2), numpy.float64 )

    for s in tri.getSegments1():
        rhs = rm.setUnitNormalDerivative(s)
        A11[:,s[0]] = rm.getResponse(nodes1, rhs)
        A21[:,s[0]] = rm.getResponse(nodes2, rhs)

    for s in tri.getSegments2():
        rhs = rm.setUnitNormalDerivative(s)
        A12[:,s[0]-n1] = rm.getResponse(nodes1, rhs)
        A22[:,s[0]-n1] = rm.getResponse(nodes2, rhs)

    print A21

    # apply cos m theta source
    mMode = 1
    thetaMid1 = numpy.array( [ dt1*(i + 0.5) for i in range(n1) ] )
    dChiSrce1 = numpy.cos( mMode * thetaMid1 )
    print dChiSrce1
    thetaMid2 = numpy.array( [ dt2*(i + 0.5) for i in range(n2) ] )
    chiResps2 = numpy.dot( A21, dChiSrce1 )
    print chiResps2
    for i in range(n2):
        numVal = chiResps2[i]
        excVal = (b/a)**mMode / ((1.0 - (b/a)**(2*mMode)) * mMode)
        t = thetaMid2[i] - dt2/2.0
        excVal *= cos(mMode * t)
        print 'node=%d theta=%f numerical value=%g exact value=%g' % \
              (i, t, numVal, excVal)


def test2():

    # n=0 test
    
    from grMesh import Mesh
    from Triangulate import Triangulate
    from ellipt2d import ellipt2d
    from tkplot import tkplot
    import dsupralu
    from Tkinter import Tk, Frame, Canvas
    from grResponseMatrix import ResponseMatrix
    from math import pi, cos, sin, sqrt
    import numpy
    from numpy import linalg
    from numpy import matrix

    rm = ResponseMatrix()
    a = 1.0
    b = 2.0
    r0 = 3.0
    nTor = 1
    # contour 1
    nt1 = 4 # 8
    dt1 = 2*pi/float(nt1)
    pts1 = [ (r0+a*cos(i*dt1), a*sin(i*dt1)) for i in range(nt1) ]
    # contour 2
    nt2 = 16
    dt2 = 2*pi/float(nt2)
    pts2 = [ (r0+b*cos(i*dt2), b*sin(i*dt2)) for i in range(nt2) ]

    tri = Mesh()
    tri.generate(pts1, pts2)
    #tri.show()
    rm.setTriangulation( tri )
        
    rm.setOperators(f='1.0', g='%d'%nTor**2)
    #rm.setOperators(f='x', g='%d/x'%nTor**2)
    #rm.setOperators(f='1.0/x', g=0.0)

    n1 = len(tri.getContour1())
    n2 = len(tri.getContour2())
    nodes1 = tri.getNodes1()
    nodes2 = tri.getNodes2()
    A11 = numpy.zeros( (n1,n1), numpy.float64 )
    A12 = numpy.zeros( (n1,n2), numpy.float64 )
    A21 = numpy.zeros( (n2,n1), numpy.float64 )
    A22 = numpy.zeros( (n2,n2), numpy.float64 )

    for s in tri.getSegments1():
        rhs = rm.setUnitNormalDerivative(s)
        print 'segment 1 index=', s[0]
        A11[:,s[0]] = rm.getResponse(nodes1, rhs)
        A21[:,s[0]] = rm.getResponse(nodes2, rhs)

    for s in tri.getSegments2():
        rhs = rm.setUnitNormalDerivative(s)
        print 'segment 2 index=', s[0]
        A12[:,s[0]-n1] = rm.getResponse(nodes1, rhs)
        A22[:,s[0]-n1] = rm.getResponse(nodes2, rhs)

    # check:

    # construct points in the middle of segments
    pts1S = [ (r0+a*cos( (i+0.5)*dt1), a*sin((i+0.5)*dt1)) for i in range(nt1) ]
    pts2S = [ (r0+b*cos( (i+0.5)*dt2), b*sin((i+0.5)*dt2)) for i in range(nt2) ]
    # these points are a little inside (for computing normal derivatives)
    aI = a * 1.05
    pts1SI = [ (r0+aI*cos( (i+0.5)*dt1), aI*sin((i+0.5)*dt1)) for i in range(nt1) ]
    bI = b * 0.95
    pts2SI = [ (r0+bI*cos( (i+0.5)*dt2), bI*sin((i+0.5)*dt2)) for i in range(nt2) ]

    pts = pts1 + pts2 + pts1SI + pts2SI
    segs = [(i, i+1) for i in range(n1-1)]  + [(n1-1,0)] + \
           [(n1+i, n1+i+1) for i in range(n2-1)]  + [(n1+n2-1,n1)]
    holes = [(r0, 0.)]
    triangle = Triangulate()
    triangle.set_points(pts)
    triangle.set_segments(segs)
    triangle.set_holes(holes)
    triangle.triangulate(area=0.1, mode='pzq%fe' % 30.0)
    grd = triangle.get_nodes()

    equ = ellipt2d(grd, 'x', '%d/x'%nTor**2, None)
    #equ = ellipt2d(grd, '1./x', None, None)
    aMatrix, rhs = equ.stiffnessMat()

    # set Dirichlet 1 on fist node
    LARGE = 1.2534e8
    for i in range(n1):
        aMatrix[i,i] = LARGE
    rhs[0] = LARGE * 0.35059402
    rhs[1] = LARGE * 0.33901947
    rhs[2] = LARGE * 0.04367755
    rhs[3] = LARGE * 0.04185648
    
    # solve
    handles = dsupralu.new(aMatrix, aMatrix.size()[0])
    colperm = 2
    dsupralu.colperm(handles[0], colperm)
    dsupralu.lu(handles[0])
    solution = dsupralu.solve(handles[0], rhs)

    print 'normal gradients'
    i0, i1 = 40, 20
    x1, y1 =  grd[i1][0]
    x0, y0 =  grd[i0][0]
    df     = solution[i1] - solution[i0]
    dx     = x1 - x0
    dy     = y1 - y0
    print sqrt( (df/dx)**2 + (df/dy)**2 )

    sol1 = numpy.resize( numpy.array( [solution[i] for i in range(0, n1)] ), (n1,1) )
    print matrix(A11)
    A11Inverse = linalg.inv(matrix(A11))
    print 'normal deriv 1 = ', A11Inverse * sol1
##     sol2 = [solution[i] for i in range(n1, n1+n2)]
##     sol2p = numpy.dot(  numpy.dot( A21, linalg.inv(A11) ),  sol1)
##     sol2pp = numpy.dot( A21, numpy.dot( linalg.inv(A11), sol1) )
##     #print matrix(A21) * matrix(linalg.inv(A11))
##     sol2ppp = matrix(A21) * matrix(linalg.inv(A11)) * matrix(sol1)
##     print A11
##     print linalg.inv(matrix(A11))
##     print 'sol2: ', sol2
##     print 'sol2p: ', sol2p
##     print 'sol2pp: ', sol2pp
##     print 'sol2ppp: ', sol2ppp
    

    # show
    root = Tk() 
    frame = Frame(root) 
    frame.pack() 
    w, h = 800, 800 
    canvas = Canvas(bg="white", width=w, height=h) 
    canvas.pack() 
    tkplot(canvas, grd, solution, 1, 1, 1, w, h) 
    root.mainloop()
    

if __name__ == '__main__':
    test0()
