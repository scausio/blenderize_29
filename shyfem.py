import os
import numpy as np
from scipy.spatial.qhull import Delaunay

# LOAD SHYFEM GRD AS CLASS

class ShyfemGrid():
    def __init__(self, grdPath, bathyCoeff, box):
        self.path = grdPath
        self.box = box
        self.bathyCoeff = bathyCoeff
        self.getNodes_Elements()

    def untilEmtpyLine(self, data):
        while True:
            line = next(data)
            if line == "" or (line[:-1].strip() == ""):
                return
            yield line

    def getNodes_Elements(self):
        self.grid = open(self.path)
        if os.path.exists(self.path + ".npz"):
            ds = np.load(self.path + ".npz")
            self.nodes, self.elems = ds["nodes"], ds["elements"]
        else:
            self.nodes = np.loadtxt(self.untilEmtpyLine(self.grid))  # load first grid block
            self.elems = np.loadtxt(self.untilEmtpyLine(self.grid))
            np.savez(self.path, nodes=self.nodes, elements=self.elems)

    def inBox(self):
        idNodes = self.nodes[:, 1].astype(int)
        vertsIds = self.elems[:, 4:7].astype(int)
        nodeSorter = np.argsort(idNodes)
        sortedIdx = nodeSorter[
            idNodes.searchsorted(vertsIds, sorter=nodeSorter)]  # associate original position to the named index

        self.triangsArray = self.nodes[sortedIdx]
        self.triangs=sortedIdx


        self.centroids = np.average(self.triangsArray[:, :, 3:], axis=1)

        self.msk = (
            (self.centroids[:, 0] >= self.box[0][0]) &
            (self.centroids[:, 0] <= self.box[0][1]) &
            (self.centroids[:, 1] >= self.box[1][0]) &
            (self.centroids[:, 1] <= self.box[1][1]))

        self.nodesInbox = self.triangsArray[self.msk]
        self.elemsInbox = self.elems[self.msk]
        self.centroidsInbox = self.centroids[self.msk]
        self.latitude = self.centroidsInbox[:, 1]
        self.longitude = self.centroidsInbox[:, 0]
        try:
            self.depth = self.elemsInbox[:, 7]
        except:
            self.depth  = self.elemsInbox[:, -1]*0
           

    def triangulateElems(self):
        self.inBox()
        tri = Delaunay(np.vstack((self.longitude, self.latitude)).T)
        self.tri = tri.simplices.copy()

    def triFromGrdToNumpy(self,outfile):
        self.inBox()
        lon=self.nodes[:, -2]
        lat = self.nodes[:, -1]
        tri=self.triangs
        d=np.zeros_like(lat)
        np.savez(outfile, v=np.array((lon,lat)).T, t=tri)
        return np.array((lon, lat,d)).T, tri

    def boxToNumpy(self, outfile):
        self.triangulateElems()
        np.savez(outfile, v=np.array((self.longitude, self.latitude, self.depth * self.bathyCoeff)).T, t=self.tri)
        return np.array((self.longitude, self.latitude, self.depth * self.bathyCoeff)).T, self.tri


    def saveGrd(self, outfile):

        with open(outfile, 'w') as out:
            np.savetxt(out,  self.nodes, fmt='%i %i %i %f %f')
            np.savetxt(out, self.elems, fmt='%i %i %i %i %i %i %i %.1f')

        out.close()
