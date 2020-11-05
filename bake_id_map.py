# By Nothke

bl_info = {
    "name": "Bake id map",
    "description": "Bakes id map to texture with a single command.",
    "author": "Nothke",
    "category": "Object",
    "blender": (2, 80, 0),
#    "location": "Object > Apply > Unity Rotation Fix",
}

import bpy
from math import pi
from mathutils import Vector
from mathutils import Matrix

class NOTHKE_OT_bake_id_map(bpy.types.Operator):
    """Bakes id map"""
    bl_idname = "object.bake_id_map"
    bl_label = "Bake id map"
    bl_options = {'REGISTER', 'UNDO'}

    tex_size: bpy.props.IntProperty(name="Texture Size", default=512)
    ray_distance: bpy.props.FloatProperty(name="Ray Distance", default=0.1)

    def execute(self, context):

        original_active_object = context.view_layer.objects.active
        name = original_active_object.name
        filename = name + "_id.png"

        layer = context.view_layer
                        
        selected_objects = []
        
        for obj in context.selected_objects:
            selected_objects.append(obj)

        bpy.ops.object.select_all(action='DESELECT')
        
        layer.objects.active = None
        duplicated_objects = []

        # duplicate each object individually
        for obj in selected_objects:
            layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.duplicate()
            dobj = context.object
            duplicated_objects.append(dobj)

            #print(dobj.name)

            # Deselect this object
            layer.objects.active = None
            bpy.ops.object.select_all(action='DESELECT')

        bakeSize = self.tex_size

        #5 remember render engine and switch to CYCLES for baking
        orig_renderer = bpy.data.scenes[bpy.context.scene.name].render.engine
        bpy.data.scenes[bpy.context.scene.name].render.engine = "CYCLES"

        #6 create temporary bake image and material
        bakeimage = bpy.data.images.new("BakeImage", width=bakeSize, height=bakeSize)
        bakemat = bpy.data.materials.new(name="bakemat")
        bakemat.use_nodes = True

        # Set materials
        for obj in duplicated_objects:
            layer.objects.active = obj

            # remove material slots
            for x in obj.material_slots:
                obj.active_material_index = 0 
                bpy.ops.object.material_slot_remove()

            # add and assign material
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = bakemat

        # Select duplicated objects
        for obj in duplicated_objects:
            obj.select_set(True)
            layer.objects.active = obj

        # apply modifiers, will work for all selected meshes
        bpy.ops.object.convert(target='MESH')
        
        # join
        bpy.ops.object.join()
        joined_obj = layer.objects.active

        #8 select lowpoly target
        #bpy.context.view_layer.objects.active = original_active_object #context.scene.lowpoly

        #9 select lowpoly material and create temporary render target
        #orig_mat = bpy.context.active_object.data.materials[0]
        bpy.context.active_object.data.materials[0] = bakemat
        node_tree = bakemat.node_tree
        node = node_tree.nodes.new("ShaderNodeTexImage")
        node.select = True
        node_tree.nodes.active = node
        node.image = bakeimage

        # setup id baking
        bpy.context.scene.cycles.samples = context.scene.samplesColor
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True

        # select this
        context.view_layer.objects.active.select_set(True)

        # Select all original
        for obj in selected_objects:
            obj.select_set(True)


        # BAKE!
        bpy.ops.object.bake(
            type = 'DIFFUSE', 
            use_clear = True, 
            use_selected_to_active = True,
            cage_extrusion = self.ray_distance) # changed in 2.9 to max_ray_distance?

        folder_path = bpy.path.abspath("//")
        map_path = folder_path + filename
        bakeimage.filepath_raw =  map_path # context.scene.bakeFolder+context.scene.bakePrefix+"_color.tga"
        bakeimage.file_format = 'PNG'
        bakeimage.save()
        
        print("Saved at " + map_path)

        # Reselect and reactivate previously selected objects
        for obj in selected_objects:
            obj.select_set(True)

        context.view_layer.objects.active = original_active_object
        
        print("Baked")

        # Cleanup
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.images.remove(bakeimage)
        bakemat.node_tree.nodes.remove(node)
        bpy.data.materials.remove(bakemat)
        bpy.data.scenes[bpy.context.scene.name].render.engine = orig_renderer

        # Delete joined object
        layer.objects.active = joined_obj
        joined_obj.select_set(True)
        bpy.ops.object.delete(use_global=False)

        # Reselect old objects and make active
        for obj in selected_objects:
            obj.select_set(True)

        layer.objects.active = original_active_object

        self.report({'INFO'}, "Baked id successfully and saved to " + map_path)

        return {'FINISHED'}

        def invoke(self, context, event):
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

def menu_draw(self, context):
    layout = self.layout
    layout.operator("object.bake_id_map", text="Bake id map")

def register():
    bpy.utils.register_class(NOTHKE_OT_bake_id_map)
    bpy.types.VIEW3D_MT_object_apply.append(menu_draw)

def unregister():
    bpy.utils.unregister_class(NOTHKE_OT_bake_id_map)
    bpy.types.VIEW3D_MT_object_apply.remove(menu_draw)

if __name__ == "__main__":
    register()