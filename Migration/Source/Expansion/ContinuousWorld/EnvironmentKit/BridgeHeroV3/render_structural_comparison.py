"""V2 versus structural V3, identical raised-deck camera, water and neutral lighting."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
SOURCE=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bridges=[]
for path,name in [(SOURCE.parent/'BridgeHeroV2/StoneBridgeHeroV2_14m.blend','CW_StoneBridgeHeroV2_14m'),(SOURCE/'StoneBridgeHeroV3_14m.blend','CW_StoneBridgeHeroV3_14m')]:
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=[name]
    ob=dst.objects[0];bpy.context.collection.objects.link(ob);bridges.append(ob)
    for v in ob.data.vertices:v.co.z=2.8+(v.co.z*1.5 if v.co.z<0 else v.co.z)
    ob.data.update()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=20;scene.render.resolution_x=1536;scene.render.resolution_y=1024;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('Neutral structural daylight');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.38,.44,.48,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
ld=bpy.data.lights.new('Neutral sunlight','SUN');ld.energy=2.6;ld.angle=.035;sun=bpy.data.objects.new('Neutral sunlight',ld);bpy.context.collection.objects.link(sun);sun.rotation_euler=(math.radians(25),math.radians(-35),math.radians(-20))
def material(name,color,rough):
    m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;return m
wm=material('Neutral bright shallow water',(.24,.43,.46),.44);gm=material('Low river bed',(.11,.13,.12),.95)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.95));water=bpy.context.object;water.data.materials.append(wm)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-4));ground=bpy.context.object;ground.data.materials.append(gm)
cd=bpy.data.cameras.new('Unity .60 .62 structural camera');cam=bpy.data.objects.new('Unity .60 .62 structural camera',cd);bpy.context.collection.objects.link(cam);cd.type='ORTHO';cd.ortho_scale=24.6;scene.camera=cam
home=14.1/1.27;t=max(0,min(1,(home-8.2)/(home-6.5)));close=t*t*(3-2*t);follow_up=1.2-.2*close*.82;target=Vector((0,-3.5,2.8+follow_up));cam.location=target+Vector((math.sin(.60)*math.cos(.62),-math.cos(.60)*math.cos(.62),math.sin(.62)))*42;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
quad=[]
for p in [(3.25,-7,-.95),(3.25,7,-.95),(3.25,7,2.8),(3.25,-7,2.8)]:
    q=world_to_camera_view(scene,cam,Vector(p));quad.append([q.x*1536,(1-q.y)*1024])
report={'camera_angle':.60,'camera_elevation':.62,'orthographic_size_unity':8.2,'source_camera_position':list(cam.location),'source_camera_target':list(target),'handedness':'positive source camera X, negative source length-Y; matches observed imported FBX orientation in Unity','deck_world_height':2.8,'only_negative_local_up_scale':1.5,'water_world_height':-.95,'river_bed_world_height':-4,'near_facade_projection_quad_pixels':quad,'near_facade_world_x':3.25,'near_facade_range_length':[-7,7],'near_facade_vertical_range':[-.95,2.8],'cases':[]}
for ob in bridges:
    for other in bridges:other.hide_render=other!=ob
    label='v2' if 'V2' in ob.name else 'v3';scene.render.film_transparent=False;water.hide_render=False;ground.hide_render=False;scene.cycles.samples=20
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/('structural-'+label+'-raised-camera-preview.png'));bpy.ops.render.render(write_still=True)
    water.hide_render=True;ground.hide_render=True;scene.render.film_transparent=True;scene.cycles.samples=8;scene.render.filepath=str(SOURCE/('structural-'+label+'-geometry-alpha.png'));bpy.ops.render.render(write_still=True)
    report['cases'].append({'model':ob.name,'preview':'structural-'+label+'-raised-camera-preview.png','geometry_alpha':'structural-'+label+'-geometry-alpha.png'})
(SOURCE/'structural-camera-comparison.json').write_text(json.dumps(report,indent=2));print('STRUCTURAL_CAMERA_COMPARISON_COMPLETE')
