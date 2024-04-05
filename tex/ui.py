import bpy
from bpy.types import Panel
from bpy_extras.io_utils import ImportHelper, ExportHelper
import addon_utils

import os

import logging
logger = logging.getLogger("mhworld_import")

from .tex_loader import load_tex

def SetLoggingLevel(level):
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)
    elif level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif level == "ERROR":
        logger.setLevel(logging.ERROR)

class IMPORT_PT_TexSettingPanel_1(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Import Settings"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHWORLD_IMPORT_OT_mhworld_tex"
    
    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator
        

class IMPORT_PT_TexSettingPanel_2(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Texture Settings"
    bl_parent_id = "IMPORT_PT_TexSettingPanel_1"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHWORLD_IMPORT_OT_mhworld_tex"

    def draw(self, context):
        layout = self.layout
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        layout.prop(operator, 'use_png_cache')
        row = layout.row()
        row.enabled = operator.use_png_cache
        row.prop(operator, 'overwrite_png_cache')


class ImportTex(bpy.types.Operator, ImportHelper):
    """Import from Tex file format (.tex.*)"""
    bl_idname = "mhworld_import.mhworld_tex"
    bl_label = 'Import MHWorld Tex'
    bl_options = {'UNDO'}
    filename_ext = ".tex"
    
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    filter_glob: bpy.props.StringProperty(default="*.tex")
    use_png_cache: bpy.props.BoolProperty(name="Use PNG cache", description="Save a copy of imported .tex in a .png file next to it (subsequent imports will be much faster)", default=False)
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
        for filepath in filepaths:
            self.import_tex(filepath)
        return {"FINISHED"}
    
    def import_tex(self, filepath):
        load_tex(filepath, use_loaded=False, use_png_cache=self.use_png_cache, overwrite_png_cache=self.overwrite_png_cache)

        
