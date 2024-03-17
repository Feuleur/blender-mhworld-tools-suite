import bpy
from mathutils import Quaternion, Vector
import logging
logger = logging.getLogger("mhworld_import")

from .lmt_parser import LmtParser
from ..common.bone_rename import bone_rename

def load_lmt_data(lmt_data, bones_baseposs, bones_baserots, rename_bones=False, set_fake_user=False):
    animation_name = lmt_data["name"]
    action = bpy.data.actions.new(animation_name)
    action.use_fake_user = set_fake_user
    for bone_idx, bone_action in lmt_data["bone_action"].items():
        if bone_idx == -1:
            bone_name_raw = "bone_root"
        else:
            bone_name_raw = "bone_" + str(bone_idx).zfill(3)
        if rename_bones and bone_name_raw in bone_rename.keys():
            bone_name = bone_rename[bone_name_raw]
        else:
            bone_name = bone_name_raw
        if "pos" in bone_action.keys():
            pos_keyframes = bone_action["pos"]
            loc_data_path = "pose.bones[\"" + bone_name + "\"].location"
            fcurve_loc_x = action.fcurves.new(data_path=loc_data_path, index=0)
            fcurve_loc_y = action.fcurves.new(data_path=loc_data_path, index=1)
            fcurve_loc_z = action.fcurves.new(data_path=loc_data_path, index=2)
            for time, values in pos_keyframes.items():
                keyframe_pos = Vector([values[0], values[1], values[2]])
                if bone_name in bones_baseposs and bone_action["pos_referencial"] == "local":
                    keyframe_pos = keyframe_pos - (bones_baseposs[bone_name])

                keyframe = fcurve_loc_x.keyframe_points.insert(frame=int(time),value=keyframe_pos[0])
                keyframe.handle_left_type = "VECTOR"
                keyframe.handle_right_type = "VECTOR"
                keyframe = fcurve_loc_y.keyframe_points.insert(frame=int(time),value=keyframe_pos[1])
                keyframe.handle_left_type = "VECTOR"
                keyframe.handle_right_type = "VECTOR"
                keyframe = fcurve_loc_z.keyframe_points.insert(frame=int(time),value=keyframe_pos[2])
                keyframe.handle_left_type = "VECTOR"
                keyframe.handle_right_type = "VECTOR"
        if "rot" in bone_action.keys():
            rot_keyframes = bone_action["rot"]
            rot_data_path = "pose.bones[\"" + bone_name + "\"].rotation_quaternion"
            fcurve_rot_w = action.fcurves.new(data_path=rot_data_path, index=0)
            fcurve_rot_x = action.fcurves.new(data_path=rot_data_path, index=1)
            fcurve_rot_y = action.fcurves.new(data_path=rot_data_path, index=2)
            fcurve_rot_z = action.fcurves.new(data_path=rot_data_path, index=3)
            previous_quaternion = None
            for time, values in rot_keyframes.items():
                keyframe_rot = Quaternion([values[3], values[0], values[1], values[2]])
                #if bone_name == "bone_155":
                #    print(int(time), keyframe_rot)
                if bone_name in bones_baserots and bone_action["rot_referencial"] == "local":
                    keyframe_rot.rotate(-bones_baserots[bone_name])
                if previous_quaternion is not None:
                   keyframe_rot.make_compatible(previous_quaternion)
                previous_quaternion = keyframe_rot.copy()
                keyframe = fcurve_rot_w.keyframe_points.insert(frame=int(time),value=keyframe_rot[0])
                keyframe.handle_left_type = "VECTOR"
                keyframe.handle_right_type = "VECTOR"
                keyframe = fcurve_rot_x.keyframe_points.insert(frame=int(time),value=keyframe_rot[1])
                keyframe.handle_left_type = "VECTOR"
                keyframe.handle_right_type = "VECTOR"
                keyframe = fcurve_rot_y.keyframe_points.insert(frame=int(time),value=keyframe_rot[2])
                keyframe.handle_left_type = "VECTOR"
                keyframe.handle_right_type = "VECTOR"
                keyframe = fcurve_rot_z.keyframe_points.insert(frame=int(time),value=keyframe_rot[3])
                keyframe.handle_left_type = "VECTOR"
                keyframe.handle_right_type = "VECTOR"
        if "scl" in bone_action.keys():
            scl_keyframes = bone_action["scl"]
            scl_data_path = "pose.bones[\"" + bone_name + "\"].scale"
            fcurve_scl_x = action.fcurves.new(data_path=scl_data_path, index=0)
            fcurve_scl_y = action.fcurves.new(data_path=scl_data_path, index=1)
            fcurve_scl_z = action.fcurves.new(data_path=scl_data_path, index=2)
            for time, values in scl_keyframes.items():
                #if time > mot_data["frame_count"]:
                    #time = 0
                keyframe = fcurve_scl_x.keyframe_points.insert(frame=int(time),value=values[0])
                keyframe.handle_left_type = "VECTOR"
                keyframe.handle_right_type = "VECTOR"
                keyframe = fcurve_scl_y.keyframe_points.insert(frame=int(time),value=values[1])
                keyframe.handle_left_type = "VECTOR"
                keyframe.handle_right_type = "VECTOR"
                keyframe = fcurve_scl_z.keyframe_points.insert(frame=int(time),value=values[2])
                keyframe.handle_left_type = "VECTOR"
                keyframe.handle_right_type = "VECTOR"

def load_lmt(filepath, armature, set_fake_user=False):
    bones_baseposs = {}
    for bone in armature.bones:
        if bone.parent is not None:
            bones_baseposs[bone.name] = (bone.parent.matrix_local.inverted() @ bone.matrix_local).to_translation()
    bones_baserots = {}
    for bone in armature.bones:
        if bone.parent is not None:
            #inter_bone_rot_diff = bone.matrix.inverted().to_quaternion()
            bones_baserots[bone.name] = bone.matrix.inverted().to_quaternion()

    if "renamed_bones" in armature and armature["renamed_bones"]:
        rename_bones = True
    else:
        rename_bones = False

    parser = LmtParser(filepath)
    lmt_datas = parser.read()
    for lmt_data in lmt_datas[:]:
        logger.info("Loading mot " + lmt_data["name"] + "... ")
        load_lmt_data(lmt_data, bones_baseposs, bones_baserots, rename_bones, set_fake_user=set_fake_user)
