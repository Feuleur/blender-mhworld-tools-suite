import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

import os
import logging
import math

from .ipr_parser import IprParser
from ..common.object_loader import load_object_instances

logger = logging.getLogger("mhworld_import")

def load_ipr(game_path, filepath, LOD=0, mesh_cache={}, mesh_hashes={}, import_material=True, use_png_cache=True, overwrite_png_cache=False):
    parser = IprParser(path=filepath)
    obj_instances = parser.read()

    scn_name = os.path.basename(filepath)
    master_collection = bpy.context.scene.collection
    if scn_name not in bpy.data.collections.keys():
        scene_collection = bpy.data.collections.new(scn_name)
        master_collection.children.link(scene_collection)
    else:
        scene_collection = bpy.data.collections[scn_name]

    return load_object_instances(obj_instances, scene_collection, game_path, LOD, mesh_cache, mesh_hashes, load_materials=import_material, use_png_cache=use_png_cache, overwrite_png_cache=overwrite_png_cache)

