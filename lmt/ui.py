import bpy
from bpy.types import Panel
from bpy_extras.io_utils import ImportHelper, ExportHelper
import addon_utils

import os

import logging
logger = logging.getLogger("mhworld_import")

from .lmt_loader import load_lmt

def SetLoggingLevel(level):
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)
    elif level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif level == "ERROR":
        logger.setLevel(logging.ERROR)
        
class IMPORT_PT_LmtSettingPanel_1(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Import Settings"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHWORLD_IMPORT_OT_mhworld_lmt"

    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'set_fake_user')

class ImportLmt(bpy.types.Operator, ImportHelper):
    """Import from Lmt file format (.lmt)"""
    bl_idname = "mhworld_import.mhworld_lmt"
    bl_label = 'Import MHWorld Lmt'
    bl_options = {'UNDO'}
    filename_ext = ".lmt"
    
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    filter_glob: bpy.props.StringProperty(default="*.lmt")
    set_fake_user: bpy.props.BoolProperty(name="Keep animations on file save", description="Unused animations are deleted when a .blend file is saved unless explicitely set not to (this is a vanilla blender behavior). Enabling this will flag the imported animations to not lose them.", default=False)

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
        
        selected_objects = context.selected_objects
        armature = None
        for obj in selected_objects:
            if obj.type == "ARMATURE":
                armature = obj
                break
        if armature is None:
            self.report({"ERROR"}, "No armature selected! ")
            return {"CANCELLED"}
        
        for filepath in filepaths:
            import traceback
            try:
                load_lmt(filepath, armature.data, set_fake_user=self.set_fake_user)
            except Exception as e:
                logger.error("Error while loading lmt " + filepath + ", reason = " + str(e))
                self.report({"ERROR"}, "Error while loading lmt " + filepath + ", reason = " + str(e))
                traceback.print_exc()
                return {"CANCELLED"}
        return {"FINISHED"}
