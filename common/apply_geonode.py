import bpy

def apply_VM_geonode(obj):
    if len(obj.material_slots) > 0 and obj.material_slots[0] is not None and obj.material_slots[0].material is not None:
        if "tVertexPositionMap__disclosure" in obj.material_slots[0].material.keys():
            if obj.material_slots[0].material["tVertexPositionMap__disclosure"] != "Assets\\default_tex\\null_black":
                if "noimage" not in obj.material_slots[0].material["tVertexPositionMap__disclosure"].lower():
                    vm_geonode = obj.modifiers.new("VM_Geonode", 'NODES')
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_move_up(modifier="VM_Geonode")
                    vm_geonode.node_group = bpy.data.node_groups["VM_geonode"]
                    vm_texture = obj.material_slots[0].material["tVertexPositionMap__disclosure"].split("\\")[-1] + ".tex"
                    vm_geonode["Input_3"] = bpy.data.images[vm_texture]
                    ratio = sum([v.co[0]<0 for v in obj.data.vertices]) / len(obj.data.vertices)
                    if ratio > 0.9:
                        vm_geonode["Input_4"] = True

