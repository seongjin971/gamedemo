"""Render source and candidate from the identical isolated studio camera."""
import bpy
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent
ROOT=next(r for r in W.parents if (r/'Migration/Source/AtmosphereV2/Knight').is_dir())
for version,file in [('before',ROOT/'Migration/Source/AtmosphereV2/Knight/knight-v3.blend'),('after',W/'knight-v5.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(file))
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32
 s.render.resolution_x=800;s.render.resolution_y=900;s.render.resolution_percentage=100
 s.world.color=(.08,.08,.08);target=Vector((0,.13,.85))
 bpy.ops.object.camera_add(location=(-3,7,5));cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.05;s.camera=cam
 for loc,col,power,size in [((3,-4,7),(.63,.77,1),600,5),((-4,2,4),(1,.57,.23),700,4),((0,4,7),(.5,.7,1),850,5)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.color=col;o.data.size=size;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 s.view_settings.view_transform='AgX';s.render.filepath=str(W/f'preview-{version}.png');bpy.ops.render.render(write_still=True)
