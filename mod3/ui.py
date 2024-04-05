import bpy
from bpy.types import Panel
from bpy_extras.io_utils import ImportHelper, ExportHelper

import os
import traceback
import logging
logger = logging.getLogger("mhworld_import")

from .mod3_loader import load_mod3
from ..mrl3.mrl3_loader import load_mrl3
from ..common.apply_geonode import apply_VM_geonode

def SetLoggingLevel(level):
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)
    elif level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif level == "ERROR":
        logger.setLevel(logging.ERROR)

class IMPORT_PT_Mod3SettingPanel_1(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Import Settings"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHWORLD_IMPORT_OT_mhworld_mod3"
    
    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator
        
        layout.prop(operator, 'LOD')
        layout.prop(operator, 'fix_rotation')
        layout.prop(operator, 'fix_scale')
        layout.prop(operator, 'rename_bones')
        layout.prop(operator, 'connect_bones')
        layout.prop(operator, 'import_material')
        layout.prop(operator, 'add_VM_geonode')


class IMPORT_PT_Mod3SettingPanel_2(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Texture Settings"
    bl_parent_id = "IMPORT_PT_Mod3SettingPanel_1"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHWORLD_IMPORT_OT_mhworld_mod3"

    def draw(self, context):
        layout = self.layout
        
        sfile = context.space_data
        operator = sfile.active_operator
        layout.enabled = operator.import_material
        layout.prop(operator, 'use_png_cache')
        row = layout.row()
        row.enabled = operator.use_png_cache
        row.prop(operator, 'overwrite_png_cache')


class ImportMod3(bpy.types.Operator, ImportHelper):
    """Import from Mod3 file format (.mod3)"""
    bl_idname = "mhworld_import.mhworld_mod3"
    bl_label = 'Import MHWorld Mod3'
    bl_options = {'UNDO'}
    filename_ext = ".mod3"
    
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    filter_glob: bpy.props.StringProperty(default="*.mod3")
    LOD: bpy.props.IntProperty(name="LoD", description="Import a specific Level of Detail (lower is more detailed)", default=0, min=0, max=10, step=1)
    fix_rotation: bpy.props.BoolProperty(name="Fix rotation", description="Rotate the mesh 90° to fit blender's frame of reference",  default=True)
    fix_scale: bpy.props.BoolProperty(name="Fix scale", description="Scale the mesh x0.01 to fit blender's frame of reference",  default=True)
    rename_bones: bpy.props.BoolProperty(name="Rename bones", description="Try to apply names to the bones instead of indices. May break animations sometimes. ",  default=False)
    connect_bones: bpy.props.BoolProperty(name="Connect bones", description="Connect the bones to their children when available. WILL break animations. ",  default=False)
    import_material: bpy.props.BoolProperty(name="Import material", description="Import the material .mrl3 file",  default=True)
    add_VM_geonode: bpy.props.BoolProperty(name="Import VM geonode", description="Import the VM textures as a geonode modifier",  default=True)
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
        
        if self.files:
            folder = (os.path.dirname(self.filepath))
            filepaths = [os.path.join(folder, x.name) for x in self.files]
        else:
            filepaths = [str(self.filepath)]

        if addon_prefs.game_path == "" and self.import_material:
            self.report({"ERROR"}, "Import material was enabled, while the game path in not set in the addon preferences")
            return {"CANCELLED"}

        if self.import_material:
            logger.info("Linking node groups...")
            node_group_blend_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mrl3", "materials_groups.blend")
            #print(node_group_blend_file)
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

        for filepath in filepaths:
            objs = load_mod3(filepath, collection=None, LOD=self.LOD, fix_rotation=self.fix_rotation, fix_scale=self.fix_scale, rename_bones=self.rename_bones, connect_bones=self.connect_bones)
            if self.import_material:
                mrl3_filepath = ".".join(filepath.split(".")[:-1]) + ".mrl3"

                try:
                    load_mrl3(addon_prefs.game_path, mrl3_filepath, use_loaded_mat=False, use_loaded_tex=True, use_png_cache=self.use_png_cache, overwrite_png_cache=self.overwrite_png_cache)
                    if self.add_VM_geonode:
                        for obj in objs:
                            apply_VM_geonode(obj)
                except Exception as e:
                    logger.warning("Unable to load material of path " + str(mrl3_filepath) + ", reason = " + str(e))
                    self.report({"WARNING"}, "Unable to load material of path " + str(mrl3_filepath) + ", reason = " + str(e))
                    traceback.print_exc()
                    continue
        return {"FINISHED"}


        
