


def checkQuads(faces):
    return [f for f in list(faces) if len(f.verts)!=3]

def wrongConnectivity(vs):
    return [v for v in vs if (len(v.link_edges)-2) == (len(v.link_faces))]

def nestedTri(vs):
    return [v for v in vs if (len(v.link_edges)==3) and (len(v.link_faces)==3)]

def quads(vs):
    return [v for v in vs if (len(v.link_edges)==4) and (len(v.link_faces)==4)]

def vertexArea(vs):
    return {v:sum([f.calc_area() for f in v.link_faces]) for v in vs}

def lowQuality(fs, varea=None):
    if varea is None:
        vs = set([v for f in fs for v in f.verts])
        varea=vertexArea(vs)
    return [f for f in bm.faces if (max([varea[v] for v in f.verts])/f.calc_area())>30]

def badAngles(fs,maxAngle=160):
    threshold = math.cos(maxAngle*math.pi/180)
    return [f for f in fs if
        (f.verts[1].co-f.verts[0].co).normalized() * (f.verts[2].co-f.verts[0].co).normalized() < threshold or
        (f.verts[2].co-f.verts[1].co).normalized() * (f.verts[0].co-f.verts[1].co).normalized() < threshold or
        (f.verts[0].co-f.verts[2].co).normalized() * (f.verts[1].co-f.verts[2].co).normalized() < threshold]

def aloneVerts(vs):
    return [v for v in vs if len(v.link_edges) == 1]

def tipTouch(vs):
    return [v for v in vs if (len(v.link_edges)-2) & (len(v.link_faces)==1)]



def denestTri(v):
    otherVerts = [e.other_vert(v) for e in v.link_edges]
    bm.verts.remove(v)
    f = bm.faces.new(otherVerts)
    f.select = True
    return otherVerts


def selectDepth(bm, depth):
    vToCheck = list(bm.verts)
    for f in vToCheck:
        if f.co[-1]==depth:
            f.select=True

def saveSelection(bm,name):
    mask=np.array([f.select for f in list(bm.verts)])
    np.save(name,mask)


def unvalidVerts(vs):
    return [v for v in vs if len(v.link_edges) > 2]

def alonePoint(vs):
    return [v for v in vs if len(v.link_edges) ==0]

#------------------------------- clean a grid --------------------------------
import bpy
import bmesh

def aloneVerts(vs):
    return [v for v in vs if len(v.link_edges) == 1]

def nestedTri(vs):
    return [v for v in vs if (len(v.link_edges)==3) and (len(v.link_faces)==3)]
def tipTouch(vs):
    return [v for v in vs if (len(v.link_edges)-2) & (len(v.link_faces)==1)]
    
    
bpy.ops.object.mode_set(mode = 'OBJECT')
a=bpy.context.view_layer.objects.active
bm=bmesh.new()
bm.from_mesh(a.data)


vToCheck = list(bm.verts)

for v in aloneVerts(vToCheck):
    v.select=True


for v in tipTouch(vToCheck):
    v.select=True


bpy.ops.object.mode_set(mode = 'OBJECT')
bm.to_mesh(a.data)
bpy.ops.object.mode_set(mode = 'EDIT')

for v in nestedTri(vToCheck):
    v.select=True



while len(vToCheck)>0:
    vToRemove = nestedTri(vToCheck)
    vToCheck = [v for r in vToRemove for v in denestTri(r)]

for f in badAngles(bm.faces,160):
    f.select=True
   

for f in lowQuality(bm.faces):
    f.select=True

wc= wrongConnectivity(bm.verts)
for v in wc:
    v.select=True

for f in checkQuads(bm.faces):
    f.select=True

for v in aloneVerts(vToCheck):
    v.select=True

bpy.ops.object.mode_set(mode = 'OBJECT')
bm.to_mesh(a.data)
bpy.ops.object.mode_set(mode = 'EDIT')
#-------------------------------


#------------------------------- find elements with more then 3 vertices
import bpy
bpy.ops.object.mode_set(mode = 'OBJECT')
m = bpy.context.object.data
a=[i for i in m.polygons if len(i.loop_indices)>3]
for i in a:
    i.select=True
#-------------------------------
#------------------------------- find elements with less than 3 faces and select them if 1 angle less then 30 deg
import bpy
import bmesh
import math

def badAngles_NOgrid(f,maxAngle=160):
    threshold = math.cos(maxAngle*math.pi/180)
    if (((f.verts[1].co-f.verts[0].co).normalized() * (f.verts[2].co-f.verts[0].co).normalized() < threshold) or
       ((f.verts[2].co-f.verts[1].co).normalized() * (f.verts[0].co-f.verts[1].co).normalized() < threshold) or
       ((f.verts[0].co-f.verts[2].co).normalized() * (f.verts[1].co-f.verts[2].co).normalized() < threshold)):
       return f

bpy.ops.object.mode_set(mode = 'OBJECT')
a=bpy.context.scene.objects.active
bm=bmesh.new()
bm.from_mesh(a.data)

for face in list(bm.faces):
    if len(list(face.verts))<4:
        if badAngles_NOgrid(face,maxAngle=30):
            face.select=True

bpy.ops.object.mode_set(mode = 'OBJECT')
bm.to_mesh(a.data)
bpy.ops.object.mode_set(mode = 'EDIT')
#-------------------------------

"""SELECT NODES ACCORDING DEPTH"""
import bpy
obj = bpy.context.object
mesh = obj.data
obj.update_from_editmode()
dpt=7
idx = [i for i in mesh.vertices if i.co.z<(dpt*-bathyCoeff)]
for i in idx:
     i.select=True

"""SELECT NODES ACCORDING MASK"""
import numpy as np
import bpy

obj = bpy.context.object
mesh = obj.data
obj.update_from_editmode()
msk = np.load('/Users/scausio/Desktop/condivisa_VM/grid_global/pos_landMask_2.npy')
for i, j in zip(mesh.vertices, msk):
    if j == True:
        i.select = j
        
#------------------------------- find elements linked to 1 other element if bad angle

import bpy
import bmesh
import math

def badAngles_NOgrid(f,maxAngle=160):
    threshold = math.cos(maxAngle*math.pi/180)
    if (((f.verts[1].co-f.verts[0].co).normalized() * (f.verts[2].co-f.verts[0].co).normalized() < threshold) or
       ((f.verts[2].co-f.verts[1].co).normalized() * (f.verts[0].co-f.verts[1].co).normalized() < threshold) or
       ((f.verts[0].co-f.verts[2].co).normalized() * (f.verts[1].co-f.verts[2].co).normalized() < threshold)):
       return f
       
       
bpy.ops.object.mode_set(mode = 'OBJECT')
a=bpy.context.scene.objects.active
bm=bmesh.new()
bm.from_mesh(a.data)
vToCheck = list(bm.verts)

for face in list(bm.faces):
    for v in face.verts:
         if (len(v.link_faces)==1):
             if badAngles_NOgrid(face,maxAngle=130):
                face.select=True

bpy.ops.object.mode_set(mode = 'OBJECT')
bm.to_mesh(a.data)
bpy.ops.object.mode_set(mode = 'EDIT')

#-------------------------------
#------------------------------- find elements with area smaller then value
import bpy
bpy.ops.object.mode_set(mode = 'OBJECT')
m = bpy.context.object.data
a=[i for i in m.polygons if len(i.area)<0.2]
for i in a:
    i.select=True

bpy.ops.object.mode_set(mode = 'OBJECT')

bpy.ops.object.mode_set(mode = 'EDIT')
#-------------------------------
#------------------------------- save blender mesh as v and t  or GRD with bathy
import numpy as np
import bpy
import os


def saveGrd(v,t, outPath):
    x = v[:, 0]
    y = v[:, 1]
    z=v[:, 2]
    ran = [i + 1 for i, j in enumerate(x)]
    em = np.zeros_like(y)
    nodes = np.array((em + 1, ran, em+2, x, y)).T
    base = np.zeros(t.shape[0])
    ranE = [i + 1 for i, j in enumerate(base)]
    elems = np.array((base + 2, ranE, base, base + 3, t[:, 0]+1, t[:, 1]+1, t[:, 2]+1),z).T
    with open(os.path.join(outPath, 'newGrd.file_path'), 'w') as outfile:
        np.savetxt(outfile, nodes, fmt='%i %i %i %f %f')
        np.savetxt(outfile, elems, fmt='%i %i %i %i %i %i %i %.2f')

outPath='/Users/scausio/Desktop/condivisa_VM/grid_global/definitivi/'
data = bpy.context.scene.objects.active.data
verts=np.array([list(v.co.xyz) for v in data.vertices])
tris=np.array([list(p.vertices) for p in data.polygons])


saveGrd(verts,tris, outPath)
#np.savez('/Users/scausio/Desktop/condivisa_VM/grid_global/definitivi/global20200414.npz',v=verts,t=tris)


#------------------------------- save indices of selected vertices
import numpy as np
import bpy

bm=bpy.context.scene.objects.active.data
selected=np.array([i for  i,f in enumerate(list(bm.vertices)) if f.select==True])
np.save('/Users/scausio/Desktop/condivisa_VM/grid_global/definitivi/id_boundary.npy',selected)
#-------------------------------
			# find tip-touching tris
		
import bpy
import bmesh

def notvalidTri(vs):
    return [v for v in vs if (len(v.link_edges)-len(v.link_faces))>1]

bpy.ops.object.mode_set(mode = 'OBJECT')
a=bpy.context.scene.objects.active
bm=bmesh.new()
bm.from_mesh(a.data)
vToCheck = list(bm.verts)

for f in notvalidTri(vToCheck):
    f.select=True

bpy.ops.object.mode_set(mode = 'OBJECT')
bm.to_mesh(a.data)
bpy.ops.object.mode_set(mode = 'EDIT')

# -------------------  FROM	BLENDER TO GRD
import numpy as np
import bpy
import os

def saveGrd(v,t, outPath):
    x = v[:, 0]
    y = v[:, 1]
    z=v[:, 2]
    ran = [i + 1 for i, j in enumerate(x)]
    em = np.zeros_like(y)
    nodes = np.array((em + 1, ran, em+2, x, y)).T
    base = np.zeros(t.shape[0])
    ranE = [i + 1 for i, j in enumerate(base)]
    elems = np.array((base + 2, ranE, base, base + 3, t[:, 0]+1, t[:, 1]+1, t[:, 2]+1,z)).T
    with open(os.path.join(outPath, 'newGrd.file_path'), 'w') as outfile:
        np.savetxt(outfile, nodes, fmt='%i %i %i %f %f')
        np.savetxt(outfile, elems, fmt='%i %i %i %i %i %i %i %f')

outPath='/Users/scausio/Desktop/condivisa_VM/grid_global/definitivi/'
data = bpy.context.scene.objects.active.data
verts=np.array([list(v.co.xyz) for v in data.vertices])
tris=np.array([list(p.vertices) for p in data.polygons])

saveGrd(verts,tris, outPath)








