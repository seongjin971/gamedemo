"""KnightV7 cape-only art derivative; no physics-equilibrium claim.
Blender5.2.1 --background --threads3 --python build_knight_v7.py.
"""
import bpy,json,math,hashlib,shutil
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parent;S=W.parent/'KnightV6';NAME='Heavy folded crimson cape';KEY='Heavy_folded_crimson_cape'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected_files={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()}
(W/'protected-v6-hashes.json').write_text(json.dumps(protected_files,indent=2),encoding='utf-8')
bpy.ops.wm.open_mainfile(filepath=str(S/'knight-v6.blend'))
def state(o):return dict(parent=o.parent.name if o.parent else None,matrix=[list(r) for r in o.matrix_local],materials=[m.name for m in o.data.materials] if o.type=='MESH' else [],hidden=o.hide_render)
def meshhash(o):
 m=o.data
 return hashlib.sha256(repr(([tuple(v.co) for v in m.vertices],[(tuple(p.vertices),p.material_index,p.use_smooth) for p in m.polygons],[[tuple(x.uv) for x in uv.data] for uv in m.uv_layers],[tuple(n.vector) for n in m.corner_normals])).encode()).hexdigest()
protected={o.name:state(o) for o in bpy.data.objects};others={o.name:meshhash(o) for o in bpy.data.objects if o.type=='MESH' and o.name!=NAME}
o=bpy.data.objects[NAME];m=o.data;old=[v.co.copy() for v in m.vertices];oldUV=[tuple(x.uv) for x in m.uv_layers.active.data];oldFaces=[tuple(f.vertices) for f in m.polygons];m.calc_loop_triangles();sourceTriangleLoops=[tuple(t.loops) for t in m.loop_triangles]
# UV grid parameters are identical for both solidified cloth surfaces and rim.
params=[[] for _ in m.vertices]
for li,loop in enumerate(m.loops):params[loop.vertex_index].append(Vector(oldUV[li]))
params=[sum(vs,Vector((0,0)))/len(vs) for vs in params]
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def gaussian(x,width):return math.exp(-.5*(x/width)**2)
def deformation(u,t):
 grow=smooth((t-.14)/.38)
 # Three unequal, individually authored spreading fold paths; no periodic wave.
 centers=(.42-.24*t+.025*math.sin(t*math.pi),.52+.055*t+.030*math.sin(t*math.pi*1.3),.63+.23*t-.035*math.sin(t*math.pi))
 depth=sum(amp*gaussian(u-center,width)*grow*(.65+.35*t) for amp,center,width in zip((.034,.058,.043),centers,(.080,.069,.095)))
 # Shallow oblique tension fold crosses only the upper-central panel.
 diag_center=.24+.90*(t-.22);diag=.013*gaussian(u-diag_center,.047)*smooth((t-.20)/.12)*smooth((.73-t)/.17)
 hem=smooth((t-.72)/.28);dx=.026*math.sin(math.pi*u)*hem
 hem_scallop=gaussian(u-.40,.18)-(1-u)*gaussian(-.40,.18)-u*gaussian(.60,.18)
 dz=.0714*(u-.5)*hem-.010*hem_scallop*hem
 return Vector((dx,depth+diag,dz))
for i,v in enumerate(m.vertices):v.co=old[i]+deformation(*params[i])
m.update()
if m.has_custom_normals:m.normals_split_custom_set([(0,0,0)]*len(m.loops))
m.update();m.calc_loop_triangles()
new=[v.co.copy() for v in m.vertices]
assert oldUV==[tuple(x.uv) for x in m.uv_layers.active.data]
assert oldFaces==[tuple(f.vertices) for f in m.polygons]
assert all(new[i]==old[i] for i,(u,t) in enumerate(params) if t<=.14)
assert min(new[i].y-old[i].y for i in range(len(old)))>=-1e-7
width=lambda ps:max(p.x for p in ps)-min(p.x for p in ps)
assert abs(width(new)-width(old))<1e-6
# Actual inherited body meshes in cape-local coordinates. No proxies are added.
bodyverts=[];bodyfaces=[];bodylabels=[];inverse=o.matrix_world.inverted()
for ob in bpy.data.objects:
 if ob.type!='MESH' or ob==o or ob.hide_render:continue
 matrix=inverse@ob.matrix_world;me=ob.data;me.calc_loop_triangles();offset=len(bodyverts);bodyverts.extend(matrix@v.co for v in me.vertices)
 for tri in me.loop_triangles:bodyfaces.append(tuple(offset+i for i in tri.vertices));bodylabels.append(ob.name)
body=BVHTree.FromPolygons(bodyverts,bodyfaces,all_triangles=True,epsilon=0)
faces=[tuple(m.loops[li].vertex_index for li in loops) for loops in sourceTriangleLoops]
def overlaps(ps):return set(BVHTree.FromPolygons(ps,faces,all_triangles=True,epsilon=0).overlap(body))
before_hits=overlaps(old);after_hits=overlaps(new);new_hits=after_hits-before_hits
# Preserve any inherited attachment contacts; disallow new collisions.
assert not new_hits,[(a,bodylabels[b]) for a,b in list(new_hits)[:20]]
assert protected=={x.name:state(x) for x in bpy.data.objects}
assert all(meshhash(bpy.data.objects[n])==h for n,h in others.items())
pack=json.loads((S/'knight-v6-unity-meshes.json').read_text());before=json.loads((S/'knight-v6-unity-meshes.json').read_text());entry=next(e for e in pack['objects'] if e['gameObjectName']==KEY)
positions=[];normals=[];uv=[];indices=[]
for loops in sourceTriangleLoops:
 base=len(positions)//3
 for li in loops:
  p=m.vertices[m.loops[li].vertex_index].co;n=m.corner_normals[li].vector;positions.extend((-p.x,p.z,-p.y));normals.extend((-n.x,n.z,-n.y));uv.extend(m.uv_layers.active.data[li].uv)
 indices.extend((base,base+2,base+1))
entry.update(positions=positions,normals=normals,uv=uv,indices=indices,vertexCount=len(positions)//3,triangleCount=len(indices)//3)
assert all(a==b for a,b in zip(pack['objects'],before['objects']) if a['gameObjectName']!=KEY)
assert entry['uv']==next(e for e in before['objects'] if e['gameObjectName']==KEY)['uv']
(W/'knight-v7-unity-meshes.json').write_text(json.dumps(pack),encoding='utf-8');shutil.copyfile(S/'helmet-v6-unity-mesh.json',W/'helmet-v6-unity-mesh.json')
bpy.ops.wm.save_as_mainfile(filepath=str(W/'knight-v7.blend'))
hem=[(float(u),old[i].z,new[i].z) for i,(u,t) in enumerate(params) if t>.9999]
report=dict(status='AWAITING_DIRECT_REVIEW',artDerivative=True,physicsSimulationEquilibriumClaim=False,capeTriangles=entry['triangleCount'],capeVertices=entry['vertexCount'],boundsBefore=[[min(p[k] for p in old),max(p[k] for p in old)] for k in range(3)],boundsAfter=[[min(p[k] for p in new),max(p[k] for p in new)] for k in range(3)],widthMetersBefore=width(old),widthMetersAfter=width(new),maxFoldDepthAdded=max(new[i].y-old[i].y for i in range(len(old))),hemLeftToRightAuthoredDifference=.0714,hemRelativeToWidth=.0714/width(old),hemSamples=hem,collarBandExact=True,topologyExact=True,UVExact=True,allOtherObjectStatesExact=True,allOtherBlenderMeshesIncludingNormalsExact=True,allSixOtherJSONRecordsExact=True,helmetJSONByteExact=sha(W/'helmet-v6-unity-mesh.json')==sha(S/'helmet-v6-unity-mesh.json'),actualBodyOverlapPairsBefore=len(before_hits),actualBodyOverlapPairsAfter=len(after_hits),newBodyOverlapPairs=len(new_hits),bodyContactObjectsBefore=sorted(set(bodylabels[b] for a,b in before_hits)),sourceFilesUnchanged=all(sha(S/n)==h for n,h in protected_files.items()),sha256={p.name:sha(p) for p in [W/'knight-v7.blend',W/'knight-v7-unity-meshes.json',W/'helmet-v6-unity-mesh.json']})
(W/'build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='hemSamples'},indent=2),flush=True)
