import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

import os
import logging
import math
from glob import glob

from .sobj_parser import SobjParser
from ..common.object_loader import load_object_instances

logger = logging.getLogger("mhworld_import")



def load_sobj(game_path, filepath, LOD=0, mesh_cache={}, mesh_hashes={}, use_png_cache=True, import_material=True, overwrite_png_cache=False, override_collection=None):
    parser = SobjParser(path=filepath)
    obj_instances_raw = parser.read()

    ressouce_swap = {
        "gm000_005_00":{
            "model_swap":"cmn005_000_00",
        },
        "gm000_006_00":{
            "model_swap":"cmn002_000_00",
        },
        "gm000_007_00":{
            "model_swap":"cmn002_000_00",
            "textures_swap":{
                "cmn002_000_00_00_BML":"cmn002_000_04_00_BML"
            },
            "material_suffix":"_pur"
        },
        "gm000_010_00":{
            "model_swap":"cmn000_000_00",
        },
        "gm000_012_00":{
            "model_swap":"cmn003_000_00",
        },
        "gm000_021_00":{
            "model_swap":"cmn000_000_00",
            "textures_swap":{
                "cmn000_000_00_00_leaf01_BML":"cmn000_000_01_00_leaf01_BML"
            },
            "material_suffix":"_ant"
        },
        "gm000_022_00":{
            "model_swap":"cmn000_000_00",
            "textures_swap":{
                "cmn000_000_00_00_leaf01_BML":"cmn000_000_02_00_leaf01_BML"
            },
            "material_suffix":"_ivy"
        },
        "gm000_023_00":{
            "model_swap":"cmn001_001_00",
            "material_suffix":"_lat"
        },
        "gm000_024_00":{
            "model_swap":"cmn001_001_00",
            "textures_swap":{
                "cmn001_001_00_00_seed01_BML":"cmn001_001_03_00_seed01_BML"
            },
            "material_suffix":"_bom"
        },
        "gm000_025_00":{
            "model_swap":"cmn002_000_00",
            "textures_swap":{
                "cmn002_000_00_00_BML":"cmn002_000_01_00_BML"
            },
            "material_suffix":"_nit"
        },
        "gm000_026_00":{
            "model_swap":"cmn002_000_00",
            "textures_swap":{
                "cmn002_000_00_00_BML":"cmn002_000_02_00_BML"
            },
            "material_suffix":"_ora"
        },
        "gm000_028_00":{
            "model_swap":"cmn004_000_00",
        },
        "gm000_029_00":{
            "model_swap":"cmn007_000_00",
        },
        "gm000_031_00":{
            "model_swap":"cmn001_001_00",
            "textures_swap":{
                "cmn001_001_00_00_seed01_BML":"cmn001_001_05_00_seed01_BML"
            },
            "material_suffix":"_dra"
        },
        "gm000_042_00":{
            "model_swap":"cmn000_001_00",
            "material_suffix":"_fir"
        },
        "gm000_043_00":{
            "model_swap":"cmn000_001_00",
            "textures_swap":{
                "cmn000_001_00_00_flower01_BML":"cmn000_001_02_00_flower01_BML"
            },
            "material_suffix":"_sle"
        },
        "gm000_044_00":{
            "model_swap":"cmn000_001_00",
            "textures_swap":{
                "cmn000_001_00_00_flower01_BML":"cmn000_001_01_00_flower01_BML"
            },
            "material_suffix":"_sno"
        },
        "gm000_049_00":{
            "model_swap":"cmn000_001_00",
            "textures_swap":{
                "cmn000_001_00_00_flower01_BML":"cmn000_001_03_00_flower01_BML"
            },
            "material_suffix":"_flo"
        },
        "gm000_050_00":{
            "model_swap":"cmn001_000_00",
            "textures_swap":{
                "cmn001_000_00_00_BML":"cmn001_000_04_00_BML"
            },
            "material_suffix":"_smo"
        },
        "gm000_051_00":{
            "model_swap":"cmn002_000_00",
            "textures_swap":{
                "cmn002_000_00_00_BML":"cmn002_000_03_00_BML"
            },
            "material_suffix":"_yel"
        },
        "gm000_052_00":{
            "model_swap":"cmn002_000_00",
            "textures_swap":{
                "cmn002_000_00_00_BML":"cmn002_000_06_00_BML"
            },
            "material_suffix":"_red"
        },
        "gm000_053_00":{
            "model_swap":"cmn002_000_00",
            "textures_swap":{
                "cmn002_000_00_00_BML":"cmn002_000_05_00_BML"
            },
            "material_suffix":"_gre"
        },
        "gm000_054_00":{
            "model_swap":"cmn001_001_00",
            "textures_swap":{
                "cmn001_001_00_00_seed01_BML":"cmn001_001_01_00_seed01_BML"
            },
            "material_suffix":"_nee"
        },
        "gm000_055_00":{
            "model_swap":"cmn001_001_00",
            "textures_swap":{
                "cmn001_001_00_00_seed01_BML":"cmn001_001_04_00_seed01_BML"
            },
            "material_suffix":"_bl1"
        },
        "gm000_056_00":{
            "model_swap":"cmn001_001_00",
            "textures_swap":{
                "cmn001_001_00_00_seed01_BML":"cmn001_001_02_00_seed01_BML"
            },
            "material_suffix":"_sla"
        },
        "gm000_061_00":{
            "model_swap":"cmn001_000_00",
            "textures_swap":{
                "cmn001_000_00_00_BML":"cmn001_000_02_00_BML"
            },
            "material_suffix":"_mig"
        },
        "gm000_062_00":{
            "model_swap":"cmn001_000_00",
            "textures_swap":{
                "cmn001_000_00_00_BML":"cmn001_000_01_00_BML"
            },
            "material_suffix":"_ada"
        },
        "gm000_063_00":{
            "model_swap":"cmn001_000_00",
            "textures_swap":{
                "cmn001_000_00_00_BML":"cmn001_000_03_00_BML"
            },
            "material_suffix":"_dr2"
        },
        "gm000_064_00":{
            "model_swap":"cmn001_000_00",
            "material_suffix":"_nul"
        },
        "gm000_067_00":{
            "model_swap":"cmn003_000_00",
            "textures_swap":{
                "cmn003_000_00_00_BML":"cmn003_000_01_00_BML"
            },
            "material_suffix":"_red"
        },
        "gm000_078_00":{
            "model_swap":"cmn007_001_00",
        },
        "gm000_079_00":{
            "model_swap":"cmn007_002_00",
        },
        "gm000_080_00":{
            "model_swap":"cmn007_003_00",
        },
        "gm000_093_00":{
            "model_swap":"cmn001_001_00",
            "textures_swap":{
                "cmn001_001_00_00_seed01_BML":"cmn001_001_06_00_seed01_BML"
            },
            "material_suffix":"_fla"
        },
        "gm000_094_00":{
            "model_swap":"cmn001_001_00",
            "textures_swap":{
                "cmn001_001_00_00_seed01_BML":"cmn001_001_07_00_seed01_BML"
            },
            "material_suffix":"_bl2"
        },
        "gm000_095_00":{
            "model_swap":"cmn006_000_00",
        },
        "gm000_133_00":{
            "model_swap":"cmn002_000_00",
            "textures_swap":{
                "cmn002_000_00_00_BML":"cmn002_000_07_00_BML"
            },
            "material_suffix":"_whi"
        },

    }

    #swap_dict = {
        #"gm000_005_00": "cmn005_000_00", # honey
        #"gm000_006_00": "cmn002_000_00", # blue mushroom
        #"gm000_007_00": "cmn002_000_00", # toadstool
        #"gm000_010_00": "cmn000_000_00", # herb
        #"gm000_012_00": "cmn003_000_00", # mining outcrop -blue
        #"gm000_021_00": "cmn000_000_00", # antidote herb
        #"gm000_022_00": "cmn000_000_00", # ivy
        #"gm000_023_00": "cmn001_001_00", # latchberry
        #"gm000_024_00": "cmn001_001_00", # bomberry
        #"gm000_025_00": "cmn002_000_00", # nitroshroom
        #"gm000_026_00": "cmn002_000_00", # mandragora
        #"gm000_028_00": "cmn004_000_00", # bonepile
        #"gm000_029_00": "cmn007_000_00", # flowerbed
        #"gm000_031_00": "cmn001_001_00", # dragonstrike nut
        #"gm000_042_00": "cmn000_001_00", # fire herb
        #"gm000_043_00": "cmn000_001_00", # sleep herb
        #"gm000_044_00": "cmn000_001_00", # snow harb
        #"gm000_049_00": "cmn000_001_00", # flowfern
        #"gm000_050_00": "cmn001_000_00", # smokenut
        #"gm000_051_00": "cmn002_000_00", # parashroom
        #"gm000_052_00": "cmn002_000_00", # devil's blight
        #"gm000_053_00": "cmn002_000_00", # exciteshroom
        #"gm000_054_00": "cmn001_001_00", # needleberry
        #"gm000_055_00": "cmn001_001_00", # blastnut
        #"gm000_056_00": "cmn001_001_00", # slashberry
        #"gm000_061_00": "cmn001_000_00", # might seed
        #"gm000_062_00": "cmn001_000_00", # adamant seed
        #"gm000_063_00": "cmn001_000_00", # dragonfell berry
        #"gm000_064_00": "cmn001_000_00", # nulberry
        #"gm000_067_00": "cmn003_000_00", # mining outcrop -red
        #"gm000_078_00": "cmn007_001_00", # unique mushroom colony
        #"gm000_079_00": "cmn007_002_00", # round Cactus
        #"gm000_080_00": "cmn007_003_00", # tough skinned fruit
        #"gm000_093_00": "cmn001_001_00", # flamenut
        #"gm000_094_00": "cmn001_001_00", # blazenut
        #"gm000_095_00": "cmn006_000_00", # spiderweb
        #"gm000_133_00": "cmn002_000_00" # chillshroom
    #}
    obj_instance_i = 0
    obj_instances = []
    for obj_instance_raw in obj_instances_raw:
        obj_instance = obj_instance_raw.copy()
        if obj_instance_raw["name"] in ressouce_swap.keys():
            obj_instance["no_cache"] = True
            obj_instance["name"] = ressouce_swap[obj_instance_raw["name"]]["model_swap"]
            obj_instance["original_name"] = obj_instance_raw["name"]
            if "textures_swap" in ressouce_swap[obj_instance_raw["name"]].keys():
                obj_instance["textures_swap"] = ressouce_swap[obj_instance_raw["name"]]["textures_swap"]
            if "material_suffix" in ressouce_swap[obj_instance_raw["name"]].keys():
                obj_instance["material_suffix"] = ressouce_swap[obj_instance_raw["name"]]["material_suffix"]
        else:
            obj_instance["name"] = obj_instance_raw["name"]

        name_components = obj_instance["name"].split("_")
        primary = name_components[0]
        secondary = name_components[1].zfill(3)
        if len(name_components) > 2:
            tercary = name_components[2].zfill(2)
        else:
            tercary="00"
        tentative_paths = [
            os.path.join(game_path, "Assets/gm/"+primary+"/"+primary+"_"+secondary),
            os.path.join(game_path, "Assets/gm/"+primary+"/"+primary+"_000")
        ]
        candidate_mod3 = []
        for tentative_path in tentative_paths:
            #print(glob(tentative_path+"/**/"+primary+"_"+secondary+".mod3", recursive=True))
            candidate_mod3.extend(glob(tentative_path+"/**/"+primary+"_"+secondary+".mod3", recursive=True))
            candidate_mod3.extend(glob(tentative_path+"/**/"+primary+"_"+secondary+"_"+tercary+".mod3", recursive=True))
        if len(candidate_mod3) > 0:
            obj_instance["path"] = candidate_mod3[0][:-5]
        else:
            obj_instance["as_empty"] = True
            obj_instance["path"] = obj_instance["name"]
            #print("COULD NOT RESOLVE INSTANCE TYPE: ", str(obj_instance_raw["name"]))
            pass
        obj_instances.append(obj_instance)

    scn_name = os.path.basename(filepath)
    if override_collection is not None:
        master_collection = override_collection
    else:
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
