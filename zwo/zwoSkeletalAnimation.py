from ..utils.PyBinaryReader.binary_reader import *
from .zwoEntity import zwoEntity
from .zwoEntity3D import zwoEntity3D
from .zwoTypes import zwoTypes
from .zwoHelpers import zwoVector, zwoQuaternion



class zwoSkeletalAnimation(BrStruct):
    def __init__(self) -> None:
        self.Type = zwoTypes.SkeletalAnimation

    def __br_read__(self, br: BinaryReader, *args) -> None:
        
        self.Entity = br.read_struct(zwoEntity)
        self.Entity2 = br.read_struct(zwoEntity)

        self.Flags = br.read_uint32()
        flag1 = self.Flags >> 1 & 1
        flag2 = self.Flags >> 2 & 1

        self.EntryCount = br.read_uint32()
        self.FrameCount = br.read_uint32()
        self.FrameCountMultiplied = br.read_uint32()
        self.FrameRate = br.read_uint32()

        if flag1 == 0:
            br.set_endian(Endian.LITTLE)
            self.Entries = [br.read_struct(Entry) for i in range(self.EntryCount)]
        else:
            br.read_bytes(14 * 4)
        
        br.set_endian(Endian.BIG)

        self.CurveCount = br.read_uint32()

        br.set_endian(Endian.LITTLE)
        self.Curves = [zwoQuaternion(br) for i in range(self.CurveCount)]

        br.set_endian(Endian.BIG)

        if self.Flags & 1:
            self.Transformer1Curve = (zwoVector(br), zwoVector(br), zwoQuaternion(br))

        if self.Flags & 4:
            self.Transformer2Curve = (zwoVector(br), zwoVector(br), zwoQuaternion(br))

class Entry(BrStruct):
    def __br_read__(self, br: BinaryReader, *args) -> None:
        
        self.EntryTypeFlag = br.read_uint32()
        self.CurveStartIndex = br.read_uint32()
        self.CurvesPerFrame = br.read_uint32()