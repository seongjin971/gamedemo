import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parents[2]/'Evidence/Expansion/P1-Run/source-qa';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'prepared-01/Adventurer.blend'))
scene=bpy.context.scene;arm=bpy.data.objects['TravelerRig'];mesh=bpy.data.objects['TravelerSkin']
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=540;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Source QA World');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.17,.19,.22,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
for loc,power,size in [((2,-3,4),350,4),((-3,-1,2),160,3),((1,3,3),240,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));plane=bpy.context.object;mat=bpy.data.materials.new('QA Ground');mat.diffuse_color=(.18,.20,.22,1);plane.data.materials.append(mat)
bpy.ops.object.camera_add(location=(2.3,-4,2));cam=bpy.context.object;scene.camera=cam;cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.05
bounds=[]
for clip,frames in [('Run',[1,6,12,17])]:
 arm.animation_data.action=bpy.data.actions[clip]
 for f in frames:
  scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();ev=mesh.evaluated_get(dg);me=ev.to_mesh();verts=[ev.matrix_world@v.co for v in me.vertices];bounds.append({'clip':clip,'frame':f,'min':[min(v[i] for v in verts) for i in range(3)],'max':[max(v[i] for v in verts) for i in range(3)]});ev.to_mesh_clear()
  scene.render.filepath=str(OUT/(clip+'-'+str(f)+'.png'));bpy.ops.render.render(write_still=True)
(OUT/'bounds.json').write_text(json.dumps(bounds,indent=2))
