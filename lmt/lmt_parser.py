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
        self.partial_offset = 0
        self.partial_data = None

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

    # this function will definitelly stop working if you look at it too hard
    def readBytes_unpackbin(self, bits, block_size, signed=False):
        value = 0
        remaining_bits = bits
        movement = min(remaining_bits, block_size)
        while True:
            if self.partial_offset == 0:
                if block_size == 8:
                    self.partial_data = self.readUByte()
                elif block_size == 16:
                    self.partial_data = self.readUShort()
                elif block_size == 32:
                    self.partial_data = self.readUInt()
                elif block_size == 64:
                    self.partial_data = self.readUInt64()
            movement = min(remaining_bits, block_size-self.partial_offset)
            value = value << movement
            value = value | (self.partial_data & ((2**movement)-1))
            self.partial_data = self.partial_data >> movement
            remaining_bits -= movement
            self.partial_offset = (self.partial_offset + movement)%block_size
            movement = min(remaining_bits, block_size)
            
            if remaining_bits == 0:
                if signed == True:
                    maxval = ((1 << bits) - 1)
                    if value > (maxval >> 1):
                        value -= maxval
                    value = value / (maxval >> 1)
                return value

    def readBytes_to_int(self, size):
        self.readUByte()
        value = int.from_bytes(self.readBytes(size), byteorder='little')
        self.offset += size
        return value

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

class LmtParser():
    def __init__(self, path=None, data=None):
        self.path = path
        self.basename = ""
        if data is None:
            with open(path, "rb") as file_in:
                data = file_in.read()
            self.basename = os.path.splitext(os.path.basename(self.path))[0]
        self.bs = Reader(data)

    def read(self):
        self.magic = self.bs.readUInt()
        self.version = self.bs.readUShort()
        if self.magic != 5524812 and self.version != 95:
            raise RuntimeError(str(self.path) + " is not a mhworld lmt file (magic = " + str(self.magic) + ", version = " + str(self.version) + ")")
        
        animation_count = self.bs.readUShort()
        _ = self.bs.readUInt64()
        
        animations_info_offsets = []
        for count_i in range(animation_count):
            animations_info_offsets.append(self.bs.readUInt64())
        #print(animation_count)
        
        animations_infos = []
        for animations_info_offset_i, animations_info_offset in enumerate(animations_info_offsets):
            #print("animations_info_offset_i", animations_info_offset_i)
            if animations_info_offset == 0:
                #print("animations_info_offset_i", "SKIPPED")
                continue
            self.bs.seek(animations_info_offset)
            animation_info = {}
            animation_info["animation_idx"] = animations_info_offset_i
            animation_info["bone_infos_offset"] = self.bs.readUInt64()
            animation_info["bone_info_count"] = self.bs.readUInt()
            animation_info["unk2"] = self.bs.readUInt()
            animation_info["unk3"] = self.bs.readUInt()
            animation_info["unk4"] = self.bs.readUInt()
            animation_info["unk5"] = self.bs.readUInt()
            animation_info["unk6"] = self.bs.readUInt()
            animation_info["float_array"] = [self.bs.readFloat() for _ in range(8)]
            animation_info["unk7"] = self.bs.readUInt64()
            animation_info["unk8"] = self.bs.readUInt64()
            animation_info["unk9"] = self.bs.readUInt64()
            animation_info["unk_offset1"] = self.bs.readUInt()
            animations_infos.append(animation_info)
            
        animation_data = []
        for animation_i, animation_info in enumerate(animations_infos):
            self.bs.seek(animation_info["bone_infos_offset"])
            track_infos = []
            for bone_info_i in range(animation_info["bone_info_count"]):
                track_info = {}
                track_info["encoding"] = self.bs.readUByte()
                track_info["type"] = self.bs.readUByte()
                track_info["unk2"] = self.bs.readUByte()
                track_info["unk3"] = self.bs.readUByte()
                track_info["bone_id"] = self.bs.readInt()

                track_info["unk_float"] = self.bs.readFloat()
                track_info["array_size"] = self.bs.readUInt()
                track_info["keyframe_array_offset"] = self.bs.readUInt64()
                track_info["unk_float_array"] = [self.bs.readFloat() for _ in range(4)]
                track_info["coef_offset"] = self.bs.readUInt64()
                #if track_info["bone_id"] == 32:
                    #print(track_info)
                #if track_info["encoding"] == 14:
                    #print(track_info)
                #print(track_info)
                track_infos.append(track_info)
            #print(track_infos)
            bone_action_dict = {}
            
            for track_info in track_infos:
                coef_a = np.array([1.0, 1.0, 1.0, 1.0])
                coef_b = np.array([0.0, 0.0, 0.0, 0.0])
                coef_found = False
                if track_info["coef_offset"] != 0:
                    self.bs.seek(track_info["coef_offset"])
                    coef_a = np.array([self.bs.readFloat() for _ in range(4)])
                    coef_b = np.array([self.bs.readFloat() for _ in range(4)])
                    coef_found = True
                else:
                    pass
                
                if track_info["bone_id"] not in bone_action_dict:
                    bone_action_dict[track_info["bone_id"]] = {}

                action_type = "UNK_" + str(track_info["type"])
                if track_info["type"]%3 == 0:
                    action_type = "rot"
                    if track_info["type"] > 1:
                        bone_action_dict[track_info["bone_id"]]["rot_referencial"] = "global"
                    else:
                        bone_action_dict[track_info["bone_id"]]["rot_referencial"] = "local"
                elif track_info["type"]%3 == 1:
                    action_type = "pos"
                    if track_info["type"] > 1:
                        bone_action_dict[track_info["bone_id"]]["pos_referencial"] = "global"
                    else:
                        bone_action_dict[track_info["bone_id"]]["pos_referencial"] = "local"
                elif track_info["type"]%3 == 2:
                    action_type = "scl"
                    if track_info["type"] > 1:
                        bone_action_dict[track_info["bone_id"]]["scl_referencial"] = "global"
                    else:
                        bone_action_dict[track_info["bone_id"]]["scl_referencial"] = "local"
                else:
                    logger.warning("UNSUPPORTED KEYFRAME TYPE: " + str(track_info["type"]) + ".")

                bone_action_dict[track_info["bone_id"]]["encoding"] = track_info["encoding"]

                if track_info["keyframe_array_offset"] != 0:

                    self.bs.seek(track_info["keyframe_array_offset"])
                    if track_info["encoding"] == 1:
                        keyframe_count = int(round(track_info["array_size"]/12))
                        keyframe_values = np.array([[self.bs.readFloat() for _ in range(3)]])
                        time_values = []
                        time_values.append(1)
                    elif track_info["encoding"] == 2:
                        keyframe_count = int(round(track_info["array_size"]/16))
                        keyframe_values = np.array([[self.bs.readFloat() for _ in range(3)]])
                        time_values = []
                        time_values.append(self.bs.readUInt())
                    elif track_info["encoding"] == 3:
                        keyframe_count = int(round(track_info["array_size"]/16))
                        keyframe_values = np.array([[self.bs.readFloat() for _ in range(3)]])
                        time_values = []
                        time_values.append(self.bs.readUInt())
                    elif track_info["encoding"] == 4:
                        keyframe_count = int(round(track_info["array_size"]/8))
                        keyframe_values_raw = []
                        time_values = []
                        current_time = 0
                        for _ in range(keyframe_count):
                            keyframe_values_raw.append([self.bs.readUShort() / 65535 for _ in range(3)])
                            time_values.append(current_time)
                            current_time += self.bs.readUShort()
                        keyframe_values = np.array(keyframe_values_raw) * coef_a[:3] + coef_b[:3]
                    elif track_info["encoding"] ==5:
                        keyframe_count = int(round(track_info["array_size"]/4))
                        keyframe_values_raw = []
                        time_values = []
                        current_time = 0
                        for _ in range(keyframe_count):
                            keyframe_values_raw.append([self.bs.readUByte() / 255 for _ in range(3)])
                            time_values.append(current_time)
                            current_time += self.bs.readUByte()
                        keyframe_values = np.array(keyframe_values_raw) * coef_a[:3] + coef_b[:3]
                    elif track_info["encoding"] == 6:
                        keyframe_count = int(round(track_info["array_size"]/8))
                        keyframe_values_raw = []
                        time_values = []
                        current_time = 0
                        for _ in range(keyframe_count):
                            w = self.bs.readBytes_unpackbin(14, 64, signed=True) *2.0
                            z = self.bs.readBytes_unpackbin(14, 64, signed=True) *2.0
                            y = self.bs.readBytes_unpackbin(14, 64, signed=True) *2.0
                            x = self.bs.readBytes_unpackbin(14, 64, signed=True) *2.0
                            time_values.append(current_time)
                            current_time += self.bs.readBytes_unpackbin(8, 64)
                            keyframe_values_raw.append([
                                x, #x
                                y, #y
                                z, #z
                                w, #w
                            ])
                        keyframe_values = np.array(keyframe_values_raw)
                        #print(animation_info["animation_idx"], track_info["bone_id"])
                    elif track_info["encoding"] == 7:
                        keyframe_count = int(round(track_info["array_size"]/4))
                        keyframe_values_raw = []
                        time_values = []
                        current_time = 0
                        for _ in range(keyframe_count):
                            tmp = self.bs.readUInt()
                            w = (tmp & ((2**7)-1)) / 127.0
                            z = ((tmp >> 7) & ((2**7)-1)) / 127.0
                            y = ((tmp >> 14) & ((2**7)-1)) / 127.0
                            x = ((tmp >> 21) & ((2**7)-1)) / 127.0
                            time_values.append(current_time)
                            current_time += ((tmp >> 28) & ((2**4)-1))
                            keyframe_values_raw.append([
                                x, #x
                                y, #y
                                z, #z
                                w #w
                            ])
                        keyframe_values = np.array(keyframe_values_raw) * coef_a + coef_b
                    elif track_info["encoding"] == 11:
                        keyframe_count = int(round(track_info["array_size"]/4))
                        keyframe_values = []
                        time_values = []
                        current_time = 0
                        for _ in range(keyframe_count):
                            tmp = self.bs.readUInt()
                            
                            if coef_found:
                                x = (((tmp & ((2**14)-1)) / 16383.0) * coef_a[0]) + coef_b[0]
                                w = ((((tmp >> 14) & ((2**14)-1)) / 16383.0) * coef_a[3]) + coef_b[3]
                            else:
                                w = (tmp & ((2**14)-1)) / 0xFFF
                                x = ((tmp >> 14) & ((2**14)-1))
                                if (x > 0x1fff != 0):
                                    x = -(0x1fff - x)
                                x /= 0x8ff
                            keyframe_values.append([

                                x, #x
                                0.0, #y
                                0.0, #z
                                w, #w
                            ])
                            #print("11 ", np.linalg.norm(keyframe_values[-1]))
                            time_values.append(current_time)
                            current_time += ((tmp >> 28) & ((2**4)-1))
                        keyframe_values = np.array(keyframe_values)
                    elif track_info["encoding"] == 12:
                        keyframe_count = int(round(track_info["array_size"]/4))
                        keyframe_values = []
                        time_values = []
                        current_time = 0
                        for _ in range(keyframe_count):
                            tmp = self.bs.readUInt()
                            
                            if coef_found:
                                y = (((tmp & ((2**14)-1)) / 16383.0) * coef_a[1]) + coef_b[1]
                                w = ((((tmp >> 14) & ((2**14)-1)) / 16383.0) * coef_a[3]) + coef_b[3]
                            else:
                                w = (tmp & ((2**14)-1)) / 0xFFF
                                y = ((tmp >> 14) & ((2**14)-1))
                                if (y > 0x1fff != 0):
                                    y = -(0x1fff - y)
                                y /= 0x8ff
                            keyframe_values.append([
                                0.0, #x
                                y, #y
                                0.0, #z
                                w, #w
                            ])
                            time_values.append(current_time)
                            current_time += ((tmp >> 28) & ((2**4)-1))
                        keyframe_values = np.array(keyframe_values)
                        #print("12 ", np.linalg.norm(keyframe_values[-1]))
                    elif track_info["encoding"] == 13:
                        keyframe_count = int(round(track_info["array_size"]/4))
                        keyframe_values = []
                        time_values = []
                        current_time = 0
                        for _ in range(keyframe_count):
                            tmp = self.bs.readUInt()
                            
                            if coef_found:
                                z = (((tmp & ((2**14)-1)) / 16383.0) * coef_a[2]) + coef_b[2]
                                w = ((((tmp >> 14) & ((2**14)-1)) / 16383.0) * coef_a[3]) + coef_b[3]
                            else:
                                w = (tmp & ((2**14)-1)) / 0xFFF
                                z = ((tmp >> 14) & ((2**14)-1))
                                if (z > 0x1fff != 0):
                                    z = -(0x1fff - z)
                                z /= 0x8ff
                            keyframe_values.append([
                                0.0, #x
                                0.0, #y
                                z, #z
                                w, #w
                            ])
                            time_values.append(current_time)
                            current_time += ((tmp >> 28) & ((2**4)-1))
                        keyframe_values = np.array(keyframe_values)
                        #print("12 ", np.linalg.norm(keyframe_values[-1]))
                    elif track_info["encoding"] == 14:
                        keyframe_count = int(round(track_info["array_size"]/6))
                        keyframe_values_raw = []
                        time_values = []
                        current_time = 0
                        for _ in range(keyframe_count):
                            x = self.bs.readBytes_unpackbin(11, 16) / 2047.0
                            y = self.bs.readBytes_unpackbin(11, 16) / 2047.0
                            z = self.bs.readBytes_unpackbin(11, 16) / 2047.0
                            w = self.bs.readBytes_unpackbin(11, 16) / 2047.0
                            time_values.append(current_time)

                            current_time += self.bs.readBytes_unpackbin(4, 16)
                            keyframe_values_raw.append([
                                x, #x
                                y, #y
                                z, #z
                                w, #w
                            ])
                        keyframe_values = np.array(keyframe_values_raw) * coef_a + coef_b
                    elif track_info["encoding"] == 15:
                        keyframe_count = int(round(track_info["array_size"]/5))
                        keyframe_values_raw = []
                        time_values = []
                        current_time = 0
                        for _ in range(keyframe_count):
                            x = self.bs.readBytes_unpackbin(9, 8) / 511.0
                            y = self.bs.readBytes_unpackbin(9, 8) / 511.0
                            z = self.bs.readBytes_unpackbin(9, 8) / 511.0
                            w = self.bs.readBytes_unpackbin(9, 8) / 511.0
                            time_values.append(current_time)

                            current_time += self.bs.readBytes_unpackbin(4, 8)
                            keyframe_values_raw.append([
                                x, #x
                                y, #y
                                z, #z
                                w, #w
                            ])
                        keyframe_values = np.array(keyframe_values_raw) * coef_a + coef_b
                    else:
                        print("UNSUPPORTED ENCODING = ", track_info["encoding"])
                        continue
                    #frame_data_array = [self.bs.readUByte() for _ in range(track_info["array_size"])]



                    
                    bone_action_dict[track_info["bone_id"]][action_type] = {time:value.tolist() for time, value in zip(time_values, keyframe_values)}
                    #break
                    #
                else:
                    bone_action_dict[track_info["bone_id"]][action_type] = {0:track_info["unk_float_array"]}
            if self.basename != "":
                animation_name = self.basename + "_" + str(animation_info["animation_idx"]).zfill(3)
            else:
                animation_name = str(animation_info["animation_idx"]).zfill(3)

            animation_data.append({
                "name":animation_name,
                "bone_action":bone_action_dict
            })
            #break
            #print(bone_action_dict)
        return animation_data
            #self.bs.seek(animation_info["unk_offset1"])
            #array_offset = self.bs.readUInt64()
            #array_counter = self.bs.readUInt64()
            #unk1 = self.bs.readUInt()
            #unk2 = self.bs.readUInt()
            #unk3_length = self.bs.readFloat()
            #unk4_loop = self.bs.readFloat()
            #nu = self.bs.readUInt()
            #h = self.bs.readUInt()
            #nu = self.bs.readUInt()
            #nu = self.bs.readUInt()
            
            #self.bs.seek(array_offset)
            #lv2_infos = []
            #for array_i in range(array_counter):
                #lv2_info = {}
                #lv2_info["array_offset"] = self.bs.readUInt64()
                #lv2_info["array_count"] = self.bs.readUInt64()
                #lv2_info["h2"] = self.bs.readUInt()
                #nu = self.bs.readUInt()
                #lv2_infos.append(lv2_info)
            
            
            #for lv2_info in lv2_infos:
                #lv3_infos = []
                
                #self.bs.seek(lv2_info["array_offset"])
                #for array_i in range(lv2_info["array_count"]):
                    #lv3_info = {}
                    #lv3_info["array_offset"] = self.bs.readUInt64()
                    #lv3_info["array_count"] = self.bs.readUInt64()
                    #lv3_info["h3"] = self.bs.readUInt()
                    #lv3_info["unk1"] = self.bs.readUInt()
                    #lv3_infos.append(lv3_info)
                    #print(hex(lv3_info["array_offset"]), lv3_info["array_count"])
                    
                
                
            #break
                #print(" ", offset_counter)
            #print(unk6, unk7)
        #return []

if __name__ == "__main__":
    parser = LmtParser(path="em050_00.lmt")
    ##parser = LmtParser(path="em001_00.lmt")
    animation_data = parser.read()
    print(animation_data[0]["bone_action"][0])
    
    ##with open("out.json", "w") as json_out:
    #with open("out.json", "w") as json_out:
        #json.dump(animation_data, json_out, indent="\t")
    ##print(mesh_datas[0]["material"])
