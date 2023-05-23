from PyBinaryReader.binary_reader import *
from dds import DDS, DDS_Header, DDS_PixelFormat
from brDDS import BrDDS
from bmp import BMP, bmpHeader, bmpDIBHeader
from enum import Enum
import sys
import os

def read_dic(filepath):
    with open(filepath, 'rb') as f:
        filebytes = f.read()
    
    br = BinaryReader(filebytes, Endian.BIG, encoding='cp932')

    dic = dicFile()
    dic.TexturesCount = br.read_uint32()
    for i in range(dic.TexturesCount):
        texture = dicTexture()
        br.seek(4, 1)
        NameLength = br.read_uint32()
        texture.Name = br.read_str(NameLength)
        texture.MipmapsCount = br.read_uint32()
        texture.AlphaFlag = br.read_uint32()
        texture.OneBitAlphaFlag = br.read_uint32()
        texture.Width = br.read_uint32()
        texture.Height = br.read_uint32()
        texture.Format = TextureFormats(br.read_uint32())
        for i in range(texture.MipmapsCount):
            mipmapSize = br.read_uint32()
            texture.Mipmaps.append(br.read_bytes(mipmapSize))
        
        texture.Data = texture.Mipmaps[0]
        dic.Textures.append(texture)

    return dic
    

class dicFile:
    def __init__(self):
        self.TexturesCount = 0
        self.Textures = []

class dicTexture:
    def __init__(self):
        self.Name = ""
        self.Width = 0
        self.Height = 0
        self.Format = 0
        self.AlphaFlag = 0
        self.OneBitAlphaFlag = 0
        self.MipmapsCount = 0
        self.Mipmaps = []
        self.Data = None

class TextureFormats(Enum):
    R8G8B8A8 = 0x15
    R5G6B5 = 0x17
    R5G5B5A1 = 0x19

BitMasks = {
    TextureFormats.R8G8B8A8: [0x00ff0000, 0x0000ff00, 0x000000ff, 0xff000000],
    TextureFormats.R5G6B5: [0x0000f800, 0x000007e0, 0x0000001f, 0x00000000],
    TextureFormats.R5G5B5A1: [0x00007c00, 0x000003e0, 0x0000001f, 0x00008000]
}

BitCount = {
    TextureFormats.R8G8B8A8: 32,
    TextureFormats.R5G6B5: 16,
    TextureFormats.R5G5B5A1: 16
}

def dic2dds(dic: dicTexture):
    dds = DDS()
    dds.magic = 'DDS '
    header = dds.header = DDS_Header()
    header.pixel_format = DDS_PixelFormat()
    header.size = 124
    # DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT
    header.flags = 0x1 | 0x2 | 0x4 | 0x1000

    header.width = dic.Width
    header.height = dic.Height
    header.mipMapCount = dic.MipmapsCount

    # check dic format
    header.flags |= 0x8  # DDSD_PITCH
    header.pitchOrLinearSize = dic.Width * BitCount[dic.Format]
    header.pixel_format.fourCC = None
    header.pixel_format.rgbBitCount = BitCount[dic.Format]
    header.pixel_format.bitmasks = BitMasks[dic.Format]
    header.pixel_format.flags = 0x40 # DDPF_RGB
    if dic.AlphaFlag:
        header.pixel_format.flags |= 0x01 #DDPF_ALPHAPIXELS
    
    dds.mipmaps = dic.Mipmaps

    dds.texture_data = dic.Data

    header.pixel_format.size = 32
    if header.mipMapCount > 1:
        header.flags |= 0x20000  # DDSD_MIPMAPCOUNT
        header.caps1 = 0x8 | 0x1000 | 0x400000
    else:
        header.caps1 = 0x8
    
    header.depth = 1
    header.reserved = [0] * 11
    header.caps2 = 0
    header.caps3 = 0
    header.caps4 = 0
    header.reserved2 = 0

    br = BinaryReader(endianness=Endian.LITTLE)
    br.write_struct(BrDDS(), dds)
    return br.buffer()


def dic2ddso(dic: dicTexture):
    dds = DDS()
    dds.magic = 'DDS '
    header = dds.header = DDS_Header()
    header.pixel_format = DDS_PixelFormat()
    header.size = 124
    # DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT
    header.flags = 0x1 | 0x2 | 0x4 | 0x1000

    header.width = dic.Width
    header.height = dic.Height
    header.mipMapCount = dic.MipmapsCount

    # check dic format
    header.flags |= 0x8  # DDSD_PITCH
    header.pitchOrLinearSize = dic.Width * BitCount[dic.Format]
    header.pixel_format.fourCC = None
    header.pixel_format.rgbBitCount = BitCount[dic.Format]
    header.pixel_format.bitmasks = BitMasks[dic.Format]
    header.pixel_format.flags = 0x40 # DDPF_RGB
    if dic.AlphaFlag:
        header.pixel_format.flags |= 0x01 #DDPF_ALPHAPIXELS
    
    dds.mipmaps = dic.Mipmaps

    dds.texture_data = dic.Data

    header.pixel_format.size = 32
    if header.mipMapCount > 1:
        header.flags |= 0x20000  # DDSD_MIPMAPCOUNT
        header.caps1 = 0x8 | 0x1000 | 0x400000
    else:
        header.caps1 = 0x8
    
    header.depth = 1
    header.reserved = [0] * 11
    header.caps2 = 0
    header.caps3 = 0
    header.caps4 = 0
    header.reserved2 = 0

    return dds


def rgb565_to_rgb888(data, order = "BGR"):
    pixels = []
    if order == "BGR":
        for i in range(0, len(data), 2):
            b = data[i] & 0x1f
            g = ((data[i] & 0xe0) >> 5) | ((data[i + 1] & 0x07) << 3)
            r = (data[i + 1] & 0xf8) >> 3
            pixels.append((r, g, b))
    elif order == "RGB":
        for i in range(0, len(data), 2):
            r = data[i] & 0x1f
            g = ((data[i] & 0xe0) >> 5) | ((data[i + 1] & 0x07) << 3)
            b = (data[i + 1] & 0xf8) >> 3
            pixels.append((r, g, b))
    return pixels


def dic2dds_file(dic: dicTexture, filepath):
    dds = dic2dds(dic)
    name = dic.Name
    
    #check if folder exists
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    
    path = os.path.join(filepath, name + ".dds")

    with open(path, 'wb') as f:
        f.write(dds)


def dic2bmp(dic: dicTexture):
    bmp = BMP()

    bmp.Header.FileSize = 0
    bmp.Header.Reserved1 = 0
    bmp.Header.Reserved2 = 0
    bmp.Header.OffsetToPixelData = 0x36

    bmp.DIBHeader.Size = 0x28
    bmp.DIBHeader.Width = dic.Width
    bmp.DIBHeader.Height = dic.Height
    bmp.DIBHeader.Planes = 1
    bmp.DIBHeader.BitCount = BitCount[dic.Format]
    bmp.DIBHeader.Compression = 0
    bmp.DIBHeader.ImageSize = 0
    bmp.DIBHeader.XPelsPerMeter = 0
    bmp.DIBHeader.YPelsPerMeter = 0
    bmp.DIBHeader.ColorsUsed = 0
    bmp.DIBHeader.ColorsImportant = 0

    bmp.PixelData = dic.Data



if __name__ == "__main__":
    '''if len(sys.argv) > 1:
        dicfile = sys.argv[1]
        dumpfolder = os.path.dirname(dicfile)
        folder = dicfile.split("\\")[-1].split(".")[0]
        dic = read_dic(dicfile)
        for texture in dic.Textures:
            dic2dds_file(texture, f"{dumpfolder}\\{folder}")
            print(f"{texture.Name} {TextureFormats(texture.Format).name} {texture.Width}x{texture.Height}")
        
        print(f"textures were saved in {dumpfolder}\\{folder}")
        input("Press enter to exit...")'''
    
    from time import perf_counter

    start = perf_counter()
    dicfile = r"D:\Games\Obscure 2\adatapack\texpc_pc.dic"

    dic = read_dic(dicfile)

    print(f"dic with {dic.TexturesCount} textures read in {perf_counter() - start} seconds")

    #use multiprocessing to export textures
    from multiprocessing import Pool
    from functools import partial


    start = perf_counter()

    for texture in dic.Textures:
        dic2dds_file(texture, r"D:\Games\Obscure 2\adatapack\textures")

    print(f"dic with {dic.TexturesCount} textures exported in {perf_counter() - start} seconds Using single process")


    from concurrent.futures import ThreadPoolExecutor, as_completed

    start = perf_counter()

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(dic2dds_file, texture, r"D:\Games\Obscure 2\adatapack\textures") for texture in dic.Textures]
        for future in as_completed(futures):
            future.result()

    print(f"dic with {dic.TexturesCount} textures exported in {perf_counter() - start} seconds Using multithreading")

    
    start = perf_counter()
    with Pool() as p:
        p.map(partial(dic2dds_file, filepath=r"D:\Games\Obscure 2\adatapack\textures"), dic.Textures)
    
    print(f"dic with {dic.TexturesCount} textures exported in {perf_counter() - start} seconds Using multiprocessing")
    
    