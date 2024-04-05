import bpy
from bpy.types import Panel
from bpy_extras.io_utils import ImportHelper, ExportHelper

import os

import logging
logger = logging.getLogger("mhworld_import")

from .sdl_loader import load_sdl

class IMPORT_PT_SdlSettingPanel_1(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Import Settings"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHWORLD_IMPORT_OT_mhworld_sdl"

    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'LOD')
        layout.prop(operator, 'import_material')


class IMPORT_PT_SdlSettingPanel_2(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Texture Settings"
    bl_parent_id = "IMPORT_PT_SdlSettingPanel_1"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHWORLD_IMPORT_OT_mhworld_sdl"

    def draw(self, context):
        layout = self.layout

        sfile = context.space_data
        operator = sfile.active_operator
        layout.enabled = operator.import_material
        layout.prop(operator, 'use_png_cache')
        row = layout.row()
        row.enabled = operator.use_png_cache
        row.prop(operator, 'overwrite_png_cache')

def SetLoggingLevel(level):
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)
    elif level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif level == "ERROR":
        logger.setLevel(logging.ERROR)
        
class ImportSdl(bpy.types.Operator, ImportHelper):
    """Import from Sdl file format (.sdl)"""
    bl_idname = "mhworld_import.mhworld_sdl"
    bl_label = 'Import MHWorld Sdl'
    bl_options = {'UNDO'}
    filename_ext = ".sdl"

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    filter_glob: bpy.props.StringProperty(default="*.sdl")
    LOD: bpy.props.IntProperty(name="LoD", description="Import a specific Level of Detail (lower is more detailed)", default=0, min=0, max=10, step=1)
    import_material: bpy.props.BoolProperty(name="Import material", description="Import the material .mrl3 files",  default=True)
    use_png_cache: bpy.props.BoolProperty(name="Use PNG cache", description="Save a copy of imported .tex in a .png file next to it (subsequent imports will be much faster)", default=True)
    overwrite_png_cache: bpy.props.BoolProperty(name="Overwrite PNG cache", description="Overwrite cached .png", default=False)

    def draw(self, context):
        pass

    def execute(self, context):
        candidate_modules = [mod for mod in addon_utils.modules() if mod.bl_info["name"] == "MHWorld tool suite"]
        if len(candidate_modules) > 1:
            logger.warning("Inconsistencies while loading the addon preferences: make sure you don't have multiple versions of the addon installed.")
        mod = candidate_modules[0]
        addon_prefs = context.preferences.addons[mod.__name__].preferences
        SetLoggingLevel(addon_prefs.logging_level)

        folder = (os.path.dirname(self.filepath))
        filepaths = [os.path.join(folder, x.name) for x in self.files]


        if addon_prefs.game_path == "":
            self.report({"ERROR"}, "The game path needs to be set in the addon preferences to import map files.")
            return {"CANCELLED"}

        if self.import_material:
            logger.info("Linking node groups...")
            node_group_blend_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mrl3", "materials_groups.blend")
            if not os.path.exists(node_group_blend_file):
                self.report({"ERROR"}, "Could not access node group .blend file")
                return {"CANCELLED"}
            logger.info("Importing nodes...")
            installed = [i.name for i in bpy.data.node_groups]
            por = []
            with bpy.data.libraries.load(node_group_blend_file, link = False) as (data_from, data_to):
                for i in data_from.node_groups:
                    if not i in installed:
                        por.append(i)
                data_to.node_groups = por

        mesh_cache = {}
        logger.info("Building mesh hashes...")
        mesh_hashes = {}
        for mesh_name in bpy.data.meshes.keys():
            mesh_hashes[mesh_name] = hash(str([x.co for x in bpy.data.meshes[mesh_name].vertices]))

        for filepath in filepaths:
            load_sdl(addon_prefs.game_path, filepath, LOD=self.LOD, mesh_cache=mesh_cache, mesh_hashes=mesh_hashes, import_material=self.import_material, use_png_cache=self.use_png_cache, overwrite_png_cache=self.overwrite_png_cache)
        return {"FINISHED"}
