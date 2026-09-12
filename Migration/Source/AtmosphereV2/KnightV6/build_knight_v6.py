"""V6: repair pauldron pole topology; round the helmet shell within old bounds.

Only shoulder steel records change in the seven-part pack. Cape, two shoulder
rims and two arm-trim records are copied EXACT. Helmet is a separate supplement.
"""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent;ROOT=next(p for p in W.parents if (p/'ArtSource').is_dir())
S=ROOT/'Migration/Source/AtmosphereV2/KnightV5';OUT=ROOT/'.dream-loop/unity-atmosphere-v2/knight-v6';OUT.mkdir(parents=True,exist_ok=True)
SRC=S/'knight-v5.blend';J=S/'knight-v5-unity-meshes.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_hashes={str(p):sha(p) for p in [SRC,J]}
bpy.ops.wm.open_mainfile(filepath=str(SRC))
def state(o):return dict(parent=o.parent.name if o.parent else None,matrix=[list(r) for r in o.matrix_local],materials=[m.name for m in o.data.materials] if o.type=='MESH' else [],hidden=o.hide_render)
def mesh_hash(o):
 m=o.data
 return hashlib.sha256(repr(([tuple(v.co) for v in m.vertices],[(tuple(p.vertices),p.material_index,p.use_smooth) for p in m.polygons],[[tuple(d.uv) for d in uv.data] for uv in m.uv_layers])).encode()).hexdigest()
protected={o.name:state(o) for o in bpy.data.objects};hashes={o.name:mesh_hash(o) for o in bpy.data.objects if o.type=='MESH'}
mutable={'Left shoulder pauldron','Right shoulder pauldron','Angular closed bascinet'}
changes=[]
for label in ['Left','Right']:
 o=bpy.data.objects[label+' shoulder pauldron'];m=o.data;before=len(m.vertices)
 rim_normals={}
 for p in m.polygons:
  if p.material_index==1:
   for li in p.loop_indices:
    key=tuple(m.vertices[m.loops[li].vertex_index].co)+tuple(m.uv_layers.active.data[li].uv)
    rim_normals[key]=m.corner_normals[li].vector.copy()
 bm=bmesh.new();bm.from_mesh(m)
 caps=[f for f in bm.faces if len(f.verts)>32 and f.material_index==0]
 pole_count=sum(len(f.verts) for f in caps)
 # The original r=.001 ring made microscopic nearly collinear 64-gon caps.
 # Collapsing each top/bottom pole ring removes the bad cap triangulation.
 # Solidify offsets the underside pole sideways; detect both actual tiny
 # cap polygons topologically rather than assuming both poles lie on XY zero.
 for cap in caps:
  verts=list(cap.verts);center=sum((v.co for v in verts),Vector())/len(verts)
  bmesh.ops.pointmerge(bm,verts=verts,merge_co=center)
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
 bm.to_mesh(m);bm.free();m.update()
 for p in m.polygons:p.use_smooth=True
 m.set_sharp_from_angle(angle=math.radians(55));m.update()
 # The rim JSON record is copied exactly; retain its original loop normals in
 # the candidate blend too, so isolated previews match the actual export pack.
 custom=[n.vector.copy() for n in m.corner_normals]
 for p in m.polygons:
  if p.material_index==1:
   for li in p.loop_indices:
    key=tuple(m.vertices[m.loops[li].vertex_index].co)+tuple(m.uv_layers.active.data[li].uv)
    custom[li]=rim_normals[key]
 m.normals_split_custom_set(custom);m.update()
 changes.append(dict(object=o.name,beforeVertices=before,afterVertices=len(m.vertices),poleCandidates=pole_count,operation='Collapse both tiny 64-sided pole caps and recalculate closed-shell normals; preserve outer profile and material indices'))

helmet=bpy.data.objects['Angular closed bascinet'];m=helmet.data
bounds=[[min(v.co[k] for v in m.vertices),max(v.co[k] for v in m.vertices)] for k in range(3)]
old_tri=len(m.polygons)
bpy.context.view_layer.objects.active=helmet
mod=helmet.modifiers.new('Continuous forged helmet shell','SUBSURF');mod.subdivision_type='CATMULL_CLARK';mod.levels=2;mod.render_levels=2
bpy.ops.object.modifier_apply(modifier=mod.name)
m=helmet.data;new_bounds=[[min(v.co[k] for v in m.vertices),max(v.co[k] for v in m.vertices)] for k in range(3)]
# Constrain to original six bound planes; no helmet inflation or transform edit.
for v in m.vertices:
 for k in range(3):
  t=(v.co[k]-new_bounds[k][0])/(new_bounds[k][1]-new_bounds[k][0]);v.co[k]=bounds[k][0]+t*(bounds[k][1]-bounds[k][0])
for p in m.polygons:p.use_smooth=True
m.update();m.calc_loop_triangles()
changes.append(dict(object=helmet.name,beforeTriangles=old_tri,afterTriangles=len(m.loop_triangles),boundsBefore=bounds,boundsAfter=[[min(v.co[k] for v in m.vertices),max(v.co[k] for v in m.vertices)] for k in range(3)],operation='Two bounded shell subdivision levels plus smooth normals; unchanged visor, nasal ridge, eye slit and hinges'))
assert protected=={o.name:state(o) for o in bpy.data.objects}
assert all(mesh_hash(bpy.data.objects[name])==h for name,h in hashes.items() if name not in mutable)

def export(o,gameobject,material=None):
 m=o.data;m.calc_loop_triangles();ps=[];ns=[];uv=[];ids=[]
 for tri in m.loop_triangles:
  if material is not None and m.polygons[tri.polygon_index].material_index!=material:continue
  base=len(ps)//3
  for li in tri.loops:
   p=m.vertices[m.loops[li].vertex_index].co;n=m.corner_normals[li].vector
   ps.extend((-p.x,p.z,-p.y));ns.extend((-n.x,n.z,-n.y));uv.extend(m.uv_layers.active.data[li].uv if m.uv_layers.active else (p.x,p.z))
  ids.extend((base,base+2,base+1))
 return dict(gameObjectName=gameobject,sourceObject=o.name,positions=ps,normals=ns,uv=uv,indices=ids,vertexCount=len(ps)//3,triangleCount=len(ids)//3)
pack=json.loads(J.read_text());original=json.loads(J.read_text());modified=[]
for e in pack['objects']:
 if e['gameObjectName'] in ['Icosphere004_rounded_v2','Icosphere007_rounded_v2']:
  e.update(export(bpy.data.objects[e['sourceObject']],e['gameObjectName'],0));modified.append(e['gameObjectName'])
for e,before in zip(pack['objects'],original['objects']):
 if e['gameObjectName'] not in modified:assert e==before
helmetpack=dict(coordinateBasis=pack['coordinateBasis'],objects=[export(helmet,'Angular_closed_bascinet')])
(W/'knight-v6-unity-meshes.json').write_text(json.dumps(pack));(W/'helmet-v6-unity-mesh.json').write_text(json.dumps(helmetpack))
bpy.ops.wm.save_as_mainfile(filepath=str(W/'knight-v6.blend'))
report=dict(sourceHashes=source_hashes,sourceUnchanged=all(sha(Path(p))==h for p,h in source_hashes.items()),allObjectNamesParentsTransformsMaterialSlotsAndVisibilityExact=protected=={o.name:state(o) for o in bpy.data.objects},allOtherBlenderMeshesExact=all(mesh_hash(bpy.data.objects[name])==h for name,h in hashes.items() if name not in mutable),exactCopiedRecords=[e['gameObjectName'] for e,b in zip(pack['objects'],original['objects']) if e==b],changedRecords=modified,changes=changes,helmetMapping=dict(gameObjectName='Angular_closed_bascinet',blenderObject=helmet.name,blenderParent=helmet.parent.name,sourceTransform=protected[helmet.name],unitySource='Unity/Vesper/Assets/Vesper/Import/unity-scene.json',unityObjectId='2507cff0-bb1f-4e6e-802a-38e85ddda457',unityParentId='280be315-6128-47ac-988d-3a693604496e',unityMaterialId='f7d20fcf-c1c0-4764-a247-8511f3551f90'),coordinateRule='Already Unity (-x,z,-y), reversed [0,2,1] once; do not reconvert or bake object transform')
(W/'build-report.json').write_text(json.dumps(report,indent=2));(OUT/'build-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
