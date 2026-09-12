"""Blender: --background --python build_knight_v4.py [-- --source-dir DIR].
Only the cape mesh is replaced. Six other exported records are copied exactly.
"""
import bpy, math, json, hashlib, sys, argparse
from pathlib import Path
from mathutils import Vector

W=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
ROOT=next((r for r in W.parents if (r/'Migration/Source/AtmosphereV2/Knight').is_dir()),None)
S=a.source_dir or ROOT/'Migration/Source/AtmosphereV2/Knight'
SRC=S/'knight-v3.blend';J=S/'knight-v3-unity-meshes.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_hashes={str(p):sha(p) for p in [SRC,J]}
bpy.ops.wm.open_mainfile(filepath=str(SRC))
transform=lambda o:dict(parent=o.parent.name if o.parent else None,matrix=[float(v) for row in o.matrix_local for v in row])
protected={o.name:transform(o) for o in bpy.data.objects}
def mesh_hash(o):
 m=o.data
 return hashlib.sha256(repr(([tuple(v.co) for v in m.vertices],[(tuple(p.vertices),p.material_index,p.use_smooth) for p in m.polygons],[[tuple(v.uv) for v in uv.data] for uv in m.uv_layers])).encode()).hexdigest()
other_hashes={o.name:mesh_hash(o) for o in bpy.data.objects if o.type=='MESH' and o.name!='Heavy folded crimson cape'}
o=bpy.data.objects['Heavy folded crimson cape'];old=o.data
old.calc_loop_triangles();old_tri=len(old.loop_triangles)
old_bounds=[[min(v.co[k] for v in old.vertices),max(v.co[k] for v in old.vertices)] for k in range(3)]
materials=[m for m in old.materials]
cage=json.loads((W/'settled-cage.json').read_text());vs=cage['vertices'];fs=cage['faces'];C=cage['C'];R=cage['R']
m=bpy.data.meshes.new('Heavy cape v5 baked cloth');m.from_pydata(vs,[],fs);m.update()
for mat in materials:m.materials.append(mat)
o.data=m
for f in m.polygons:f.use_smooth=True
uv=m.uv_layers.new(name='UVMap')
for f in m.polygons:
 for li in f.loop_indices:
  vi=m.loops[li].vertex_index;uv.data[li].uv=(vi%C/(C-1),vi//C/(R-1))
bpy.context.view_layer.objects.active=o
sol=o.modifiers.new('Sewn wool 7mm','SOLIDIFY');sol.thickness=.007;sol.offset=0
bpy.ops.object.modifier_apply(modifier=sol.name)
bpy.context.view_layer.update()
assert protected=={ob.name:transform(ob) for ob in bpy.data.objects}
assert all(mesh_hash(bpy.data.objects[n])==v for n,v in other_hashes.items())
assert list(o.data.materials)==materials
bpy.ops.wm.save_as_mainfile(filepath=str(W/'knight-v5.blend'))

# Retain exact original six JSON records, including float values and metadata.
pack=json.loads(J.read_text(encoding='utf-8'));before=json.loads(J.read_text(encoding='utf-8'))
m=o.data;m.calc_loop_triangles();pos=[];nor=[];uv=[];idx=[]
for tri in m.loop_triangles:
 base=len(pos)//3
 for li in tri.loops:
  v=m.vertices[m.loops[li].vertex_index].co;n=m.corner_normals[li].vector
  pos.extend([-v.x,v.z,-v.y]);nor.extend([-n.x,n.z,-n.y]);uv.extend(m.uv_layers.active.data[li].uv)
 idx.extend([base,base+2,base+1])
cape=next(e for e in pack['objects'] if e['gameObjectName']=='Heavy_folded_crimson_cape')
cape.update(positions=pos,normals=nor,uv=uv,indices=idx,vertexCount=len(pos)//3,triangleCount=len(idx)//3)
assert cape['triangleCount']<=16000
checks=[]
for n,e in enumerate(pack['objects']):
 count=e['vertexCount'];ps=e['positions'];ns=e['normals'];inds=e['indices']
 assert len(ps)==count*3 and len(ns)==count*3 and len(e['uv'])==count*2
 assert all(math.isfinite(v) for v in ps+ns+e['uv'])
 assert len(inds)%3==0 and all(isinstance(i,int) and 0<=i<count for i in inds)
 normal_error=max(abs(math.sqrt(sum(ns[k+j]**2 for j in range(3)))-1) for k in range(0,len(ns),3))
 assert normal_error<1e-5 and count<65535
 min_area=float('inf');min_normal_alignment=1
 for k in range(0,len(inds),3):
  ids=inds[k:k+3];v=[Vector(ps[q*3:q*3+3]) for q in ids]
  cross=(v[1]-v[0]).cross(v[2]-v[0]);area=cross.length*.5
  min_area=min(min_area,area)
  if area>1e-12:
   avg=sum((Vector(ns[q*3:q*3+3]) for q in ids),Vector()).normalized()
   min_normal_alignment=min(min_normal_alignment,cross.normalized().dot(avg))
 unchanged=e==before['objects'][n]
 if e['gameObjectName']!='Heavy_folded_crimson_cape':assert unchanged
 checks.append(dict(name=e['gameObjectName'],vertices=count,triangles=e['triangleCount'],exactRecordPreserved=unchanged,normalMaxLengthError=normal_error,minTriangleArea=min_area,minFaceNormalAlignment=min_normal_alignment,bounds=[[min(ps[k::3]),max(ps[k::3])] for k in range(3)]))
(W/'knight-v5-unity-meshes.json').write_text(json.dumps(pack),encoding='utf-8')
report=dict(sourceHashesBefore=source_hashes,sourceHashesAfter={str(p):sha(p) for p in [SRC,J]},sourceUnchanged=all(sha(Path(p))==v for p,v in source_hashes.items()),allOriginalTransformsAndParentsPreserved=True,allOtherBlenderMeshesExact=True,allMaterialsPreserved=True,capePreviousTriangles=old_tri,capeNewTriangles=len(idx)//3,capeTriangleDelta=len(idx)//3-old_tri,capeBlenderLocalBoundsBefore=old_bounds,capeBlenderLocalBoundsAfter=[[min(v.co[k] for v in m.vertices),max(v.co[k] for v in m.vertices)] for k in range(3)],meshes=checks)
(W/'export-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
