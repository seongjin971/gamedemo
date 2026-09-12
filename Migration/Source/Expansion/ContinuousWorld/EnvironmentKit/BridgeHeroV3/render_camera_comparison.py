"""Read-only V2 geometry diagnosis at exact Unity camera conventions. No Art writes."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
SOURCE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(SOURCE.parent/'BridgeHeroV2/StoneBridgeHeroV2_14m.blend'))
bridge=bpy.data.objects['CW_StoneBridgeHeroV2_14m'];original=[v.co.copy() for v in bridge.data.vertices]
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=1536;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Controlled daylight');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.35,.39,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4
ld=bpy.data.lights.new('Controlled warm sun','SUN');ld.energy=2.5;ld.angle=.045;sun=bpy.data.objects.new('Controlled warm sun',ld);bpy.context.collection.objects.link(sun);sun.rotation_euler=(math.radians(25),math.radians(-35),math.radians(-20))
watermat=bpy.data.materials.new('Shadow-receiving water body');watermat.use_nodes=True;nt=watermat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.12,.37,.43,1);bs.inputs['Roughness'].default_value=.40
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.95));water=bpy.context.object;water.name='Controlled water plane';water.data.materials.append(watermat)
unlit=bpy.data.materials.new('Control: water body without shadow response');unlit.use_nodes=True;nt=unlit.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.12,.37,.43,1);em.inputs['Strength'].default_value=1;nt.links.new(em.outputs[0],out.inputs['Surface'])
cd=bpy.data.cameras.new('Exact Unity camera');cam=bpy.data.objects.new('Exact Unity camera',cd);bpy.context.collection.objects.link(cam);cd.type='ORTHO';cd.ortho_scale=16.4*1536/1024;scene.camera=cam;scene.view_settings.view_transform='AgX'
home=14.1/1.27;t=max(0,min(1,(home-8.2)/(home-6.5)));close=t*t*(3-2*t);follow_up=1.2-.2*close*.82
report={'basis':'Camera sourceX sign mirrors the Unity camera X to match imported FBX handedness in C04; sourceY=-UnityZ, sourceZ=UnityY','geometry':'Original V2, no Art/FBX modification','orthographic_vertical_extent':16.4,'orthographic_horizontal_extent':24.6,'target_relative_to_bridge_x_length_up':[0,-3.5,follow_up],'negative_up_stretch':1.5,'water_world_y':-.95,'cases':[]}
cases=[('A-current-angle-raised-shadow',2.8,.46,.72,False),('B-wider-lower-angle-raised-shadow',2.8,.60,.62,False),('C-current-angle-original-deck-shadow',.8,.46,.72,False),('D-wider-lower-angle-original-deck-shadow',.8,.60,.62,False),('E-current-angle-raised-water-unlit-control',2.8,.46,.72,True)]
for label,deck,a,e,no_shadow in cases:
    for v,p in zip(bridge.data.vertices,original):v.co=Vector((p.x,p.y,deck+(p.z*1.5 if p.z<0 else p.z)))
    bridge.data.update();water.data.materials[0]=unlit if no_shadow else watermat
    target=Vector((0,-3.5,deck+follow_up));offset=Vector((math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))*42;cam.location=target+offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/(label+'.png'));bpy.ops.render.render(write_still=True)
    report['cases'].append({'label':label,'deck_world_height':deck,'angle_radians':a,'elevation_radians':e,'elevation_degrees':math.degrees(e),'water_body_shadow_response':not no_shadow,'arch_crown_world_height':deck-.22*1.5,'max_opening_above_water':deck-.22*1.5+.95,'camera_source_xyz':list(cam.location),'target_source_xyz':list(target)})
    (SOURCE/'camera-comparison.json').write_text(json.dumps(report,indent=2));print('COMPARISON_RENDER_COMPLETE '+label)
