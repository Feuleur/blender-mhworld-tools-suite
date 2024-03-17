import struct
import os
from glob import glob
import json
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

class Mrl3Parser():
    def __init__(self, path=None, data=None):
        self.path = path
        if data is None:
            with open(path, "rb") as file_in:
                data = file_in.read()
        self.bs = Reader(data)
        self.debug_data = {}
        local_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(local_path, "texture_dict.json"), "r") as json_in:
            self.texture_dict = json.load(json_in)
        with open(os.path.join(local_path, "property_dict.json"), "r") as json_in:
            self.property_dict = json.load(json_in)
        with open(os.path.join(local_path, "shader_dict.json"), "r") as json_in:
            self.shader_dict = json.load(json_in)
        

    def read(self):
        self.magic = self.bs.readUInt()
        if self.magic != 5001805:
            raise RuntimeError(str(self.path) + " is not a mdf2 file (magic = " + str(self.magic) + ")")
        _ = self.bs.readUInt()
        _ = self.bs.readUInt()
        _ = self.bs.readUInt()
        mat_count = self.bs.readUInt()
        tex_count = self.bs.readUInt()
        tex_offset = self.bs.readUInt64()
        mat_offset = self.bs.readUInt64()

        texture_paths = []
        for tex_i in range(tex_count):
            self.bs.seek(tex_offset + (256+16)*tex_i)
            _ = self.bs.readUInt()
            _ = self.bs.readUInt()
            _ = self.bs.readUInt()
            _ = self.bs.readUInt()
            texture_paths.append(self.bs.readString())

        self.bs.seek(mat_offset)
        #mat_offset
        mat_infos = []
        for mat_i in range(mat_count):
            mat_info = {}
            mat_info["_0"] = self.bs.readUInt()
            mat_info["matname_hash"] = self.bs.readUInt()
            mat_info["shader_hash"] = self.bs.readUInt()
            mat_info["skin_id"] = self.bs.readUInt()
            mat_info["mat_size"] = self.bs.readUInt()
            mat_info["_1"] = self.bs.readUShort()
            mat_info["data_size"] = self.bs.readUByte()
            mat_info["_2"] = self.bs.readUByte()
            mat_info["alpha_coef"] = self.bs.readUByte()
            mat_info["_4"] = self.bs.readUByte()
            mat_info["alpha_flag_1"] = self.bs.readUByte()
            mat_info["alpha_flag_2"] = self.bs.readUByte()
            mat_info["_7"] = self.bs.readUByte()
            mat_info["_8"] = self.bs.readUByte()
            mat_info["_9"] = self.bs.readUByte()
            mat_info["_10"] = self.bs.readUByte()
            mat_info["_11"] = self.bs.readUInt64()
            mat_info["_12"] = self.bs.readUInt64()
            mat_info["data_offset"] = self.bs.readUInt()
            mat_info["_13"] = self.bs.readUInt()
            mat_infos.append(mat_info)

        all_materials = {}
        for mat_i, mat_info in enumerate(mat_infos):
            current_material = {}
            current_material["textures"] = {}
            current_material["properties"] = {}
            current_material["matname_hash"] = mat_info["matname_hash"]
            current_material["shader_hash"] = mat_info["shader_hash"]
            current_material["_1"] = mat_info["_1"]
            current_material["_2"] = mat_info["_2"]
            current_material["_4"] = mat_info["_4"]
            current_material["alpha_flag_1"] = mat_info["alpha_flag_1"]
            current_material["alpha_flag_2"] = mat_info["alpha_flag_2"]
            current_material["_7"] = mat_info["_7"]
            current_material["_8"] = mat_info["_8"]
            current_material["_9"] = mat_info["_9"]
            current_material["has_alpha"] = bool(mat_info["alpha_coef"] < 255)
            current_material["alpha_coef"] = mat_info["alpha_coef"]/255.0
            self.bs.seek(mat_info["data_offset"])
            property_infos = []
            for tex_i in range(mat_info["data_size"]//2):
                ressource_type = self.bs.readUByte()
                
                _ = self.bs.readUByte()
                _ = self.bs.readUByte()
                _ = self.bs.readUByte()
                ressource_hash = self.bs.readUInt()
                ressource_id = self.bs.readUInt()
                if ressource_type & 0xF == 2:
                    current_material["textures"][self.texture_dict[str(ressource_hash >> 12)]] = texture_paths[ressource_id-1]
                    
                if ressource_type & 0xF == 0:
                    property_infos.append(ressource_hash >> 12)
                unkn = self.bs.readUInt()
            
            current_material["property_block_hashes"] = property_infos
            property_block_names = [self.property_dict[str(x)]["name"] for x in property_infos]
            current_material["property_block_names"] = property_block_names.copy()
            property_block_names.remove("CBMaterialCommon__disclosure")
            current_material["shader_name"] = property_block_names[0]
            for property_info in property_infos:
                if "fields" in self.property_dict[str(property_info)].keys():
                    for field_name, field_type_raw in self.property_dict[str(property_info)]["fields"].items():
                        #print(field_name)
                        if field_type_raw.find("[") != -1:
                            field_type = field_type_raw[:field_type_raw.find("[")]
                            array_size = int(field_type_raw[field_type_raw.find("[")+1:field_type_raw.find("]")])
                        else:
                            field_type = field_type_raw
                            array_size = 1
                        content = []
                        for field_i in range(array_size):
                            if field_type == "float":
                                content.append(self.bs.readFloat())
                            elif field_type == "uint":
                                content.append(self.bs.readUInt())
                            elif field_type == "int":
                                content.append(self.bs.readInt())
                            elif field_type == "ubyte":
                                content.append(self.bs.readUByte())
                            elif field_type == "byte":
                                content.append(self.bs.readByte())
                            elif field_type == "bbool":
                                content.append(bool(self.bs.readUInt() >> 30))
                            else:
                                print("ERROR ERROR", field_type)
                                content.append(self.bs.readFloat())
                        current_material["properties"][field_name] = content
            all_materials[mat_info["matname_hash"]] = current_material
            
        return all_materials

if __name__ == "__main__":
    parser = Mrl3Parser(path="/mnt/Windows_heavy/GAMES/WORLD/EXTRACT_0/chunkG0/pl/f_equip/pl074_0000/wst/mod/f_wst074_0000.mrl3")
    parser.read()
