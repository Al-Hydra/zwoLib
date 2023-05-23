from PyBinaryReader.binary_reader import *

class zwoEntity(BrStruct):
    def __init__(self):
        self.Size = 0
        self.HeaderType = 0
        self.Name = None
        self.Type = 0
        self.unk2 = 0
        self.unk3 = 0
        self.unk4 = 0
        self.unk5 = 0
        self.unk6 = 0
        
    def __br_read__(self, br: BinaryReader):
        self.Size = br.read_uint32()
        if self.Size != 0:
            self.HeaderType = br.read_uint8()
            if self.HeaderType == 0:
                print("***INVALID HEADER***\n Header Type Can't be 0\n")
            if self.HeaderType == 5:
                self.Name = br.read_str(br.read_uint32())
                self.Type = br.read_uint32()
            if self.HeaderType == 6:
                self.Name = br.read_str(br.read_uint32())
                self.Type = br.read_uint32()
                self.unk2 = br.read_uint32()
                self.unk3 = br.read_uint32()
                self.unk4 = br.read_uint32()
                self.unk5 = br.read_uint32()
                self.unk6 = br.read_uint32()
    
    def __br_write__(self, br: BinaryReader):
        pass
