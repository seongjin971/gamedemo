import bpy
from pathlib import Path
from mathutils import Vector
SOURCE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'ChapelBroken.blend'))
wall=bpy.data.objects['CW_ChapelBrokenWall6m'];pier=bpy.data.objects['CW_ChapelBrokenPier3m'];wall.hide_render=True;assets=[pier]
s=(SOURCE/'generate_chapel_broken.py').read_text().split('scene=bpy.context.scene;scene.render.engine=')[1]
exec('scene=bpy.context.scene;scene.render.engine='+s)
