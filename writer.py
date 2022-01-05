import os
import xarray as xr
import numpy as np
import bpy


class Writer:
    def __init__(self,grid_obj,fillValue=False):
        self.grid_obj=grid_obj
        self.obj_type=self.grid_obj.dataType
        bpy.ops.object.mode_set(mode='OBJECT')
        self.m = bpy.context.view_layer.objects.active.data
        self.mesh = np.array([i.co for i in self.m.vertices])
        self.fv=fillValue


    def writeGrd(self):
        x = self.mesh[:, 0]
        y = self.mesh[:, 1]
        ran = [i + 1 for i, j in enumerate(x)]
        em = np.zeros_like(y)
        nodes = np.array((em + 1, ran, em, x, y)).T
        tri = np.array([list(np.array(t.vertices) + 1) for t in self.m.polygons])
        base = np.zeros(tri.shape[0])
        ranE = [i + 1 for i, j in enumerate(base)]
        elems = np.array((base + 2, ranE, base, base + 3, tri[:, 0], tri[:, 1], tri[:, 2])).T

        with open(os.path.join(self.grid_obj.outPath,'%s.grd'%self.grid_obj.name), 'w') as out:
            np.savetxt(out, nodes, fmt='%i %i %i %f %f')
            np.savetxt(out, elems, fmt='%i %i %i %i %i %i %i')


    def write(self):

        if self.obj_type=='shyfem_grid':
            self.writeGrd()
        else:
            print ("%s write not implemented yet"%self.obj_type)