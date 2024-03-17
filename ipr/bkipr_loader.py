import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

import os
import logging
import math

from .bkipr_parser import BkiprParser
from .ipr_parser import IprParser
from ..common.object_loader import load_object_instances

logger = logging.getLogger("mhworld_import")

def load_bkipr(game_path, filepath, LOD=0, mesh_cache={}, mesh_hashes={}, import_material=True, use_png_cache=True, overwrite_png_cache=False):
    parser = BkiprParser(path=filepath)
    obj_instances, dependencies = parser.read()
    # Ugh
    obj_instances = []
    for dependency in dependencies:
        if os.path.exists(os.path.join(game_path, dependency + ".ipr")):
            #print(os.path.join(game_path, dependency + ".ipr"))
            parser_dep = IprParser(path=os.path.join(game_path, dependency + ".ipr"))
            instances = parser_dep.read()
            #print(len(instances))
            obj_instances.extend(instances)
        else:
            print("Dependency doesn't exists: ", os.path.join(game_path, dependency + ".ipr"))

    scn_name = os.path.basename(filepath)
    master_collection = bpy.context.scene.collection

    #if scn_name not in bpy.data.collections.keys():
    scene_collection = bpy.data.collections.new(scn_name)
    master_collection.children.link(scene_collection)
    #else:
        #scene_collection = bpy.data.collections[scn_name]

    zone_names = []
    zone_collection_dict = {}
    for obj_instance in obj_instances:
        if obj_instance["zone"] not in zone_names:
            zone_names.append(obj_instance["zone"])
    for zone_name in zone_names:
        zone_collection = bpy.data.collections.new(zone_name)
        scene_collection.children.link(zone_collection)
        zone_collection_dict[zone_name] = zone_collection
    #obj_instances = []
    #[obj_instances.append(x) for x in obj_instances_raw if x not in obj_instances]

    return load_object_instances(obj_instances, scene_collection, game_path, LOD, mesh_cache, mesh_hashes, zone_collection_dict=zone_collection_dict, load_materials=import_material, use_png_cache=use_png_cache, overwrite_png_cache=overwrite_png_cache)

