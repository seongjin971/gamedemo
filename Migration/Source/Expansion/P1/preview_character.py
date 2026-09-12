"""Render the prepared skin/animation in neutral Blender light for deformation QA."""
import bpy, math, sys, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'prepared-v3/Adventurer.blend'))
scene=bpy.context.scene;arm=bpy.data.objects['TravelerRig'];mesh=bpy.data.objects['TravelerSkin']
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=700;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('QA neutral world');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.15,.17,.20,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
for loc,power,size in [((2,-3,4),350,4),((-3,-1,2),160,3),((1,3,3),240,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size
    l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.3,-4,2.0));cam=bpy.context.object;scene.camera=cam
cam.rotation_euler=(Vector((0,0,.95))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.25
OUT=ROOT.parents[2]/'Evidence/Expansion/P1/skin-qa-v3';OUT.mkdir(parents=True,exist_ok=True)
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'Idle'
arm.animation_data.action=bpy.data.actions[mode]
report=[]
for frame in ([1] if mode=='Idle' else [1,9,17,25]):
    scene.frame_set(frame)
    dg=bpy.context.evaluated_depsgraph_get();evaluated=mesh.evaluated_get(dg);temp=evaluated.to_mesh()
    vertices=[evaluated.matrix_world@v.co for v in temp.vertices]
    report.append({'action':mode,'frame':frame,'min':[min(v[i] for v in vertices) for i in range(3)],'max':[max(v[i] for v in vertices) for i in range(3)]})
    evaluated.to_mesh_clear()
    scene.render.filepath=str(OUT/(mode+'-'+str(frame)+'.png'));bpy.ops.render.render(write_still=True)
(OUT/(mode+'-bounds.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
