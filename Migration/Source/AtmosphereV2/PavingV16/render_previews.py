"""Eight matched actual Blender views; not native Unity acceptance."""
import bpy,json,math,hashlib,sys,shutil
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;PREVIEW=OUT/'previews';PREVIEW.mkdir(exist_ok=True)
qa=json.loads((OUT/'export-qa.json').read_text());assert qa['passed'] and qa['mesh_sha256']==hashlib.sha256((OUT/'paving-v16-mesh.json').read_bytes()).hexdigest()
after_only='--after-only' in sys.argv
if after_only:
 for p in (OUT/'rejected-first-fill-pass/previews').glob('before-v15-*.png'):shutil.copy2(p,PREVIEW/p.name)
metadata=json.loads((OUT/'fracture-metadata.json').read_text());old=[bpy.data.objects[s['name']] for s in metadata['selected_records']];new=[o for o in bpy.context.scene.objects if o.name.startswith('V16_') and o.type=='MESH']
textured=bpy.data.materials['Actual source4K Color roughness NormalGL .4'];neutral=bpy.data.materials.get('Neutral geometry only')
if neutral is None:
 neutral=bpy.data.materials.new('Neutral geometry only');neutral.use_nodes=True;bs=neutral.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.205,.22,1);bs.inputs['Roughness'].default_value=.72
scene=bpy.context.scene;camera=scene.camera;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.cycles.samples=16
for view,target,width in [('full',(0,-.7,2.9),33.3070866),('zoom-patch',(-2.1,-8.3,0),6.2)]:
 a=.46;e=.72;target=Vector(target);camera.location=target+Vector((-math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))*42;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=width
 for mode,material in [('neutral',neutral),('textured',textured)]:
  for o in scene.objects:
   if o.type=='MESH' and o.data.materials:o.data.materials[0]=material
  for version,before in ([('after-v16',False)] if after_only else [('before-v15',True),('after-v16',False)]):
   for o in old:o.hide_render=not before
   for o in new:o.hide_render=before
   scene.render.filepath=str(PREVIEW/f'{version}-{mode}-{view}.png');bpy.ops.render.render(write_still=True)
for o in old:o.hide_render=True
for o in new:o.hide_render=False
for o in scene.objects:
 if o.type=='MESH' and o.data.materials:o.data.materials[0]=textured
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'paving-v16.blend'))
print('PAVING_V16_PREVIEWS_DONE',qa['mesh_sha256'])
