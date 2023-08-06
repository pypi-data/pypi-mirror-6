#!/usr/bin/env python

import re, string, time
try:
    from tkinter import Tk, Frame, Button, BOTTOM, Label, Canvas # python 3
except:
    from Tkinter import Tk, Frame, Button, BOTTOM, Label, Canvas # python 2

header1=re.compile('^\s*(.*)\s+(\d+)\s+(\d+)\s*$',re.I)

header2=re.compile('^\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)')

class geqdsk:
    """
    Turns the content of a GEQDSK file into a object
    Among the members of the gedsk class are grid dimensions, global
    quantities (current, magnetic field on axis, etc.), radial profiles
    (poloidal current function, pressure, etc.), the poloidal flux on the
    (R,Z) uniform grid, as well as the geometry of the boundary wall and
    limiter.

    For additional information about the content of the geqdsk file refer
    to the "G EQDSK FORMAT" document by Lang Lao.

   A. Pletzer July 17 2000
    """
    def __init__(self, file):
        f = open(file, 'r')
        thisLine=f.readline()
        pat=header1.match(thisLine)
        try:
            self.header=pat.group(1)
            self.nw=string.atoi(pat.group(2)) # r grid size
            self.nh=string.atoi(pat.group(3))

            print(self.header)
            print(self.nw)
            print(self.nh)
        except:
            print('error while reading line \n',thisLine)

        thisLine = f.readline()
        thisLine = re.sub('([^Ee])-', '\\1 -', thisLine) # separate fields
        pat=header2.match(thisLine)
        try:
            self.rdim=string.atof(pat.group(1))
            self.zdim=string.atof(pat.group(2))
            self.rcentr=string.atof(pat.group(3))
            self.rleft=string.atof(pat.group(4))
            self.zmid=string.atof(pat.group(5))
        except:
            print('error while reading line \n',thisLine)
        
        thisLine = f.readline()
        thisLine = re.sub('([^Ee])-', '\\1 -', thisLine) # separate fields
        pat=header2.match(thisLine)
        try:
            self.rmaxis=string.atof(pat.group(1)) # magnetic axis position
            self.zmaxis=string.atof(pat.group(2)) 
            self.psimag=string.atof(pat.group(3)) # poloidal flux on mag. axis
            self.psibdy=string.atof(pat.group(4)) # poloidal flux on last closed surface
            self.bcentr=string.atof(pat.group(5)) # B at the geometry centre
        except:
            print('error while reading line \n',thisLine)
            
        thisLine = f.readline()
        thisLine = re.sub('([^Ee])-', '\\1 -', thisLine) # separate fields
        pat=header2.match(thisLine)
        try:
            self.currentA=string.atof(pat.group(1)) # total current in Amps
        except:
            print('error while reading line \n',thisLine)

        thisLine = f.readline()

        # read remaining lines

        lines = f.read()
        lines = re.sub('\n', ' ', lines) # merge
        lines = re.sub('(\d)\-', '\\1 -', lines) # add space between numbers
        fields =  re.split('\s+', lines)
        numbers = []
        for n in fields:
            try:
                numbers.append(string.atof(n))
            except:
                pass

        nw, nh = self.nw, self.nh
        
        self.fpol   =numbers[0   :  nw]
        self.pres   =numbers[  nw:2*nw]
        self.ffprime=numbers[2*nw:3*nw]
        self.pprime =numbers[3*nw:4*nw]
        ia = 4*nw
        self.psirz = []
        for ih in range(nh):
            self.psirz.append(numbers[ia:ia+nh])
            ia = ia + nw
        self.qpsi   =numbers[ia:ia+nw]
        ia = ia + nw
        self.nbbbs  =int(numbers[ia])
        ia = ia + 1
        self.limitr =int(numbers[ia])
        ia = ia + 1
        self.rbbbs=[]
        self.zbbbs=[]
        for i in range(self.nbbbs):
            self.rbbbs.append(numbers[ia  ])
            self.zbbbs.append(numbers[ia+1])
            ia = ia + 2
        self.rlim=[]
        self.zlim=[]
        for i in range(self.limitr):
            self.rlim.append(numbers[ia  ])
            self.zlim.append(numbers[ia+1])
            ia = ia + 2

    def getPlasmaGeometry(self):
        """ return plasma boundary coordinates as [[r1,z1], [r2,z2],...] list """
        res=[]
        for i in range(self.nbbbs):
            res.append((self.rbbbs[i], self.zbbbs[i]))
        return res

    def getLimiterGeometry(self):
        """ return limiter geometry """
        res=[]
        for i in range(self.limitr):
            res.append((self.rlim[i], self.zlim[i]))
        return res
        
    def plot(self, what="all"):
        # default sizes
        WIDTH=400
        HEIGHT=400
        OFFSET = 0.05*min([WIDTH, HEIGHT])
        EPS = 4
        (xmin, ymin, xmax, ymax) = (self.rcentr-self.rdim/2., self.zmid-self.zdim/2.,
                                    self.rcentr+self.rdim/2., self.zmid+self.zdim/2.)
        SCALE = min([0.9*WIDTH, 0.9*HEIGHT])/max([xmax-xmin, ymax-ymin])
        root = Tk()
        frame = Frame(root)
        frame.pack()
        button = Button(frame, text="OK?", fg="red", command=frame.quit)
        button.pack(side=BOTTOM)
        canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT)
        canvas.pack()
        title=what
        if what== "all": title="plasma and limiter geometry"
        
        text = Label(width=30, height=10, text=title)
        text.pack()

        if what=='plasma' or what=="all":
            for i in range(self.nbbbs-1):
                x1, y1 = self.rbbbs[i  ], self.zbbbs[i  ]
                x2, y2 = self.rbbbs[i+1], self.zbbbs[i+1]
                X1, Y1 = OFFSET+SCALE* (x1-xmin), HEIGHT-OFFSET-SCALE* (y1-ymin)
                X2, Y2 = OFFSET+SCALE* (x2-xmin), HEIGHT-OFFSET-SCALE* (y2-ymin)
                canvas.create_line(X1, Y1, X2, Y2, fill='red', width=2)
        if what=='limiter' or what=="all":
            for i in range(self.limitr-1):
                x1, y1 = self.rlim[i  ], self.zlim[i  ]
                x2, y2 = self.rlim[i+1], self.zlim[i+1]
                X1, Y1 = OFFSET+SCALE* (x1-xmin), HEIGHT-OFFSET-SCALE* (y1-ymin)
                X2, Y2 = OFFSET+SCALE* (x2-xmin), HEIGHT-OFFSET-SCALE* (y2-ymin)
                canvas.create_line(X1, Y1, X2, Y2, fill='blue', width=2)
            
        root.mainloop()


##############################################################################

if __name__ == '__main__':
    import sys
    try:
        file = sys.argv[1]
    except:
        print(" ERROR: must supply EFIT file name")
        print(sys.argv[0]," <filename>")
        sys.exit(1)
    g1 = geqdsk(file)
    print(g1.__doc__)
    print('g-function')
    print(g1.fpol)
    print('pressure')
    print(g1.pres)
    print("gg'")
    print(g1.ffprime)
    print("p'")
    print(g1.pprime)
    print("q")
    print(g1.qpsi)
    print("wall boundary (r,z) doublets")
    print(g1.getPlasmaGeometry())
    print("limiter geometry  (r,z) doublets")
    print(g1.getLimiterGeometry())
    g1.plot()

    print('       psi             pres            fpol            qpsi')
    for i in range(len(g1.qpsi)):
        psi = g1.psimag + float(i)*(g1.psibdy-g1.psimag)/float(g1.nw-1)
        print('%15.6f %15.6f %15.6f %15.6f' % (psi, g1.pres[i], g1.fpol[i], g1.qpsi[i]))
