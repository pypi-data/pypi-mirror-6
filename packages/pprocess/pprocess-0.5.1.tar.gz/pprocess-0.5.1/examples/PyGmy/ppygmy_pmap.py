#!/usr/bin/env python

"""
An adaptation of pygmy.py ("a rubbish raytracer") employing pprocess
functionality in order to take advantage of multiprocessing environments.

--------

Copyright (C) 2005 Dave Griffiths
Copyright (C) 2006, 2007 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""

import Image, ImageDraw, random, copy
from math import *
import pprocess
import sys

def sq(a):
    return a*a
    
class vec:
    def __init__(self, x, y, z):
        self.x=float(x)
        self.y=float(y)
        self.z=float(z)

    def __add__(self,other):
        return vec(self.x+other.x,self.y+other.y,self.z+other.z)

    def __sub__(self,other):
        return vec(self.x-other.x,self.y-other.y,self.z-other.z)

    def __mul__(self,amount):
        return vec(self.x*amount,self.y*amount,self.z*amount)

    def __div__(self,amount):
        return vec(self.x/amount,self.y/amount,self.z/amount)

    def __neg__(self):
        return vec(-self.x,-self.y,-self.z)

    def dot(self,other):
        return (self.x*other.x)+(self.y*other.y)+(self.z*other.z)
        
    def cross(self,other):
        return vec(self.y*other.z - self.z*other.y,
                    self.z*other.x - self.x*other.z,
                    self.x*other.y - self.y*other.x)

    def dist(self,other):
        return sqrt((other.x-self.x)*(other.x-self.x)+
                    (other.y-self.y)*(other.y-self.y)+
                    (other.z-self.z)*(other.z-self.z))

    def sq(self):
        return sq(self.x)+sq(self.y)+sq(self.z)

    def mag(self):
        return self.dist(vec(0,0,0))

    def norm(self):
        mag=self.mag()
        if mag!=0:
            self.x=self.x/mag
            self.y=self.y/mag
            self.z=self.z/mag
            
    def reflect(self,normal):
        vdn=self.dot(normal)*2
        return self-normal*vdn

class line: 
    def __init__(self, start, end):
        self.start=start
        self.end=end
            
    def vec(self):
        return self.end-self.start
    
    def closestpoint(self, point):
        l=self.end-self.start
        l2=point-self.start        
        t=l.dot(l2)
        if t<=0: return self.start
        if t>l.mag(): return self.end
        return self.start+l*t
    
class renderobject:
    def __init__(self, shader):
        self.shader=shader        
    
    def intersect(self,l):
        return "none",vec(0,0,0),vec(0,0,0) # type, position, normal

class plane(renderobject):
    def __init__(self,plane,dist,shader):
        renderobject.__init__(self,shader)
        self.plane=plane
        self.dist=dist
        
    def intersect(self,l):        
        vd=self.plane.dot(l.vec()) 
        if vd==0: return "none",vec(0,0,0),vec(0,0,0)
        v0 = -(self.plane.dot(l.start)+self.dist)
        t = v0/vd
        if t<0 or t>1: return "none",vec(0,0,0),vec(0,0,0)
        return "one",l.start+(l.vec()*t),self.plane
        
    
class sphere(renderobject):
    def __init__(self, pos, radius, shader):
        renderobject.__init__(self,shader)
        self.pos=pos
        self.radius=radius

    def disttoline(self,l):
        return self.pos.dist(l.closestpoint(self.pos))
    
    def intersect(self,l):
        lvec=l.vec()
        a = sq(lvec.x)+sq(lvec.y)+sq(lvec.z)
          
        b = 2*(lvec.x*(l.start.x-self.pos.x)+ \
               lvec.y*(l.start.y-self.pos.y)+ \
               lvec.z*(l.start.z-self.pos.z))
               
        c = self.pos.sq()+l.start.sq() - \
             2*(self.pos.x*l.start.x+self.pos.y*l.start.y+self.pos.z*l.start.z)-sq(self.radius)
    
        i = b*b-4*a*c 

        intersectiontype="none"
        pos=vec(0,0,0)
        norm=vec(0,0,0)
        t=0
        
        if i>0 :    
            if i==0:
                intersectiontype="one"
                t = -b/(2*a);
            else:  
                intersectiontype="two"
                t = (-b - sqrt( b*b - 4*a*c )) / (2*a)
                # just bother with one for the moment
                # t2= (-b + sqrt( b*b - 4*a*c )) / (2*a) 

            if t>0 and t<1: 
                pos = l.start+lvec*t
                norm=pos-self.pos 
                norm.norm()
            else: 
                intersectiontype="none"
                
        return intersectiontype,pos,norm
        
    def intersects(self,l):
        return self.disttoline(l)<self.radius

class light:
    def __init__(self):
        pass
        
    def checkshadow(self, obj, objects,l):
        # shadowing built into the lights (is this right?)
        for ob in objects:
            if ob is not obj:
                intersects,pos,norm = ob.intersect(l)
                if intersects is not "none":
                    return 1
        return 0
        
    def light(self, obj, objects, pos, normal):
        pass

class parallellight(light):
    def __init__(self, direction, col):
        direction.norm()
        self.direction=direction
        self.col=col

    def inshadow(self, obj, objects, pos):        
        # create a longish line towards the light
        l = line(pos,pos+self.direction*1000) 
        return self.checkshadow(obj,objects,l)

    def light(self, shaderinfo):
        if self.inshadow(shaderinfo["thisobj"],shaderinfo["objects"],shaderinfo["position"]): return vec(0,0,0)
        return self.col*self.direction.dot(shaderinfo["normal"])

class pointlight(light):
    def __init__(self, position, col):
        self.position=position
        self.col=col
    
    def inshadow(self, obj, objects, pos):
        l = line(pos,self.position)
        return self.checkshadow(obj,objects,l)
            
    def light(self, shaderinfo):
        if self.inshadow(shaderinfo["thisobj"],shaderinfo["objects"],shaderinfo["position"]): return vec(0,0,0)
        direction = shaderinfo["position"]-self.position;
        direction.norm()
        direction=-direction
        return self.col*direction.dot(shaderinfo["normal"])

class shader:
    def __init__(self):
        pass

    # a load of helper functions for shaders, need much improvement

    def getreflected(self,shaderinfo):
        depth=shaderinfo["depth"]
        col=vec(0,0,0)
        if depth>0:
            lray=copy.copy(shaderinfo["ray"])
            ray=lray.vec()
            normal=copy.copy(shaderinfo["normal"])
            ray=ray.reflect(normal)
            reflected=line(shaderinfo["position"],shaderinfo["position"]+ray)
            obj=shaderinfo["thisobj"]
            objects=shaderinfo["objects"]
            newshaderinfo = copy.copy(shaderinfo)
            newshaderinfo["ray"]=reflected
            newshaderinfo["depth"]=depth-1
            # todo - depth test
            for ob in objects:
                if ob is not obj:
                    intersects,position,normal = ob.intersect(reflected)
                    if intersects is not "none":
                        newshaderinfo["thisobj"]=ob
                        newshaderinfo["position"]=position
                        newshaderinfo["normal"]=normal
                        col=col+ob.shader.shade(newshaderinfo)
        return col

    def isoccluded(self,ray,shaderinfo):
        dist=ray.mag()
        test=line(shaderinfo["position"],shaderinfo["position"]+ray)
        obj=shaderinfo["thisobj"]
        objects=shaderinfo["objects"]
        # todo - depth test
        for ob in objects:
            if ob is not obj:
                intersects,position,normal = ob.intersect(test)
                if intersects is not "none":
                    return 1
        return 0

    def doocclusion(self,samples,shaderinfo):
        # not really very scientific, or good in any way...
        oc=0.0
        for i in range(0,samples):
            ray=vec(random.randrange(-100,100),random.randrange(-100,100),random.randrange(-100,100))
            ray.norm()
            ray=ray*2.5
            if self.isoccluded(ray,shaderinfo):
                oc=oc+1
        oc=oc/float(samples)
        return 1-oc

    def getcolour(self,ray,shaderinfo):
        depth=shaderinfo["depth"]
        col=vec(0,0,0)
        if depth>0:
            test=line(shaderinfo["position"],shaderinfo["position"]+ray)
            obj=shaderinfo["thisobj"]
            objects=shaderinfo["objects"]
            newshaderinfo = copy.copy(shaderinfo)
            newshaderinfo["ray"]=test
            newshaderinfo["depth"]=depth-1
            # todo - depth test
            for ob in objects:
                if ob is not obj:
                    intersects,position,normal = ob.intersect(test)
                    if intersects is not "none":
                        newshaderinfo["thisobj"]=ob
                        newshaderinfo["position"]=position
                        newshaderinfo["normal"]=normal
                        col=col+ob.shader.shade(newshaderinfo)
        return col

    def docolourbleed(self,samples,shaderinfo):
        # not really very scientific, or good in any way...
        col=vec(0,0,0)
        for i in range(0,samples):
            ray=vec(random.randrange(-100,100),random.randrange(-100,100),random.randrange(-100,100))
            ray.norm()
            ray=ray*5
            col=col+self.getcolour(ray,shaderinfo)
        col=col/float(samples)
        return col

    def shade(self,shaderinfo):
        col=vec(0,0,0)
        for lite in shaderinfo["lights"]:
            col=col+lite.light(shaderinfo)
        return col

class world:
    def __init__(self,width,height):
        self.lights=[]
        self.objects=[]
        self.cameratype="persp"
        self.width=width
        self.height=height
        self.backplane=2000.0
        self.imageplane=5.0
        self.aspect=self.width/float(self.height)

    def render_row(self, sy):

        """
        Render the given row, using the 'channel' provided to communicate
        result data back to the coordinating process, and using 'sy' as the row
        position. A tuple containing 'sy' and a list of result numbers is
        returned by this function via the given 'channel'.
        """

        row = []
        for sx in range(0,self.width):
            x=2*(0.5-sx/float(self.width))*self.aspect
            y=2*(0.5-sy/float(self.height))
            if self.cameratype=="ortho":
                ray = line(vec(x,y,0),vec(x,y,self.backplane))
            else:
                ray = line(vec(0,0,0),vec(x,y,self.imageplane))
                ray.end=ray.end*self.backplane

            col=vec(0,0,0)
            depth=self.backplane
            shaderinfo={"ray":ray,"lights":self.lights,"objects":self.objects,"depth":2}

            for obj in self.objects:                            
                intersects,position,normal = obj.intersect(ray)
                if intersects is not "none":
                    if position.z<depth and position.z>0:
                        depth=position.z
                        shaderinfo["thisobj"]=obj
                        shaderinfo["position"]=position
                        shaderinfo["normal"]=normal
                        col=obj.shader.shade(shaderinfo)
            row.append(col)

        return row

    def render(self, filename, limit):

        """
        Render the image with many processes, saving it to 'filename', using the
        given process 'limit' to constrain the number of processes used.
        """

        image = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(image)
        total = self.width * self.height
        count = 0

        for sy, row in enumerate(pprocess.pmap(self.render_row, xrange(0, self.height), limit)):
            for sx, col in enumerate(row):
                draw.point((sx,sy),fill=(col.x*255,col.y*255,col.z*255))
                count = count + 1
            percent = int((count/float(total))*100)
            sys.stdout.write(("\010" * 9) + "%3d%% %3d" % (percent, sy))
            sys.stdout.flush()

        image.save(filename)

# vim: tabstop=4 expandtab shiftwidth=4
