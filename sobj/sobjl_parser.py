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


class SobjlParser():
    def __init__(self, path=None, data=None):
        self.path = path
        if data is None:
            with open(path, "rb") as file_in:
                data = file_in.read()
        self.bs = Reader(data)


    def read(self):

        self.magic = self.bs.readUInt()
        self.version = self.bs.readUInt()
        if self.magic != 403247105:
            if self.path is not None:
                raise RuntimeError(str(self.path) + " is not a mhworld sobjl file (magic = " + str(self.magic) + ")")
            else:
                raise RuntimeError("Data is not a mhworld sobjl file (magic = " + str(self.magic) + ")")

        entry_count = self.bs.readUInt()
        sobj_list = []
        for entry_i in range(entry_count):
            _ = self.bs.readUInt()
            entry_idx = self.bs.readUInt()
            some_float = self.bs.readFloat()
            sobj_path = self.bs.readString().replace("\\", "/")
            _ = self.bs.readUInt()
            sobj_list.append(sobj_path)

        return sobj_list

if __name__ == "__main__":
    from glob import glob
    sobjs = glob("/mnt/Windows_heavy/GAMES/WORLD/EXTRACT_0/chunkG0/stage/st101/common/set/st101.sobjl")
    for sobj in sobjs:
        parser = SobjlParser(path=sobj)
        data = parser.read()
        import json
        print(json.dumps(data, indent=4))
