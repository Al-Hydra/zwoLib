from ..utils.PyBinaryReader.binary_reader import *
from .zwoTypes import zwoTypes
from .zwoEntity import zwoEntity
from .zwoEntity3D import zwoEntity3D
from .zwoHelpers import zwoVector, zwoQuaternion, zwoMatrix, zwoOBB
import json

class zwoMesh(BrStruct):
    def __init__(self):
        self.Type = zwoTypes.Mesh
        self.MeshType = 0
        self.Size = 0
        self.Name = ""
        self.Materials = []
        self.VertexBuffers = []
        self.FaceBuffer = []
        self.Data = None
        self.VertexBufferFlag = 0
        self.unk2 = 0
        self.unk3 = 0
        self.unk4 = 0
        
    def __br_read__(self, br:BinaryReader):
        self.Entity: zwoEntity = br.read_struct(zwoEntity)
        
        self.Name = self.Entity.Name
        
        self.Entity3D: zwoEntity3D = br.read_struct(zwoEntity3D)
        if self.Entity3D.flags1 != 2:
            self.Geometry = br.read_struct(zwoGeometry)
            self.VertexBufferFlag = br.read_uint32()
            self.unk2 = br.read_uint32()

            if self.Entity3D.MeshType == 2:
                self.unk3 = br.read_float()
                self.unk4 = br.read_float()

                if self.VertexBufferFlag >> 2 & 1:
                    VertexBufferCount = 1
                else:
                    VertexBufferCount = self.Geometry.TransformerCount

            else:
                VertexBufferCount = 1

            self.VertexBuffers = br.read_struct(VertexBuffer, VertexBufferCount)
            
            self.FaceBuffer = br.read_struct(FaceBuffer)
    
    def __br_write__(self, br:BinaryReader):
        
        mesh_buf = BinaryReader(endianness=Endian.BIG, encoding='cp932')
        
        mesh_buf.write_uint8(self.Entity.HeaderType)
        
        if self.Entity.HeaderType == 5:
            mesh_buf.write_uint32(len(self.Entity.Name))
            mesh_buf.write_str(self.Entity.Name)
            mesh_buf.write_uint32(self.Entity.Type)
        
        elif self.Entity.HeaderType == 6:
            mesh_buf.write_uint32(len(self.Entity.Name))
            mesh_buf.write_str(self.Entity.Name)
            mesh_buf.write_uint32(self.Entity.Type)
            mesh_buf.write_uint32(self.Entity.unk2)
            mesh_buf.write_uint32(self.Entity.unk3)
            mesh_buf.write_uint32(self.Entity.unk4)
            mesh_buf.write_uint32(self.Entity.unk5)
            mesh_buf.write_uint32(self.Entity.unk6)
            
        mesh_buf.write_struct(self.Entity3D)
        mesh_buf.write_struct(self.Geometry)
        mesh_buf.write_uint32(self.VertexBufferFlag)
        mesh_buf.write_uint32(self.unk2)
        
        if self.Entity3D.MeshType == 2:
            mesh_buf.write_float(self.unk3)
            mesh_buf.write_float(self.unk4)
        
        for vb in self.VertexBuffers:
            mesh_buf.write_struct(vb)

        mesh_buf.write_struct(self.FaceBuffer)
        
        mesh_size = mesh_buf.size()
        br.write_uint32(mesh_size + 4)
        br.write_bytes(bytes(mesh_buf.buffer()))


class zwoGeometry(BrStruct):
    def __init__(self):
        self.TransformerCount = 0
        self.unk = 0
        self.LocalTransformer = zwoTransformer()
        self.WorldTransformer = zwoTransformer()
        self.OrientedBoundingBox = zwoOBB()

    def __br_read__(self, br:BinaryReader):
        self.TransformerCount = br.read_uint32()
        self.unk = br.read_uint32(self.TransformerCount)

        for i in range(self.TransformerCount):
            self.LocalTransformer = br.read_struct(zwoTransformer)
            self.WorldTransformer = br.read_struct(zwoTransformer)
            self.OrientedBoundingBox = br.read_struct(zwoOBB)
    
    def __br_write__(self, br:BinaryReader):
        br.write_uint32(self.TransformerCount)
        br.write_uint32(self.unk)

        for i in range(self.TransformerCount):
            br.write_struct(self.LocalTransformer)
            br.write_struct(self.WorldTransformer)
            br.write_struct(self.OrientedBoundingBox)


class zwoTransformer(BrStruct):
    def __init__(self):
        self.Position = (0, 0, 0)
        self.Scale = (0, 0, 0)
        self.Rotation = (0, 0, 0, 0)
        self.Matrix = None

    def __br_read__(self, br: BinaryReader):
        self.Position = zwoVector(br)
        self.Scale = zwoVector(br)
        self.Rotation = zwoQuaternion(br)
        self.Matrix = zwoMatrix(br)
    
    def __br_write__(self, br: BinaryReader):
        br.write_float(self.Position)
        br.write_float(self.Scale)
        br.write_float(self.Rotation)
        for m in self.Matrix:
            br.write_float(m)
        
class VertexBuffer(BrStruct):
    def __init__(self):
        self.VertexCount = 0
        self.VertexFlags = 0
        self.Vertices = []

        self.PosPerVertex = 1
        self.NormPerVertex = 0
        self.ColorPerVertex = 0
        self.UVPerVertex = 0
        self.WeightPerVertex = 0

    def __br_read__(self, br:BinaryReader):
        #start = perf_counter()
        self.VertexCount = br.read_uint32()
        self.VertexFlags = br.read_uint32()
        
        if self.VertexFlags & 0x1:
            self.NormPerVertex = 1

        if self.VertexFlags & 0x2:
            self.ColorPerVertex += 1

        if self.VertexFlags & 0x4:
            self.ColorPerVertex += 1

        if self.VertexFlags & 0x8:
            self.UVPerVertex += 1

        if self.VertexFlags & 0x10:
            self.UVPerVertex += 1

        if self.VertexFlags & 0x20:
            self.UVPerVertex += 1

        if self.VertexFlags & 0x40:
            self.UVPerVertex += 1

        if self.VertexFlags & 0x80:
            self.WeightPerVertex += 1

        if self.VertexFlags & 0x100:
            self.WeightPerVertex += 1

        if self.VertexFlags & 0x200:
            self.WeightPerVertex += 1

        if self.VertexFlags & 0x400:
            self.WeightPerVertex += 1
                
        for i in range(self.VertexCount):
            vertex = Vertex()
            vertex.Position = br.read_float(3)
            vertex.Normal = br.read_float(3) if self.NormPerVertex else (0,0,0)
            vertex.Colors = br.read_int8(4) if self.ColorPerVertex else (0,0,0,0)
            
            for u in range(self.UVPerVertex):
                vertex.UVs.append((br.read_float(), br.read_float()))
            
            #list(map((br.read_float, br.read_float), range(self.UVPerVertex)))
            
            for w in range(self.WeightPerVertex):
                vertex.BoneIndices.append(br.read_uint32())
                vertex.BoneWeights.append(br.read_float())

            self.Vertices.append(vertex)
        
        #print(f"Vertex Buffer read in {perf_counter() - start} seconds")
    
    
    def __br_write__(self, br:BinaryReader):
        br.write_uint32(len(self.Vertices))
        br.write_uint32(self.VertexFlags)
        
        for vertex in self.Vertices:
            br.write_float(vertex.Position)
            br.write_float(vertex.Normal)
            
            for color in vertex.Colors:
                br.write_uint8(color)
            
            for uv in vertex.UVs:
                br.write_float(uv)
            
            for i in range(len(vertex.BoneIndices)):
                br.write_uint32(vertex.BoneIndices[i])
                br.write_float(vertex.BoneWeights[i])
        


class Vertex(BrStruct):
    def __init__(self):
        self.Position = (0,0,0)
        self.Normal = (0,0,0)
        self.UVs = []
        self.Colors = []
        self.BoneWeights = []
        self.BoneIndices = []


class FaceBuffer(BrStruct):
    def __init__(self) -> None:
        self.FaceCount = 0
        self.TrianglesType = 0
        self.IndexType = 0

        self.Faces = []
    
    def __br_read__(self, br:BinaryReader):
        self.FaceCount = br.read_uint32()
        self.TrianglesType = br.read_uint32()
        self.IndexType = br.read_uint32()

        if self.IndexType == 1:
            self.Faces = br.read_struct(Face32, self.FaceCount)
        else:
            self.Faces = br.read_struct(Face, self.FaceCount)
    
    def __br_write__(self, br:BinaryReader):
        br.write_uint32(len(self.Faces))
        br.write_uint32(self.TrianglesType)
        br.write_uint32(self.IndexType)
        
        if self.IndexType == 1:
            for face in self.Faces:
                br.write_uint32(face.Indices)
                br.write_uint32(face.MaterialIndex)
        else:
            for face in self.Faces:
                br.write_uint16(face.Indices)
                br.write_uint16(face.MaterialIndex)


class Face(BrStruct):
    def __init__(self):
        self.Indices = (0, 0, 0)
        self.MaterialIndex = 0
    
    def __br_read__(self, br:BinaryReader):
        self.Indices = br.read_uint16(3)
        self.MaterialIndex = br.read_uint16()
    
    def __br_write__(self, br:BinaryReader):
        br.write_uint16(self.Indices)
        br.write_uint16(self.MaterialIndex)

class Face32(BrStruct):
    def __init__(self):
        self.Indices = (0, 0, 0)
        self.MaterialIndex = 0
    
    def __br_read__(self, br:BinaryReader):
        self.Indices = br.read_uint32(3)
        self.MaterialIndex = br.read_uint32()
    
    def __br_write__(self, br:BinaryReader):
        br.write_uint32(self.Indices)
        br.write_uint32(self.MaterialIndex)


def ModelToJson(zwoMesh, path):
    mesh = {"Name": zwoMesh.Name,
            "Vertices": [],
            "Faces": [],
            "Materials": [],
    }

    with open(path + "mesh.json", "w") as f:
        json.dump(mesh["Materials"], f, indent=4)

