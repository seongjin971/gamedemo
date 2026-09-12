"""Identical inherited material, camera, lights and exposure before/after."""
import bpy
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent;ROOT=next(p for p in W.parents if (p/'ArtSource').is_dir());OUT=ROOT/'.dream-loop/unity-atmosphere-v2/knight-v6';OUT.mkdir(parents=True,exist_ok=True)
for version,file in [('before',W.parent/'KnightV5/knight-v5.blend'),('after',W/'knight-v6.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=900;s.render.resolution_percentage=100;s.world.color=(.08,.08,.08)
 target=Vector((0,.13,.85));bpy.ops.object.camera_add(location=(-3,7,5));cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.05;s.camera=cam
 for loc,col,power,size in [((3,-4,7),(.63,.77,1),600,5),((-4,2,4),(1,.57,.23),700,4),((0,4,7),(.5,.7,1),850,5)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.color=col;o.data.size=size;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 s.view_settings.view_transform='AgX';s.render.filepath=str(OUT/f'preview-{version}.png');bpy.ops.render.render(write_still=True)
 # A second close view exposes helmet/rim discontinuities hidden at full scale.
 target=Vector((0,.03,1.4));cam.location=(-1.5,3,2.5);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.82;s.render.resolution_x=900;s.render.resolution_y=900;s.render.filepath=str(OUT/f'armor-{version}.png');bpy.ops.render.render(write_still=True)
