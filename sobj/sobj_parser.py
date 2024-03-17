import struct
import os
import json
import math
import logging
logger = logging.getLogger("mhworld_import")

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

    def readStringUTFAt(self, offset):
        previous_offset = self.tell()
        self.seek(offset)
        text = ""
        while True:
            char = self.readUShort()
            if char == 0:
                break
            else:
                text += chr(char)
        self.seek(previous_offset)
        return text

    def readStringUTF(self):
        text = ""
        while True:
            char = self.readUShort()
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

def euler_to_quaternion(euler):
    #print(euler)
    lacet = math.radians(euler[2])
    tangage = math.radians(euler[1])
    roulis = math.radians(euler[0])
    qx = math.sin(roulis/2) * math.cos(tangage/2) * math.cos(lacet/2) - math.cos(roulis/2) * math.sin(tangage/2) * math.sin(lacet/2)
    qy = math.cos(roulis/2) * math.sin(tangage/2) * math.cos(lacet/2) + math.sin(roulis/2) * math.cos(tangage/2) * math.sin(lacet/2)
    qz = math.cos(roulis/2) * math.cos(tangage/2) * math.sin(lacet/2) - math.sin(roulis/2) * math.sin(tangage/2) * math.cos(lacet/2)
    qw = math.cos(roulis/2) * math.cos(tangage/2) * math.cos(lacet/2) + math.sin(roulis/2) * math.sin(tangage/2) * math.sin(lacet/2)
    return [qx, qy, qz, qw]

class SobjParser():
    def __init__(self, path=None, data=None):
        self.path = path
        if data is None:
            with open(path, "rb") as file_in:
                data = file_in.read()
        self.bs = Reader(data)


    def read(self):
        _ = self.bs.readUInt()
        self.magic = self.bs.readUInt()

        if self.magic != 6451059:
            if self.path is not None:
                raise RuntimeError(str(self.path) + " is not a mhworld sobj file (magic = " + str(self.magic) + ")")
            else:
                raise RuntimeError("Data is not a mhworld sobj file (magic = " + str(self.magic) + ")")

        search_offset = 0
        object_offsets = []
        while True:
            object_offset = self.bs.data.find("FcAssetBasicSetObject".encode(), search_offset)
            if object_offset != -1:
                object_offsets.append(object_offset)
                search_offset = object_offset+1
            else:
                break

        object_instances = []
        for object_offset in object_offsets:
            object_instance = {}
            self.bs.seek(object_offset)
            _ = self.bs.readString()
            _ = self.bs.readUInt()
            object_instance["position"] = [self.bs.readFloat() for _ in range(3)]
            object_instance["rotation"] = euler_to_quaternion([self.bs.readFloat() for _ in range(3)])
            object_instance["scale"] = [self.bs.readFloat() for _ in range(3)]
            object_instance["name"] = self.bs.readString()
            object_instance["zone"] = "UNKNOWN"

            self.bs.readUInt()
            self.bs.readUInt()
            nu = self.bs.readUInt()
            self.bs.readFloat()
            #print(self.bs.readUInt())
                #print(self.bs.readUInt())
                #print(self.bs.readUInt())
                #print(self.bs.readUInt())
                #print(self.bs.readUInt())
                #print(self.bs.readUInt())
            object_instances.append(object_instance)
        return object_instances

if __name__ == "__main__":
    from glob import glob
    sobjs = glob("/mnt/Windows_heavy/GAMES/WORLD/EXTRACT_0/chunkG0/stage/st101/common/set/*.sobj")
    for sobj in sobjs:
        parser = SobjParser(path=sobj)
        data = parser.read()
    #import json
    #print(json.dumps(data, indent=4))
