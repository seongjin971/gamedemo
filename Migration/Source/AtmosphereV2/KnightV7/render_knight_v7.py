"""Matched V6/V7 cape views; no asset file saves or material changes."""
import bpy
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent
for tag,file in [('before',W.parent/'KnightV6/knight-v6.blend'),('after',W/'knight-v7.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.world.color=(.08,.08,.08);s.view_settings.view_transform='AgX'
 target=Vector((0,.13,.85));bpy.ops.object.camera_add(location=(-3,7,5));cam=bpy.context.object;cam.data.type='ORTHO';s.camera=cam
 for loc,col,power,size in [((3,-4,7),(.63,.77,1),600,5),((-4,2,4),(1,.57,.23),700,4),((0,4,7),(.5,.7,1),850,5)]:
  bpy.ops.object.light_add(type='AREA',location=loc);li=bpy.context.object;li.data.energy=power;li.data.color=col;li.data.size=size;li.rotation_euler=(target-li.location).to_track_quat('-Z','Y').to_euler()
 for name,loc,aim,scale,res in [('whole',(-3,7,5),(0,.13,.85),2.05,(800,900)),('cape',(1.0,4,2.1),(0,.24,.90),1.35,(900,1000)),('side',(4,2.5,2.2),(0,.17,.9),1.90,(800,900))]:
  cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.resolution_x=res[0];s.render.resolution_y=res[1];s.render.filepath=str(W/f'{name}-{tag}.png');bpy.ops.render.render(write_still=True)
print('Matched previews complete, no asset writes',flush=True)
