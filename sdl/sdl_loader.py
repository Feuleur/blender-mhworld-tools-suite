import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

import os
import logging
import math

from .sdl_parser import SdlParser
from ..common.object_loader import load_object_instances

logger = logging.getLogger("mhworld_import")

def load_sdl(game_path, filepath, LOD=0, mesh_cache={}, mesh_hashes={}, import_material=True, use_png_cache=True, overwrite_png_cache=False):
    parser = SdlParser(path=filepath)

    obj_instances, dependencies = parser.read(recursive=True)
    while True:
        if len(dependencies) == 0:
            break
        next_dependancy = dependencies.pop(0)
        logger.info("Loading dependency: " + str(next_dependancy))
        if os.path.exists(os.path.join(game_path, next_dependancy + ".sdl")):
            next_parser = SdlParser(path=os.path.join(game_path, next_dependancy + ".sdl"))
            instances, next_dependencies = next_parser.read(recursive=True)
            #logger.info("Found dependency: " + str(next_dependencies))
            obj_instances.extend(instances)
            dependencies.extend(next_dependencies)



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

    return load_object_instances(obj_instances, scene_collection, game_path, LOD, mesh_cache, mesh_hashes, zone_collection_dict=zone_collection_dict, load_materials=import_material, use_png_cache=use_png_cache, overwrite_png_cache=overwrite_png_cache)
