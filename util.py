# -*- coding: utf-8 -*-
"""
General utility functions to accompany vmodels (mogi, yang, okada...)
Created on Tue Jun 21 14:59:15 2016

@author: scott
"""
import numpy as np
import rasterio
import numpy.ma as ma

def psi_phi(h):
    t,w=gauleg(0,1,41)
    g=-2.0*t/np.pi
    d=np.concatenate((g,np.zeros(g.size)))
    T1,T2,T3,T4=giveT(h,t,t)
    T1p=np.zeros(T1.shape)
    T2p=np.zeros(T1.shape)
    T3p=np.zeros(T1.shape)
    T4p=np.zeros(T1.shape)
    N=t.size
    for j in range(N):
        T1p[:,j]=w[j]*T1[:,j]
        T2p[:,j]=w[j]*T2[:,j]
        T3p[:,j]=w[j]*T3[:,j]
        T4p[:,j]=w[j]*T4[:,j]
    M1=np.concatenate((T1p,T3p),axis=1)
    M2=np.concatenate((T4p,T2p),axis=1)
    Kp=np.concatenate((M1,M2),axis=0)
    y=np.matmul(np.linalg.inv(np.eye(2*N,2*N)-(2/np.pi)*Kp),d)
    phi=y[0:N]
    psi=y[N:2*N]
    return phi,psi,t,w

def giveP(h,x):
    P=np.zeros((4,x.size))
    P[0]=(12*np.power(h,2)-np.power(x,2))/np.power((4*np.power(h,2)+np.power(x,2)),3)
    P[1] = np.log(4*np.power(h,2)+np.power(x,2)) + (8*np.power(h,4)+2*np.power(x,2)*np.power(h,2)-np.power(x,4))/np.power(4*np.power(h,2)+np.power(x,2),2)
    P[2] = 2*(8*np.power(h,4)-2*np.power(x,2)*np.power(h,2)+np.power(x,4))/np.power(4*np.power(h,2)+np.power(x,2),3)
    P[3] = (4*np.power(h,2)-np.power(x,2))/np.power((4*np.power(h,2)+np.power(x,2)),2)
    return P

def giveT(h,t,r):
    M = t.size
    N = r.size
    T1 = np.zeros((M,N)) 
    T2 = np.zeros((M,N)) 
    T3 = np.zeros((M,N))
    for i in range(M):
        Pm=giveP(h,t[i]-r)
        Pp=giveP(h,t[i]+r)
        T1[i] = 4*np.power(h,3)*(Pm[0,:]-Pp[0,:])
        T2[i] = (h/(t[i]*r))*(Pm[1,:]-Pp[1,:]) +h*(Pm[2,:]+Pp[2,:])
        T3[i] = (np.power(h,2)/r)*(Pm[3,:]-Pp[3,:]-2*r*((t[i]-r)*Pm[0,:]+(t[i]+r)*Pp[0,:]))
    T4=np.copy(T3.T)
    return T1,T2,T3,T4

def legpol(x,N):
    dim=x.size
    if not dim==1:
        dP=np.zeros((N,dim))
        P=np.zeros((N+1,dim))
        P[0]=np.ones(dim)
    else:
        dP=np.zeros(N)
        P=np.zeros(N+1)
        P[0]=1.0
    P[1]=x
    for j in range(1,N):
        P[j+1] = ((2*j+1)*x*P[j] - j*P[j-1])/(j+1)
        dP[j] = j*(x*P[j] - P[j-1])/(np.power(x,2)-1)
    return P[N-1],dP[N-1]

def gauleg(x1,x2,N):
    eps=1e-8
    z=np.zeros(N)
    xm = 0.5*(x2+x1)
    xl = 0.5*(x2-x1)
    for n in range(N):
        z[n] = np.cos(np.pi*((n+1)-0.25)/(N+0.5))
        z1 = 100*z[n]
        while np.abs(z1-z[n])>eps:
            pN,dpN=legpol(z[n],N+1)
            z1=z[n]
            z[n]=z1-pN/dpN
    pN,dpN=legpol(z,N+1)
    x=xm-xl*z
    w = 2*xl/((1-np.power(z,2))*np.power(dpN,2))
    return x,w

def world2rc(x,y,affine, inverse=False):
    '''
    World coordinates (lon,lat) to image (row,col) center pixel coordinates
    '''
    #NOTE: src.xy() does this I think...
    #T0 = src.meta['affine']
    T0 = affine
    T1 = T0 * rasterio.Affine.translation(0.5, 0.5)
    rc2xy = lambda r, c: (c, r) * T1
    # can probable simpligy,,, also int() acts like floor()
    xy2rc = lambda x, y: [int(i) for i in [x, y] * ~T1][::-1]

    if inverse:
        return rc2xy(y,x)
    else:
        return xy2rc(x,y)


def save_rasterio(path, data, profile):
    '''
    save single band raster file
    intended to use with load_rasterio() to open georeferenced data manipulate
    with numpy and then resave modified data
    '''
    with rasterio.drivers():
        with rasterio.open(path, 'w', **profile) as dst:
            dst.write(data, 1) #single band


def load_rasterio(path):
    '''
    load single bad georeference data as 'f4', convert NoDATA to np.nan
    not sure this works with 'scale' in vrt
    '''
    with rasterio.drivers():
        with rasterio.open(path, 'r') as src:
            data = src.read()
            meta = src.profile
            extent = src.bounds[::2] + src.bounds[1::2]

    return data, extent, meta


def load_cor_mask(path='phsig.cor.8alks_8rlks.geo.vrt', corthresh=0.1):
    '''
    load geocoded correlation file to use as mask
    '''
    cordata, extent, meta = load_rasterio(path)
    cor = cordata[0]
    # Geocoding seems to create outliers beyond realistic range (maybe interpolation)
    ind_outliers = (np.abs(cor) > 1)
    cor[ind_outliers] = 0.0
    # Can go further and remove pixels with low coherence (or just set to 0.0)
    mask = (cor < corthresh)
    #data[mask] = np.nan

    return mask


def calc_ramp(array, ramp='quadratic', custom_mask=None):
    '''
    Remove a quadratic surface from the interferogram Subtracting
    the best-fit quadratic surface forces the background mean surface
    displacement to be zero

    Note: exclude known signal, unwrapping errors, etc. with custom_mask

    ramp = 'dc','linear','quadratic'

    returns ramp
    '''
    X,Y = np.indices(array.shape)
    x = X.reshape((-1,1))
    y = Y.reshape((-1,1))

    # Work with numpy mask array
    phs = np.ma.masked_invalid(array)

    if custom_mask != None:
        phs[custom_mask] = ma.masked

    d = phs.reshape((-1,1))
    g = ~d.mask
    dgood = d[g].reshape((-1,1))

    if ramp == 'quadratic':
        print('fit quadtratic surface')
        G = np.concatenate([x, y, x*y, x**2, y**2, np.ones_like(x)], axis=1) #all pixels
        Ggood = np.vstack([x[g], y[g], x[g]*y[g], x[g]**2, y[g]**2, np.ones_like(x[g])]).T
        try:
            m,resid,rank,s = np.linalg.lstsq(Ggood,dgood)
        except ValueError as ex:
            print('{}: Unable to fit ramp with np.linalg.lstsq'.format(ex))


    elif ramp == 'linear':
        print('fit linear surface')
        G = np.concatenate([x, y, x*y, np.ones_like(x)], axis=1)
        Ggood = np.vstack([x[g], y[g], x[g]*y[g], np.ones_like(x[g])]).T
        try:
            m,resid,rank,s = np.linalg.lstsq(Ggood,dgood)
        except ValueError as ex:
            print('{}: Unable to fit ramp with np.linalg.lstsq'.format(ex))

    elif ramp == 'dc':
        G = np.ones_like(array)
        m = np.mean(phs)
        print('fit dc offset')

    ramp = np.dot(G,m)
    ramp = ramp.reshape(phs.shape)

    return ramp

def get_enu2los(enuFile='enu.rdr.geo'):
    '''
    Get conversion of cartesian ground displacements to radar LOS

    To avoid incidence and heading convention issues, assume 3 band GDAL file with
    conversion factors. Convension used is RECENT MASTER - OLDER SLAVE such that
    positive phase in interferogram is uplift.

    Example:
    model = np.array([ux,uy,uz])
    enu2los = get_enu2los('enu.rdr.geo')
    dlos = model*enu2los

    To generate this file with ISCE:
    imageMath.py --eval='sin(rad(a_0))*cos(rad(a_1+90)); sin(rad(a_0)) * sin(rad(a_1+90)); cos(rad(a_0))' --a=los.rdr.geo -t FLOAT -s BIL -o enu.rdr.geo
    imageMath.py --eval='a_0*b_0;a_1*b_1;a_2*b_2' --a=enu.rdr.geo --b=model.geo -t FLOAT -o model_LOS.geo
    '''
    data,junk,junk = load_rasterio(enuFile)
    data[data==0] = np.nan
    e2los,n2los,u2los = data
    # NOTE: some sort of bug in conversion code why is there z=1 in z2los
    u2los[u2los==1] = np.nan

    cart2los = np.dstack([e2los, n2los, u2los])
    return cart2los


def get_cart2los(incidence,heading):
    '''
    coefficients for projecting cartesian displacements into LOS vector
    assuming convention of Hannsen text figure 5.1 where angles are clockwise +
    relative to north!
    is Azimuth look direction (ALD=heading-270)
    vm.util.get_cart2los(23,190)

    ISCE descending los file has heading=-100
    '''
    incidence = np.deg2rad(incidence)
    ALD = np.deg2rad(heading-270)

    EW2los = -np.sin(ALD) * np.sin(incidence)
    NS2los = -np.cos(ALD) * np.sin(incidence)
    Z2los = np.cos(incidence)

    cart2los = np.dstack([EW2los, NS2los, Z2los])

    return cart2los



def cart2pol(x1,x2):
    #theta = np.arctan(x2/x1)
    theta = np.arctan2(x2,x1) #sign matters -SH
    r = np.hypot(x2,x1)
    return theta, r


def pol2cart(theta,r):
    x1 = r * np.cos(theta)
    x2 = r * np.sin(theta)
    return x1,x2


def shift_utm(X,Y,xcen,ycen):
    '''
    Avoid large numbers in UTM grid by creating local (0,0) origin
    '''
    x0 = X.min()
    y0 = Y.min()

    X = X - x0
    Y = Y - y0
    xcen = xcen - x0
    ycen = ycen - y0

    return X,Y,xcen,ycen


def get_cart2los_bak(inc, ald, x):
    '''
    NOTE: possible sign convention issues with this function...
    '''
    # x is data array
    # converted to LOS
    # los = data.dot(cart2los) * 1e2 # maybe use numpy.tensordot? not sure...
    # For now fake it:
    look = np.deg2rad(inc) * np.ones_like(x)  # incidence
    # heading (degreees clockwise from north)
    head = np.deg2rad(ald) * np.ones_like(x)
    # NOTE: matlab code default is -167 'clockwise from north' (same as hannsen text fig 5.1)
    # This is for descending envisat beam 2, asizmuth look direction (ALD) is
    # perpendicular to heading (-77)

    # however, make_los.pl generates unw file with [Incidence, ALD], ALD for ascending data is 77
    # make_los.pl defines "(alpha) azimuth pointing of s/c"
    EW2los = np.sin(head) * np.sin(look)
    NS2los = np.cos(head) * np.sin(look)
    Z2los = -np.cos(look)
    # NOTE: negative here implies uplift=positive in LOS
    cart2los = -np.dstack([EW2los, NS2los, Z2los])

    return cart2los
