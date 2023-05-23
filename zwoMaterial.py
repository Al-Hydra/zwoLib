from PyBinaryReader.binary_reader import *
from zwoEntity import zwoEntity
from zwoTypes import zwoTypes


class zwoMaterial(BrStruct):
    def __init__(self) -> None:
        self.Type = zwoTypes.Material
        self.Name = ""


    def __br_read__(self, br: BinaryReader, *args) -> None:
        self.FileSize = br.read_uint32()
        self.Flag = br.read_uint8()
        if (self.Flag - 2) < 2:
            nameLength = br.read_uint32()
            if nameLength > 0:
                self.Name = br.read_str(nameLength)
            else:
                self.Name = ""

            self.vector1 = br.read_float(3)
            self.vector2 = br.read_float(3)
            self.vector3 = br.read_float(3)

            self.unk1 = br.read_float()
            self.unk2 = br.read_float()
            self.unk3 = br.read_float()
            self.unk4 = br.read_float()
            self.unk5 = br.read_float()

            self.vector4 = br.read_float(3)

            self.unkint1 = br.read_uint32()
            self.unkint2 = br.read_uint32()

            self.ScaleUV = br.read_float(3)

            self.MoveUV = br.read_float(3)

            self.RotateUV = br.read_float(3)

            self.unkint3 = br.read_uint32()

            self.TextureName = br.read_str(br.read_uint32())
            self.TextureName2 = br.read_str(br.read_uint32())

            if self.Flag == 0x03:
                self.unk15 = br.read_uint32()
                self.unk16 = br.read_uint32()

                if (self.unk16 & 1) == 1:
                    self.UnkString = br.read_str(br.read_uint32())

                if (self.unk16 & 2) == 2:
                    self.unk17 = br.read_float()
                    self.unk18 = br.read_uint32()
    
    def __br_write__(self, br: BinaryReader):

        bw = BinaryReader(bytearray(), Endian.BIG)
        bw.write_uint8(self.Flag)
        bw.write_uint32(len(self.Name))
        bw.write_str(self.Name)
        bw.write_float(self.vector1)
        bw.write_float(self.vector2)
        bw.write_float(self.vector3)
        bw.write_float((0)*5)
        bw.write_float(self.vector4)
        bw.write_uint32(self.unkint1)
        bw.write_uint32(self.unkint2)

        bw.write_float(self.ScaleUV)
        bw.write_float(self.MoveUV)
        bw.write_float(self.RotateUV)

        bw.write_uint32(self.unkint3)

        bw.write_uint32(len(self.TextureName))
        bw.write_str(self.TextureName)
        bw.write_uint32(len(self.TextureName2))
        bw.write_str(self.TextureName2)

        if self.Flag == 0x03:
            bw.write_uint32(self.unk15)
            bw.write_uint32(self.unk16)

            if (self.unk16 & 1) == 1:
                bw.write_uint32(len(self.UnkString))
                bw.write_str(self.UnkString)

            if (self.unk16 & 2) == 2:
                bw.write_float(self.unk17)
                bw.write_uint32(self.unk18)

        self.FileSize = len(bw.data)
        br.write_uint32(self.FileSize)
        br.write_bytes(bw.data)