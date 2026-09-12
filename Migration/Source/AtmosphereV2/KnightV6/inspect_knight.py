import bpy,json
from pathlib import Path
W=Path(__file__).resolve().parent;ROOT=next(p for p in W.parents if (p/'ArtSource').is_dir())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Migration/Source/AtmosphereV2/KnightV5/knight-v5.blend'))
objects=[]
for o in bpy.data.objects:
 d=dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,location=list(o.location),scale=list(o.scale),rotation=list(o.rotation_euler),hidden=o.hide_render)
 if o.type=='MESH':
  m=o.data;m.calc_loop_triangles();d.update(mesh=m.name,vertices=len(m.vertices),polygons=len(m.polygons),triangles=len(m.loop_triangles),smooth=sum(p.use_smooth for p in m.polygons),materials=[mat.name for mat in m.materials],modifiers=[mod.type for mod in o.modifiers],bounds=[[min(v.co[k] for v in m.vertices),max(v.co[k] for v in m.vertices)] for k in range(3)])
 objects.append(d)
(W/'inspection.json').write_text(json.dumps(objects,indent=2));print(json.dumps(objects,indent=2))
