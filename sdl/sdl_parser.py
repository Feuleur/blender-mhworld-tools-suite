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
    lacet = euler[2]
    tangage = euler[1]
    roulis = euler[0]
    qx = math.sin(roulis/2) * math.cos(tangage/2) * math.cos(lacet/2) - math.cos(roulis/2) * math.sin(tangage/2) * math.sin(lacet/2)
    qy = math.cos(roulis/2) * math.sin(tangage/2) * math.cos(lacet/2) + math.sin(roulis/2) * math.cos(tangage/2) * math.sin(lacet/2)
    qz = math.cos(roulis/2) * math.cos(tangage/2) * math.sin(lacet/2) - math.sin(roulis/2) * math.sin(tangage/2) * math.cos(lacet/2)
    qw = math.cos(roulis/2) * math.cos(tangage/2) * math.cos(lacet/2) + math.sin(roulis/2) * math.sin(tangage/2) * math.sin(lacet/2)
    return [qx, qy, qz, qw]

class SdlParser():
    def __init__(self, path=None, data=None):
        self.path = path
        #self.basename = None
        if data is None:
            with open(path, "rb") as file_in:
                data = file_in.read()
            #self.basename = os.path.splitext(os.path.basename(self.path))[0]
        self.bs = Reader(data)
        
    
    def read(self, recursive=False):
        self.magic = self.bs.readUInt()

        if self.magic != 4998227:
            if self.path is not None:
                raise RuntimeError(str(self.path) + " is not a mhworld sdl file (magic = " + str(self.magic) + ")")
            else:
                raise RuntimeError("Data is not a mhworld sdl file (magic = " + str(self.magic) + ")")
        _ = self.bs.readUShort()
        thing_count = self.bs.readUShort()
        _ = self.bs.readUInt()
        _ = self.bs.readUShort()
        _ = self.bs.readUShort()
        
        _ = self.bs.readUInt64()
        name_offset = self.bs.readUInt64()
        #print(thing_count)
        thing_infos = []
        for thing_i in range(thing_count):
            thing_info = {}
            thing_info["index"] = thing_i
            thing_info["offset"] = self.bs.tell()
            thing_info["children"] = []
            thing_info["unk1_offset"] = self.bs.readUInt64()
            
            _ = self.bs.readUInt()
            thing_info["thing_parent"] = self.bs.readUShort()
            if len(thing_infos) > thing_info["thing_parent"]: 
                thing_infos[thing_info["thing_parent"]]["children"].append(thing_i)
            _ = self.bs.readUByte()
            thing_info["thing_type"] = self.bs.readUByte()
            thing_info["string_offset"] = self.bs.readUInt64()
            _ = self.bs.readUInt64()
            nu = self.bs.readUInt64()
            #print(thing_info["offset"])
            thing_info["unk2_offset"] = self.bs.readUInt64()
            
            thing_infos.append(thing_info)
        
        # Resolve names
        for thing_info_i in range(len(thing_infos)):
            self.bs.seek(name_offset + thing_infos[thing_info_i]["string_offset"])
            thing_infos[thing_info_i]["thing_name"] = self.bs.readString()
        
        #print(json.dumps(thing_infos, indent=4))
        for thing_info_i in range(len(thing_infos)):
            #print(thing_infos[thing_info_i])
            if thing_infos[thing_info_i]["thing_name"] == "mpModel":
                self.bs.seek(thing_infos[thing_info_i]["unk2_offset"])
                self.bs.readUInt()
                self.bs.allign(16)
                path_offset = self.bs.readUInt()
                self.bs.seek(name_offset + path_offset + 4)
                thing_infos[thing_info_i]["data"] = {
                    "name":thing_infos[thing_info_i]["thing_name"], 
                    "model_path":self.bs.readString().replace("\\", "/")
                }
            elif thing_infos[thing_info_i]["thing_name"] == "mGeometry":
                self.bs.seek(thing_infos[thing_info_i]["unk2_offset"])
                self.bs.readUInt()
                self.bs.allign(16)
                path_offset = self.bs.readUInt()
                self.bs.seek(name_offset + path_offset + 4)
                thing_infos[thing_info_i]["data"] = {
                    "name":thing_infos[thing_info_i]["thing_name"], 
                    "model_path":self.bs.readString().replace("\\", "/")
                }
            elif thing_infos[thing_info_i]["thing_name"] == "mPos":
                
                self.bs.seek(thing_infos[thing_info_i]["unk2_offset"])
                self.bs.readUInt()
                self.bs.allign(16)
                thing_infos[thing_info_i]["data"] = {
                    "name":thing_infos[thing_info_i]["thing_name"], 
                    "pos":[self.bs.readFloat() for _ in range(3)]
                }
            elif thing_infos[thing_info_i]["thing_name"] == "mAngle":
                self.bs.seek(thing_infos[thing_info_i]["unk2_offset"])
                self.bs.readUInt()
                self.bs.allign(16)
                # Si possible a transformer en quat
                thing_infos[thing_info_i]["data"] = {
                    "name":thing_infos[thing_info_i]["thing_name"], 
                    "euler":[self.bs.readFloat() for _ in range(3)]
                }
            elif thing_infos[thing_info_i]["thing_name"] == "mScale":
                self.bs.seek(thing_infos[thing_info_i]["unk2_offset"])
                self.bs.readUInt()
                self.bs.allign(16)
                thing_infos[thing_info_i]["data"] = {
                    "name":thing_infos[thing_info_i]["thing_name"], 
                    "scl":[self.bs.readFloat() for _ in range(3)]
                }
            elif thing_infos[thing_info_i]["thing_name"] == "mQuat":
                self.bs.seek(thing_infos[thing_info_i]["unk2_offset"])
                self.bs.readUInt()
                self.bs.allign(16)
                thing_infos[thing_info_i]["data"] = {
                    "name":thing_infos[thing_info_i]["thing_name"], 
                    "quat":[self.bs.readFloat() for _ in range(4)]
                }
            elif thing_infos[thing_info_i]["thing_name"] == "mpScheduler":
                self.bs.seek(thing_infos[thing_info_i]["unk2_offset"])
                self.bs.readUInt()
                self.bs.allign(16)
                path_offset = self.bs.readUInt()
                self.bs.seek(name_offset + path_offset + 4)
                #print("")
                #print(hex(thing_infos[thing_info_i]["unk2_offset"]))
                #print(hex(path_offset))
                #print(hex(name_offset+path_offset))
                thing_infos[thing_info_i]["data"] = {
                    "name":thing_infos[thing_info_i]["thing_name"], 
                    "dependency_path":self.bs.readString().replace("\\", "/")
                }

        object_instances = []
        dependencies = []
        
        for thing_info in thing_infos:
            if thing_info["thing_name"] == "mpModel" or thing_info["thing_name"] == "mGeometry":
                object_instance = {}
                
                object_instance["path"] = thing_info["data"]["model_path"]
                parent_idx = thing_info["thing_parent"]
                object_instance["name"] = thing_infos[parent_idx]["thing_name"]
                
                object_instance["position"] = [0.0, 0.0, 0.0]
                object_instance["rotation"] = [0.0, 0.0, 0.0, 1.0]
                object_instance["scale"] = [1.0, 1.0, 1.0]
                for child_idx in thing_infos[parent_idx]["children"]:
                    
                    if thing_infos[child_idx]["thing_name"] == "mPos":
                        object_instance["position"] = thing_infos[child_idx]["data"]["pos"].copy()
                    elif thing_infos[child_idx]["thing_name"] == "mAngle":
                        object_instance["rotation"] = euler_to_quaternion(thing_infos[child_idx]["data"]["euler"])
                    elif thing_infos[child_idx]["thing_name"] == "mScale":
                        object_instance["scale"] = thing_infos[child_idx]["data"]["scl"].copy()
                object_instance["zone"] = "UNKNOWN"
                object_instances.append(object_instance)
            if thing_info["thing_name"] == "mpScheduler" and recursive:
                dependencies.append(thing_info["data"]["dependency_path"])
        return object_instances, dependencies

#if __name__ == "__main__":
    #parser = SdlParser(path="st101.sdl")
    #data = parser.read()
    #import json
    #print(json.dumps(data, indent=4))
