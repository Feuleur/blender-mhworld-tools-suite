import struct
import codecs
import numpy as np
import ctypes
#import addon_utils
import os
import sys 
import logging
logger = logging.getLogger("mhworld_import")

shared_library_path = None
shared_library_filename = "read_dxgi_format.so"
if sys.platform == "linux" or sys.platform == "linux2":
    shared_library_filename = "read_dxgi_format.so"
elif sys.platform == "win32":
    shared_library_filename = "read_dxgi_format.dll"
    
#for mod in addon_utils.modules():
    #if mod.bl_info.get("name") == "MHRise tool suite":
        #shared_library_path = os.path.join(os.path.dirname(os.path.abspath(mod.__file__)), "tex", shared_library_filename)
        #break
shared_library_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), shared_library_filename)

lib = ctypes.cdll.LoadLibrary(shared_library_path)
lib.read_bc1.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
lib.read_bc1.restype = ctypes.c_int

lib.read_bc3.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
lib.read_bc3.restype = ctypes.c_int

lib.read_bc4.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
lib.read_bc4.restype = ctypes.c_int

lib.read_bc5.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
lib.read_bc5.restype = ctypes.c_int

lib.read_bc7.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
lib.read_bc7.restype = ctypes.c_int

lib.read_r8.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
lib.read_r8.restype = ctypes.c_int

lib.read_r8g8.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
lib.read_r8g8.restype = ctypes.c_int

lib.read_r8g8b8a8.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
lib.read_r8g8b8a8.restype = ctypes.c_int


DXGI_FORMAT = {
    1:"VECTOR_F32",
    2:"VECTOR_F16",
    7:"R8G8B8A8_UNORM",
    9:"R8G8B8A8_UNORM_SRGB",
    22:"BC1_UNORM",
    23:"BC1_UNORM_SRGB",
    24:"BC4_UNORM",
    25:"BC4_UNORM_SRGB",
    26:"BC5_UNORM",
    27:"BC5_UNORM_SRGB",
    28:"BC6H_UF16",
    29:"BC6H_SF16",
    30:"BC7_UNORM", 
    31:"BC7_UNORM_SRGB"
}
#DXT1 23
#DXT3 24
#DXT5 25
#DXT2 26
#DXT4 27
#BC4U 28
#BC4S 29
#BC5U 30
#BC5S 31
#ATI1 32
#ATI2 33
#RGBG 34
#GRGB 35
#YUY2 36
#UYVY 37

#DXGI_FORMAT = {
    #0: "UNKNOWN",
    #1: "R32G32B32A32_TYPELESS",
    #2: "R32G32B32A32_FLOAT",
    #3: "R32G32B32A32_UINT",
    #4: "R32G32B32A32_SINT",
    #5: "R32G32B32_TYPELESS",
    #6: "R32G32B32_FLOAT",
    #7: "R32G32B32_UINT",
    #8: "R32G32B32_SINT",
    #9: "R16G16B16A16_TYPELESS",
    #10: "R16G16B16A16_FLOAT",
    #11: "R16G16B16A16_UNORM",
    #12: "R16G16B16A16_UINT",
    #13: "R16G16B16A16_SNORM",
    #14: "R16G16B16A16_SINT",
    #15: "R32G32_TYPELESS",
    #16: "R32G32_FLOAT",
    #17: "R32G32_UINT",
    #18: "R32G32_SINT",
    #19: "R32G8X24_TYPELESS",
    #20: "D32_FLOAT_S8X24_UINT",
    #21: "R32_FLOAT_X8X24_TYPELESS",
    #22: "X32_TYPELESS_G8X24_UINT",
    #23: "R10G10B10A2_TYPELESS",
    #24: "R10G10B10A2_UNORM",
    #25: "R10G10B10A2_UINT",
    #26: "R11G11B10_FLOAT",
    #27: "R8G8B8A8_TYPELESS",
    #28: "R8G8B8A8_UNORM",
    #29: "R8G8B8A8_UNORM_SRGB",
    #30: "R8G8B8A8_UINT",
    #31: "R8G8B8A8_SNORM",
    #32: "R8G8B8A8_SINT",
    #33: "R16G16_TYPELESS",
    #34: "R16G16_FLOAT",
    #35: "R16G16_UNORM",
    #36: "R16G16_UINT",
    #37: "R16G16_SNORM",
    #38: "R16G16_SINT",
    #39: "R32_TYPELESS",
    #40: "D32_FLOAT",
    #41: "R32_FLOAT",
    #42: "R32_UINT",
    #43: "R32_SINT",
    #44: "R24G8_TYPELESS",
    #45: "D24_UNORM_S8_UINT",
    #46: "R24_UNORM_X8_TYPELESS",
    #47: "X24_TYPELESS_G8_UINT",
    #48: "R8G8_TYPELESS",
    #49: "R8G8_UNORM",
    #50: "R8G8_UINT",
    #51: "R8G8_SNORM",
    #52: "R8G8_SINT",
    #53: "R16_TYPELESS",
    #54: "R16_FLOAT",
    #55: "D16_UNORM",
    #56: "R16_UNORM",
    #57: "R16_UINT",
    #58: "R16_SNORM",
    #59: "R16_SINT",
    #60: "R8_TYPELESS",
    #61: "R8_UNORM",
    #62: "R8_UINT",
    #63: "R8_SNORM",
    #64: "R8_SINT",
    #65: "A8_UNORM",
    #66: "R1_UNORM",
    #67: "R9G9B9E5_SHAREDEXP",
    #68: "R8G8_B8G8_UNORM",
    #69: "G8R8_G8B8_UNORM",
    #70: "BC1_TYPELESS",
    #71: "BC1_UNORM",
    #72: "BC1_UNORM_SRGB",
    #73: "BC2_TYPELESS",
    #74: "BC2_UNORM",
    #75: "BC2_UNORM_SRGB",
    #76: "BC3_TYPELESS",
    #77: "BC3_UNORM",
    #78: "BC3_UNORM_SRGB",
    #79: "BC4_TYPELESS",
    #80: "BC4_UNORM",
    #81: "BC4_SNORM",
    #82: "BC5_TYPELESS",
    #83: "BC5_UNORM",
    #84: "BC5_SNORM",
    #85: "B5G6R5_UNORM",
    #86: "B5G5R5A1_UNORM",
    #87: "B8G8R8A8_UNORM",
    #88: "B8G8R8X8_UNORM",
    #89: "R10G10B10_XR_BIAS_A2_UNORM",
    #90: "B8G8R8A8_TYPELESS",
    #91: "B8G8R8A8_UNORM_SRGB",
    #92: "B8G8R8X8_TYPELESS",
    #93: "B8G8R8X8_UNORM_SRGB",
    #94: "BC6H_TYPELESS",
    #95: "BC6H_UF16",
    #96: "BC6H_SF16",
    #97: "BC7_TYPELESS",
    #98: "BC7_UNORM",
    #99: "BC7_UNORM_SRGB",
    #100: "AYUV",
    #101: "Y410",
    #102: "Y416",
    #103: "NV12",
    #104: "P010",
    #105: "P016",
    #106: "_420_OPAQUE",
    #107: "YUY2",
    #108: "Y210",
    #109: "Y216",
    #110: "NV11",
    #111: "AI44",
    #112: "IA44",
    #113: "P8",
    #114: "A8P8",
    #115: "B4G4R4A4_UNORM",
    #130: "P208",
    #131: "V208",
    #132: "V408",
    #0xffffffff:  "FORCE_UINT"
#}

class Reader():
    def __init__(self, data):
        self.offset = 0
        self.data = data
    
    def read(self, kind, size):
        result = struct.unpack(kind, self.data[self.offset:self.offset+size])[0]
        self.offset += size
        return result

    def seek(self, offset, start = None):
        if start is None:
            self.offset = offset
        else:
            self.offset += offset

    def readUInt(self):
        return self.read("I", 4)
    
    def readInt(self):
        return self.read("i", 4)
        
    def readUInt64(self):
        return self.read("Q", 8)
    
    def readHalf(self):
        return self.read("e", 2)

    def readFloat(self):
        return self.read("f", 4)

    def readShort(self):
        return self.read("h", 2)
    
    def readUShort(self):
        return self.read("H", 2)

    def readByte(self):
        return self.read("b", 1)
    
    def readBytes(self, size):
        return self.data[self.offset:self.offset + size]
    
    def readUByte(self):
        return self.read("B", 1)

    def readString(self):
        text = ""
        while True:
            char = self.readUByte()
            if char == 0:
                break
            else:
                text += chr(char)
        return text

    def allign(self, size):
        self.offset = (int((self.offset)/size)*size)+size
        
    def tell(self):
        return self.offset
    
    def getSize(self):
        return len(self.data)

class TexParser():
    def __init__(self, path=None, data=None):
        self.path = path
        if data is None:
            with open(path, "rb") as file_in:
                data = file_in.read()
        self.bs = Reader(data)
        magic = self.bs.readUInt()
        if magic != 5784916:
            raise RuntimeError(str(self.path) + " is not a tex file (magic = " + str(magic) + ")")
        _ = self.bs.readUInt()
        nu = self.bs.readUInt()
        nu = self.bs.readUInt()
        _ = self.bs.readUInt()
        self.mipCount = self.bs.readUInt()
        self.width = self.bs.readUInt()
        self.height = self.bs.readUInt()
        _ = self.bs.readUInt()
        self.format = self.bs.readUInt()
        _ = self.bs.readUInt()
        nu = self.bs.readUInt()

        nu = self.bs.readUInt()
        nu = self.bs.readUInt()
        ff = self.bs.readUInt()
        nu = self.bs.readUInt()

        nu = self.bs.readUInt()
        _ = self.bs.readUInt()
        nu = self.bs.readUInt()
        nu = self.bs.readUInt()

        nu = self.bs.readUInt64()
        ff = self.bs.readUInt64()

        ff = self.bs.readUInt64()
        ff = self.bs.readUInt64()

        ff = self.bs.readUInt64()
        _ = self.bs.readUInt64()

        _ = self.bs.readUInt64()
        _ = self.bs.readUInt64()

        _ = self.bs.readUInt64()
        nu = self.bs.readUInt64()

        nu = self.bs.readUInt64()
        nu = self.bs.readUInt64()

        nu = self.bs.readUInt64()
        self.mipOffsets = []
        for _ in range(self.mipCount):
            self.mipOffsets.append(self.bs.readUInt64())

        #unk00 = self.bs.readUShort()
        #self.numImages = self.bs.readUByte()
        #oneImgMipHdrSize = self.bs.readUByte()
        #self.mipCount = int(oneImgMipHdrSize / 16)
        #self.format = self.bs.readUInt()
        if self.format in DXGI_FORMAT.keys():
            self.DXGI_format = DXGI_FORMAT[self.format]
        else:
            raise RuntimeError("Unknown format (DXGI indice: " + str(self.format) + ")")
        #unk02 = self.bs.readUInt()
        #unk03 = self.bs.readUInt()
        #unk04 = self.bs.readUInt()
        
        #self.bs.seek(8,1)
        #self.mipData = []
        #for i in range(self.numImages):
            #mipDataImg = []
            #for j in range(self.mipCount):
                #mipDataImg.append([self.bs.readUInt64(), self.bs.readUInt(), self.bs.readUInt()]) #[0]offset, [1]pitch, [2]size
            #self.mipData.append(mipDataImg)

    def read_BC1(self, texData, mipWidth, mipHeight, format):
        img_array = np.empty([mipHeight, mipWidth, 4], dtype=np.uint8)
        ret = lib.read_bc1(
            np.frombuffer(texData, np.uint8).ctypes.data_as(ctypes.c_void_p), 
            img_array.ctypes.data_as(ctypes.c_void_p), 
            mipWidth, 
            mipHeight
        )
        return img_array
    
    def read_BC3(self, texData, mipWidth, mipHeight, format):
        img_array = np.empty([mipHeight, mipWidth, 4], dtype=np.uint8)
        ret = lib.read_bc3(
            np.frombuffer(texData, np.uint8).ctypes.data_as(ctypes.c_void_p),
            img_array.ctypes.data_as(ctypes.c_void_p),
            mipWidth,
            mipHeight
        )
        return img_array

    def read_BC4(self, texData, mipWidth, mipHeight, format):
        img_array = np.empty([mipHeight, mipWidth, 4], dtype=np.uint8)
        ret = lib.read_bc4(
            np.frombuffer(texData, np.uint8).ctypes.data_as(ctypes.c_void_p), 
            img_array.ctypes.data_as(ctypes.c_void_p), 
            mipWidth, 
            mipHeight
        )
        return img_array
    
    def read_BC5(self, texData, mipWidth, mipHeight, format):
        img_array = np.empty([mipHeight, mipWidth, 4], dtype=np.uint8)
        ret = lib.read_bc5(
            np.frombuffer(texData, np.uint8).ctypes.data_as(ctypes.c_void_p), 
            img_array.ctypes.data_as(ctypes.c_void_p), 
            mipWidth, 
            mipHeight
        )
        return img_array
    
    def read_BC7(self, texData, mipWidth, mipHeight, format):
        img_array = np.empty([mipHeight, mipWidth, 4], dtype=np.uint8)
        ret = lib.read_bc7(
            np.frombuffer(texData, np.uint8).ctypes.data_as(ctypes.c_void_p), 
            img_array.ctypes.data_as(ctypes.c_void_p), 
            mipWidth, 
            mipHeight
        )
        return img_array

    def read_R8(self, texData, mipWidth, mipHeight, format):
        img_array = np.empty([mipHeight, mipWidth, 4], dtype=np.uint8)
        ret = lib.read_r8(
            np.frombuffer(texData, np.uint8).ctypes.data_as(ctypes.c_void_p), 
            img_array.ctypes.data_as(ctypes.c_void_p), 
            mipWidth, 
            mipHeight
        )
        return img_array
    
    def read_R8G8(self, texData, mipWidth, mipHeight, format):
        img_array = np.empty([mipHeight, mipWidth, 4], dtype=np.uint8)
        ret = lib.read_r8g8(
            np.frombuffer(texData, np.uint8).ctypes.data_as(ctypes.c_void_p), 
            img_array.ctypes.data_as(ctypes.c_void_p), 
            mipWidth, 
            mipHeight
        )
        return img_array

    def read_R8G8B8A8(self, texData, mipWidth, mipHeight, format):
        img_array = np.empty([mipHeight, mipWidth, 4], dtype=np.uint8)
        ret = lib.read_r8g8b8a8(
            np.frombuffer(texData, np.uint8).ctypes.data_as(ctypes.c_void_p), 
            img_array.ctypes.data_as(ctypes.c_void_p), 
            mipWidth, 
            mipHeight
        )
        return img_array

    def read_F32F32F32F32(self, texData, mipWidth, mipHeight, format):
        img_array = np.frombuffer(texData, dtype=np.float32)
        return img_array.reshape([mipHeight, mipWidth, 4])

    def read_F16F16F16F16(self, texData, mipWidth, mipHeight, format):
        img_array = np.frombuffer(texData, dtype=np.float16)
        return img_array.reshape([mipHeight, mipWidth, 4])
    
    def read(self, mipLevel=0):
        img_array = np.ones([4, 4, 4], dtype=np.uint8)*255
        could_read = False
        mipWidth = self.width//(2**mipLevel)
        mipHeight = self.height//(2**mipLevel)
        self.bs.seek(self.mipOffsets[mipLevel])

        texData = self.bs.data[self.bs.offset:]
        could_read = True

        if DXGI_FORMAT[self.format] in ["BC1_TYPELESS", "BC1_UNORM", "BC1_UNORM_SRGB"]:
            img_array = self.read_BC1(texData, mipWidth, mipHeight, self.format)
        elif DXGI_FORMAT[self.format] in ["BC3_TYPELESS", "BC3_UNORM", "BC3_UNORM_SRGB"]:
            img_array = self.read_BC3(texData, mipWidth, mipHeight, self.format)
        elif DXGI_FORMAT[self.format] in ["BC4_TYPELESS", "BC4_UNORM", "BC4_SNORM"]:
            img_array = self.read_BC4(texData, mipWidth, mipHeight, self.format)
        elif DXGI_FORMAT[self.format] in ["BC5_TYPELESS", "BC5_UNORM", "BC5_SNORM"]:
            img_array = self.read_BC5(texData, mipWidth, mipHeight, self.format)
        #elif DXGI_FORMAT[format] in ["BC6H_TYPELESS", "BC6H_UF16", "BC6H_SF16"]:
            # fuck that, bc7 was hard enough
        elif DXGI_FORMAT[self.format] in ["BC7_TYPELESS", "BC7_UNORM", "BC7_UNORM_SRGB"]:
            img_array = self.read_BC7(texData, mipWidth, mipHeight, self.format)
        elif DXGI_FORMAT[self.format] in ["R8_SINT", "R8_UNORM", "R8_SNORM", "R8_TYPELESS"]:
            img_array = self.read_R8(texData, mipWidth, mipHeight, self.format)
        elif DXGI_FORMAT[self.format] in ["R8G8_SINT", "R8G8_UNORM", "R8G8_SNORM", "R8G8_TYPELESS", "R8G8_UINT"]:
            img_array = self.read_R8G8(texData, mipWidth, mipHeight, self.format)
        elif DXGI_FORMAT[self.format] in ["R8G8B8A8_SINT", "R8G8B8A8_SNORM", "R8G8B8A8_TYPELESS", "R8G8B8A8_UINT", "R8G8B8A8_UNORM", "R8G8B8A8_UNORM_SRGB"]:
            img_array = self.read_R8G8B8A8(texData, mipWidth, mipHeight, self.format)
        elif DXGI_FORMAT[self.format] in ["VECTOR_F32"]:
            img_array = self.read_F32F32F32F32(texData, mipWidth, mipHeight, self.format)
        elif DXGI_FORMAT[self.format] in ["VECTOR_F16"]:
            img_array = self.read_F16F16F16F16(texData, mipWidth, mipHeight, self.format)
        else:
            could_read = False
        return img_array, could_read

if __name__ == "__main__":
    import cv2
    parser = TexParser("./ems001_00_01_BML.tex")
    data = parser.read()
    #print()
    cv2.imwrite("test.png", data[0])
    #print(data)
