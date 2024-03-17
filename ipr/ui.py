import bpy
from bpy.types import Panel
from bpy_extras.io_utils import ImportHelper, ExportHelper

import os

import logging
logger = logging.getLogger("mhworld_import")

from .bkipr_loader import load_bkipr
from .ipr_loader import load_ipr


def SetLoggingLevel(level):
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)
    elif level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif level == "ERROR":
        logger.setLevel(logging.ERROR)
        

class IMPORT_PT_IprSettingPanel_1(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Import Settings"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHWORLD_IMPORT_OT_mhworld_ipr"

    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'LOD')
        layout.prop(operator, 'import_material')


class IMPORT_PT_IprSettingPanel_2(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Texture Settings"
    bl_parent_id = "IMPORT_PT_IprSettingPanel_1"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHWORLD_IMPORT_OT_mhworld_ipr"

    def draw(self, context):
        layout = self.layout

        sfile = context.space_data
        operator = sfile.active_operator
        layout.enabled = operator.import_material
        layout.prop(operator, 'use_png_cache')
        row = layout.row()
        row.enabled = operator.use_png_cache
        row.prop(operator, 'overwrite_png_cache')


        
class ImportIpr(bpy.types.Operator, ImportHelper):
    """Import from Ipr file format (.ipr)"""
    bl_idname = "mhworld_import.mhworld_ipr"
    bl_label = 'Import MHWorld Ipr'
    bl_options = {'UNDO'}
    filename_ext = ".ipr"

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    filter_glob: bpy.props.StringProperty(default="*.ipr")
    LOD: bpy.props.IntProperty(name="LoD", description="Import a specific Level of Detail (lower is more detailed)", default=0, min=0, max=10, step=1)
    import_material: bpy.props.BoolProperty(name="Import material", description="Import the material .mrl3 files",  default=True)
    use_png_cache: bpy.props.BoolProperty(name="Use PNG cache", description="Save a copy of imported .tex in a .png file next to it (subsequent imports will be much faster)", default=True)
    overwrite_png_cache: bpy.props.BoolProperty(name="Overwrite PNG cache", description="Overwrite cached .png", default=False)

    def draw(self, context):
        pass

    def execute(self, context):
        addon_prefs = context.preferences.addons["mhworld_tool_suite"].preferences
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
            load_ipr(addon_prefs.game_path, filepath, LOD=self.LOD, mesh_cache=mesh_cache, mesh_hashes=mesh_hashes, import_material=self.import_material, use_png_cache=self.use_png_cache, overwrite_png_cache=self.overwrite_png_cache)
        return {"FINISHED"}


class IMPORT_PT_BkiprSettingPanel_1(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Import Settings"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHWORLD_IMPORT_OT_mhworld_bkipr"

    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'LOD')
        layout.prop(operator, 'import_material')


class IMPORT_PT_BkiprSettingPanel_2(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Texture Settings"
    bl_parent_id = "IMPORT_PT_BkiprSettingPanel_1"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHWORLD_IMPORT_OT_mhworld_bkipr"

    def draw(self, context):
        layout = self.layout

        sfile = context.space_data
        operator = sfile.active_operator
        layout.enabled = operator.import_material
        layout.prop(operator, 'use_png_cache')
        row = layout.row()
        row.enabled = operator.use_png_cache
        row.prop(operator, 'overwrite_png_cache')


        
class ImportBkipr(bpy.types.Operator, ImportHelper):
    """Import from Bkipr file format (.bkipr)"""
    bl_idname = "mhworld_import.mhworld_bkipr"
    bl_label = 'Import MHWorld Bkipr'
    bl_options = {'UNDO'}
    filename_ext = ".bkipr"

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    filter_glob: bpy.props.StringProperty(default="*.bkipr")
    LOD: bpy.props.IntProperty(name="LoD", description="Import a specific Level of Detail (lower is more detailed)", default=0, min=0, max=10, step=1)
    import_material: bpy.props.BoolProperty(name="Import material", description="Import the material .mrl3 files",  default=True)
    use_png_cache: bpy.props.BoolProperty(name="Use PNG cache", description="Save a copy of imported .tex in a .png file next to it (subsequent imports will be much faster)", default=True)
    overwrite_png_cache: bpy.props.BoolProperty(name="Overwrite PNG cache", description="Overwrite cached .png", default=False)

    def draw(self, context):
        pass

    def execute(self, context):
        addon_prefs = context.preferences.addons["mhworld_tool_suite"].preferences
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
            load_bkipr(addon_prefs.game_path, filepath, LOD=self.LOD, mesh_cache=mesh_cache, mesh_hashes=mesh_hashes, import_material=self.import_material, use_png_cache=self.use_png_cache, overwrite_png_cache=self.overwrite_png_cache)
        return {"FINISHED"}
