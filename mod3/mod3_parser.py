import struct
import codecs
import json
import zlib
from glob import glob
import os
import math
import numpy as np
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

class Mod3Parser():
    def __init__(self, path=None, data=None):
        self.path = path
        if data is None:
            with open(path, "rb") as file_in:
                data = file_in.read()
        self.bs = Reader(data)

    def read(self):
        self.magic = self.bs.readUInt()
        self.version = self.bs.readUShort()
        if self.magic != 4476749 and self.version != 237:
            raise RuntimeError(str(self.path) + " is not a mhworld mod3 file (magic = " + str(self.magic) + ", version = " + str(self.version) + ")")

        bone_count = self.bs.readUShort()
        mesh_count = self.bs.readUShort()
        mat_count = self.bs.readUShort()
        vert_count = self.bs.readUInt()
        face_count = self.bs.readUInt()
        edge_count = self.bs.readUInt()
        vbuffer_size = self.bs.readUInt64()
        group_count = self.bs.readUInt64()
        timestamp = self.bs.readUInt64()
        bone_offset = self.bs.readUInt64()
        group_offset = self.bs.readUInt64()
        matname_offset = self.bs.readUInt64()
        mesh_offset = self.bs.readUInt64()
        vert_offset = self.bs.readUInt64()
        face_offset = self.bs.readUInt64()
        _offset = self.bs.readUInt64()
        _offset = self.bs.readUInt64()

        materials = []
        for mat_i in range(mat_count):
            self.bs.seek(matname_offset + mat_i*128)
            material_name = self.bs.readString()
            materials.append(material_name)

        skeleton_infos = []
        self.bs.seek(bone_offset)
        #print(bone_count)

        armature_datas = []
        for bone_i in range(bone_count):
            bone_info = {}
            bone_info["id"] = bone_i
            bone_info["function"] = self.bs.readUShort()
            bone_info["parent"] = self.bs.readUByte()
            bone_info["child"] = self.bs.readUByte()
            bone_info["float1"] = self.bs.readFloat()
            bone_info["length"] = self.bs.readFloat()
            bone_info["x"] = self.bs.readFloat()
            bone_info["y"] = self.bs.readFloat()
            bone_info["z"] = self.bs.readFloat()
            armature_datas.append(bone_info)
        for bone_i in range(bone_count):
            matrix = []
            matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
            matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
            matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
            matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
            armature_datas[bone_i]["local_matrix"] = matrix
        for bone_i in range(bone_count):
            matrix = []
            matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
            matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
            matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
            matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
            armature_datas[bone_i]["global_matrix"] = matrix

        remap = {}
        for bone_i in range(512):
            remapping = self.bs.readUByte()
            if remapping != 255:
                remap[bone_i] = remapping
                try:
                    armature_datas[remapping]["remap"] = bone_i
                except:
                    pass
        remap_inv = {v:k for k,v in remap.items()}
        #print("remap = ", remap)

        mesh_infos = []
        self.bs.seek(mesh_offset)
        for mesh_i in range(mesh_count):

            mesh_info = {}

            # Grabbed from the previous importer by asteriskampersand, those were hard to figure out
            mesh_info["shadow_flag"] = self.bs.readUShort()

            mesh_info["vert_count"] = self.bs.readUShort()
            mesh_info["visibleCondition"] = self.bs.readUShort()
            mesh_info["materialIdx"] = self.bs.readUShort()
            tmp_lod = self.bs.readUInt()
            mesh_info["lod"] = int(round(math.log2(tmp_lod & -tmp_lod)))
            mesh_info["weightDynamics"] = self.bs.readUShort()
            mesh_info["blockSize"] = self.bs.readUByte()
            mesh_info["unkn3"] = self.bs.readUByte()
            mesh_info["vertexSub"] = self.bs.readUInt()
            mesh_info["vertexOffset"] = self.bs.readUInt()

            mesh_info["blocktype"] = self.bs.readUInt()
            mesh_info["faceOffset"] = self.bs.readUInt()
            mesh_info["faceCount"] = self.bs.readUInt()
            mesh_info["vertexBase"] = self.bs.readUInt()
            mesh_info["NULL_0"] = self.bs.readUByte()
            mesh_info["boundingBoxCount"] = self.bs.readUByte()
            mesh_info["unknownIndex"] = self.bs.readUShort()

            mesh_info["vertexSubMirror"] = self.bs.readUShort()
            mesh_info["vertexIndexSub"] = self.bs.readUShort()
            mesh_info["mapData_1"] = self.bs.readUShort()
            mesh_info["mapData_2"] = self.bs.readUShort()
            mesh_info["NULL_1"] = self.bs.readUInt()
            mesh_info["intUnknown"] = self.bs.readUInt()
            mesh_info["vertexSubTotal"] = self.bs.readUInt()
            mesh_info["NULL_2"] = self.bs.readUInt()
            mesh_info["NULL_2"] = self.bs.readUInt()
            mesh_info["NULL_2"] = self.bs.readUInt()
            mesh_info["NULL_2"] = self.bs.readUInt()
            mesh_infos.append(mesh_info)

            #print(mesh_info)

        mesh_datas = []
        running_offset = vert_offset
        for mesh_i, mesh_info in enumerate(mesh_infos):

            mesh = {}
            vert_size = mesh_info["blockSize"]
            
            self.bs.seek(running_offset)
            running_offset += mesh_info["blockSize"]*mesh_info["vert_count"]

            has_position = True
            has_normals = True
            has_tangents = True
            has_bitangent = True
            UV_number = 1
            weights_bytes = 0
            has_color = False

            if mesh_info["blocktype"] == 2807493369:
                UV_number = 1
                weights_bytes = 0
                has_color = False
            elif mesh_info["blocktype"] == 2769308832:
                UV_number = 2
                weights_bytes = 0
                has_color = False
            elif mesh_info["blocktype"] == 3282830241:
                UV_number = 3
                weights_bytes = 0
                has_color = True
            elif mesh_info["blocktype"] == 3379104440:
                UV_number = 4
                weights_bytes = 0
                has_color = True
            elif mesh_info["blocktype"] == 2173240540:
                UV_number = 1
                weights_bytes = 0
                has_color = True
            elif mesh_info["blocktype"] == 252052287:
                UV_number = 2
                weights_bytes = 0
                has_color = True
            elif mesh_info["blocktype"] == 4130816028:
                UV_number = 1
                weights_bytes = 4
                has_color = False
            elif mesh_info["blocktype"] == 4101111365:
                UV_number = 2
                weights_bytes = 4
                has_color = False
            elif mesh_info["blocktype"] == 1014171488:
                UV_number = 1
                weights_bytes = 4
                has_color = True
            elif mesh_info["blocktype"] == 3002859651:
                UV_number = 2
                weights_bytes = 4
                has_color = True
            elif mesh_info["blocktype"] == 2180350055:
                UV_number = 1
                weights_bytes = 8
                has_color = False
            elif mesh_info["blocktype"] == 2209562174:
                UV_number = 2
                weights_bytes = 8
                has_color = False
            elif mesh_info["blocktype"] == 912889255:
                UV_number = 1
                weights_bytes = 8
                has_color = True
            elif mesh_info["blocktype"] == 3102118468:
                UV_number = 2
                weights_bytes = 8
                has_color = True
            else:
                logger.warning("UNKNOWN BLOCK TYPE = " + str(mesh_info["blocktype"]))
            
            positions = []
            normals = []
            tangents = []
            bitangent_sign = []

            UVs = []
            for UV_i in range(UV_number):
                UVs.append([])
            weights_raw = []
            bone_ids = []
            colors = []
            for vert_i in range(mesh_info["vert_count"]):

                if has_position:
                    positions.append([self.bs.readFloat() for _ in range(3)])
                if has_normals:
                    normals.append([self.bs.readByte() for _ in range(4)][:3])
                if has_tangents:
                    tangents.append([self.bs.readByte() for _ in range(3)])
                if has_bitangent:
                    bitangent_sign.append(self.bs.readByte())
                for UV_i in range(UV_number):
                    UVs[UV_i].append([self.bs.readHalf(), 1.0-self.bs.readHalf()])
                if weights_bytes == 4:
                    weights_raw.append(self.bs.readUInt())
                    bone_ids.append([self.bs.readUByte() for _ in range(4)])
                elif weights_bytes == 8:
                    weights_raw.append(self.bs.readUInt64())
                    bone_ids.append([self.bs.readUByte() for _ in range(8)])
                if has_color:
                    colors.append([self.bs.readUByte() for _ in range(4)])
            if mesh_info["weightDynamics"] == 1:
                pass
            elif mesh_info["weightDynamics"] == 5:
                pass
            elif mesh_info["weightDynamics"] == 9:
                weights = np.array([
                    ((np.array(weights_raw, dtype=np.uint32) & 1023) / 1023),
                ]).transpose([1,0])
                bone_ids = np.array(bone_ids)[:,:1]
            elif mesh_info["weightDynamics"] == 17:
                weights = np.array([
                    ((np.array(weights_raw, dtype=np.uint32) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint32) >> 10) & 1023) / 1023)
                ]).transpose([1,0])
                bone_ids = np.array(bone_ids)[:,:2]
            elif mesh_info["weightDynamics"] == 25:
                weights = np.array([
                    ((np.array(weights_raw, dtype=np.uint32) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint32) >> 10) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint32) >> 20) & 1023) / 1023)
                ]).transpose([1,0])
                bone_ids = np.array(bone_ids)[:,:3]
            elif mesh_info["weightDynamics"] == 33:
                weights = np.array([
                    ((np.array(weights_raw, dtype=np.uint32) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint32) >> 10) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint32) >> 20) & 1023) / 1023),
                    1.0-(((np.array(weights_raw, dtype=np.uint32) & 1023) / 1023) + (((np.array(weights_raw, dtype=np.uint32) >> 10) & 1023) / 1023) + (((np.array(weights_raw, dtype=np.uint32) >> 20) & 1023) / 1023))
                ]).transpose([1,0])
                bone_ids = np.array(bone_ids)[:,:4]
            elif mesh_info["weightDynamics"] == 41:
                weights = np.array([
                    ((np.array(weights_raw, dtype=np.uint64) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 10) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 20) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 32) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 40) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 48) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 56) & 255) / 1023),
                    #1.0-(((np.array(weights_raw) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 10) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 20) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 32) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 40) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 48) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 56) & 255) / 1023))
                ]).transpose([1,0])
                bone_ids = np.array(bone_ids)[:,:8]
            elif mesh_info["weightDynamics"] == 49:
                weights = np.array([
                    ((np.array(weights_raw, dtype=np.uint64) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 10) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 20) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 32) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 40) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 48) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 56) & 255) / 1023),
                    #1.0-(((np.array(weights_raw) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 10) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 20) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 32) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 40) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 48) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 56) & 255) / 1023))
                ]).transpose([1,0])
                bone_ids = np.array(bone_ids)[:,:8]
            elif mesh_info["weightDynamics"] == 57:
                weights = np.array([
                    ((np.array(weights_raw, dtype=np.uint64) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 10) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 20) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 32) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 40) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 48) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 56) & 255) / 1023),
                    #1.0-(((np.array(weights_raw) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 10) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 20) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 32) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 40) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 48) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 56) & 255) / 1023))
                ]).transpose([1,0])
                bone_ids = np.array(bone_ids)[:,:8]
            elif mesh_info["weightDynamics"] == 65:
                weights = np.array([
                    ((np.array(weights_raw, dtype=np.uint64) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 10) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 20) & 1023) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 32) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 40) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 48) & 255) / 1023),
                    (((np.array(weights_raw, dtype=np.uint64) >> 56) & 255) / 1023),
                    #1.0-(((np.array(weights_raw) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 10) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 20) & 1023) / 1023) + 
                         #(((np.array(weights_raw) >> 32) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 40) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 48) & 255) / 1023) + 
                         #(((np.array(weights_raw) >> 56) & 255) / 1023))
                ]).transpose([1,0])
                bone_ids = np.array(bone_ids)[:,:8]
            else:
                #print("")
                #ind = 0
                #tmp_val = weights_raw[ind]
                #print(tmp_val, tmp_val & (2**(32)-1), tmp_val >> 32)
                #a = ((tmp_val >> 0) & 1023)/1023
                #b = ((tmp_val >> 10) & 1023)/1023
                #c = ((tmp_val >> 20) & 1023)/1023
                #d = ((tmp_val >> 30) & 3)/3
                ##e = ((tmp_val >> 32) & 255)/255
                ##f = ((tmp_val >> 40) & 255)/255
                ##g = ((tmp_val >> 48) & 255)/255
                ##h = ((tmp_val >> 56) & 255)/255
                ##e = ((tmp_val >> 32) & 1023)/1023
                ##f = ((tmp_val >> 40) & 1023)/1023
                ##g = ((tmp_val >> 48) & 1023)/1023
                ##h = ((tmp_val >> 56) & 1023)/1023
                #e = ((tmp_val >> 32) & 255)/1023
                #f = ((tmp_val >> 40) & 255)/1023
                #g = ((tmp_val >> 48) & 255)/1023
                #h = ((tmp_val >> 56) & 255)/1023
                #print("a\t", bone_ids[ind][0], "\t", a)
                #print("b\t", bone_ids[ind][1], "\t", b)
                #print("c\t", bone_ids[ind][2], "\t", c)
                #print("d\t", bone_ids[ind][3], "\t", d)
                #print("e\t", bone_ids[ind][4], "\t", e)
                #print("f\t", bone_ids[ind][5], "\t", f)
                #print("g\t", bone_ids[ind][6], "\t", g)
                #print("h\t", bone_ids[ind][7], "\t", h)
                #print(a+b+c+d)
                #print(e+f+g+h)
                #print(a+b+c+d+e+f+g+h)
                #print(bin(weights_raw[ind]))
                #print(bone_ids[ind])
                logger.warning("UNKNOWN WEIGHT SCHEME = " + str(mesh_info["weightDynamics"]) + " block type = " +  str(mesh_info["blocktype"]) + " weight bytes = " + str(weights_bytes))
            weights_names = []
            for x in bone_ids:
                weight_list = []
                for y in x:
                    try:
                        weight_list.append("bone_" + str(remap_inv[y]).zfill(3))
                    except:
                        weight_list.append("bone_err")
                weights_names.append(weight_list)
                #try:
                    #weights_names.append(["bone_" + str(remap_inv[y]).zfill(3) for y in x])
                #except:
                    #weights_names.append(["bone_err" for y in x])
            normals = np.array(normals, dtype=np.float32) + 128
            normals /= 127.5
            normals -= 1.0
            faces = []

            self.bs.seek(face_offset + 2*mesh_info["faceOffset"])
            for face_i in range(mesh_info["faceCount"]//3):
                faces.append([self.bs.readUShort() - mesh_info["vertexSub"] for _ in range(3)])

            mesh["lod"] = mesh_info["lod"]
            mesh["id"] = mesh_i
            mesh["positions"] = positions
            mesh["faces"] = faces
            mesh["normals"] = normals
            mesh["UVs"] = UVs
            mesh["group"] = mesh_info["visibleCondition"]
            if len(weights_raw) > 0:
                mesh["weights_values"] = weights
                mesh["weights_names"] = weights_names
            if len(colors) > 0:
                mesh["colors"] = colors
            mesh["material"] = materials[mesh_info["materialIdx"]]
            mesh["material_name_hash"] = int("0b"+"1"*32, 2) - zlib.crc32(materials[mesh_info["materialIdx"]].encode())
            mesh_datas.append(mesh)

        return armature_datas, mesh_datas

if __name__ == "__main__":
    parser = Mod3Parser(path="m_face000.mod3")
    armature_datas, mesh_datas = parser.read()
    #print(mesh_datas[0]["material"])
