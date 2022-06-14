import numpy as np
from scipy.spatial.qhull import Delaunay
import os
import netCDF4 as nc

def findCoord(ds, coords):
    for coord in coords:
        if coord in ds.variables.keys():
            return coord

def getCoordsName(ds):
    lons=['longitude','lon', 'x','X']
    lats=['latitude','lat','y','Y']
    depths=['total_depth', 'depth', 'Bathy', 'Bathymetry', 'z','Z','bathy','bathymetry','bathy_metry']
    lonName=findCoord(ds, lons)
    latName=findCoord(ds,lats)
    depthName=findCoord(ds,depths)

    return lonName,latName,depthName

class NcBathy_unstruct():
    def __init__(self, filePath, bathyCoeff):
        self.path = filePath
        self.bathyCoeff = bathyCoeff
        self.readFile()

    def readFile(self):
        ds = nc.Dataset(self.path)

        lonName, latName, depthName=getCoordsName(ds)

        self.lon= ds[lonName][:].filled()
        self.lat = ds[latName][:].filled()
        self.depth = ds[depthName][:].filled()

        try:
            self.tri = (ds['element_index'][:] - 1).filled()
        except:
            self.tri = (ds['tri'][:] - 1).filled()
        self.ds = ds

    def toNumpy(self, outfile):
        np.savez(outfile, v=np.array((self.lon, self.lat, self.depth * -self.bathyCoeff)).T, t=self.tri)
        return np.array((self.lon, self.lat, self.depth * -self.bathyCoeff)).T, self.tri


class NcBathy_regular():
    def __init__(self, filePath,bathyCoeff,fillValue=10):
        self.path = filePath
        self.bathyCoeff=bathyCoeff
        self.fv=fillValue
        self.regularToScatter()
    def readFile(self):
        ds = nc.Dataset(self.path)
        #lonName, latName, depthName = getCoordsName(ds)
        print (ds)
        print (ds['bathy_metry'])

        lon = ds['nav_lon'][0].filled()
        lat =ds['nav_lat'][:,0].filled()
        depth = -ds['bathy_metry'][0].filled()
        #lon= ds[lonName][:].filled()
        #lat = ds[latName][:].filled()
        #depth = ds[depthName][0].filled()
        print (np.nanmin(depth),np.nanmax(depth))
        if self.fv:
            pass
            #depth[depth==self.fv]=np.nan
        self.nan = np.isnan(depth).flatten()
        self.ds=ds
        return lon,lat,depth

    def regularToScatter(self):

        x,y,z=self.readFile()
        xx,yy=np.meshgrid(x,y)
        self.lon=xx.flatten()
        self.lat=yy.flatten()
        self.depth=z.flatten()*self.bathyCoeff
        self.triangulate()

    def triangulate(self):
        tri = Delaunay(np.vstack((self.lon[np.logical_not(self.nan)], self.lat[np.logical_not(self.nan)])).T)
        self.tri = tri.simplices.copy()

    def toNumpy(self):
        out=np.array((self.lon, self.lat, self.depth)).T
        return np.array(out), self.tri

