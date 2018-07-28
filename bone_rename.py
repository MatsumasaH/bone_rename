import bpy
import blf

bl_info = {
    'name': 'Bone Renamer',
    'author': 'Hijiri',
    'version': (1, 0, 0),
    'blender': (2, 78, 0),
    'location': 'View3D > Alt-C',
    'category': 'Rigging'
}


def draw_callback_px(self, context):
    font_id = 0
    blf.position(font_id, 15, 30, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, ' / '.join([b.name for b in self.bones]))


class BoneLogger(bpy.types.Operator):
    bl_idname = 'view3d.bone_logger'
    bl_label = 'Bone Logger'

    def modal(self, context, event):
        context.area.tag_redraw()
        if(context.area.type == 'VIEW_3D' and context.mode == 'EDIT_ARMATURE') != True:
            bpy.context.scene['my_bones'] = []
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif(event.type in {'ESC'}):
            bpy.context.scene['my_bones'] = []
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        else:
            self.bones = [b for b in context.selected_bones if b not in self.bones] + \
                         [b for b in self.bones if b in context.selected_bones]
            bpy.context.scene['my_bones'] = [b.name for b in self.bones]
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.bones = []
        bpy.context.scene['my_bones'] = self.bones
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class BoneRenameOperator(bpy.types.Operator):
    '''Rename bone'''
    bl_idname = 'pose.bone_rename'
    bl_label = 'Bone rename'
    bl_options = {'REGISTER', 'UNDO'}
    new_name = bpy.props.StringProperty()
    format = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        if not bool(context.active_bone):
            return False

        if 'my_bones' not in bpy.context.scene:
            return False
        else:
            if len(bpy.context.scene['my_bones']) == 0:
                return False

        return True

    def execute(self, context):
        abc = [chr(i) for i in range(65, 65 + 26)]  # Get Alphabetical Array
        if self.new_name and self.format:
            temp = bpy.context.scene['my_bones'].copy()
            temp.reverse()
            if len(temp) == 1:
                old_name = context.active_bone.name
                bpy.context.object.data.edit_bones[temp[0]].name = self.new_name
                self.report({'INFO'}, '{} renamed to {}'.format(old_name, self.new_name))
            else:
                for i, name in enumerate(temp):
                    bpy.context.object.data.edit_bones[name].name = self.format.format(self.new_name + '.' + abc[i])
            return {'FINISHED'}
        else:
            self.report({'INFO'}, 'No Input, Operation Cancelled')
            return {'CANCELLED'}

    def invoke(self, context, event):
        wm = context.window_manager
        self.new_name = context.active_bone.name
        self.format = '{}'
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, 'new_name', text='New Name')
        self.layout.prop(self, 'format', text='Format')


addon_keymaps = []


def register():
    bpy.utils.register_class(BoneRenameOperator)
    bpy.utils.register_class(BoneLogger)
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
    bpy.utils.unregister_class(BoneLogger)

try:
    unregister()
except:
    pass
finally:
    register()
