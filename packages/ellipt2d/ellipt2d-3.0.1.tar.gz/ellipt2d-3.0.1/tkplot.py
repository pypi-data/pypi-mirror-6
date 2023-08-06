#! /usr/bin/env python
# $Id: tkplot.py,v 1.14 2013/12/20 20:22:31 pletzer Exp $

"""
Tkinter color plot utility (for real functions)
"""

try:
    from tkinter import Tk, Frame, Button, Canvas, BOTTOM # python 3
except:
    from Tkinter import Tk, Frame, Button, Canvas, BOTTOM # python 2
import cell, colormap
import math

EPS = 4 # small no of pixels

def tkplot(canvas, grid, f=[], draw_mesh=1, node_no=0, 
           add_minmax=1, WIDTH=300, HEIGHT=300, title=None):

    """
    General purpose plotting routine with the following functionality:
    
    1) color code array 'f' on grid (f must be a node array). Each
    triangular cell color coded according to the average of the 'f'
    values at the 3 nodes.
    
    2) display nodes where Dirichlet, Neumann or Robin BCs are applied.
    Dirichlet boundary conditions are represented as discs, Neumann BCs
    as segments and Robin as double segments. The color of each object
    represents the magnitude of the boundary attribute. 'f' must be a
    boundary object of the above type.
    
    Options:
        draw_mesh: draw mesh on top of v data
        node_no: write node numbers
        add_minmax: add min/max values at min/max locations of f
        WIDTH and HEIGHT: window's dimensions
        title: a string
 
    """

    border_x, border_y = 0.2, 0.2
    xmin, ymin, xmax, ymax = grid.boxsize()
    SCALE = min((1.-border_x)*WIDTH/(xmax-xmin), (1.-border_y)*HEIGHT/(ymax-ymin))
    a = max(border_x * WIDTH/2., (WIDTH-SCALE*(xmax-xmin))/2.)
    b = max(border_y * HEIGHT/2.,(HEIGHT-SCALE*(ymax-ymin))/2.)
    
    box_pix = (a, HEIGHT-SCALE*(ymax-ymin) - b, SCALE*(xmax-xmin) + a, HEIGHT - b)
    # draw the box
    addBox(canvas, (xmin,ymin,xmax,ymax), box_pix)

    isDirichlet = 0
    isNeumann = 0
    isRobin = 0
    try:
        isDirichlet = f.isDirichletBound()
    except:
        try:
            isNeumann = f.isNeumannBound()
        except:
            try:
                isRobin = f.isRobinBound()
            except:
                pass
    
    
    # data color plot
    if f != [] and not isDirichlet and not isNeumann and not isRobin:
        cmax = max(f)
        cmin = min(f)
        if cmax==cmin: add_minmax=0
        
        
        cells = cell.cell(grid)
        for index in range(len(cells.data)):
                [ia, ib, ic] = cells.data[index]
                xa, ya = SCALE*(grid.x(ia)-xmin) + a, HEIGHT -SCALE*(grid.y(ia)-ymin) - b
                xb, yb = SCALE*(grid.x(ib)-xmin) + a, HEIGHT -SCALE*(grid.y(ib)-ymin) - b
                xc, yc = SCALE*(grid.x(ic)-xmin) + a, HEIGHT -SCALE*(grid.y(ic)-ymin) - b

                fabc = (f[ia] + f[ib] + f[ic])/3.0
                color = colormap.strRgb(fabc, cmin, cmax)
                canvas.create_polygon(xa, ya, xb, yb, xc, yc, fill=color)
    

    # draw the grid
    if draw_mesh == 1 or f == []:
        for inode in list(grid.data.keys()):
            for inode2 in grid.data[inode][1]:
                x1, y1 = SCALE*(grid.x(inode )-xmin) + a,  HEIGHT-SCALE*(grid.y(inode )-ymin) - b 
                x2, y2 = SCALE*(grid.x(inode2)-xmin) + a,  HEIGHT-SCALE*(grid.y(inode2)-ymin) - b 
                canvas.create_line(x1, y1, x2, y2)
                if node_no == 1 : canvas.create_text(x1+EPS, y1-EPS, text=str(inode))

    # add min/max labels
    if f != [] and add_minmax != 0 and isDirichlet+isNeumann+isRobin==0:
        flag_top, flag_bottom = 1, 1
        for inode in list(grid.data.keys()):
            x, y = SCALE*(grid.x(inode)-xmin) + a, HEIGHT-SCALE*(grid.y(inode)-ymin) - b
            val = f[inode]
            if val == cmax and flag_top:
                addTop(canvas, x, y, val)
                flag_top = 0
            if val == cmin and flag_bottom:
                addBottom(canvas, x, y, val)
                flag_bottom = 0

    # add title
    if title:
        x, y = WIDTH/3., HEIGHT/15.0
        canvas.create_text(x, y, text=str(title), font =("Helvetica", 14),
                           fill='black')
                
    # Dirichlet boundary values
    if isDirichlet:
        cmax = max(f.data.values())
        cmin = min(f.data.values())
        for i in list(f.data.keys()):
            x1, y1 = SCALE*(grid.x(i)-xmin)+a, HEIGHT-SCALE*(grid.y(i)-ymin)-b
            col = colormap.strRgb(f.data[i], cmin, cmax)
            canvas.create_oval(x1-5,y1-5,x1+5,y1+5, fill=col)

    # Neumann boundary values
    if isNeumann:
        cmax = max(f.data.values())
        cmin = min(f.data.values())
        for seg in list(f.data.keys()):
            (ia, ib) = seg
            xa, ya = SCALE*(grid.x(ia)-xmin)+a, HEIGHT-SCALE*(grid.y(ia)-ymin)-b
            xb, yb = SCALE*(grid.x(ib)-xmin)+a, HEIGHT-SCALE*(grid.y(ib)-ymin)-b
            col = colormap.strRgb(f.data[seg], cmin, cmax)
            ds = math.sqrt( (xb-xa)**2 + (yb-ya)**2 )
            delta_x = (yb-ya)/ds
            delta_y = -(xb-xa)/ds
            canvas.create_polygon(xa-3*delta_x, ya-3*delta_y, xb, yb, xa+3*delta_x, ya+3*delta_y, fill=col)
            
    # Robin boundary values
    if isRobin:
        cmax = max(max(f.data.values()))
        cmin = min(max(f.data.values()))
        for seg in list(f.data.keys()):
            (ia, ib) = seg
            xa, ya = SCALE*(grid.x(ia)-xmin)+a, HEIGHT-SCALE*(grid.y(ia)-ymin)-b
            xb, yb = SCALE*(grid.x(ib)-xmin)+a, HEIGHT-SCALE*(grid.y(ib)-ymin)-b
            colA = colormap.strRgb(f.data[seg][0], cmin, cmax)
            colB = colormap.strRgb(f.data[seg][1], cmin, cmax)
            ds = math.sqrt( (xb-xa)**2 + (yb-ya)**2 )
            delta_x = (yb-ya)/ds
            delta_y = -(xb-xa)/ds
            canvas.create_polygon(xa-5*delta_x, ya-5*delta_y, xb, yb, xa, ya, fill=colA)
            canvas.create_polygon(xa, ya, xb, yb, xa+5*delta_x, ya+5*delta_y, fill=colB)

 
def addTop(canvas, xpix, ypix, val):
    """
    Add a top pointing triangle with value at (pixel) coordinates (xpix, ypix)
    """
    canvas.create_polygon(xpix-5,ypix+5,xpix+5,ypix+5,xpix,
                          ypix-5, fill='blue')
    canvas.create_polygon(xpix-16,ypix-1,xpix+24,ypix-1,xpix+24, ypix-12, xpix-16, ypix-12, fill='blue')
    canvas.create_text(xpix+2,ypix-6, text=str('%8.2g' % val), fill='yellow')

def addBottom(canvas, xpix, ypix, val):
    """
    Add a bottom pointing triangle with value at canvas (pixel) coordinates (xpix, ypix)
    """
    canvas.create_polygon(xpix-5,ypix-5,xpix+5,ypix-5,xpix,
                          ypix+5, fill='yellow')
    canvas.create_polygon(xpix-16,ypix-1,xpix+24,ypix-1,xpix+24, ypix-12, xpix-16, ypix-12, fill='yellow')
    canvas.create_text(xpix+2,ypix-6, text=str('%8.2g' % val), fill='blue')

def addBox(canvas, xxx_todo_changeme, xxx_todo_changeme1):
    """
    Add Box. Min/Max coordinates are in pixels.
    """
    (xmin,ymin,xmax,ymax) = xxx_todo_changeme
    (xmin_pix, ymin_pix, xmax_pix, ymax_pix) = xxx_todo_changeme1
    canvas.create_line(xmin_pix, ymax_pix, xmax_pix, ymax_pix)
    canvas.create_text(xmin_pix   ,ymax_pix+ 8, text=('%4.1f' % xmin))
    canvas.create_text(xmin_pix-12,ymax_pix   , text=('%4.1f' % ymin))
    canvas.create_line(xmax_pix, ymax_pix, xmax_pix, ymin_pix)
    canvas.create_text(xmax_pix   ,ymax_pix+ 8, text=('%4.1f' % xmax))
    canvas.create_line(xmax_pix, ymin_pix, xmin_pix, ymin_pix)
    canvas.create_text(xmin_pix-12,ymin_pix   , text=('%4.1f' % ymax))
    canvas.create_line(xmin_pix, ymin_pix, xmin_pix, ymax_pix)
    
###############################################################################
if __name__ == "__main__":

    import math
    import node, reg2tri, vector
    import DirichletBound, NeumannBound, RobinBound

    pos = []
    nx1 = 11
    ny1 = 4

    for iy in range(ny1):
            pos.append([])
            for ix in range(nx1):
                    rho, phi = 1.+iy/float(ny1-1), math.pi*ix/float(nx1-1)
                    x, y = rho*math.cos(phi), rho*math.sin(phi)
                    pos[iy].append((x, y))

    grid = reg2tri.cross(pos)

    
    dB = DirichletBound.DirichletBound()
    for i in range(ny1):
        dB[i] = float(i)

    nb = NeumannBound.NeumannBound()
    nb[(nx1*ny1-2,nx1*ny1-1)] = 3.0

    rb = RobinBound.RobinBound()
    rb[(nx1*ny1-3,nx1*ny1-2)] = [2.0,1.34]

    n = len(grid)
    f = vector.zeros(n)
    for i in range(n):
        x, y = grid.x(i), grid.y(i)
        f[i] = x**2 + y**2


    root = Tk()
    frame = Frame(root)
    frame.pack()
    WIDTH, HEIGHT = 400, 300
    button = Button(frame, text="OK", fg="red", command=frame.quit)
    button.pack(side=BOTTOM)
    canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT)
    canvas.pack()

    tkplot(canvas, grid, dB,0, 0, 0, WIDTH, HEIGHT)
    tkplot(canvas, grid, nb,0, 0, 0, WIDTH, HEIGHT)
    tkplot(canvas, grid, rb,1, 1, 1, WIDTH, HEIGHT)
    
    
    canvas2 = Canvas(bg="white", width=WIDTH, height=HEIGHT)
    canvas2.pack()
    tkplot(canvas2, grid, f, 0, 0,  0,WIDTH, HEIGHT)

    
    root.mainloop()
  
