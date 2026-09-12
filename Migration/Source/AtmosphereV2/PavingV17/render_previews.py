"""Six actual matched views. Mirror render context only to native handedness."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
OUT=Path(__file__).resolve().parent;P=OUT/'previews';P.mkdir(exist_ok=True)
qa=json.loads((OUT/'export-qa.json').read_text());assert qa['passed'] and qa['mesh_sha256']==hashlib.sha256((OUT/'paving-v17-mesh.json').read_bytes()).hexdigest()
m=json.loads((OUT/'fracture-metadata.json').read_text());scene=bpy.context.scene
old=[bpy.data.objects[s['name']] for s in m['selected_records']]
new=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('V17_')]
textured=bpy.data.materials['Actual source4K Color roughness NormalGL .4']
neutral=bpy.data.materials.get('Neutral geometry only')
if neutral is None:
 neutral=bpy.data.materials.new('Neutral geometry only');neutral.use_nodes=True
bs=neutral.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.205,.22,1);bs.inputs['Roughness'].default_value=.72
# The source export bridge (x,-z,y) is kept unchanged. Only this unsaved render
# context is mirrored to match Unity's native screen-right direction.
mirror=Matrix.Diagonal((-1,1,1,1));matrices=[(o,o.matrix_world.copy()) for o in scene.objects if o.type!='CAMERA']
def depth(o):return 0 if o.parent is None else 1+depth(o.parent)
for o,mw in sorted(matrices,key=lambda item:depth(item[0])):o.matrix_world=mirror@mw
cam=scene.camera;scene.render.resolution_x=1536;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
scene.render.threads_mode='FIXED';scene.render.threads=3;scene.cycles.samples=16
checks=[]
for view,focus,width,mode in [('full',(0,2.9,.7),33.3070866,'textured'),('patch',(-1.8,0,5.7),13.8,'neutral'),('patch',(-1.8,0,5.7),13.8,'textured')]:
 a=.46;e=.72;f=Vector((-focus[0],-focus[2],focus[1]));cam.location=f+Vector((math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))*42
 cam.rotation_euler=(f-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=width;bpy.context.view_layer.update()
 native_cam=Vector((-cam.location.x,cam.location.z,-cam.location.y));right=Vector((-math.cos(a),0,-math.sin(a)));up=Vector((math.sin(a)*math.sin(e),math.cos(e),-math.cos(a)*math.sin(e)))
 for name,point in [('tree',(7.2,0,3.7)),('portal',(-2.8,5.62,-8.1)),('knight',(-3.08,0,5.21)),('patch',(-1.8,0,5.7))]:
  q=Vector(point);d=q-native_cam;expected=(.5+d.dot(right)/width,.5+d.dot(up)/(width/1.5));actual=world_to_camera_view(scene,cam,Vector((-q.x,-q.z,q.y)))
  error=max(abs(actual.x-expected[0]),abs(actual.y-expected[1]));assert error<2e-6,(view,name,expected,actual)
  checks.append(dict(view=view,landmark=name,expected=list(expected),actual=[actual.x,actual.y],error=error))
 material=neutral if mode=='neutral' else textured
 for o in scene.objects:
  if o.type=='MESH' and o.data.materials:o.data.materials[0]=material
 for version,before in [('before-v16',True),('after-v17',False)]:
  for o in old:o.hide_render=not before
  for o in new:o.hide_render=before
  scene.render.filepath=str(P/f'{version}-{mode}-{view}.png');bpy.ops.render.render(write_still=True)
(OUT/'preview-projection-qa.json').write_text(json.dumps(dict(bridge='(-nativeX,-nativeZ,nativeY), render-only mirror; source export unchanged',landmarks_are_projection_tests_not_scene_objects=True,checks=checks),indent=2))
print('PAVING_V17_SIX_PREVIEWS_DONE',qa['mesh_sha256'])
