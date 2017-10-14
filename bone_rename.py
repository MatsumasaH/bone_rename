import bpy
import re

# pep8
# Add-on information
bl_info = {
    "name": "Bone Renamer",
    "author": "Hijiri",
    "version": (1, 0, 0),
    "blender": (2, 78, 0),
    "location": "View3D > Alt-C",
    "category": "Rigging"
}


class BoneRenameOperator(bpy.types.Operator):
    """Rename bone"""
    bl_idname = "pose.bone_rename"
    bl_label = "Bone rename"
    bl_options = {'REGISTER', 'UNDO'}
    type = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        flag = True
        if bool(context.active_bone):
            pass
        else:
            flag = False
        return flag

    def execute(self, context):
        
        user_input = self.type
        
        if user_input:
            # Correct Input
            old_name = context.active_bone.name
            context.active_bone.name = user_input
            self.report({'INFO'}, "{} renamed to {}".format(old_name, user_input))
            return {'FINISHED'}

        else:
            # No input
            self.report({'INFO'}, "No input, operation cancelled")
            return {'CANCELLED'}

    def invoke(self, context, event):
        wm = context.window_manager
        self.type = context.active_bone.name
        # return wm.invoke_popup(self, width=400, height=200)
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.prop(self, "type", text="New name")

# ------------------------------------------------------------------------
#    register and unregister functions
# ------------------------------------------------------------------------

addon_keymaps = []


def register():
    bpy.utils.register_class(BoneRenameOperator)
    # handle the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(BoneRenameOperator.bl_idname, type='C', value='PRESS', alt=True)
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(BoneRenameOperator)
    # del bpy.types.Scene.bone_rename
