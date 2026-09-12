"""Run on preserved PavingV14 blend in an explicitly coordinated Blender slot."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;PREVIEW=OUT/'previews';PREVIEW.mkdir(exist_ok=True)
qa=json.loads((OUT/'export-qa.json').read_text());assert qa['passed']
assert hashlib.sha256((OUT/'paving-v15-mesh.json').read_bytes()).hexdigest()==qa['mesh_sha256']
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.cycles.samples=16
camera=scene.camera;changed=bpy.data.objects[qa['modified_body']]
assert tuple(changed.location)==(0,0,0)
old=bpy.data.objects.get('BEFORE V13 preserved')
if old:old.hide_render=True;old.hide_viewport=True
objects=[o for o in scene.objects if o.type=='MESH' and o!=old]
textured=bpy.data.materials['Actual source4K Color roughness NormalGL .4']
neutral=bpy.data.materials.get('Neutral geometry only')
if neutral is None:
 neutral=bpy.data.materials.new('Neutral geometry only');neutral.use_nodes=True
 bs=neutral.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.205,.22,1);bs.inputs['Roughness'].default_value=.72
for view,target,width,e,material in [('native-ground',(0,-.7,2.9),33.3070866,.72,textured),('neutral-close',(.55,-.87,-.008),2.8,.48,neutral),('textured-close',(.55,-.87,-.008),2.8,.48,textured)]:
 a=.46;target=Vector(target);camera.location=target+Vector((-math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))*42;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=width
 for o in objects:o.hide_render=False;o.data.materials[0]=material
 for kind,z in [('before-v14',0),('after-v15',-.011)]:
  changed.location.z=z;scene.render.filepath=str(PREVIEW/f'{kind}-{view}.png');bpy.ops.render.render(write_still=True)
for o in objects:o.data.materials[0]=textured
changed.location.z=-.011
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'paving-v15.blend'))
print('PAVING_V15_PREVIEWS_DONE',qa['mesh_sha256'])
