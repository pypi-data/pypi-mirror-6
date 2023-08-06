#!/usr/bin/env python

VERSION = "$Id: grInput.py,v 1.3 2009/11/03 13:13:52 pletzer Exp $"

"""
Read in contours coordinates for grin

"""

import re

class Input:

    def __init__(self):
        """
        Constructor
        """
        self.contours = {}
        

    def open(self, filename='grin.dat'):
        """
        Read data file containing contour coordinates

        @param filename
        """
        patHeader = re.compile(r'^\s*(\w\d)\s+(\d+)')
        parData   = re.compile(r'^\s+\-?\d+\.\d+[Ee][\+\-]\d+')
        coordName = ''
        coordSize = 0
        for line in file(filename, 'r').readlines():
           
           m = re.match(patHeader, line)
           if m:
               coordName = m.group(1)
               coordSize = m.group(2)
           elif re.match(parData,line) and coordName and (coordSize > 0):
               self.contours[coordName] = self.contours.get(coordName, []) + \
                           eval('[' + re.sub(r'(\d)\s+([\d\-])','\\1,\\2', line) + ']')

        # checks
        for k in self.contours:
            if k[0] == 'x':
                xName = k
                nx = len(self.contours[xName])
                yName = re.sub(r'x','y', xName)
                ny = len(self.contours[yName])
                if nx != ny:
                    print 'readGrinData ERROR: lengths of %s (%d) and %s (%d) do not match!' % \
                          (xName, nx, yName, ny)
                    print xName, '=', self.contours[xName]
                    print yName, '=', self.contours[yName]
                    raise ValueError

    def getContour1(self):
        """
        @return coordinate points on contour 1
        """
        n = len(self.contours['x1'])
        return [ (self.contours['x1'][i], self.contours['y1'][i]) for i in range(n) ]

    def getContour2(self):
        """
        @return coordinate points on contour 2
        """
        n = len(self.contours['x2'])
        return [ (self.contours['x2'][i], self.contours['y2'][i]) for i in range(n) ]

    def getMaxX(self):
        """
        @return max X
        """
        return max(self.contours['x2'])

    def getMinY(self):
        """
        @return min Y
        """
        return min(self.contours['y2'])

    def getMaxY(self):
        """
        @return max Y
        """
        return max(self.contours['y2'])

    def show(self, width=500, height=600):
        import Tkinter
        root = Tkinter.Tk()
        canvas = Tkinter.Canvas(bg="white", width=width, height=height)
        canvas.pack()
        xmin, xmax = 0.0, self.getMaxX()
        ymin, ymax = self.getMinY(), self.getMaxY()
        scale = max(xmax - xmin, ymax - ymin)
        cont = [ (width*(xy[0]-xmin)/scale, height*(ymax-xy[1])/scale) \
                  for xy in self.getContour1() ]
        canvas.create_line(cont, fill = 'blue', width=2)
        cont = [ (width*(xy[0]-xmin)/scale, height*(ymax-xy[1])/scale) \
                  for xy in self.getContour2() ]
        canvas.create_line(cont, fill = 'red', width=2)
        root.mainloop()

######################################################################

def main():

    gri = Input()
    gri.open(filename = 'grin.dat')
    gri.show()

if __name__ == '__main__':
    main()
