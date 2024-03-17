import struct
import os
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

class IprParser():
    def __init__(self, path=None, data=None):
        self.path = path
        self.basename = None
        if data is None:
            with open(path, "rb") as file_in:
                data = file_in.read()
            self.basename = os.path.basename(self.path)
        self.bs = Reader(data)
    
    def read(self):
        #print("AAA")
        self.magic = self.bs.readUInt()
        #print("BBB")
        if self.magic != 7499881:
            if self.path is not None:
                raise RuntimeError(str(self.path) + " is not a mhworld ipr file (magic = " + str(self.magic) + ")")
            else:
                raise RuntimeError("Data is not a mhworld ipr file (magic = " + str(self.magic) + ")")
            
        self.bs.allign(16)
        _ = self.bs.readUInt64()
        _ = self.bs.readUInt64()
        _ = self.bs.readUInt64()
        _ = self.bs.readUInt64()
        _ = self.bs.readUInt64()
        _ = self.bs.readUInt64()
        
        object_info_offset = self.bs.readUInt64()
        object_info_counter = self.bs.readUInt64()
        
        references_info_offset = self.bs.readUInt64()
        references_info_counter = self.bs.readUInt64()
        
        self.bs.seek(object_info_offset)
        object_infos = []
        for object_info_i in range(object_info_counter):
            object_info = {}
            _ = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            object_info["object_path_offset"] = self.bs.readUInt64()
            object_info["object_offset"] = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            object_info["object_instance_offset"] = self.bs.readUInt64()
            object_info["object_instance_count"] = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            object_infos.append(object_info)
        
        object_instances = []
        for object_info in object_infos[:]:
            self.bs.seek(object_info["object_path_offset"])
            object_path = self.bs.readString().replace("\\", "/")
            self.bs.seek(object_info["object_instance_offset"])
            for instance_i in range(object_info["object_instance_count"])[:]:
                instance_data = {}
                instance_data["path"] = object_path
                
                if self.basename is not None:
                    instance_data["zone"] = self.basename
                else:
                    instance_data["zone"] = "UNKNOWN"
                instance_data["position"] = [self.bs.readFloat() for _ in range(3)]
                instance_data["scale"] = [self.bs.readFloat() for _ in range(3)]
                instance_data["rotation"] = [self.bs.readFloat() for _ in range(4)]
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                _ = self.bs.readUInt64()
                object_instances.append(instance_data)

        return object_instances

if __name__ == "__main__":
    parser = IprParser(path="./st101.bkipr")
    data = parser.read()
    import json
    #print(len(data))
    #print(json.dumps(data, indent=4))
