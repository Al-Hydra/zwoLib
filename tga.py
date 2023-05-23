from PyBinaryReader.binary_reader import *
from enum import Enum
from PIL import Image
class TGA(BrStruct):
    def __init__(self):
        pass

    def __br_read__(self, br: BinaryReader):
        self.IdLength = br.read_uint8()
        self.ColorMapType = br.read_uint8()
        self.DataTypeCode = br.read_uint8()
        self.ColorMapOrigin = br.read_uint16()
        self.ColorMapLength = br.read_uint16()
        self.ColorMapDepth = br.read_uint8()
        self.x_Origin = br.read_uint16()
        self.y_Origin = br.read_uint16()
        self.Width = br.read_uint16()
        self.Height = br.read_uint16()
        self.BitsPerPixel = br.read_uint8()
        self.ImageDescriptor = br.read_uint8()
        self.ImageID = br.read_str(self.IdLength)
        self.ImageData = br.read_bytes(self.Width * self.Height * self.BitsPerPixel // 8)


class DataTypes(Enum):
    NO_IMAGE_DATA = 0
    UNCOMPRESSED_COLOR_MAPPED = 1
    UNCOMPRESSED_TRUE_COLOR = 2
    UNCOMPRESSED_BLACK_AND_WHITE = 3
    RUN_LENGTH_ENCODED_COLOR_MAPPED = 9
    RUN_LENGTH_ENCODED_TRUE_COLOR = 10
    RUN_LENGTH_ENCODED_BLACK_AND_WHITE = 11


def ARGB_to_RGBA(data: bytes) -> bytes:
    new_data = bytearray(data[::-1])
    for i in range(0, len(new_data), 4):
        a = new_data[i]
        r = new_data[i + 1]
        g = new_data[i + 2]
        b = new_data[i + 3]
        new_data[i] = r
        new_data[i + 1] = g
        new_data[i + 2] = b
        new_data[i + 3] = a

    
    return bytes(new_data)


if __name__ == "__main__":
    path = r"D:\SteamLibrary\steamapps\common\Obscure\data\_common\textures\b1bonus3.tga"
    with open(path, "rb") as f:
        filebytes = f.read()
    
    br = BinaryReader(filebytes, Endian.LITTLE, "cp932")
    tga = br.read_struct(TGA)
    print(tga.Width)

    img = Image.frombytes("RGBA", (tga.Height, tga.Width), ARGB_to_RGBA(tga.ImageData)).show()

