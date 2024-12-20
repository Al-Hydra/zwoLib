from .PyBinaryReader.binary_reader import *
from enum import Enum
from .zwo import *

def read_zwo(filepath):
    with open(filepath, 'rb') as f:
        filebytes = f.read()
    
    br = BinaryReader(filebytes, Endian.BIG, encoding='cp932')

    zwo: zwoFile = br.read_struct(zwoFile)
    return zwo
