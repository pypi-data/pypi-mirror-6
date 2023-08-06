#!/usr/bin/env python

# $Id: test_triangulate.py,v 1.6 2005/11/09 15:18:59 pletzer Exp $

import triangulate
import node
import sys

n = 1
if len(sys.argv)>1: n = float(sys.argv[1])

for i in range(n):
    # run repeatly to check reference count
    
    h = triangulate.new()
    print triangulate.set_points.__doc__

    import math
    nto = 8
    nti = 4
    dto = 2*math.pi/float(nto)
    dti = 2*math.pi/float(nti)
    
    ptso = [(math.cos(i*dto), math.sin(i*dto)) for i in range(nto)]
    atto = [(1+1*i,1+2*i, 1+3*i) for i in range(nto)]
    mrko = [1 for i in range(nto)]
    
    ptsi = [(0.5+0.1*math.cos(i*dti), 0.1*math.sin(i*dti)) for i in range(nti)]
    atti = [(0,0,0) for i in range(nti)]
    mrki = [0 for i in range(nti)]

    pts = ptso + ptsi
    
    sgo = [(i,i+1) for i in range(nto-1)] + [(nto-1,0)]
    sgi = [(i,i+1) for i in range(nto, nto+nti-1)] + [(nto+nti-1,nto)]

    seg = sgo + sgi
    att = atto + atti
    mrk = mrko + mrki

    triangulate.set_points(h, pts, mrk)

    triangulate.set_attributes(h, att)

    print 'pts=',pts
    print 'att=',att
    print 'mrk=',mrk
    

    triangulate.set_segments(h, seg)

    print 'seg=',seg

    triangulate.set_holes(h, [(0.5,0.0),])

    hout = triangulate.new()
    hvor = triangulate.new()

    # mode
    # z starting with zero
    # e edges
    # q<angle> quality mesh
    triangulate.triangulate('pzeq30Q', h, hout, hvor)

    hout2 = triangulate.new()
    max_area = 0.2
    triangulate.triangulate('rcezsq27a%fVn'%max_area, hout, hout2, hvor)

    nds = triangulate.get_nodes(hout2)

    atts = triangulate.get_attributes(hout2)

    edges = triangulate.get_edges(hout2)

    tris  = triangulate.get_triangles(hout2)

print triangulate.get_nodes.__doc__
print triangulate.get_attributes.__doc__
print triangulate.get_edges.__doc__
print triangulate.get_triangles.__doc__

grid = node.node()
grid.setData(nds)

import Tkinter
import tkplot

root = Tkinter.Tk() 
frame = Tkinter.Frame(root) 
frame.pack() 
WIDTH, HEIGHT = 300, 250 
canvas = Tkinter.Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack()
tkplot.tkplot(canvas, grid, f=[], draw_mesh=1, node_no=1, add_minmax=0,
       WIDTH=WIDTH, HEIGHT=HEIGHT) 
root.mainloop() 

#print atts


