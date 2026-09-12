"""Render the already saved final mesh with exactly the build script's rig.
This never changes mesh JSON or blend. Use TREE_V12_SKIP_ROOTS=1 after a reviewed
root-only diagnostic render to complete the three remaining matched views.
"""
import bpy,os
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent;D=W/'derivative'
bpy.ops.wm.open_mainfile(filepath=str(D/'tree-v12.blend'))
o=next(obj for obj in bpy.data.objects if obj.type=='MESH');m=o.data
source=(W/'build_tree_v12.py').read_text();code=source[source.index('# Matched before/after'):source.index('report=dict')]
code='\n'.join(line for line in code.splitlines() if not line.startswith('before=o.copy();'))
code=code.replace("for tag,obj in [('before',before),('after',o)]:","for tag,obj in [('after',o)]:")
code=code.replace("before.hide_render=tag!='before';o.hide_render=tag!='after'","o.hide_render=False")
code=code.replace("for name,(loc,target,scale) in views.items():","for name,(loc,target,scale) in views.items():\n  if os.environ.get('TREE_V12_SKIP_ROOTS')=='1' and name=='roots':continue")
exec(compile(code,'matched_preview_rig','exec'))
print('Final saved asset rendered; JSON/blend not mutated',flush=True)
