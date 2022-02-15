import bpy
import numpy as np
import os


def saveGrd( nodes,elems, outname):
    with open(outname, 'w') as outfile:
        np.savetxt(outfile, nodes, fmt='%i %i %i %f %f')
        outfile.write('\n')
        np.savetxt(outfile, elems, fmt='%i %i %i %i %i %i %i')
        outfile.write('\n')

def toGrd(outname):
    a=bpy.context.view_layer.objects.active
    tri=np.array([[list(tri.vertices)[0],list(tri.vertices)[1],list(tri.vertices)[2]]  for tri in a.data.polygons])+1
    points= np.array([(coords.co.x,coords.co.y) for coords in list(a.data.vertices)])
    nodes=np.c_[np.ones(points.shape[0]),np.arange(points.shape[0])+1,np.zeros(points.shape[0]),points]
    elems= np.c_[np.ones(tri.shape[0])+1,np.arange(tri.shape[0])+1,np.zeros(tri.shape[0]),np.ones(tri.shape[0])+2,tri]
    saveGrd(nodes,elems, outname)


toGrd('/Users/scausio/Downloads/zaky_clean.grd')

def toXYZ(outname):
    a=bpy.context.scene.objects.active
    points= np.array([(coords.co.x,coords.co.y,coords.co.z/bathyCoeff) for coords in list(a.data.vertices)])
    np.savetxt(outname,points)
