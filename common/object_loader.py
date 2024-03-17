import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

import os
import logging
import math

from ..mod3.mod3_loader import load_mod3
from ..mrl3.mrl3_loader import load_mrl3
logger = logging.getLogger("mhworld_import")

def load_object_instances(obj_instances, scene_collection, game_path, LOD, mesh_cache={}, mesh_hashes={}, zone_collection_dict={}, load_materials=True, use_png_cache=True, overwrite_png_cache=False):
    returned_objects = []
    for obj_instance_i, obj_instance in enumerate(obj_instances[:]):
        if obj_instance_i%100 == 0:
            print("Loading object " + str(obj_instance_i) + " of " + str(len(obj_instances)))
        try:
            obj_name = os.path.basename(obj_instance["path"])

            if obj_instance["zone"] in zone_collection_dict.keys():
                parent_collection = zone_collection_dict[obj_instance["zone"]]
            else:
                parent_collection = scene_collection

            local_collection = bpy.data.collections.new(obj_name)
            parent_collection.children.link(local_collection)

            obj_pos = Vector([obj_instance["position"][0]/100.0, -obj_instance["position"][2]/100.0, obj_instance["position"][1]/100.0])
            obj_rot = Quaternion([obj_instance["rotation"][3], obj_instance["rotation"][0], obj_instance["rotation"][1], obj_instance["rotation"][2]])
            obj_scl = Vector([obj_instance["scale"][0]/100.0, obj_instance["scale"][1]/100.0, obj_instance["scale"][2]/100.0])

            # Need to fix the GM paths
            object_path = None
            if os.path.basename(obj_instance["path"]).lower().startswith("gm"):
                if not os.path.exists(os.path.join(game_path, obj_instance["path"] + ".mod3")):
                    folder_tree_list = obj_instance["path"].split("/")
                    object_path = "Assets/gm/" + "/".join(folder_tree_list[2:4]) + "/mod/" + folder_tree_list[-1]
            if object_path is None:
                mod3_filepath = os.path.join(game_path, obj_instance["path"] + ".mod3")
            else:
                mod3_filepath = os.path.join(game_path, object_path + ".mod3")

            if mod3_filepath in mesh_cache and not ("no_cache" in obj_instance.keys() and obj_instance["no_cache"]):
                cached_obj_datas = mesh_cache[mod3_filepath]
                for cached_obj_data in cached_obj_datas:
                    obj = bpy.data.objects.new(cached_obj_data["object_name"], bpy.data.meshes[mesh_hashes[cached_obj_data["mesh_hash"]]])
                    local_collection.objects.link(obj)
                    obj.location = obj_pos
                    obj.rotation_mode = "QUATERNION"
                    obj.rotation_quaternion = obj_rot
                    obj.rotation_quaternion.rotate(Euler([math.radians(90),0,0]))
                    obj.scale = obj_scl
                    returned_objects.append(obj)

                    #obj.material_slots[0].link = 'OBJECT'
                    obj.material_slots[0].material = bpy.data.materials[cached_obj_data["material_name"]]
            else:
                if not ("as_empty" in obj_instance.keys() and obj_instance["as_empty"]):
                    objs = load_mod3(mod3_filepath, collection=local_collection, LOD=LOD, fix_rotation=False, fix_scale=False, obj_name=obj_name, obj_overload=obj_instance)
                else:
                    empty = bpy.data.objects.new(obj_name + "_empty", None )
                    local_collection.objects.link(empty)
                    empty.rotation_mode = "XYZ"
                    empty.empty_display_size = 100
                    objs = [empty]

                for obj in objs:
                    if obj.type == "MESH":
                        mesh_hash = hash(str([x.co for x in obj.data.vertices]))
                        if mesh_hash in mesh_hashes:
                            to_delete_name = obj.data.name
                            obj.data = bpy.data.meshes[mesh_hashes[mesh_hash]]
                            bpy.data.meshes.remove(bpy.data.meshes[to_delete_name])
                        else:
                            mesh_hashes[mesh_hash] = obj.data.name
                    if obj.parent is None:
                        obj.location = obj_pos
                        obj.rotation_mode = "QUATERNION"
                        obj.rotation_quaternion = obj_rot
                        obj.rotation_quaternion.rotate(Euler([math.radians(90),0,0]))
                        obj.scale = obj_scl
                    returned_objects.append(obj)
                if object_path is None:
                    mrl3_filepath = os.path.join(game_path, obj_instance["path"] + ".mrl3")
                else:
                    mrl3_filepath = os.path.join(game_path, object_path + ".mrl3")
                if load_materials and os.path.exists(mrl3_filepath):
                    try:
                        mats = load_mrl3(game_path, mrl3_filepath, use_loaded_mat=True, use_loaded_tex=True, use_png_cache=use_png_cache, overwrite_png_cache=overwrite_png_cache, mat_prefix=obj_name, obj_overload=obj_instance)
                    except Exception as e:
                        logger.error("Could not load material, exception during parsing (path=" + mrl3_filepath + ", exception=" + str(e) + ")")
                # Put data in cache
                cached_data = []
                cache_compatible = True
                for obj_i, obj in enumerate(objs):
                    if not (obj.type == "MESH"):
                        cache_compatible = False
                        break
                    cached_obj = {}
                    cached_obj["mesh_hash"] = hash(str([x.co for x in obj.data.vertices]))
                    cached_obj["object_name"] = obj.name
                    cached_obj["material_name"] = obj.material_slots[0].material.name
                    cached_data.append(cached_obj)
                if cache_compatible:
                    mesh_cache[mod3_filepath] = cached_data
        except Exception as e:
            path = obj_instance["path"] if "path" in obj_instance.keys() else "UNKNOWN"
            logger.error("Could not load object, exception during loading (path = "+ str(path) + ", exception=" + str(e) + ")")
    print("Object import done.")
    return returned_objects

