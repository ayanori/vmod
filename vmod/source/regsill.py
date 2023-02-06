import numpy as np
from .. import util
from . import Source
from . import Okada

class Regsill(Source):
    def __init__(self, data, typ=None, ln=None, wn=None):
        if typ==None:
            typ='open'
        else:
            typ='slip'
        if ln==None:
            self.ln=1
        else:
            self.ln=ln
        if wn==None:
            self.wn=1
        else:
            self.wn=wn
        
        super().__init__(data)
        
    def time_dependent(self):
        return False
    
    def set_parnames(self):
        self.parameters=("xcen","ycen","depth","length","width","strike","dip","slips/openings")
        
    def rotate_xyz(self,xcen,ycen,depth,length,width,strike,dip):
        cx=xcen
        cy=ycen
        cz=-depth
        wp=width*np.cos(np.radians(dip))
        wr=width*np.sin(np.radians(dip))
        l=length
        phi=strike
        x1 = cx + wp/2 * np.cos(np.radians(phi)) - l/2 * np.sin(np.radians(phi))
        y1 = cy + wp/2 * np.sin(np.radians(phi)) + l/2 * np.cos(np.radians(phi))
        z1 = cz - wr/2
        x2 = cx - wp/2 * np.cos(np.radians(phi)) - l/2 * np.sin(np.radians(phi))
        y2 = cy - wp/2 * np.sin(np.radians(phi)) + l/2 * np.cos(np.radians(phi))
        z2 = cz + wr/2
        x3 = cx - wp/2 * np.cos(np.radians(phi)) + l/2 * np.sin(np.radians(phi))
        y3 = cy - wp/2 * np.sin(np.radians(phi)) - l/2 * np.cos(np.radians(phi))
        z3 = cz + wr/2
        x4 = cx + wp/2 * np.cos(np.radians(phi)) + l/2 * np.sin(np.radians(phi))
        y4 = cy + wp/2 * np.sin(np.radians(phi)) - l/2 * np.cos(np.radians(phi))
        z4 = cz - wr/2
        
        return [x1,x2,x3,x4],[y1,y2,y3,y4],[z1,z2,z3,z4]
        
    def get_centers(self,xcen,ycen,depth,length,width,strike,dip,ln,wn):
        xc=xcen
        yc=ycen
        zc=-depth
        ln=self.ln
        wn=self.wn
        lslice=length/ln
        wslice=width/wn
        fwc=xcen-width/2+width/(2*wn)
        flc=ycen-length/2+length/(2*ln)
        #print(fwc,flc)
        xcs,ycs,zcs=[],[],[]
        if wn%2==0:
            wi=wn/2
        else:
            wi=(wn-1)/2
            
        if ln%2==0:
            li=ln/2
        else:
            li=(ln-1)/2
            
        for i in range(int(wi)):
            wfake=2*np.abs(fwc-xcen+float(i)*wslice)
            for j in range(int(li)):
                lfake=2*np.abs(flc-ycen+float(j)*lslice)
                xs,ys,zs=self.rotate_xyz(xcen,ycen,depth,lfake,wfake,strike,dip)
                for x in xs:
                    xcs.append(x)
                for y in ys:
                    ycs.append(y)
                for z in zs:
                    zcs.append(z)
        print('Puntos 1',len(xcs),wn%2,ln%2)
        if not ln%2==0:
            for j in range(int(li)):
                wfake=0
                lfake=2*np.abs(flc-ycen+float(j)*lslice)
                xs,ys,zs=self.rotate_xyz(xcen,ycen,depth,lfake,wfake,strike,dip)
                for x in xs[1:3]:
                    xcs.append(x)
                for y in ys[1:3]:
                    ycs.append(y)
                for z in zs[1:3]:
                    zcs.append(z)
        print('Puntos 2',len(xcs))
        if not wn%2==0:
            for i in range(int(wi)):
                wfake=2*np.abs(fwc-xcen+float(i)*wslice)
                lfake=0
                xs,ys,zs=self.rotate_xyz(xcen,ycen,depth,lfake,wfake,strike,dip)
                for x in xs[0:2]:
                    xcs.append(x)
                for y in ys[0:2]:
                    ycs.append(y)
                for z in zs[0:2]:
                    zcs.append(z)
        print('Puntos 3',len(xcs))
        if (not wn%2==0) and (not ln%2==0):
            print('Ninguno')
            xcs.append(xcen)
            ycs.append(ycen)
            zcs.append(-depth)
        print('Puntos 4',len(xcs))
        return xcs,ycs,zcs
    
    def get_laplacian(self,xcen,ycen,depth,length,width,strike,dip,ln,wn):
        xcs,ycs,zcs=self.get_centers(xcen,ycen,depth,length,width,strike,dip,ln,wn)
        L=np.zeros((ln*wn,ln*wn))
        for i in range(len(xcs)):
            dist=(np.array(xcs)-xcs[i])**2+(np.array(ycs)-ycs[i])**2+(np.array(zcs)-zcs[i])**2
            pos=np.argsort(dist)
            #print(dist[pos[0:5]])
            if dist[pos[1]]==dist[pos[2]] and dist[pos[1]]==dist[pos[3]] and dist[pos[1]]==dist[pos[4]]:
                L[i,pos[0]]=-2
                L[i,pos[1]]=1
                L[i,pos[2]]=1
                L[i,pos[3]]=1
                L[i,pos[4]]=1
            elif dist[pos[1]]==dist[pos[2]] and dist[pos[1]]==dist[pos[3]]:
                L[i,pos[0]]=-2
                L[i,pos[1]]=1
                L[i,pos[2]]=1
                L[i,pos[3]]=1
            elif dist[pos[1]]==dist[pos[2]]:
                L[i,pos[0]]=-2
                L[i,pos[1]]=1
                L[i,pos[2]]=1
        return L
        
    def get_reg_sill(self,xcen,ycen,depth,length,width,strike,dip,ops):
        xs,ys,zs=self.get_centers(xcen,ycen,depth,length,width,strike,dip,ln,wn)
        oks=[]
        params=[]
        ln=self.ln
        wn=self.wn
        dat=self.data
        for i in range(len(xs)):
            oki = Okada(dat,typ='open')
            #Initial parameters [xcen,ycen,depth,length,width,opening,strike,dip]
            oki.set_bounds(low_bounds = [0, 0, 1e3, 1e3, 1e3,10.0,1.0,1.0], high_bounds = [0, 0, 1e3, 1e3, 1e3,10.0,1.0,1.0])
            oks.append(oki)
            params+=[xs[i],ys[i],-zs[i],length/ln,width/wn,ops[i],strike,dip]

        return oks,params
    
    def get_greens(self,x,y,xcen,ycen,depth,length,width,strike,dip):
        ln=self.ln
        wn=self.wn
        xcs,ycs,zcs=self.get_centers(xcen,ycen,depth,length,width,strike,dip)
        xo=[xcen,ycen,depth,length,width,1,strike,dip]
        defo=self.get_model(xo)
        slength=length/ln
        swidth=width/wn
        oki=Okada(None)
        if typ=='open':
            op=1
            sl=0
        else:
            op=0
            sl=1
        G=np.zeros((len(defo),ln*wn))
        for i in range(len(xcs)):
            xp=[xcs[i],ycs[i],-zcs[i],slength,swidth,sl,op,strike,dip]
            defo=oki.model(x,y,*xp)
            G[:,i]=defo
        return G
    
    def get_laplacian(self,xcen,ycen,depth,length,width,strike,dip):
        ln=self.ln
        wn=self.wn
        xcs,ycs,zcs=self.get_centers(xcen,ycen,depth,length,width,strike,dip)
        L=np.zeros((ln*wn,ln*wn))
        for i in range(len(xcs)):
            dist=(np.array(xcs)-xcs[i])**2+(np.array(ycs)-ycs[i])**2+(np.array(zcs)-zcs[i])**2
            pos=np.argsort(dist)
            #print(dist[pos[0:5]])
            if dist[pos[1]]==dist[pos[2]] and dist[pos[1]]==dist[pos[3]] and dist[pos[1]]==dist[pos[4]]:
                L[i,pos[0]]=-2
                L[i,pos[1]]=1
                L[i,pos[2]]=1
                L[i,pos[3]]=1
                L[i,pos[4]]=1
            elif dist[pos[1]]==dist[pos[2]] and dist[pos[1]]==dist[pos[3]]:
                L[i,pos[0]]=-2
                L[i,pos[1]]=1
                L[i,pos[2]]=1
                L[i,pos[3]]=1
            elif dist[pos[1]]==dist[pos[2]]:
                L[i,pos[0]]=-2
                L[i,pos[1]]=1
                L[i,pos[2]]=1
        return L
    
    def model(self,x,y,xcen,ycen,depth,length,width,strike,dip,ops):
        G=self.get_greens(x,y,xcen,ycen,depth,length,width,strike,dip)
        data=G@model
        
        ux=data[0:len(x)]
        uy=data[len(x):2*len(x)]
        uz=data[2*len(x):3*len(x)]
        
        return ux,uy,uz
        
        