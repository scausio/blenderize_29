import numpy as np

class GmeshMSH():
    def __init__(self, grdPath):
        self.path = grdPath
        self.getNodes_Elements()
        self.bathyCoeff=0.0001

    def getNodes_Elements(self):
        self.grid = open(self.path).read()
        self.nodes = np.array(self.grid [(self.grid.index('$Nodes')+len('$Nodes')):self.grid.index('$EndNodes')].split())[1:].astype('float').reshape(-1,4)
        self.allGeom = np.array(self.grid [(self.grid.index('$Elements')+len('$Elements')):self.grid.index('$EndElements')].split('\n'))[2:]
        me=[i for i, j in enumerate(self.allGeom) if len(j.split())==8]
        tris=self.allGeom[me]
        self.elems=np.array([i.split() for i in tris]).astype(int)


    def triToNumpy(self,outfile):
        self.getTri()
        lon=self.nodes[:, -3]
        lat = self.nodes[:, -2]
        #d = np.zeros(len(self.nodes))#self.nodes[:, -1]
        d = self.nodes[:, -1]*self.bathyCoeff
        tri=self.triangs
        return np.array((lon, lat,d)).T, tri

    def getTri(self):
        idNodes = self.nodes[:, 0].astype(int)
        nodeSorter = np.argsort(idNodes)
        vertsIds = self.elems[:, 5:].astype(int)
        sortedTri = nodeSorter[
            idNodes.searchsorted(vertsIds, sorter=nodeSorter)]  # associate original position to the named index
        self.triangs = sortedTri