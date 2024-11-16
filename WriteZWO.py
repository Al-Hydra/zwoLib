from .PyBinaryReader.binary_reader import *
from .zwo import *
from .zwoHelpers import *
from .zwoTypes import *
from .zwoEntity import *
from .zwoEntity3D import *
from .zwoMesh import *
from .zwoNode import *

def write_zwo(zwo: zwoFile, path):
    br = BinaryReader(encoding= "cp932", endianness= Endian.BIG)
    br.write_struct(zwo)
    with open(path, "wb") as f:
        f.write(br.buffer())
