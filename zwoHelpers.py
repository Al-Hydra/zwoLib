from PyBinaryReader.binary_reader import *

def zwoVector(br: BinaryReader):
    return br.read_float(3)

def zwoQuaternion(br: BinaryReader):
    return br.read_float(4)

def zwoMatrix(br: BinaryReader):
    return [br.read_float(4), br.read_float(4), br.read_float(4), br.read_float(4)]   

class zwoOBB(BrStruct):
    def __init__(self):
        self.unk1 = 0
        self.unk2 = 0
        self.unk3 = 0
        self.Center = None
        self.Extents = None
        self.Orientation = None
    def __br_read__(self, br: BinaryReader):
        self.unk1 = br.read_uint32()
        self.unk2 = br.read_uint32()
        self.unk3 = br.read_uint32()

        self.Center = zwoVector(br)
        self.Extents = zwoVector(br)
        self.Orientation = zwoVector(br)

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

