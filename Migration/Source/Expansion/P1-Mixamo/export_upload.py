import bpy
from pathlib import Path
root=Path.cwd()
bpy.ops.wm.open_mainfile(filepath=str(root/'Migration/Source/Expansion/P1/prepared-v3/Adventurer.blend'))
arm=bpy.data.objects['TravelerRig']; mesh=bpy.data.objects['TravelerSkin']
arm.animation_data_clear()
for b in arm.pose.bones:
 b.matrix_basis.identity()
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);bpy.context.view_layer.objects.active=mesh
# Freeze the authored neutral skin without its skeleton for Mixamo's own rig.
for mod in list(mesh.modifiers):
 if mod.type=='ARMATURE':bpy.ops.object.modifier_apply(modifier=mod.name)
mesh.parent=None
bpy.ops.export_scene.fbx(filepath=str(root/'Migration/Source/Expansion/P1-Mixamo/Traveler-Upload.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',bake_anim=False,path_mode='COPY',embed_textures=True)
print('MIXAMO_UPLOAD_EXPORT_DONE')
