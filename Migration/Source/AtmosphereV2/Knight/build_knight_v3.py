import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent
SRC=next(p for p in W.parents if (p/'ArtSource').is_dir())/'ArtSource/knight-v2.blend'
hash_before=hashlib.sha256(SRC.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SRC))
protected={o.name:(o.parent.name if o.parent else None,list(sum((list(r) for r in o.matrix_local),[]))) for o in bpy.data.objects}

def replace(o,vs,fs,uvs=None):
 m=bpy.data.meshes.new(o.data.name+' plate-v3');m.from_pydata(vs,[],fs);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 o.data=m
 for p in m.polygons:p.use_smooth=True
 uv=m.uv_layers.new(name='UVMap')
 for p in m.polygons:
  for li in p.loop_indices:
   vi=m.loops[li].vertex_index
   uv.data[li].uv=uvs[vi] if uvs else (vs[vi][0]*.5+.5,vs[vi][1]*.5+.5)
 return m

# Rounded quadrilateral shell with a shallow crown, outward droop and articulated edge.
# All authored dimensions below are meters, then divided by original local object scale.
for side,label in [(-1,'Left'),(1,'Right')]:
 o=bpy.data.objects[label+' shoulder pauldron'];vs=[];fs=[];uvs=[];N=64;R=12
 def surface(r,a):
  cx=math.cos(a);sy=math.sin(a)
  x=.142*r*math.copysign(abs(cx)**.79,cx)
  y=.146*r*math.copysign(abs(sy)**.82,sy)
  x*=1-.10*(y/.146)
  z=.079*(1-r**1.65)-.018-.026*side*x/.142-.008*y/.146
  z+=.010*(1-r)*math.exp(-(y/.058)**2)
  return Vector((x,y,z))
 for j in range(R+1):
  r=.001+(1-.001)*j/R
  for i in range(N):
   p=surface(r,i*math.tau/N);vs.append(tuple(p[k]/o.scale[k] for k in range(3)));uvs.append((p.x/.32+.5,p.y/.32+.5))
 for j in range(R):
  for i in range(N):
   k=(i+1)%N;fs.append((j*N+i,(j+1)*N+i,(j+1)*N+k,j*N+k))
 fs.append(tuple(range(N)))
 m=replace(o,vs,fs,uvs)
 bpy.context.view_layer.objects.active=o
 sol=o.modifiers.new('Forged shell 3mm','SOLIDIFY');sol.thickness=.020;sol.offset=-1
 bpy.ops.object.modifier_apply(modifier=sol.name)
 # Thin rolled seam follows the entire perimeter, built directly in same mesh, material 1.
 oldvs=[tuple(v.co) for v in m.vertices];oldfs=[tuple(p.vertices) for p in m.polygons]
 olduv=[tuple(m.uv_layers.active.data[next(li for p in m.polygons for li in p.loop_indices if m.loops[li].vertex_index==v.index)].uv) for v in m.vertices]
 start=len(oldvs);rings=6
 for i in range(N):
  a=i*math.tau/N;p=surface(1,a)
  radial=Vector((math.cos(a),math.sin(a),0)).normalized()
  for k in range(rings):
   ang=k*math.tau/rings;q=p+radial*(.0033*math.cos(ang))+Vector((0,0,.0033*math.sin(ang)))
   oldvs.append(tuple(q[k]/o.scale[k] for k in range(3)));olduv.append((i/N,k/rings))
 shellfaces=len(oldfs)
 for i in range(N):
  for k in range(rings):oldfs.append((start+i*rings+k,start+((i+1)%N)*rings+k,start+((i+1)%N)*rings+(k+1)%rings,start+i*rings+(k+1)%rings))
 m=replace(o,oldvs,oldfs,olduv)
 for p in m.polygons:p.material_index=1 if p.index>=shellfaces else 0

# Broad weighted folds, restrained secondary creases and an uneven weighted hem.
o=bpy.data.objects['Heavy folded crimson cape'];vs=[];fs=[];uvs=[];C=65;R=48
for j in range(R):
 t=j/(R-1);width=.17+.18*math.sin(t*math.pi*.6)
 for i in range(C):
  s=i/(C-1)*2-1
  x=s*width+.050*t*t
  phase=(s+.055*math.sin(s*math.pi+.5))*math.pi*3+.20*t+.3
  y=.017+.29*t+.10*t*t+(.010+.041*t**.8)*math.cos(phase)
  y+=.006*t*math.sin(s*math.pi*7+1.3*t)*(0.5+0.5*math.cos(phase))
  z=-.97*t+t**5*(.016*math.sin(s*math.pi*2+.4)+.008*math.sin(s*math.pi*5+.9))
  vs.append((x,y,z));uvs.append((i/(C-1),t))
for j in range(R-1):
 for i in range(C-1):fs.append((j*C+i,j*C+i+1,(j+1)*C+i+1,(j+1)*C+i))
m=replace(o,vs,fs,uvs)
bpy.context.view_layer.objects.active=o
sol=o.modifiers.new('Sewn wool 7mm','SOLIDIFY');sol.thickness=.007;sol.offset=0
bpy.ops.object.modifier_apply(modifier=sol.name)

bpy.context.view_layer.update()
for name,p in protected.items():
 o=bpy.data.objects[name];assert p==(o.parent.name if o.parent else None,list(sum((list(r) for r in o.matrix_local),[])))
for label in ['Left','Right']:
 bpy.data.objects[label+' pauldron rim'].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(W/'knight-v3.blend'))

# Flatten loop corners to preserve smooth normals and UV seams. Unity receives reflected
# coordinates and reversed triangle order, with no further winding/axis changes needed.
exports=[]
def export(name,target,matindex=None):
 o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles();pos=[];nor=[];uv=[];idx=[]
 for tri in m.loop_triangles:
  if matindex is not None and m.polygons[tri.polygon_index].material_index!=matindex:continue
  base=len(pos)//3
  for li in tri.loops:
   v=m.vertices[m.loops[li].vertex_index].co;n=m.corner_normals[li].vector
   pos.extend([-v.x,v.z,-v.y]);nor.extend([-n.x,n.z,-n.y]);uv.extend(m.uv_layers.active.data[li].uv)
  idx.extend([base,base+2,base+1])
 assert all(math.isfinite(v) for v in pos+nor+uv)
 e=dict(gameObjectName=target,sourceObject=name,positions=pos,normals=nor,uv=uv,indices=idx,vertexCount=len(pos)//3,triangleCount=len(idx)//3)
 exports.append(e)
export('Left shoulder pauldron','Icosphere004_rounded_v2',0)
export('Left shoulder pauldron','Icosphere004_rounded_v2_1',1)
export('Right shoulder pauldron','Icosphere007_rounded_v2',0)
export('Right shoulder pauldron','Icosphere007_rounded_v2_1',1)
export('Heavy folded crimson cape','Heavy_folded_crimson_cape')
# Existing importer merged direct arm children per material. Recreate edge group,
# omitting only the obsolete broad pauldron bar. Other edge objects stay exact.
for label in ['Left','Right']:
 pos=[];nor=[];uv=[];idx=[]
 arm=bpy.data.objects[label+'Arm']
 for o in arm.children:
  if o.type!='MESH' or o.name==label+' pauldron rim' or 'shoulder pauldron' in o.name:continue
  m=o.data;m.calc_loop_triangles();M=o.matrix_local;NM=M.to_3x3().inverted().transposed()
  for tri in m.loop_triangles:
   if m.materials[m.polygons[tri.polygon_index].material_index].name!='Polished forged edges':continue
   base=len(pos)//3
   for li in tri.loops:
    v=M@m.vertices[m.loops[li].vertex_index].co;n=(NM@m.corner_normals[li].vector).normalized()
    pos.extend([-v.x,v.z,-v.y]);nor.extend([-n.x,n.z,-n.y]);uv.extend(m.uv_layers.active.data[li].uv if m.uv_layers.active else (v.x,v.z))
   idx.extend([base,base+2,base+1])
 exports.append(dict(gameObjectName=label+'Arm_Polished forged edges',sourceObject=label+'Arm direct Polished forged edges except obsolete pauldron rim',positions=pos,normals=nor,uv=uv,indices=idx,vertexCount=len(pos)//3,triangleCount=len(idx)//3))
(W/'knight-v3-unity-meshes.json').write_text(json.dumps(dict(coordinateBasis='Already Unity (-Blender X, Blender Z, -Blender Y); triangle winding already reversed',objects=exports)),encoding='utf-8')
report=dict(source=str(SRC),sourceSHA256Before=hash_before,sourceSHA256After=hashlib.sha256(SRC.read_bytes()).hexdigest(),sourceUnchanged=hash_before==hashlib.sha256(SRC.read_bytes()).hexdigest(),allOriginalTransformsAndParentsPreserved=True,meshes=[{k:v for k,v in e.items() if k not in ['positions','normals','uv','indices']} for e in exports])
(W/'manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
