"""Render the QA-passed V14 blend. Run only in the coordinated render slot."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
qa=json.loads((OUT/'export-qa.json').read_text())
assert qa['passed'] and qa['mesh_sha256']==hashlib.sha256((OUT/'paving-v14-mesh.json').read_bytes()).hexdigest()
scene=bpy.context.scene;camera=scene.camera;PREVIEW=OUT/'previews'
oldob=bpy.data.objects['BEFORE V13 preserved'];objects=[ob for ob in scene.objects if ob.type=='MESH' and ob!=oldob]
neutral=bpy.data.materials.get('Neutral geometry only')
if neutral is None:
 neutral=bpy.data.materials.new('Neutral geometry only');neutral.use_nodes=True
 bs=neutral.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.72;bs.inputs['Base Color'].default_value=(.18,.205,.22,1)
textured=bpy.data.materials['Actual source4K Color roughness NormalGL .4']
a=.46;e=.72
for view,target,width in [('native-ground',(0,-.7,2.9),33.3070866),('close',(0,-8,0),13.0)]:
 target=Vector(target);camera.location=target+Vector((-math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))*42;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=width
 for kind in ['before-v13-neutral','after-v14-neutral','after-v14-textured']:
  before=kind.startswith('before');oldob.hide_render=not before;oldob.data.materials[0]=neutral
  for ob in objects:ob.hide_render=before;ob.data.materials[0]=textured if kind.endswith('textured') else neutral
  scene.render.filepath=str(PREVIEW/f'{kind}-{view}.png');bpy.ops.render.render(write_still=True)
print('PAVING_V14_PREVIEWS_DONE',qa['mesh_sha256'])
