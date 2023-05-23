from PyBinaryReader.binary_reader import *
from enum import Enum
from zwo import *
def read_zwo(filepath):
    with open(filepath, 'rb') as f:
        filebytes = f.read()
    
    br = BinaryReader(filebytes, Endian.BIG, encoding='cp932')

    zwo: zwoFile = br.read_struct(zwoFile)
    return zwo


if __name__ == '__main__':
    zwo = read_zwo(r"D:\SteamLibrary\steamapps\common\Obscure\data\_common\players\boy2\skin\boy2hi.zwo")
    for chunk in zwo.Entities:
        print(zwoTypes(chunk.Type))