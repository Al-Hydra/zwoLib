from PyBinaryReader.binary_reader import *
from PyBinaryReader.binary_reader.binary_reader import BinaryReader
from zwoTypes import zwoTypes
from zwoEntity import zwoEntity
from zwoEntity3D import zwoEntity3D
from zwoHelpers import zwoVector, zwoQuaternion, zwoMatrix, zwoOBB
import json

class zwoMesh(BrStruct):
    def __init__(self):
        self.Type = zwoTypes.Mesh
        self.MeshType = 0
        self.Size = 0
        self.Name = ""
        self.Materials = []
        self.VertexBuffer = []
        self.FaceBuffer = []
        self.Data = None

    def __br_read__(self, br:BinaryReader):
        self.Entity: zwoEntity = br.read_struct(zwoEntity)
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
        pass


class zwoGeometry(BrStruct):
    def __init__(self):
        self.TransformerCount = 0
        self.unk = 0
        self.Transformer1 = zwoTransformer()
        self.Transformer2 = zwoTransformer()
        self.OBB = zwoOBB()

    def __br_read__(self, br:BinaryReader):
        self.TransformerCount = br.read_uint32()
        self.unk = br.read_uint32(self.TransformerCount)

        for i in range(self.TransformerCount):
            self.Transformer1 = br.read_struct(zwoTransformer)
            self.Transformer2 = br.read_struct(zwoTransformer)
            self.OBB = br.read_struct(zwoOBB)


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
        self.unk1 = 0
        self.unk2 = 0

        self.Faces = []
    
    def __br_read__(self, br:BinaryReader):
        self.FaceCount = br.read_uint32()
        self.unk1 = br.read_uint32()
        self.unk2 = br.read_uint32()

        self.Faces = [br.read_struct(Face) for i in range(self.FaceCount)]


class Face(BrStruct):
    def __init__(self):
        self.Indices = (0, 0, 0)
        self.MaterialIndex = 0
    
    def __br_read__(self, br:BinaryReader):
        self.Indices = br.read_uint16(3)
        self.MaterialIndex = br.read_uint16()


def ModelToJson(zwoMesh, path):
    mesh = {"Name": zwoMesh.Name,
            "Vertices": [],
            "Faces": [],
            "Materials": [],
    }

    with open(path + "mesh.json", "w") as f:
        json.dump(mesh["Materials"], f, indent=4)

