import bpy
import os
import sys
from mathutils import Matrix, Vector, Quaternion
import bmesh
sys.path.append("D:\Dev\zwoLib")
from ReadZWO import read_zwo
from ReadDIC import read_dic, dic2ddso
from zwo import *
from zwoSkeletalAnimation import Entry

zwoPath = r"D:\SteamLibrary\steamapps\common\Obscure2\data\characters\boy2\anims_pc.zwo"
zwo = read_zwo(zwoPath)
texturesPath = r"D:\Games\Obscure 2\adatapack\levels\k\k003\lvl_pc"
levelTextures = r"D:\Games\Obscure 2\adatapack\levels\k\k003\lvl_pc.dic"

Skeleton: zwoSkeleton = None
Models = []
Materials = []
Textures = []
Animations = []

dic = read_dic(levelTextures)

for tex in dic.Textures:
    dds = dic2ddso(tex)
    
    img = bpy.data.images.new(tex.Name, tex.Width, tex.Height, alpha=True)
    img.pack(data=(dds.texture_data), data_len=len(dds.texture_data))
    img.source = "FILE"

for chunk in zwo.Entities:
    if chunk.Type == zwoTypes.Skeleton:
        Skeleton = chunk
    elif chunk.Type == zwoTypes.Mesh:
        Models.append(chunk)
    elif chunk.Type == zwoTypes.Material:
        Materials.append(chunk)
    elif chunk.Type == zwoTypes.SkeletalAnimation:
        Animations.append(chunk)

BoneDict = {}
ReverseBoneDict = {}


def RigidModel(Model):
    mesh = bpy.data.meshes.new(Model.Entity.Name)
    obj = bpy.data.objects.new(Model.Entity.Name, mesh)
    #obj.matrix_world = Matrix(Model.Geometry.Transformer1.Matrix).transpose()
    #obj.matrix_local = Matrix(Model.Geometry.Transformer2.Matrix)
    obj.location = Model.Geometry.Transformer1.Position
    obj.rotation_quaternion = Model.Geometry.Transformer1.Rotation
    obj.scale = Model.Geometry.Transformer1.Scale

    #assign materials
    for material in Model.Entity3D.Materials:
        if bpy.data.materials.get(material):
            obj.data.materials.append(bpy.data.materials[material])

    bm = bmesh.new()
    
    #weight layer
    w_layer = bm.verts.layers.deform.new("weights")
    
    
    vertex_buffer = Model.VertexBuffers[0]
    for v in vertex_buffer.Vertices:
        bv = bm.verts.new(v.Position)
        bv.normal = v.Normal[0]

    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    for f in Model.FaceBuffer.Faces:
        try:
            face = bm.faces.new([bm.verts[i] for i in f.Indices])
            face.smooth = True
            bm.faces.ensure_lookup_table()
            bm.faces.index_update()
            face.material_index = f.MaterialIndex
        except:
            pass
    bm.to_mesh(mesh)
    bm.free()
    
    for i in range(vertex_buffer.UVPerVertex):
        uv_layer = mesh.uv_layers.new(name = f"UVMap_{i}")
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                uv = vertex_buffer.Vertices[mesh.loops[loop_index].vertex_index].UVs[i]
                mesh.uv_layers[0].data[loop_index].uv = (uv[0], 1 - uv[1])
    bpy.context.collection.objects.link(obj)


def DeformableModel(Model):
    mesh = bpy.data.meshes.new(Model.Entity.Name)
    obj = bpy.data.objects.new(Model.Entity.Name, mesh)
    obj.parent = armature
    obj.modifiers.new("Armature", 'ARMATURE').object = armature
    #obj.matrix_world = Matrix(Model.Geometry.Transformer1.Matrix)
    

    #assign materials
    for material in Model.Entity3D.Materials:
        if bpy.data.materials.get(material):
            obj.data.materials.append(bpy.data.materials[material])
    
    for bone in armature.data.bones:
        obj.vertex_groups.new(name = bone.name)

    bm = bmesh.new()
    
    #weight layer
    w_layer = bm.verts.layers.deform.new("weights")
    
    
    vertex_buffer = Model.VertexBuffers[0]
    for v in vertex_buffer.Vertices:
        bv = bm.verts.new(v.Position)
        bv.normal = v.Normal[0]
        for i in range(vertex_buffer.WeightPerVertex):

            '''name = ReverseBoneDict[v.BoneIndices[i]]
            index = armature.data.bones.find(name)'''
            bv[w_layer][v.BoneIndices[i]] = v.BoneWeights[i]

    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    for f in Model.FaceBuffer.Faces:
        try:
            face = bm.faces.new([bm.verts[i] for i in f.Indices])
            face.smooth = True
            bm.faces.ensure_lookup_table()
            bm.faces.index_update()
            face.material_index = f.MaterialIndex
        except:
            pass
    bm.to_mesh(mesh)
    bm.free()
    
    #mesh.transform(Matrix(Model.Geometry.Transformer2.Matrix))
    
    for i in range(vertex_buffer.UVPerVertex):
        uv_layer = mesh.uv_layers.new(name = f"UVMap_{i}")
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                uv = vertex_buffer.Vertices[mesh.loops[loop_index].vertex_index].UVs[i]
                mesh.uv_layers[0].data[loop_index].uv = (uv[0], 1 - uv[1])
    bpy.context.collection.objects.link(obj)


if Skeleton:
    EntityName = Skeleton.Entity.Name
    bpy.data.armatures.new(EntityName)
    armature = bpy.data.objects.new(EntityName, bpy.data.armatures[EntityName])
    bpy.context.collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    def add_bone(bone, parent, index):
        boneName = bone.Name
        BoneDict[boneName] = index 
        #ReverseBoneDict[index] = boneName #This will be used later to assign vertex groups

        b = armature.data.edit_bones.new(boneName)
        if parent:
            b.matrix = Matrix(bone.Matrix)
            b.parent = parent

        parent = b
        b.tail += Vector((0,0,5))

        for ChildIndex in bone.ChildIndices:
            Child = Skeleton.Bones[ChildIndex]
            add_bone(Child, parent, ChildIndex)

    for i in range(Skeleton.BonesCount):
        #recursively add bones
        parent = None
        bone = Skeleton.Bones[i]
        boneName = bone.Name
        if not BoneDict.get(boneName):
            add_bone(bone, parent, i)

    bpy.ops.object.mode_set(mode='OBJECT')

for mat in Materials:
    material = bpy.data.materials.new(mat.Name)
    material.use_nodes = True

    bsdf = material.node_tree.nodes["Principled BSDF"]

    texture = material.node_tree.nodes.new("ShaderNodeTexImage")

    path = os.path.join(texturesPath, mat.TextureName + ".dds")
    #check if texture exists
    if os.path.exists(path):
    #if bpy.data.images.get(mat.TextureName):
        texture.image = bpy.data.images.get(mat.TextureName)

        material.node_tree.links.new(bsdf.inputs['Base Color'], texture.outputs['Color'])


for Model in Models:
    if Model.Entity3D.MeshType == 6:
        DeformableModel(Model)
    elif Model.Entity3D.MeshType == 2:
        RigidModel(Model)

if Animations:
    if Skeleton:
        AnimSkeleton = Skeleton
    else:
        obj = bpy.context.object
        if obj.type == "ARMATURE":
            AnimSkeleton = obj
    
    if AnimSkeleton:
        #let's test the first animation
        anim: zwoSkeletalAnimation = Animations[0]

        #create an action
        action = bpy.data.actions.new(name = anim.Entity.Name)
        #action.use_fake_user = False
        curves = anim.Curves

        
        for bone, entry in zip(AnimSkeleton.pose.bones, anim.Entries):
            print(bone.name)
            print(entry.EntryTypeFlag, entry.CurveStartIndex, entry.CurvesPerFrame)
            entry: Entry
            entryType = entry.EntryTypeFlag
            if entryType == 0:
                continue
            elif entryType == 1:
                #set the location
                curveIndex = entry.CurveStartIndex
                rotation = curves[curveIndex]
                rotation = (rotation[3], rotation[0], rotation[2], rotation[1])
                bone.rotation_quaternion = Quaternion(rotation).conjugated()
                bone.keyframe_insert(data_path = "rotation_quaternion", frame = 0)
                curveIndex += 1
                
                bone.location = Vector(curves[curveIndex][x] * 0.01 for x in range(3))
                bone.keyframe_insert(data_path = "location", frame = 0)
                curveIndex += 1

                bone.scale = Vector(curves[curveIndex][x] for x in range(3))
                bone.keyframe_insert(data_path = "scale", frame = 0)
                curveIndex += 1
            
            elif entryType == 3:
                curveIndex = entry.CurveStartIndex

                rotation = curves[curveIndex]
                rotation = (rotation[3], rotation[0], rotation[2], rotation[1])
                bone.rotation_quaternion = Quaternion(rotation)
                bone.keyframe_insert(data_path = "rotation_quaternion", frame = 0)
                curveIndex += 1

                bone.location = Vector(curves[curveIndex][x] * 0.01 for x in range(3))
                bone.keyframe_insert(data_path = "location", frame = 0)
                curveIndex += 1

                bone.scale = Vector(curves[curveIndex][x] for x in range(3))
                bone.keyframe_insert(data_path = "scale", frame = 0)
                curveIndex += 1

                for i in range(anim.FrameCount - 1):
                    rotation = curves[curveIndex]
                    rotation = (rotation[3], rotation[0], rotation[2], rotation[1])
                    bone.rotation_quaternion = Quaternion(rotation).conjugated()
                    bone.keyframe_insert(data_path = "rotation_quaternion", frame = i + 1)
                    curveIndex += 1
                
            elif entryType == 7:

                curveIndex = entry.CurveStartIndex
                rotation = curves[curveIndex]
                rotation = (rotation[3], rotation[0], rotation[2], rotation[1])
                rotation = Quaternion(rotation)
                bone.rotation_quaternion = rotation
                bone.keyframe_insert(data_path = "rotation_quaternion", frame = 0)
                curveIndex += 1

                bone.location = Vector(curves[curveIndex][x] * 0.01 for x in range(3))
                bone.keyframe_insert(data_path = "location", frame = 0)
                curveIndex += 1

                bone.scale = Vector(curves[curveIndex][x] for x in range(3))
                bone.keyframe_insert(data_path = "scale", frame = 0)
                curveIndex += 1

                for i in range(anim.FrameCount - 1):
                    rotation = curves[curveIndex]
                    rotation = (rotation[3], rotation[0], rotation[1], rotation[2])
                    rotation = Quaternion(rotation).conjugated()
                    bone.rotation_quaternion = rotation
                    bone.keyframe_insert(data_path = "rotation_quaternion", frame = i + 1)
                    curveIndex += 1

                    location = Vector(curves[curveIndex][x] * 0.01 for x in range(3))
                    location = (location[2], location[1], location[0])
                    bone.location = location
                    bone.keyframe_insert(data_path = "location", frame = i + 1)
                    curveIndex += 1

