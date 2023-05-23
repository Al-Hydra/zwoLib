from PyBinaryReader.binary_reader import *
from zwoHelpers import zwoTransformer

class zwoEntity3D(BrStruct):
    def __init__(self):
        self.MaterialCount = 0
        self.Materials = []
        self.flags1 = 0
        self.flags2 = 0
        self.unk1 = 0
        self.value1 = 0
        self.value2 = 0
        self.Param1 = None
        self.Param2 = None
        self.unk2 = 0
        self.MeshType = 0
        self.Transformer1 = None
        self.unk5 = 0
    def __br_read__(self, br: BinaryReader):
        self.MaterialCount = br.read_uint32()
        self.Materials = [br.read_str(br.read_uint32()) for i in range(self.MaterialCount)]

        self.flags1 = br.read_uint32()
        self.flags2 = br.read_uint32()
        self.unk1 = br.read_uint32()

        if (self.flags2 & 0x10000) != 0:
            self.value1 = br.read_uint32()

        if (self.flags2 & 0x20000) != 0:
            self.value2 = br.read_uint32()

        if (self.flags1 & 4) != 0:
            self.Param1 = br.read_str(br.read_uint32())
            self.Param2 = br.read_str(br.read_uint32())

        self.unk2 = br.read_uint32()

        if (self.flags1 & 0x40) != 0:
            self.unk2 = br.read_uint32()

        if (self.flags1 & 1) != 0:
            self.MeshType = br.read_uint32()

        if (self.flags1 & 2) != 0:
            self.Param1 = br.read_str(br.read_uint32())
            self.Transformer1 = br.read_struct(zwoTransformer)

        if (self.flags1 & 0x20) != 0:
            self.unk5 = br.read_uint32()


