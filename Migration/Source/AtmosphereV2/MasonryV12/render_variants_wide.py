"""Additional complete-framing clay comparison; geometry remains unchanged."""
import bpy
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'masonry-v12.blend'))
s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
cam=s.camera;cam.location=(4,-7,4.6);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.5
for name in ['Old wall assembly','New wall assembly']:bpy.data.collections[name].hide_render=True
old=bpy.data.collections['Preserved V8 comparison'];new=bpy.data.collections['Authored normalized stones']
for suffix,before in [('before',True),('after',False)]:
    old.hide_render=not before;new.hide_render=before;s.render.filepath=str(OUT/f'variants-{suffix}-wide-clay.png');bpy.ops.render.render(write_still=True)
print('MASONRY_V12_WIDE_COMPARISON_COMPLETE')
