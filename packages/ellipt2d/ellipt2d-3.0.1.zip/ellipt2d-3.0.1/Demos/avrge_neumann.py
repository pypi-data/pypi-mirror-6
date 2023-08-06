#!/usr/bin/env python

import sys
import ellipt2d
import Triangulate
import dsupralu
import vector
import math
import operator

# boundary contour
xy = [(0.,0.), (1.,0.), (1.,2./3.), (1.,1.), (2./3.,1.), (1./3.,1.),
      (1./3.,2./3.), (0., 2./3.), (0., 1./3.)]
n = len(xy)
seglist = [(i,i+1) for i in range(n-1)] + [(n-1,0)]

# stations nodes (node index: BC value}
station_values = {0:0.0, 1:1.0, 3:2.0, 6:1.0} #{1:10., 2:40., 4:130., 8:100.,}

# triangulate
area = 0.1
tri = Triangulate.Triangulate()
tri.set_points(xy)
tri.set_segments(seglist)
tri.triangulate(area)
tri.refine(2.0)
grid = tri.get_nodes(level=-1)

#grid.plot(tag=1)

# assemble FE system
equ = ellipt2d.ellipt2d(grid, f_funct='1.0', g_funct='0.0', s_funct='0.0')
A, b = equ.stiffnessMat()

# set Dirichlet BCs. This would normally require us to set all off
# diagonal elements of the incumbing node to zero, the diagonal element
# to 1 and the value of the right hand side vector to the boundary
# value. Here, we take a shortcut, just set the diagonal element to
# a large value and mutiply the rhs value by the same factor.
LARGE = 1.e8
for i in station_values:
    A[i,i] = LARGE
    b[i]   = LARGE*station_values[i]

# now the stiffness matrix has been computed, we're not going
# to touch it. do the LU decomposition and store it.

cperm = 2 # either 0, 1, 2, or 3
m, n = A.size()
h = dsupralu.new(A, n)
dsupralu.colperm(h[0], cperm)
dsupralu.lu(h[0])

print 'LU decomposition completed'

# modified Neumann boundary conditions. We'll proceed as follows:
# 1) find the boundary edges
# 2) construct the polygons which have an edge in contact with the boundary
# 3) compute the normal gradient of the field estimate in the polygon
#    triangles and average.
# 4) set Neumann BCs

# polygon will hold the connectivity {(n1,n2): [(i1,i2,i3),(k1,k2,k3),..],..}
# (n1,n2): boundary segment
# (i1,i2,i3),... cell node triplets, with [(i1,i2,i3),(k1,k2,k3)..] defining
# the polygon.

edges     = tri.get_edges()
polygon   = {}

def find_complementary_node(i, j, not_this_node=-1):
    """
    given two boundary segment nodes, return the 3rd (interior) node that
    closes the triangle
    """
    k = None
    for el in grid.data[i][1]:
        if el != j and el != not_this_node and el in grid.data[j][1]:
            k = el
            break
    return k

def normal_gradient(e, i,j,k):

    """
    given a segment e=(i1,i2), and 3 nodes spanning a triangular cell,
    return the array which, whn multiplied by the node value array,
    will return the gradient normal to the segment.
    """
    x0, y0 = grid.data[i][0]
    x1, y1 = grid.data[j][0]
    x2, y2 = grid.data[k][0]
    # twice the triangle area
    area2 = (x1-x0)*(y2-y0) - (y1-y0)*(x2-x0)
    # segment length
    xb0, yb0 = grid.data[e[0]][0]
    xb1, yb1 = grid.data[e[1]][0]
    dxb = xb1 - xb0
    dyb = yb1 - yb0
    L   = math.sqrt(dxb**2 + dyb**2)
    denom = L*area2

##    res = [ (dxb*(x2-x1) + dyb*(y2-y1))/denom,
##            (dxb*(x0-x2) + dyb*(y0-y2))/denom,
##            (dxb*(x1-x0) + dyb*(y1-y0))/denom, ]
    res = [ (dxb*(x1-x2) + dyb*(y1-y2))/denom,
            (dxb*(x2-x0) + dyb*(y2-y0))/denom,
            (dxb*(x0-x1) + dyb*(y0-y1))/denom, ]
    
    return res, area2
            
for e_m in edges:
    e, marker = e_m
    if marker:
        # segment is on boundary
        i, j = e
        # 3rd node, k, spanning cell i,j,k
        k = find_complementary_node(i, j)
        polygon[e] = [(i,j,k)]
        jold  = i
        jnext = j
        while jnext != i:
            inext = find_complementary_node(k, jnext, not_this_node=jold)
            if inext == None: break
            polygon[e].append( (k, jnext, inext) )
            jold  = jnext
            jnext = inext

print polygon

# iterate solution
phi = vector.vector([0 for i in range(len(grid.data))])
diff = LARGE
it   = 0
max_iter = 10
while diff > 1.e-6 and it < max_iter:
    # apply modified Neumann BCs to rhs vector
    bnew = vector.vector([b[i] for i in range(len(b))])
    for e in polygon:
        xb0, yb0 = grid.data[e[0]][0]
        xb1, yb1 = grid.data[e[1]][0]
        dxb = xb1 - xb0
        dyb = yb1 - yb0
        Lsq = dxb**2 + dyb**2
        # weigh each cell contribution by its area
        total = 0.0
        total_area = 0.0
        for t in polygon[e]:
        #for t in polygon[e][:1]:
           i, j, k = t
           # values . phi values = normal_gradient for cell
           values, area2 = normal_gradient(e, i,j,k)
           total_area += area2
           total += area2*(values[0]*phi[i]+values[1]*phi[j]+values[2]*phi[k])
        total /= total_area
        bnew[i] += Lsq * total/2.0
        bnew[j] += Lsq * total/2.0
##        bnew[i] += math.sqrt(Lsq)*(dyb-dxb)/2.0
##        bnew[j] += math.sqrt(Lsq)*(dyb-dxb)/2.0
        # exact contribution
        print 'seg=(%d,%d) numeric= %g analytic= %g'%(e[0], e[1],
                                                  Lsq * total/2.0,
                                                  math.sqrt(Lsq)*(dyb-dxb)/2.0)

    phiold = phi
    phi  = dsupralu.solve(h[0], bnew)
    diff = math.sqrt(
        reduce(operator.add,
               [(phi[i]-phiold[i])**2 for i in range(len(phi))])
        )/len(phi)
    print 'it=%d diff=%f' % (it, diff)
    it += 1

# check against analytic solution 2*x + y
error = 0.0
for i in grid.data:
    x, y = grid.data[i][0]
    phi_exact = x + y
    er = phi[i] - phi_exact
##    print 'i=%d x=%f y=%f phi_exact=%f phi=%f error=%g' % \
##          (i, x, y, phi_exact, phi[i], er)
    error += abs(er)
error /= len(phi)
print 'error = ', error
    

# plot
import Tkinter
import tkplot
root = Tkinter.Tk()
canvas = Tkinter.Canvas(bg="white", width=300, height=300)
canvas.pack()
tkplot.tkplot(canvas, grid, phi, draw_mesh=1, node_no=1, add_minmax=1)
root.mainloop()
