import bpy,json
from pathlib import Path
root=Path(r'C:/Users/brian/Dev/active/Dream Loop Astra/Migration/Source/Expansion')
bpy.ops.wm.open_mainfile(filepath=str(root/'P1/prepared-v3/Adventurer.blend'))
a=bpy.data.objects['TravelerRig']; print('TARGET',a.matrix_world[:]);print('MESH',bpy.data.objects['TravelerSkin'].dimensions[:])
for b in a.data.bones:print('TB',b.name,b.parent.name if b.parent else '-',tuple(b.head_local),tuple(b.tail_local))
bpy.ops.import_scene.fbx(filepath=str(root/'P1-Mixamo/Walking-Swagger.fbx'))
a=[o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o.name!='TravelerRig'][0];print('SOURCE',a.name,a.matrix_world[:],a.animation_data.action.name,a.animation_data.action.frame_range[:])
for b in a.data.bones:
 if any(w in b.name for w in ['Hips','Spine','Neck','Head','Arm','Hand','UpLeg','Leg','Foot','ToeBase','Shoulder']): print('SB',b.name,b.parent.name if b.parent else '-',tuple(a.matrix_world@b.head_local),tuple(a.matrix_world@b.tail_local))
