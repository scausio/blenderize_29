import numpy as np

class ww3MSH():
    def __init__(self, grdPath):
        self.path = grdPath
        self.getNodes_Elements()

    def getNodes_Elements(self):
        self.grid = open(self.path).read()

        self.header=np.array(self.grid.split('\n')[:5]).T

        self.nodes = np.array(
            self.grid[(self.grid.index('$Nodes') + len('$Nodes')):self.grid.index('$EndNodes')].split())[1:].astype(
            'float').reshape(-1, 4)
        print(self.nodes)
        self.middle=np.array(
            self.grid[(self.grid.index('$EndNodes')):].split('\n'))[:3]
        print(self.middle)
        allGeom = np.array(
            self.grid[(self.grid.index('$Elements') + len('$Elements')):self.grid.index('$EndElements')].split(
                '\n'))[2:]

        me = [i for i, j in enumerate(allGeom) if len(j.split()) == 8]

        tris = allGeom[me]
        self.elems = np.array([i.split() for i in tris]).astype(int)
        self.end=np.array(
            self.grid[self.grid.index('$EndElements'):].split(
                '\n'))
        print (self.end)