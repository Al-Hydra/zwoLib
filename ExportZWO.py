import bpy
from zwo import *
from zwoMesh import *
import sys
from mathutils import Matrix, Vector
import bmesh
from PyBinaryReader.binary_reader import *
sys.path.append("D:\Dev\zwoLib")
C = bpy.context

# Get the active object
obj = C.object

# Get the active object's data
mesh = obj.data

# calculate triangles
triangles = mesh.calc_loop_triangles()

# Get the vertex colors
vcolmap = mesh.color_attributes[0].data

# Get the UV map
uvmap = mesh.uv_layers[0].data

vertices = []
tris = []

armature = obj.find_armature()

bones_dict = {b.name: i for i, b in enumerate(armature.data.bones)}


for v in mesh.vertices:
    vert = Vertex()
    vert.BoneWeights = [0,0,0,0]
    vert.BoneIndices = [0,0,0,0]
    vert.Position = v.co
    vert.Normal = v.normal
    vert.UV = uvmap[v.index].uv
    vert.Color = [vcolmap[v.index].color[0] * 255, vcolmap[v.index].color[1] * 255, vcolmap[v.index].color[2] * 255, vcolmap[v.index].color[3] * 255]
    for i, g in enumerate(sorted(v.groups, key=lambda x: x.weight, reverse=True)):
        if i < 4:
            vert.BoneWeights[i] = g.weight
            vert.BoneIndices[i] = bones_dict[armature.data.bones[g.group].name]
    vertices.append(vert)


'''# Loop through each triangle
for t in triangles:
    tri:Face = Face()
    tri.Indices = [t.vertices[0], t.vertices[1], t.vertices[2]]
    tri.Material = 0
    tris.append(tri)'''
bm = bmesh.new()
bm.from_mesh(mesh)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
for f in bm.faces:
    tri:Face = Face()
    tri.Indices = [f.verts[0].index, f.verts[1].index, f.verts[2].index]
    tri.Material = 0
    tris.append(tri)

bm.free()



#write to file

path = r"D:\Dev\zwoLib\test.bin"
vertpath = r"D:\Dev\zwoLib\testvert.bin"
tripath = r"D:\Dev\zwoLib\testtri.bin"

with open(vertpath, 'wb') as f:
    br = BinaryReader(endianness=Endian.BIG)
    
    br.write_int32(len(vertices))
    br.write_uint8(0)
    br.write_uint8(0)
    br.write_uint8(3)
    br.write_uint8(0x8b)

    for v in vertices:
        br.write_float(v.Position.x)
        br.write_float(v.Position.y)
        br.write_float(v.Position.z)
        br.write_float(v.Normal.x)
        br.write_float(v.Normal.y)
        br.write_float(v.Normal.z)
        br.write_uint8(0)
        br.write_uint8(255)
        br.write_uint8(255)
        br.write_uint8(255)
        br.write_float(v.UV.x)
        br.write_float(v.UV.y)
        for i in range(4):
            br.write_uint32(v.BoneIndices[i])
            br.write_float(v.BoneWeights[i])
    
    f.write(br.buffer())
    f.close()

with open(tripath, 'wb') as f:

    brf = BinaryReader(endianness=Endian.BIG)
    brf.write_uint32(len(tris))
    brf.write_int32(1)
    brf.write_int32(0)

    for t in tris:
        brf.write_uint16(t.Indices[0])
        brf.write_uint16(t.Indices[1])
        brf.write_uint16(t.Indices[2])
        brf.write_uint16(t.Material)
    
    f.write(brf.buffer())
    f.close()