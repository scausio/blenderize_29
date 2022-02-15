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


    def writeWW3(self):
        self.mesh[:, -1] = self.mesh[:, -1] / self.grid_obj.grid.bathyCoeff
        outNodes = np.array((range(1, len(self.mesh) + 1, 1), self.mesh[:, 0], self.mesh[:, 1], self.mesh[:, 2])).T
        elems = np.array([list(poly.vertices) for poly in self.m.polygons])
        print(len(elems))
        outElems = np.array((range(1, len(elems) + 1, 1), np.zeros(len(elems)) + 2, np.zeros(len(elems)) + 2,
                             np.zeros(len(elems)), np.zeros(len(elems)) + 1, elems[:, 0] + 1, elems[:, 1] + 1,
                             elems[:, 2] + 1)).T
        with open(os.path.join(self.grid_obj.outPath,'%s.msh'%self.grid_obj.name), 'w') as outfile:
            outfile.write('$MeshFormat\n2.2 0 8\n$EndMeshFormat\n$Nodes\n')
            outfile.write('%s\n' % len(self.mesh))
            np.savetxt(outfile, outNodes, fmt='%i %.6f %.6f %.1f')
            outfile.write('$EndNodes\n$Elements\n')
            outfile.write('%s\n' % len(elems))
            np.savetxt(outfile, outElems, fmt='%i')
            outfile.write('$EndElements\n')
        outfile.close()

    def write(self):

        if self.obj_type=='shyfem_grid':
            self.writeGrd()
        elif self.obj_type=='ww3':
            self.writeWW3()
        else:
            print ("%s write not implemented yet"%self.obj_type)