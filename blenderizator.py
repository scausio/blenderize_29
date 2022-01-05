import os
import numpy as np
from blenderize_29.shyfem import ShyfemGrid
from blenderize_29.gmsh import GmeshMSH
from blenderize_29.writer import Writer
import bpy
import xarray as xr



# SORT SEGMENT
def sortEdges(edges):
    edgesIndex = {}
    for edge in edges:
        a, b = edge
        edgesIndex.setdefault(a, []).append(b)
        edgesIndex.setdefault(b, []).append(a)
    for k, v in edgesIndex.items():
        if len(v) == 1:
            head = k
            break
    segment = [head, edgesIndex[head][0]]
    nextVertex = [v for v in edgesIndex.get(segment[-1]) if v != segment[-2]]
    while len(nextVertex) > 0:
        segment.append(nextVertex[0])
        nextVertex = [v for v in edgesIndex.get(segment[-1]) if v != segment[-2]]
    return segment


class BlenderGrid():
    def __init__(self, name, file_path, dataType, bathyCoeff=1, fillValue=False):
        self.name=name
        self.file_path=file_path
        self.outPath = outPath = os.path.dirname(file_path)
        self.dataType=dataType
        self.fv=fillValue
        box=[[ -90,90],[ -180,180]]
        print (outPath)
        if not os.path.exists(outPath):
            os.makedirs(outPath)
        if dataType=='shyfem_grid': # this get triangulation from file_path
            self.grid = ShyfemGrid(file_path, bathyCoeff, box)
            self.v, self.t = self.grid.triFromGrdToNumpy(os.path.join(outPath, 'box.npz'))
            self.l = []

        else:
            print ('NOT VALID DATATYPE!\n init:  name, path, bathyCoeff, box, dataType\n datatype:  shyfem_grid')
            return
        self.ob=self.loadObj( name)

    def mkobj(self, name):
        me = bpy.data.meshes.new(name)
        ob = bpy.data.objects.new(name, me)
        scn = bpy.context
        scn.collection.objects.link(ob)
        scn.view_layer.objects.active = ob
        ob.select_set( True)
        return ob

    def loadObj(self, name):
        v=self.v
        t=self.t
        l=self.l
        ob = self.mkobj(name)
        if v.shape[1]==2:
            v=  np.array((v.T[0],v.T[1],np.zeros_like(v.T[0]))).T
        try:
            v=v.tolist()
        except:
            pass
        try:
            l=l.tolist()
        except:
            pass
        try:
            t=t.tolist()
        except:
            pass
        ob.data.from_pydata(v, l, t)
        return ob

    def selectionToMask(self):
        obj = bpy.context.object
        mesh = obj.data
        obj.update_from_editmode()  # Loads edit-mode data into object data
        msk = [1 if e.select else 0 for e in mesh.vertices]
        #np.save(os.path.join(self.outPath, '{}_mask'.format(self.name)), msk)
        xr.Dataset({'mask': (['node'], msk)},
                              coords={'node': np.arange(len(msk))}).to_netcdf(os.path.join(self.outPath,'{}_mask.nc'.format(self.name)))

    def saveSelected(self):
        obj = bpy.context.object
        mesh = obj.data
        obj.update_from_editmode()  # Loads edit-mode data into object data
        mskTrans = [True if e.select else False for e in mesh.edges]

        selected_edges = [e for e in mesh.edges if e.select]
        selected_nodesId = np.array([tuple((i.vertices[0], i.vertices[1])) for i in selected_edges])  # GET ID
        selected_nodesCo = [mesh.vertices[i].co.xy for i in selected_nodesId.flatten()]  # GET COORDS

        sortedEdges = sortEdges(selected_nodesId)  # GET ORDERED NODES
        sortedCoords = [mesh.vertices[i].co.xy for i in sortedEdges]

        np.save(os.path.join(self.outPath, '{}_transectId'.format(self.name)), sortedEdges)
        np.save(os.path.join(self.outPath, '{}_transectCo'.format(self.name)),  sortedCoords)

    def save(self):
        Writer(self).write()
