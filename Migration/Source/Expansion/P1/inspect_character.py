"""Blender read-only source inspection. No Unity assets or existing files changed."""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
name=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'rigged.glb'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/name))
data={'file':name,'meshes':[],'armatures':[],'actions':[]}
for o in bpy.context.scene.objects:
    if o.type=='MESH':
        corners=[o.matrix_world@Vector(c) for c in o.bound_box]
        data['meshes'].append({'name':o.name,'vertices':len(o.data.vertices),
            'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),
            'bounds_min':[min(c[i] for c in corners) for i in range(3)],
            'bounds_max':[max(c[i] for c in corners) for i in range(3)],
            'groups':[g.name for g in o.vertex_groups], 'materials':[m.name for m in o.data.materials]})
    if o.type=='ARMATURE':
        data['armatures'].append({'name':o.name,'matrix':[list(r) for r in o.matrix_world],
            'bones':[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None} for b in o.data.bones]})
for a in bpy.data.actions:
    data['actions'].append({'name':a.name,'range':list(a.frame_range),'slots':[s.identifier for s in a.slots]})
dest=ROOT/(name.replace('.glb','')+'-inspection.json')
dest.write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data))
