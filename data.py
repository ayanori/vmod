"""
Class to implement interface to geodetic data types used in source inversions

Author: Ronni Grapenthin
Date: 6/23/2021


TODO:
- integrate (In)SAR LOS
- integrate tilt
"""

import pandas as pd
import numpy as np

class Data:
    def __init__(self):
        self.data = pd.DataFrame(columns=['id', 'lat', 'lon', 'height', 'x','y','ux','uy','uz','sx','sy','sz'])

    #this is useful if you've got a few GNSS stations with offsets
    def add(self, id, lat, lon, height, x, y, ux, uy, uz, sx, sy, sz):
        self.data.loc[len(self.data.index)] = [id] + list((lat,lon,height,x,y,ux,uy,uz,sx,sy,sz))

    #useful if all that's to be done is run a forward model
    def add_locs(self, x, y):
        self.data['x'] = pd.Series(x)
        self.data['y'] = pd.Series(y)
        
    def add_disp(self,ux,uy,uz):
        self.data['ux'] = pd.Series(ux)
        self.data['uy'] = pd.Series(uy)
        self.data['uz'] = pd.Series(uz)
    
    def set_refidx(self,idx):
        self.refidx=idx
        
    def get_refidx(self):
        return self.refidx
    
    def get_reduced_obs(self):
        rux=self.data['ux']-self.data['ux'][self.refidx]
        ruy=self.data['uy']-self.data['uy'][self.refidx]
        ruz=self.data['uz']-self.data['uz'][self.refidx]
      
        return np.concatenate((rux,ruy,ruz)).ravel()
        
    def get_xs(self):
        return self.data['x'].to_numpy()

    def get_ys(self):
        return self.data['y'].to_numpy()

    def get_zs(self):
        return self.data['y'].to_numpy()*0.0

    def get_site_ids(self):
        return self.data['id'].to_numpy()

    def get_lats(self):
        return self.data['lat'].to_numpy()

    def get_lons(self):
        return self.data['lon'].to_numpy()

    def get_obs(self):
        ''' returns single vector with [ux1...uxN,uy1...uyN,uz1,...,uzN] as elements'''
        return self.data[['ux','uy','uz']].to_numpy().flatten(order='F')

#class GNSS(Data):

#class LOS(Data):

#class Tilt(Data):
    

