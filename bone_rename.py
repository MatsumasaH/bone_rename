import bpy
import bgl
import blf

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

def draw_callback_px(self, context):
    font_id = 0
    blf.position(font_id, 15, 30, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, " / ".join([b.name for b in self.bones]))


class BoneLogger(bpy.types.Operator):
    bl_idname = "view3d.bone_logger"
    bl_label = "Bone Logger"

    def modal(self, context, event):
        context.area.tag_redraw()
        if(context.area.type == 'VIEW_3D' and context.mode == 'EDIT_ARMATURE') != True:
            bpy.context.scene["my_bones"] = []
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif(event.type in {'ESC'}):
            bpy.context.scene["my_bones"] = []
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        else:
            self.bones = [b for b in context.selected_bones if b not in self.bones] + [b for b in self.bones if
                                                                                       b in context.selected_bones]
            bpy.context.scene["my_bones"] = [b.name for b in self.bones]
            # print(bpy.context.scene["my_bones"])
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.bones = []
        bpy.context.scene["my_bones"] = self.bones
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


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

        if ("my_bones" in bpy.context.scene) != True:
            flag = False
        else:
            if (len(bpy.context.scene["my_bones"]) == 0):
                flag = False

        return flag

    def execute(self, context):
        user_input = self.type
        abc = [chr(i) for i in range(65, 65 + 26)]

        if user_input:
            # Correct Input.se
            # old_name = context.active_bone.name
            # context.active_bone.name = user_input
            # self.report({'INFO'}, "{} renamed to {}".format(old_name, user_input))

            number = 0
            temp = bpy.context.scene["my_bones"]
            temp.reverse()

            if len(temp) == 1:
                bpy.context.object.data.edit_bones[temp[0]].name = user_input
            else:
                for name in temp:
                    bpy.context.object.data.edit_bones[name].name = user_input + "." + abc[number]
                    number += 1

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
    # bpy.context.scene["my_bones"] = []
    bpy.utils.register_class(BoneRenameOperator)
    bpy.utils.register_class(BoneLogger)
    # handle the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(BoneRenameOperator.bl_idname, type='C', value='PRESS', alt=True)
        addon_keymaps.append((km, kmi))


def unregister():
    # bpy.context.scene["my_bones"] = []
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(BoneRenameOperator)
    bpy.utils.unregister_class(BoneLogger)
    # del bpy.types.Scene.bone_rename


# Debug ---------------------------------------------------------------------
debug = 0
if debug == 1:
    try:
        unregister()
    except:
        pass
    finally:
        register()
# ---------------------------------------------------------------------------