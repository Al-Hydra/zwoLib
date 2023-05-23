from PyBinaryReader.binary_reader import *
from zwoHelpers import zwoVector
from zwoTypes import zwoTypes
class zwoCamera(BrStruct):
    def __init__(self):
        self.Type = zwoTypes.Camera
        self.Size = 0
        self.Flag = 0
        self.Name = ""
        self.unk1 = 0
        self.unk2 = 0
        self.unkf1 = 0
        self.unkf2 = 0
        self.vec1 = (0, 0, 0)
        self.vec2 = (0, 0, 0)
        self.vec3 = (0, 0, 0)
        self.vec4 = (0, 0, 0)

    def __br_read__(self, br: BinaryReader):
        self.Size = br.read_uint32()
        self.Flag = br.read_uint8()

        if (self.Flag -2 ) < 2:
            self.Name = br.read_str(br.read_uint32())

            if self.Flag == 0x3:
                self.unk1 = br.read_int32()
                self.unk2 = br.read_int32()
            
            self.unkf1 = br.read_float()
            self.unkf2 = br.read_float()

            self.vec1 = zwoVector(br)
            self.vec2 = zwoVector(br)
            self.vec3 = zwoVector(br)
            self.vec4 = zwoVector(br)
