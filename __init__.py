bl_info = {
    "name": "MHWorld tool suite",
    "blender": (3, 6, 0),
    "version": (1, 3, 5),
    "category": "Import-Export",
}

import bpy
from bpy.types import Context, Menu, Panel, Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper

import os
import platform
import numpy as np
import logging
logger = logging.getLogger("mhworld_import")
import sys

from .ipr.ui import IMPORT_PT_BkiprSettingPanel_1
from .ipr.ui import IMPORT_PT_BkiprSettingPanel_2
from .ipr.ui import ImportBkipr

from .ipr.ui import IMPORT_PT_IprSettingPanel_1
from .ipr.ui import IMPORT_PT_IprSettingPanel_2
from .ipr.ui import ImportIpr

from .sdl.ui import IMPORT_PT_SdlSettingPanel_1
from .sdl.ui import IMPORT_PT_SdlSettingPanel_2
from .sdl.ui import ImportSdl

from .sobj.ui import IMPORT_PT_SobjSettingPanel_1
from .sobj.ui import IMPORT_PT_SobjSettingPanel_2
from .sobj.ui import ImportSobj

from .sobj.ui import IMPORT_PT_SobjlSettingPanel_1
from .sobj.ui import IMPORT_PT_SobjlSettingPanel_2
from .sobj.ui import ImportSobjl

from .mod3.ui import IMPORT_PT_Mod3SettingPanel_1
from .mod3.ui import IMPORT_PT_Mod3SettingPanel_2
from .mod3.ui import ImportMod3

from .tex.ui import IMPORT_PT_TexSettingPanel_1
from .tex.ui import IMPORT_PT_TexSettingPanel_2
from .tex.ui import ImportTex

from .lmt.ui import IMPORT_PT_LmtSettingPanel_1
from .lmt.ui import ImportLmt

class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ANSI Coloring
        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        _reset = "\x1b[0m"
        self.FORMATS = {
            logging.DEBUG: f"{grey}{self._fmt}{_reset}",
            logging.INFO: f"{grey}{self._fmt}{_reset}",
            logging.WARNING: f"{yellow}{self._fmt}{_reset}",
            logging.ERROR: f"{red}{self._fmt}{_reset}",
            logging.CRITICAL: f"{bold_red}{self._fmt}{_reset}"
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)s | %(message)s')
colored_formatter = formatter
is_windows = platform.system() == "Windows"
if not (is_windows and int(platform.release()) < 10):
    if is_windows:
        os.system("color")
    colored_formatter = ColoredFormatter('%(levelname)s | %(message)s')
handler.setFormatter(colored_formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class CustomAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    game_path: bpy.props.StringProperty(
        name="Unpacked game path",
        subtype='DIR_PATH',
    )
    
    logging_level: bpy.props.EnumProperty(
        name="Logging level",
        items = [('DEBUG','DEBUG','','',0), 
                 ('INFO','INFO','','',1),
                 ('WARNING','WARNING','','',2),
                 ('ERROR','ERROR','','',3)],
        default = 'INFO'
    )
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Path to the unpacked game (Up to the root folder of the game, for example \"C:\\XXX\\chunk\\_\")")
        layout.prop(self, "game_path")
        
        layout.prop(self, "logging_level")


def menu_func_import(self, context):
    self.layout.operator(ImportBkipr.bl_idname, text="MHWorld bulk map instance object files (.bkipr)", icon="WORLD_DATA")
    self.layout.operator(ImportIpr.bl_idname, text="MHWorld map instance object files (.ipr)", icon="WORLD_DATA")
    self.layout.operator(ImportSdl.bl_idname, text="MHWorld map static object files (.sdl)", icon="WORLD_DATA")
    self.layout.operator(ImportSobjl.bl_idname, text="MHWorld bulk map interactible object files (.sobjl)", icon="WORLD_DATA")
    self.layout.operator(ImportSobj.bl_idname, text="MHWorld map interactible object files (.sobj)", icon="WORLD_DATA")
    self.layout.operator(ImportMod3.bl_idname, text="MHWorld model files (.mod3)", icon="MESH_DATA")
    self.layout.operator(ImportTex.bl_idname, text="MHWorld texture files (.tex)", icon="TEXTURE_DATA")
    self.layout.operator(ImportLmt.bl_idname, text="MHWorld animation files (.lmt)", icon="ANIM_DATA")

def register():
    bpy.utils.register_class(ImportBkipr)
    bpy.utils.register_class(ImportIpr)
    bpy.utils.register_class(ImportSdl)
    bpy.utils.register_class(ImportSobj)
    bpy.utils.register_class(ImportSobjl)
    bpy.utils.register_class(ImportMod3)
    bpy.utils.register_class(ImportTex)
    bpy.utils.register_class(ImportLmt)
    bpy.utils.register_class(CustomAddonPreferences)
    bpy.utils.register_class(IMPORT_PT_BkiprSettingPanel_1)
    bpy.utils.register_class(IMPORT_PT_BkiprSettingPanel_2)
    bpy.utils.register_class(IMPORT_PT_IprSettingPanel_1)
    bpy.utils.register_class(IMPORT_PT_IprSettingPanel_2)
    bpy.utils.register_class(IMPORT_PT_SdlSettingPanel_1)
    bpy.utils.register_class(IMPORT_PT_SdlSettingPanel_2)
    bpy.utils.register_class(IMPORT_PT_SobjSettingPanel_1)
    bpy.utils.register_class(IMPORT_PT_SobjSettingPanel_2)
    bpy.utils.register_class(IMPORT_PT_SobjlSettingPanel_1)
    bpy.utils.register_class(IMPORT_PT_SobjlSettingPanel_2)
    bpy.utils.register_class(IMPORT_PT_Mod3SettingPanel_1)
    bpy.utils.register_class(IMPORT_PT_Mod3SettingPanel_2)
    bpy.utils.register_class(IMPORT_PT_TexSettingPanel_1)
    bpy.utils.register_class(IMPORT_PT_TexSettingPanel_2)
    bpy.utils.register_class(IMPORT_PT_LmtSettingPanel_1)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    pass

def unregister():
    bpy.utils.unregister_class(ImportBkipr)
    bpy.utils.unregister_class(ImportIpr)
    bpy.utils.unregister_class(ImportSdl)
    bpy.utils.unregister_class(ImportSobj)
    bpy.utils.unregister_class(ImportSobjl)
    bpy.utils.unregister_class(ImportMod3)
    bpy.utils.unregister_class(ImportTex)
    bpy.utils.unregister_class(ImportLmt)
    bpy.utils.unregister_class(CustomAddonPreferences)
    bpy.utils.unregister_class(IMPORT_PT_BkiprSettingPanel_1)
    bpy.utils.unregister_class(IMPORT_PT_BkiprSettingPanel_2)
    bpy.utils.unregister_class(IMPORT_PT_IprSettingPanel_1)
    bpy.utils.unregister_class(IMPORT_PT_IprSettingPanel_2)
    bpy.utils.unregister_class(IMPORT_PT_SdlSettingPanel_1)
    bpy.utils.unregister_class(IMPORT_PT_SdlSettingPanel_2)
    bpy.utils.unregister_class(IMPORT_PT_SobjSettingPanel_1)
    bpy.utils.unregister_class(IMPORT_PT_SobjSettingPanel_2)
    bpy.utils.unregister_class(IMPORT_PT_SobjlSettingPanel_1)
    bpy.utils.unregister_class(IMPORT_PT_SobjlSettingPanel_2)
    bpy.utils.unregister_class(IMPORT_PT_Mod3SettingPanel_1)
    bpy.utils.unregister_class(IMPORT_PT_Mod3SettingPanel_2)
    bpy.utils.unregister_class(IMPORT_PT_TexSettingPanel_1)
    bpy.utils.unregister_class(IMPORT_PT_TexSettingPanel_2)
    bpy.utils.unregister_class(IMPORT_PT_LmtSettingPanel_1)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    pass

