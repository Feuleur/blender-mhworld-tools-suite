import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

import os
import logging
import math

from .sobj_loader import load_sobj
from .sobjl_parser import SobjlParser
from ..common.object_loader import load_object_instances

logger = logging.getLogger("mhworld_import")

def load_sobjl(game_path, filepath, LOD=0, mesh_cache={}, mesh_hashes={}, import_material=True, use_png_cache=True, overwrite_png_cache=False):

    parser = SobjlParser(path=filepath)
    dependencies = parser.read()
    object_instances = []

    scn_name = os.path.basename(filepath)
    master_collection = bpy.context.scene.collection
    sobjl_collection = bpy.data.collections.new(scn_name)
    master_collection.children.link(sobjl_collection)

    for dependency in dependencies:
        if os.path.exists(os.path.join(game_path, dependency + ".sobj")):
            #try:
            object_instances.extend(load_sobj(
                game_path=game_path,
                filepath=os.path.join(game_path, dependency + ".sobj"),
                LOD=LOD,
                mesh_cache=mesh_cache,
                mesh_hashes=mesh_hashes,
                import_material=import_material,
                use_png_cache=use_png_cache,
                overwrite_png_cache=overwrite_png_cache,
                override_collection = sobjl_collection
            ))
            #except:
                #logger.warning("Error while importing sobj (path=" + os.path.join(game_path, dependency + ".sobj") + ")")
        else:
            logger.warning("Dependency doesn't exists: ", os.path.join(game_path, dependency + ".sobj"))
    return object_instances

