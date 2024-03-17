import bpy
from mathutils import Vector, Matrix, Euler

import os
import logging
import math

from .mod3_parser import Mod3Parser
from ..common.bone_rename import bone_rename

logger = logging.getLogger("mhworld_import")

def load_mod3(filepath, collection=None, LOD=0, fix_rotation=False, fix_scale=False, obj_name="", obj_overload={}, rename_bones=False, connect_bones=False):
    #print(filepath)
    parser = Mod3Parser(path=filepath)
    armature_datas, mesh_datas = parser.read()

    file_name = os.path.basename(filepath)
    file_sname = file_name.split(".")
    if len(file_sname) == 2 and file_sname[1] == "mod3":
        file_name = file_sname[0]

    if collection is None:
        master_collection = bpy.context.scene.collection
        col = bpy.data.collections.new("Col_" + file_name)
        master_collection.children.link(col)
    else:
        col = collection

    returned_objects = []

    armature_object = None
    if armature_datas is not None and len(armature_datas) > 0:
        if obj_name != "":
            armature_name = "Armature_" + obj_name
        else:
            armature_name = "Armature_" + file_name
        armature_data = bpy.data.armatures.new(armature_name)
        armature_object = bpy.data.objects.new(armature_name, armature_data)
        armature_object.show_in_front = True
        armature_object.rotation_mode = "XYZ"
        if fix_rotation:
            armature_object.rotation_euler.rotate(Euler([math.radians(90),0,0]))
        if fix_scale:
            armature_object.scale *= Vector([0.01,0.01,0.01])
        col.objects.link(armature_object)
        if rename_bones:
            armature_data["renamed_bones"] = True

        bpy.context.view_layer.objects.active = armature_object
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        remap_dict = {}
        root_bone = armature_data.edit_bones.new("bone_root")
        root_bone.head = (0.0, 0.0, 0.0)
        root_bone.tail = (0.0, 100.0, 0.0)
        for bone_i, bone_info in enumerate(armature_datas):
            bone_raw_name = "bone_" + str(bone_info["remap"]).zfill(3)
            if rename_bones and bone_raw_name in bone_rename.keys():
                bone_name = bone_rename[bone_raw_name]
            else:
                bone_name = bone_raw_name
                #print("MISSING BONE: ", str(bone_raw_name))
            new_bone = armature_data.edit_bones.new(bone_name)
            remap_dict[bone_info["id"]] = bone_info["remap"]
            local_matrix = Matrix(bone_info["local_matrix"])
            local_matrix.transpose()
            global_matrix = Matrix(bone_info["global_matrix"])
            global_matrix.transpose()
            new_bone.head = (0.0, 0.0, 0.0)
            new_bone.tail = (bone_info["x"], bone_info["y"], bone_info["z"])
            #if Vector([bone_info["x"], bone_info["y"], bone_info["z"]]).length < 0.001:
            new_bone.tail = (0.0, 100.0, 0.0)

            if bone_info["parent"] != 255:
                bone_parent_raw_name = "bone_" + str(remap_dict[bone_info["parent"]]).zfill(3)
                if rename_bones and bone_parent_raw_name in bone_rename.keys():
                    bone_parent_name = bone_rename[bone_parent_raw_name]
                else:
                    bone_parent_name = bone_parent_raw_name
                new_bone.parent = armature_data.edit_bones[bone_parent_name]
                new_bone.matrix = new_bone.parent.matrix @ local_matrix
            else:
                new_bone.parent = root_bone
                new_bone.matrix = new_bone.matrix @ local_matrix
            new_bone.inherit_scale = "NONE"

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        for bone in armature_data.bones:
            if bone.parent is not None:
                #inter_bone_rot_diff =
                bone["baserots"] = bone.matrix.inverted().to_quaternion()
                bone["baseposs"] = (bone.parent.matrix_local.inverted() @ bone.matrix_local).to_translation()
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        for bone_i, bone_info in enumerate(armature_datas):
            bone_raw_name = "bone_" + str(bone_info["remap"]).zfill(3)
            if rename_bones and bone_raw_name in bone_rename.keys():
                bone_name = bone_rename[bone_raw_name]
            else:
                bone_name = bone_raw_name
            new_bone = armature_data.edit_bones[bone_name]
            if bone_info["length"] > 0.01:
                new_bone.tail = new_bone.head + (new_bone.tail-new_bone.head)*bone_info["length"]*0.01




            if connect_bones:
                if new_bone.children is not None:
                    if len(new_bone.children) == 1 and (new_bone.children[0].head-new_bone.head).length > 0.0001:
                        new_bone.tail = new_bone.children[0].head
                    elif len(new_bone.children) == 0:
                        if new_bone.parent is not None:
                            parent_vector = new_bone.parent.tail - new_bone.parent.head
                            new_bone.tail = new_bone.head + (parent_vector.normalized()*(new_bone.head-new_bone.tail).length)
                    elif len(new_bone.children) > 1:
                        def recursive_seek_children(bone):
                            return 1+sum([recursive_seek_children(child) for child in bone.children])
                        best_child = None
                        best_child_score = 0
                        for child in new_bone.children:
                            if abs(new_bone.head.x) < 0.0001 and abs(child.head.x) > 0.0001:
                                continue
                            if (child.head-new_bone.head).length > 0.0001:
                                child_amount = recursive_seek_children(child)
                                if child_amount > best_child_score:
                                    best_child = child
                                    best_child_score = child_amount
                        if best_child is not None:
                            new_bone.tail = best_child.head




        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        returned_objects.append(armature_object)

    for mesh_data in mesh_datas:
        if mesh_data["lod"] == LOD:
            mesh_prefix = "LOD" + str(LOD) + "_G" + str(mesh_data["group"]) + "_I" + str(mesh_data["id"])
            if obj_name != "":
                meshName = mesh_prefix + "_" + obj_name
            else:
                meshName = mesh_prefix + "_" + file_name
            mesh = bpy.data.meshes.new(meshName)  # add the new mesh
            obj = bpy.data.objects.new(mesh.name, mesh)
            col.objects.link(obj)
            obj.rotation_mode = "XYZ"
            if fix_scale and (armature_datas is None or len(armature_datas) == 0):
                obj.scale *= Vector([0.01,0.01,0.01])
            mesh.from_pydata(mesh_data["positions"], [], mesh_data["faces"])

            if armature_object is not None:
                obj.parent = armature_object
                armature_mod = obj.modifiers.new("Armature", 'ARMATURE')
                armature_mod.object = armature_object
            else:
                if fix_rotation:
                    obj.rotation_euler.rotate(Euler([math.radians(90),0,0]))

            material_name = obj_name + mesh_data["material"]

            if "material_suffix" in obj_overload.keys():
                material_name += obj_overload["material_suffix"]

            if len(material_name) > 55:
                #FUCK blender
                material_name = "HASHED_" + str(abs(int(hash(material_name)))).zfill(20)



            if material_name not in bpy.data.materials:
                mat = bpy.data.materials.new(name=material_name)
            else:
                mat = bpy.data.materials[material_name]
            mat["original_name"] = mesh_data["material"]
            #print(mesh_data["material_name_hash"])
            mat["name_hash"] = str(mesh_data["material_name_hash"])
            mesh.materials.append(mat)
            mat_slot = obj.material_slots[0]
            mat_slot.link = 'OBJECT'
            mat_slot.material = mat

            bpy.context.view_layer.objects.active = obj

            mesh.create_normals_split()
            mesh.polygons.foreach_set("use_smooth", [True]*len(mesh.polygons))
            mesh.normals_split_custom_set_from_vertices(mesh_data["normals"])
            mesh.use_auto_smooth = True
            mesh.free_normals_split()

            if "weights_names" in mesh_data.keys() and "weights_values" in mesh_data.keys():
                used_bones = []
                for vert_weight_name in mesh_data["weights_names"]:
                    for weight_name_raw in vert_weight_name:
                        if rename_bones and weight_name_raw in bone_rename.keys():
                            weight_name = bone_rename[weight_name_raw]
                        else:
                            weight_name = weight_name_raw
                        if weight_name not in used_bones:
                            used_bones.append(weight_name)
                vertex_weight_dict = {}
                for bone_name in used_bones:
                    vertex_weight_dict[bone_name] = obj.vertex_groups.new(name=bone_name)
                for vertice, weights_name, weights_value in zip(mesh.vertices, mesh_data["weights_names"], mesh_data["weights_values"]):
                    for weight_name_raw, weight_value in zip(weights_name, weights_value):
                        if rename_bones and weight_name_raw in bone_rename.keys():
                            weight_name = bone_rename[weight_name_raw]
                        else:
                            weight_name = weight_name_raw
                        if weight_value != 0.0:
                            vertex_weight_dict[weight_name].add([vertice.index], weight_value, 'ADD')

            if "UVs" in mesh_data.keys():
                #print(mesh_data["UVs"][0][0])
                #print(mesh_data["UVs"][1][0])
                for UV_i, UV in enumerate(mesh_data["UVs"]):
                    uv_layer = mesh.uv_layers.new(name='UV' + str(UV_i+1))
                    for face in mesh.polygons:
                        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                            uv_layer.data[loop_idx].uv = UV[vert_idx]

            if "colors" in mesh_data.keys():
                color_layer = mesh.color_attributes.new(
                    name="Attribute",
                    type='BYTE_COLOR',
                    domain='CORNER',
                )
                color_layer.name = "Attribute"
                for face in mesh.polygons:
                    for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                        color_layer.data[loop_idx].color = [x/255.0 for x in mesh_data["colors"][vert_idx]]

            returned_objects.append(obj)

    return returned_objects
