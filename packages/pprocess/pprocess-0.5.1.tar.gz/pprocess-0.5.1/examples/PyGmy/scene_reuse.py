#!/usr/bin/env python

"""
An example scene from...

http://www.pawfal.org/index.php?page=PyGmy
"""

import math
from ppygmy_reuse import *
import sys

class everythingshader(shader):
    def __init__(self):
        pass
  
    def shade(self,shaderinfo):
        col = shader.shade(self,shaderinfo)
        ref = self.getreflected(shaderinfo)
        col = col*0.5+ref*0.5
        return col*self.doocclusion(10,shaderinfo)

class spotshader(shader):
    def __init__(self):
        pass
  
    def shade(self,shaderinfo):
        col = shader.shade(self,shaderinfo)
        position=shaderinfo["position"]
        jitter=(math.sin(position.x)+math.cos(position.z))
        if jitter>0.5: col=col/2
        ref = self.getreflected(shaderinfo)
        return ref*0.5+col*0.5*self.doocclusion(10,shaderinfo)

if __name__ == "__main__":
    w = world(300,200)
    numballs=10.0
    offset = vec(0,-5,55)
    rad=12.0
    radperball=(2*3.141)/numballs

    for i in range(0,int(numballs)):
        x=sin(0.3+radperball*float(i))*rad
        y=cos(0.3+radperball*float(i))*rad
        w.objects.append(sphere(vec(x,0,y)+offset,2,everythingshader()))
        
    w.objects.append(sphere(vec(3,3,0)+offset,5,everythingshader()))
    w.objects.append(plane(vec(0,1,0),7,spotshader()))
    w.lights.append(parallellight(vec(1,1,-1),vec(0.3,0.9,0.1)))
    w.lights.append(pointlight(vec(5,100,-5),vec(0.5,0.5,1)))

    if len(sys.argv) > 1:
        if "--help" in sys.argv:
            print "Specify a limit to the number of processes."
            print "For example:"
            print "python", sys.argv[0], "4"
            sys.exit(1)
        else:
            limit = int(sys.argv[1])
    else:
        limit = 1

    print "Number of processes:", limit
    w.render("test.tif", limit)

# vim: tabstop=4 expandtab shiftwidth=4
