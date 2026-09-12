import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/BridgeHeroV2/CW_StoneBridgeHeroV2_14m.fbx'))
vs=[];fs=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    off=len(vs);vs.extend([ob.matrix_world@v.co for v in ob.data.vertices]);fs.extend([[off+i for i in p.vertices] for p in ob.data.polygons])
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);report={'source':'original V2 FBX, no edits','slices':[]}
for z in (-.23,-.25,-.35,-.6,-1,-1.5,-2,-2.6):
    half=4.9*math.sqrt(1-((z+3)/2.78)**2);inside=[];outside=[]
    for i in range(81):
        y=half*.98*(-1+2*i/80);hit=bvh.ray_cast(Vector((-4,y,z)),Vector((1,0,0)),8)[0];inside.append({'y':y,'clear':hit is None,'hit':None if hit is None else list(hit)})
    for side in (-1,1):
        for margin in (.08,.2,.5,1):
            y=side*(half+margin);hit=bvh.ray_cast(Vector((-4,y,z)),Vector((1,0,0)),8)[0];outside.append({'y':y,'opaque':hit is not None})
    report['slices'].append({'height':z,'analytic_half_span':half,'inside_clear_count':sum(r['clear'] for r in inside),'inside_total':len(inside),'blocked_inside':[r for r in inside if not r['clear']],'outside':outside})
(SOURCE/'v2-diagnosis.json').write_text(json.dumps(report,indent=2));print(json.dumps([{'z':s['height'],'clear':s['inside_clear_count'],'total':s['inside_total'],'outside_opaque':sum(x['opaque'] for x in s['outside'])} for s in report['slices']]))
# Side orthographic evidence from original V2 source, unchanged geometry.
bpy.ops.wm.open_mainfile(filepath=str(SOURCE.parent/'BridgeHeroV2/StoneBridgeHeroV2_14m.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1600;scene.render.resolution_y=650;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Diagnostic side background');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.12,.05,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
ld=bpy.data.lights.new('Diagnostic front softbox','AREA');ld.energy=4000;ld.size=10;lo=bpy.data.objects.new('Diagnostic front softbox',ld);bpy.context.collection.objects.link(lo);lo.location=(10,-2,8);lo.rotation_euler=(Vector((0,0,-.8))-lo.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('True side diagnostic camera');cam=bpy.data.objects.new('True side diagnostic camera',cd);bpy.context.collection.objects.link(cam);cam.location=(20,0,-.7);cam.rotation_euler=(Vector((0,0,-.7))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=15.5;scene.camera=cam;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/'v2-true-side-diagnostic.png');bpy.ops.render.render(write_still=True)
