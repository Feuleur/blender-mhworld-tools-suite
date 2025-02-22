import bpy
from mathutils import Matrix, Vector

import numpy as np
import os
import logging

from .mrl3_parser import Mrl3Parser
from ..tex.tex_loader import load_tex

logger = logging.getLogger("mhworld_import")

def string_reformat(s):
    if s[0] in ["t", "b", "f", "i"]:
        s = s[1:]
    elif beautified_texture_type.startswith("SS"):
        s = s[2:]
    return s.split("__")[0]

def create_img_node(game_path, nodes, filepath, position, use_loaded_tex=False, use_png_cache=False, overwrite_png_cache=False):
    node_img = nodes.new(type='ShaderNodeTexImage')
    node_img.location = Vector(position)
    
    filepath = filepath.replace("\\", "/")
    new_filepath = os.path.join(game_path, filepath + ".tex")
    if not os.path.isfile(new_filepath):
        logger.warning("Could not load texture, file does not exists (path=" + new_filepath + ")")
        return node_img

    try:
        img = load_tex(new_filepath, use_loaded=use_loaded_tex, use_png_cache=use_png_cache, overwrite_png_cache=overwrite_png_cache)
    except Exception as e:
        if "Texture data format not supported" not in str(e):
            logger.warning("Could not load texture, exception during parsing (path=" + new_filepath + ", exception=" + str(e) + ")")
        img = None
    if img is not None:
        node_img.image = img
        node_img.extension = "REPEAT"

    return node_img

def load_mrl3(game_path, filepath, mod3_mat_hashes={}, use_loaded_mat=False, use_loaded_tex=False, use_png_cache=False, overwrite_png_cache=False, mat_prefix="", beautify=True, obj_overload={}):
    parser = Mrl3Parser(path=filepath)
    mat_dict = parser.read()
    returned_mats = []
    
    existing_mat_hashes = {}
    for material in bpy.data.materials:
        if "original_name" in material.keys() and "name_hash" in material.keys():
            existing_mat_hashes[int(material["name_hash"])] = material["original_name"]
    
    for mat_hashed_name, mat_values in mat_dict.items():


        if mat_hashed_name in mod3_mat_hashes.keys():
            mat_name = mod3_mat_hashes[mat_hashed_name]
        elif mat_hashed_name in existing_mat_hashes.keys():
            mat_name = existing_mat_hashes[mat_hashed_name]
        else:
            continue
            #mat_name = str(mat_hashed_name)
        if "material_suffix" in obj_overload.keys():
            mat_name += obj_overload["material_suffix"]

        mat_name = mat_prefix + mat_name
        if len(mat_name) > 55:
            #FUCK blender
            mat_name = "HASHED_" + str(abs(int(hash(mat_name)))).zfill(20)
        
        if use_loaded_mat:
            if mat_name in bpy.data.materials and bpy.data.materials[mat_name].use_nodes:
                returned_mats.append(bpy.data.materials[mat_name])
                continue
        if mat_name not in bpy.data.materials or bpy.data.materials[mat_name].use_nodes == True:
            mat = bpy.data.materials.new(name=mat_name)
        else:
            mat = bpy.data.materials[mat_name]
        
        if mat.use_nodes == False:
            mat.use_nodes = True
        has_emissive = False

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        general_frame_x = -1650.0
        general_frame_y = 500.0
        property_frame_x = -1400.0
        property_frame_y = 500.0
        texture_frame_x = -1000.0
        texture_frame_y = 500.0
        general_frame = nodes.new(type='NodeFrame')
        general_frame.label = "General"
        property_frame = nodes.new(type='NodeFrame')
        property_frame.label = "Properties"
        texture_frame = nodes.new(type='NodeFrame')
        texture_frame.label = "Texture paths for export are in the custom properties"
        texture_frame.label_size = 12

        node_BSDF = nodes["Principled BSDF"]
        nodes.remove(node_BSDF)
        world_shader_node = nodes.new(type='ShaderNodeGroup')
        world_shader_node.location = Vector((-500.0, 500.0))
        world_shader_node.node_tree = bpy.data.node_groups["WorldShader"]
        world_shader_node.label = "WorldShader"
        node_output = nodes["Material Output"]
        links.new(world_shader_node.outputs["Shader"], node_output.inputs["Surface"])
        links.new(world_shader_node.outputs["Displacement"], node_output.inputs["Displacement"])
        if mat_name.endswith("damage"):
            world_shader_node.inputs["Damage"].default_value = 1.0
            mat.cycles.displacement_method = "BOTH"

        node_UVMap1 = nodes.new(type='ShaderNodeUVMap')
        node_UVMap1.location = Vector((general_frame_x, general_frame_y-0.0))
        node_UVMap1.uv_map = "UV1"
        node_UVMap1.parent = general_frame
        node_UVMap2 = nodes.new(type='ShaderNodeUVMap')
        node_UVMap2.location = Vector((general_frame_x, general_frame_y-100.0))
        node_UVMap2.uv_map = "UV2"
        node_UVMap2.parent = general_frame
        node_UVMap3 = nodes.new(type='ShaderNodeUVMap')
        node_UVMap3.location = Vector((general_frame_x, general_frame_y-200.0))
        node_UVMap3.uv_map = "UV3"
        node_UVMap3.parent = general_frame
        node_UVMap4 = nodes.new(type='ShaderNodeUVMap')
        node_UVMap4.location = Vector((general_frame_x, general_frame_y-300.0))
        node_UVMap4.uv_map = "UV4"
        node_UVMap4.parent = general_frame
        node_VertexColor = nodes.new(type='ShaderNodeVertexColor')
        node_VertexColor.location = Vector((general_frame_x, general_frame_y-400.0))
        node_VertexColor.layer_name = "Attribute"
        node_VertexColor.parent = general_frame
        node_geometry = nodes.new(type='ShaderNodeNewGeometry')
        node_geometry.location = Vector((general_frame_x, general_frame_y-500.0))
        node_geometry.parent = general_frame
        node_object_info = nodes.new(type='ShaderNodeObjectInfo')
        node_object_info.location = Vector((general_frame_x, general_frame_y-700.0))
        node_object_info.parent = general_frame
        
        group_name = mat_values["shader_name"].replace("Local__disclosure", "").replace("CBMhMaterial", "")
        
        if group_name + "_pre" not in bpy.data.node_groups or group_name + "_post" not in bpy.data.node_groups:
            pass
        else:
            mmtr_pre = nodes.new(type='ShaderNodeGroup')
            mmtr_pre.location = Vector((-1200.0, 500.0))
            mmtr_pre.node_tree = bpy.data.node_groups[group_name + "_pre"]
            mmtr_pre.label = group_name
            
            mmtr_post = nodes.new(type='ShaderNodeGroup')
            mmtr_post.location = Vector((-700.0, 500.0))
            mmtr_post.node_tree = bpy.data.node_groups[group_name + "_post"]
            mmtr_post.label = group_name
            for texture_i, texture_type in enumerate(mat_values["textures"].keys()):
                try:
                    texture_path = mat_values["textures"][texture_type]
                    if "textures_swap" in obj_overload.keys() and texture_path.split("\\")[-1] in obj_overload["textures_swap"].keys():
                        texture_path = texture_path.replace(texture_path.split("\\")[-1], obj_overload["textures_swap"][texture_path.split("\\")[-1]])

                    node_position = (texture_frame_x, texture_frame_y)
                    texture_frame_y -= 300.0
                    node_img = create_img_node(game_path, nodes, texture_path, node_position, use_loaded_tex=use_loaded_tex, use_png_cache=use_png_cache, overwrite_png_cache=overwrite_png_cache)
                    node_img.parent = texture_frame

                    image_node_name = string_reformat(texture_type)

                    if image_node_name == "EmissiveMap" and texture_path.split("\\")[-1] not in ["NoImage_EM", "null_black"]:
                        has_emissive = True

                    #if beautify:
                    node_img.label = image_node_name
                    #else:
                        #node_img.label = texture_type
                    try:
                        links.new(mmtr_pre.outputs["vector_" + image_node_name], node_img.inputs["Vector"])
                        links.new(node_img.outputs["Color"], mmtr_post.inputs[image_node_name + "_RGB"])
                        links.new(node_img.outputs["Alpha"], mmtr_post.inputs[image_node_name + "_A"])
                    except:
                        pass
                    mat[texture_type] = texture_path
                except Exception as e:
                    logger.warning("Exception while connecting textures (path=" + filepath + ", exception=" + str(e) + ")")

            for property_i, property_type in enumerate(mat_values["properties"].keys()):
                try:
                    property_values = mat_values["properties"][property_type]
                    if property_type.startswith("align"):
                        continue
                    property_subtype_hint = ""
                    if len(property_type.split("__")) == 2:
                        property_subtype_hint = property_type.split("__")[1]

                    if "color" in property_subtype_hint.lower():
                        node_RGB = nodes.new(type='ShaderNodeRGB')
                        node_RGB.location = Vector((property_frame_x, property_frame_y))
                        property_frame_y -= 150.0
                        node_RGB.parent = property_frame
                        node_floatvalue = nodes.new(type='ShaderNodeValue')
                        node_floatvalue.location = Vector((property_frame_x, property_frame_y))
                        property_frame_y -= 100.0
                        node_floatvalue.parent = property_frame
                        if len(property_values) == 3:
                            node_RGB.outputs["Color"].default_value = Vector(property_values + [1.0])
                            node_floatvalue.outputs["Value"].default_value = 1.0
                        else:
                            node_RGB.outputs["Color"].default_value = Vector(property_values)
                            node_floatvalue.outputs["Value"].default_value = property_values[3]

                        if beautify:
                            node_RGB.label = string_reformat(property_type) + "_RGB"
                            node_floatvalue.label = string_reformat(property_type) + "_A"
                        else:
                            node_RGB.label = property_type + "_RGB"
                            node_floatvalue.label = property_type + "_A"

                        links.new(node_RGB.outputs["Color"], mmtr_pre.inputs[node_RGB.label])
                        links.new(node_RGB.outputs["Color"], mmtr_post.inputs[node_RGB.label])
                        links.new(node_floatvalue.outputs["Value"], mmtr_pre.inputs[node_floatvalue.label])
                        links.new(node_floatvalue.outputs["Value"], mmtr_post.inputs[node_floatvalue.label])
                    else:
                        if len(property_values) > 1:
                            for property_i, property_value in enumerate(property_values):
                                node_floatvalue = nodes.new(type='ShaderNodeValue')
                                node_floatvalue.location = Vector((property_frame_x, property_frame_y))
                                property_frame_y -= 20.0
                                if beautify:
                                    node_floatvalue.label = string_reformat(property_type) + "_" + str(property_i)
                                else:
                                    node_floatvalue.label = property_type + "_" + str(property_i)
                                node_floatvalue.parent = property_frame
                                node_floatvalue.outputs["Value"].default_value = float(property_value)
                                links.new(node_floatvalue.outputs["Value"], mmtr_pre.inputs[node_floatvalue.label])
                                links.new(node_floatvalue.outputs["Value"], mmtr_post.inputs[node_floatvalue.label])
                        else:
                            node_floatvalue = nodes.new(type='ShaderNodeValue')
                            node_floatvalue.location = Vector((property_frame_x, property_frame_y))
                            property_frame_y -= 20.0
                            if beautify:
                                node_floatvalue.label = string_reformat(property_type)
                            else:
                                node_floatvalue.label = property_type
                            node_floatvalue.parent = property_frame
                            node_floatvalue.outputs["Value"].default_value = float(property_values[0])
                            links.new(node_floatvalue.outputs["Value"], mmtr_pre.inputs[node_floatvalue.label])
                            links.new(node_floatvalue.outputs["Value"], mmtr_post.inputs[node_floatvalue.label])
                        property_frame_y -= 80.0
                except Exception as e:
                    logger.warning("Exception while connecting properties (path=" + filepath + ", exception=" + str(e) + ")")
        
            links.new(node_UVMap1.outputs["UV"], mmtr_pre.inputs["TexCoord1"])
            links.new(node_UVMap2.outputs["UV"], mmtr_pre.inputs["TexCoord2"])
            links.new(node_UVMap3.outputs["UV"], mmtr_pre.inputs["TexCoord3"])
            links.new(node_UVMap4.outputs["UV"], mmtr_pre.inputs["TexCoord4"])
            links.new(node_VertexColor.outputs["Color"], mmtr_pre.inputs["VertexColor"])
            links.new(node_VertexColor.outputs["Color"], mmtr_post.inputs["VertexColor"])

            for mmtr_output_key in mmtr_post.outputs.keys():
                try:
                    if mmtr_output_key in ["Emission", "Emission Strength"]:
                        if has_emissive:
                            links.new(mmtr_post.outputs[mmtr_output_key], world_shader_node.inputs[mmtr_output_key])
                    else:
                        links.new(mmtr_post.outputs[mmtr_output_key], world_shader_node.inputs[mmtr_output_key])
                except:
                    pass

            for mmtr_output_key in mmtr_post.outputs.keys():
                try:
                    links.new(mmtr_post.outputs[mmtr_output_key], node_output.inputs[mmtr_output_key])
                except:
                    pass
            
            #if "Translucency Color" in mmtr_post.outputs:
                #translucency_node = nodes.new(type='ShaderNodeGroup')
                #translucency_node.location = Vector((300.0, 300.0))
                #translucency_node.node_tree = bpy.data.node_groups["Translucency"]
                #translucency_node.label = "Translucency"
                #links.new(mmtr_post.outputs["Translucency Color"], translucency_node.inputs["Translucency Color"])
                #links.new(mmtr_post.outputs["Alpha"], translucency_node.inputs["Alpha"])
                #links.new(mmtr_post.outputs["Normal"], translucency_node.inputs["Normal"])
                #links.new(node_BSDF.outputs["BSDF"], translucency_node.inputs["BSDF"])
                #links.new(translucency_node.outputs["Shader"], nodes["Material Output"].inputs["Surface"])
                #nodes["Material Output"].location = Vector((500.0, 300.0))

            #if mat_values["has_alpha"]:

            mat.blend_method = "HASHED"
            if hasattr(mat, 'shadow_method'):
                mat.shadow_method = "HASHED"
            #mat.use_screen_refraction = True
        
        returned_mats.append(mat)
    return returned_mats
