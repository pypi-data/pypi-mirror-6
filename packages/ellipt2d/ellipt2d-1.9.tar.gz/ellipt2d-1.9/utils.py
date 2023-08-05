#!/usr/bin/env python
# $Id: utils.py,v 1.1 2005/09/12 13:51:23 pletzer Exp $

import math
import time
import cell

"""
Some plotting methods supplied by Gareth Elston
"""

def plot_mesh(gp_obj, mesh, label_nodes=False, hardcopy=False):
    """Plots the mesh nodes with optional node numbering
    
    gp_obj        - a Gnuplot.Gnuplot object
    mesh          - node.node object (from the ellipt2d package)
    label_nodes   - either True (label all nodes with node numbers)
                    or a list (or tuple) of mesh nodes to label
    hardcopy=True - produces a 'mesh.eps' file in the current directory.
    """
    import Gnuplot
    
    los = []
    for inode in mesh.data.keys():
        for jnode in mesh.data[inode][1]:
            x1, y1 = mesh.x(inode), mesh.y(inode)
            x2, y2 = mesh.x(jnode), mesh.y(jnode)
            los.append('%f\t%f\n%f\t%f\n\n' % (x1,y1,x2,y2) )
    file('mesh.dat','wb').writelines(los)

    gp_obj('unset label')
    if label_nodes:
        if not isinstance(label_nodes, (list, tuple)):
            label_nodes = mesh.nodes()
        for i in label_nodes:
            mn = mesh[i]
            gp_obj( 'set label %d "%d" at %.6f, %.6f center'
                    % (i+1, i, mn[0][0], mn[0][1]) )
            time.sleep(0.001)

#   gp_obj('set grid; set size ratio -1; set xtics 0.1; set ytics 0.1')
    gp_obj.plot(Gnuplot.File('mesh.dat', with='lines'))
    if hardcopy:
        gp_obj.hardcopy('mesh.eps', eps=1, color=1, solid=1)


def Tk_view_soln (ellipt2d_obj, soln_vec, log=0, w=800, h=800):
    """Uses Tk to plot the results on the mesh"""
    from Tkinter import Tk, Frame, Button, Canvas, BOTTOM
    import tkplot
    
    if log:
        soln_vec = [math.log10(a) for a in soln_vec]
    root = Tk() 
    frame = Frame(root) 
    frame.pack() 
    button = Button(frame, text="OK", fg="red", command=frame.quit) 
    button.pack(side=BOTTOM) 
    canvas = Canvas(bg="white", width=w, height=h) 
    canvas.pack()
    tkplot.tkplot(canvas, ellipt2d_obj.grid, soln_vec, 1,0,0, w, h) 
    root.mainloop() 

# Define RGB color sequences:
rl = [0]*125 + range(0,250,5) + [250]*76 + [0]*5
gl = [0]*25 + range(0,250,5) + [250]*100 + [int(i*10./3+0.5) for i in range(75,0,-1)] +[0]*6
bl = range(0,250,10) + [250]*50 + range(250,0,-5) + [0]*125 + [0]*6
# Set water (pixel val 0) to cornflower blue (from /usr/X11R6/lib/X11/rgb.txt)
rl[0] = 100
gl[0] = 149
bl[0] = 237
# Set land (pixel index 254)
rl[254] = gl[254] = bl[254] = 128
# Define color palette:
pal = []
tmp = [pal.extend([rl[i], gl[i], bl[i]]) for i in range(256)]
del rl,gl,bl,tmp

def image (mesh, soln_vec, w=512, h=512, color=True, valrange=None):
    """Return a PIL Image instance of the solution on the mesh
    interpolated on a uniform grid"""

    import Image
    import ImageOps as ImOps

    grid = cell.cell(mesh)
    xmin, ymin, xmax, ymax = grid.boxsize()
    grid_data = grid.interpUniform(soln_vec, w, xmin, xmax, h, ymin, ymax)

    if valrange is None:
        minval = min(soln_vec)
        maxval = max(soln_vec)
    else:
        minval = min(valrange)
        maxval = max(valrange)

    im = Image.new('L', (w, h), 254)
    if (maxval-minval) > 0.0:
        for i in range(w):
            for j in range(h):
                if grid_data[j][i] is not None:
                    im.putpixel( (i,j), 250.0 * ( (grid_data[j][i] - minval) / 
                                                             (maxval-minval) ) )
    else:
        for i in range(w):
            for j in range(h):
                if grid_data[j][i] is not None:
                    im.putpixel( (i,j), 0 )

    im = ImOps.flip(im)
    if color:
        im.putpalette(pal)
    return im

def toVTK (filename, cells, grid, names, fields):
    """Save solution(s) on the FEM mesh to a VTK data file.
    """
    
    # From Alex Pletzer's 8 Aug 2005 email
    f = open(filename, 'w')
    date = time.ctime( time.time() )
    nnodes = len(grid.nodes())
    nfields= len(fields)
    ncells = len(cells.data)
    print >>f,'# vtk DataFile Version 2.0'
    print >>f,'produced by Ellipt2d on %s' % date
    print >>f,'ASCII'
    print >>f,'DATASET UNSTRUCTURED_GRID'
    print >>f,'POINTS %d DOUBLES' % nnodes
    for node in range(nnodes):
        coordinates = (grid.x(node), grid.y(node), 0.0)
        print >>f,'%f %f %f' % coordinates
    print >>f,'CELLS %d %d ' % (ncells, ncells*4)
    for icell in range(ncells):
        #print cells.data[icell]
        print >>f,'3 %d %d %d' % tuple(cells.data[icell])
    print >>f,'CELL_TYPES %d' % ncells
    for icell in range(ncells):
        print >>f,5
    print >>f,'POINT_DATA %d' % nnodes
    for i in range(len(fields)):
        print >>f,'SCALARS %s float' % names[i]
        print >>f,'LOOKUP_TABLE default'
        for node in range(nnodes):
            print >>f, '%20.8e' % fields[i][node]
    f.close()

###############################################################################
# test unit
def main():
    from ellipt2d import ellipt2d
    from Ireg2tri import Ireg2tri
    import vector
    from math import pi, sin, cos
    import superlu

    # input parameters
    nt = 128
    d  = 0.1

    dt = 2*pi/float(nt)
    ts  = [i*dt for i in range(nt)]
    points = [ (cos(t - (pi/2.)*sin(t/2)**1000) , sin(t),) for t in ts ] + [ (d, 0.) ]
    seglist = [ (i,i+1) for i in range(nt-1) ] + [(nt-1, 0)]
    regionlist = []
    holelist = []

    # Generate the mesh:
    initialAreaBound = 0.02
    meshgen = Ireg2tri(initialAreaBound)
    meshgen.mode = 'zeq32'
    meshgen.setUpConvexHull(points, seglist, regionlist, holelist)

    # Delauney triangulation:
    mesh = meshgen.triangulate()
    mesh = meshgen.refine(2)

    # Initialize the FEM solution:
    equ = ellipt2d(mesh, f_funct='1.0', g_funct='0.0', s_funct='0.0')
    [A, b] = equ.stiffnessMat()

    # Dirichlet Boundary condition (=1) at node nt:
    LARGE = 1e8
    #A[nt/2,nt/2] = LARGE # zero Dirichlet
    A[0,0] = LARGE
    A[nt,nt] = LARGE # 1 Dirichlet
    b[nt]    = LARGE

    # Solve system
    u = superlu.solve(A, b)

    # test outputs
    toVTK('test.vtk', equ.cells, equ.grid, names=['solution,'], fields=[u,])

    Tk_view_soln(equ, u)

    try:
        img = image(mesh, u)
        print img.format, img.size, img.mode
        img.show()
        img.save('test.png')
    except:
        print 'Python image library not installed...'

    try:
        import Gnuplot
        gp = Gnuplot.Gnuplot()
        plot_mesh(gp, mesh, label_nodes=False, hardcopy=True)
    except:
        print 'Gnuplot not installed...'
    
if __name__=='__main__': main()
