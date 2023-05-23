from PyBinaryReader.binary_reader import *
from PyBinaryReader.binary_reader.binary_reader import BinaryReader
from zwoHelpers import zwoMatrix
from zwoEntity import zwoEntity
from zwoEntity3D import zwoEntity3D
from zwoTypes import zwoTypes


class zwoSkeleton(BrStruct):
    def __init__(self) -> None:
        self.Type = zwoTypes.Skeleton
        self.Entity = None
        self.Entity3D = None
        self.BonesCount = 0
        self.Bones = []
    def __br_read__(self, br: BinaryReader, *args) -> None:
        self.Entity = br.read_struct(zwoEntity)
        self.Entity3D = br.read_struct(zwoEntity3D)
        self.unk1 = br.read_uint32()
        self.BonesCount = br.read_uint32()
        self.unk2 = br.read_uint32()
        self.Bones = [br.read_struct(Bone) for i in range(self.BonesCount)]


class Bone(BrStruct):
    def __init__(self):
        self.Name = ""
        self.ChildCount = 0
        self.ChildIndices = []
        self.Matrix = []
    
    def __br_read__(self, br: BinaryReader):
        self.unk1 = br.read_uint32()
        self.Name = br.read_str(br.read_uint32())
        self.ChildCount = br.read_uint32()
        self.ChildIndices = [br.read_uint32() for i in range(self.ChildCount)]
        self.Matrix = zwoMatrix(br)