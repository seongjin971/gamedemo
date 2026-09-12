"""TreeV16: source-only V12 anatomy derivative, exact native TRS and UV.
Run Blender 5.2.1 --background --threads 3 --python this_file -- --geometry-only.
No Unity writes; no source overwrites. Rendering is a separate scheduled script.
"""
import bpy,bmesh,json,math,hashlib,ast,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
W=Path(__file__).resolve().parent;S=W.parent/'TreeV12';D=W
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
INPUTS=[S/'derivative/tree-v12.blend',S/'derivative/tree-v12-mesh.json',W.parent/'PavingV15/paving-v15-mesh.json',W.parent/'ContactV14/contact-v14-deposits.json',W.parent/'ContactV14/contact-v14-rubble.json',W.parent/'ContactV14/contact-v14.blend']
protected={str(p):sha(p) for p in INPUTS}
bpy.ops.wm.open_mainfile(filepath=str(INPUTS[0]));o=next(x for x in bpy.data.objects if x.type=='MESH');o.name='TreeV16 continuous forks and buried root endings';m=o.data
tree=ast.parse((W.parent/'TreeV11/build_tree_v11.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('coords','assign','export')],type_ignores=[]),'v11_export_functions','exec'))
old=coords(o).astype(np.float64);oldUV=[tuple(x.uv) for x in m.uv_layers.active.data]
oldfaces=[tuple(x.vertices) for x in m.polygons]
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def angular(a):return np.arctan2(np.sin(a),np.cos(a))
# Three actual horizontal masses. Cross-section influence includes their outside
# surface, unlike V12's narrow central band. End fades preserve twig attachment.
paths=[('lower_left',[(-.12,1.76),(-.66,2.22),(-1.06,2.35),(-1.62,2.10),(-2.08,2.26)],.68),('lower_right',[(.34,1.64),(.87,1.81),(1.35,2.00),(1.82,2.28),(2.36,2.27)],.64),('upper_left',[(-.05,3.48),(-.32,3.97),(-.60,4.16),(-1.16,4.06),(-1.78,4.34)],.65)]
def closest(q,points):
 xz=q[:,[0,2]];dist=np.full(len(q),999.);near=np.zeros_like(q);prog=np.zeros(len(q));length=np.linalg.norm(np.diff(points,axis=0),axis=1);cum=np.r_[0,np.cumsum(length)]
 for j,(a,b) in enumerate(zip(points[:-1],points[1:])):
  v=b-a;t=np.clip(((xz-a)*v).sum(axis=1)/(v*v).sum(),0,1);p=a+t[:,None]*v;d=np.linalg.norm(xz-p,axis=1);take=d<dist;dist[take]=d[take];near[take,0]=p[take,0];near[take,2]=p[take,1];prog[take]=(cum[j]+t[take]*length[j])/cum[-1]
 return dist,near,prog
def forks(q):
 delta=np.zeros_like(q);ws=np.zeros(len(q));records=[]
 for name,points,radius in paths:
  dist,near,prog=closest(q,np.array(points));near[:,1]=0
  cross=np.linalg.norm(q-near,axis=1)
  w=smooth((radius+.26-cross)/.26)*smooth(prog/.13)*smooth((1-prog)/.15)*smooth((4.9-q[:,2])/.30)
  delta+=(near-q)*(.18*w[:,None]);ws+=w
  records.append((name,cross,prog,w))
 return q+delta/np.maximum(1,ws)[:,None],records
p,forkdata=forks(old)
# Short selected bark projections only. Seam-identical coordinates share a field.
unique,inv=np.unique(np.round(old,6),axis=0,return_inverse=True);count=np.bincount(inv);u=np.zeros_like(unique);np.add.at(u,inv,p);u/=count[:,None]
ed=np.array([e.vertices[:] for e in m.edges]);ed=inv[ed];ed=np.unique(np.sort(ed[ed[:,0]!=ed[:,1]],axis=1),axis=0);aa=np.r_[ed[:,0],ed[:,1]];bb=np.r_[ed[:,1],ed[:,0]];degree=np.bincount(aa,minlength=len(u));relax=u.copy()
for _ in range(28):
 total=np.zeros_like(u);np.add.at(total,aa,relax[bb]);relax=.6*relax+.4*total/np.maximum(degree,1)[:,None]
res=u-relax;ns=np.zeros((len(m.vertices),3),np.float32);m.vertices.foreach_get('normal',ns.ravel());un=np.zeros_like(u);np.add.at(un,inv,ns);un/=np.maximum(np.linalg.norm(un,axis=1),1e-9)[:,None];prom=(res*un).sum(axis=1)
bulk=np.zeros(len(u));np.maximum.at(bulk,inv,np.maximum.reduce([x[3] for x in forkdata]));seeds=[]
for i in np.argsort(prom)[::-1]:
 if prom[i]<.025:break
 if bulk[i]<.5 or not 1.65<u[i,2]<4.7:continue
 if any(np.linalg.norm(u[i]-u[j])<.22 for j in seeds):continue
 seeds.append(int(i))
spurs=[]
for i in seeds[::3]:
 d=-res[i]*.75;d*=min(1,.05/max(np.linalg.norm(d),1e-8));spurs.append((u[i].copy(),d))
def spikes(q):
 out=q.copy()
 for c,d in spurs:
  w=np.clip(1-(np.linalg.norm(q-c,axis=1)/.25)**2,0,1)**3*smooth((4.9-q[:,2])/.15);out+=w[:,None]*d
 return out
p=spikes(p)
# Fixed world transform read from the accepted ContactV14 dependency evidence.
evidence=json.loads((W.parent/'ContactV14/world-contact-evidence.json').read_text());yaw=math.radians(evidence['combined_yaw_degrees']);cs,sn=math.cos(yaw),math.sin(yaw);scale=1.73
def world(q):
 native=np.c_[-q[:,0],q[:,2],-q[:,1]]
 return np.c_[7.2+scale*(cs*native[:,0]+sn*native[:,2]),scale*native[:,1],3.7+scale*(-sn*native[:,0]+cs*native[:,2])]
pave=json.loads(INPUTS[2].read_text());pv=np.array(pave['positions']).reshape(-1,3);pi=np.array(pave['indices']).reshape(-1,3);bvh=BVHTree.FromPolygons(pv.tolist(),pi.tolist(),all_triangles=True)
# Actual retained parapet is a separate physical cover where the floor ends.
# Append read-only context for geometric queries, then remove it before saving.
with bpy.data.libraries.load(str(INPUTS[5]),link=False) as (libin,libout):libout.objects=[name for name in libin.objects if name.startswith('Retained parapet ')]
wallverts=[];wallfaces=[]
for ob in libout.objects:
 bpy.context.collection.objects.link(ob)
bpy.context.view_layer.update()
for ob in libout.objects:
 offset=len(wallverts);matrix=ob.matrix_world;ob.data.calc_loop_triangles()
 for v in ob.data.vertices:
  v=matrix@v.co;wallverts.append((v.x,v.z,-v.y))
 wallfaces.extend(tuple(offset+i for i in tri.vertices) for tri in ob.data.loop_triangles)
 bpy.data.objects.remove(ob,do_unlink=True)
wallbvh=BVHTree.FromPolygons(wallverts,wallfaces,all_triangles=True)
def ground(x,z):
 hit=bvh.ray_cast(Vector((float(x),2,float(z))),Vector((0,-1,0)),4)[0]
 if hit is None:hit=wallbvh.ray_cast(Vector((float(x),3,float(z))),Vector((0,-1,0)),5)[0]
 return float(hit.y) if hit is not None else None
rootdirs=[-2.6,-.9,.45,2.15];ends=[1.76,1.60,1.73,1.75];sinks=[];rootplans=[]
def root_fields(q,k):
 r=np.linalg.norm(q[:,:2],axis=1);theta=np.arctan2(q[:,1],q[:,0]);diff=angular(theta-rootdirs[k]);height=smooth((1.35-q[:,2])/.45);side=smooth((.74-np.abs(diff))/.18);w=height*side
 t=smooth((r-.75*ends[k])/(.15*ends[k]));narrow=smooth((r-(.55 if k==3 else .38)*ends[k])/((.40 if k==3 else .43)*ends[k]))
 return r,theta,diff,w,t,narrow
def roots(q,vertical=True):
 out=q.copy();horizontal=np.zeros((len(q),2));verticalDelta=np.zeros(len(q));sumw=np.zeros(len(q))
 for k in range(4):
  r,theta,diff,w,t,narrow=root_fields(q,k)
  # Preserve radial reach for three floor roots. The wall root retracts inward
  # and turns along the real parapet; it never extends beyond the current root.
  rr=r-(.34*narrow if k==3 else 0)
  aa=theta-(.65 if k==3 else .55)*diff*narrow-(.50*narrow if k==3 else 0)
  target=np.c_[rr*np.cos(aa),rr*np.sin(aa)];horizontal+=(target-q[:,:2])*w[:,None];sumw+=w
  verticalDelta-=q[:,2]*.18*narrow*w
  if vertical:verticalDelta-=sinks[k]*t*w
 out[:,:2]+=horizontal/np.maximum(1,sumw)[:,None]
 out[:,2]+=verticalDelta/np.maximum(1,sumw)
 return out
h=roots(p,False)
for k in range(4):
 r,a,d,w,t,n=root_fields(p,k);cap=(np.abs(d)<.54)&(r>=.90*ends[k])&(r<ends[k]+.18)&(p[:,2]<.85)&(p[:,2]>-.03)
 wp=world(h[cap]);supports=[ground(x,z) for x,y,z in wp];valid=[i for i,x in enumerate(supports) if x is not None]
 assert valid,(k,'No actual paving beneath planned terminal section')
 assert len(valid)==len(supports),(k,'Terminal samples unsupported by floor or retained parapet',len(supports)-len(valid))
 # A conservative constant downward translation brings EVERY terminal top
 # vertex under its actual support; no per-vertex clamping or folded caps.
 # Solve against corresponding support at each terminal point, rather than
 # pairing the highest root point with an unrelated lowest ground depression.
 safe=min(supports[i] for i in valid)-.045
 sink=max(.10,max(float(h[cap,2][i]-(supports[i]-.045)/scale) for i in valid));sinks.append(sink)
 rootplans.append(dict(root=k+1,role='parapet' if k==3 else 'floor',sourceCenterlineEndRadiusLocal=ends[k],descentStartRadiusLocal=.75*ends[k],fullDescentRadiusLocal=.90*ends[k],terminalVertexSamples=int(cap.sum()),supportSamples=len(valid),unsupportedTerminalSamples=len(supports)-len(valid),minimumActualSupportWorldY=min(supports[i] for i in valid),minimumSupportMinus45mmWorldY=safe,downwardTranslationLocal=sink))
new=roots(p)
# Field Jacobian, checked at all source vertices. Positive determinant prevents
# the graph-local folds that were rejected during V12.
def fullwarp(q):return roots(spikes(forks(q)[0]))
eps=1e-4;jac=np.empty((len(old),3,3))
for axis in range(3):
 off=np.zeros_like(old);off[:,axis]=eps;jac[:,:,axis]=(fullwarp(old+off)-fullwarp(old-off))/(2*eps)
det=np.linalg.det(jac);assert det.min()>.025,('Invalid deformation Jacobian',float(det.min()),old[int(np.argmin(det))].tolist())
assign(o,new);m.calc_loop_triangles();corners=[x.vector.copy() for x in m.corner_normals];fixed=0
for tri in m.loop_triangles:
 a,b,c=[m.vertices[i].co for i in tri.vertices];fn=(b-a).cross(c-a).normalized();mean=sum((corners[i] for i in tri.loops),Vector())
 if fn.dot(mean)<=.03:
  amount=max(0,-fn.dot(mean)/3)+.03
  for i in tri.loops:corners[i]=(corners[i]+fn*amount).normalized()
  fixed+=1
m.normals_split_custom_set(corners);m.update()
assert oldUV==[tuple(x.uv) for x in m.uv_layers.active.data] and oldfaces==[tuple(x.vertices) for x in m.polygons]
result=export(o,'tree-v16-mesh');bpy.ops.wm.save_as_mainfile(filepath=str(W/'tree-v16.blend'))
# Terminal top-envelope evidence against exact final PavingV15 triangles.
for k,row in enumerate(rootplans):
 r,a,d,w,t,n=root_fields(p,k);sel=(np.abs(d)<.54)&(r>=.90*ends[k])&(r<ends[k]+.18)&(p[:,2]<.85)&(p[:,2]>-.03);wp=world(new[sel]);clearances=[]
 for x,y,z in wp:
  gy=ground(x,z)
  if gy is not None:clearances.append(gy-y)
 row['minimumTerminalBurialBelowActualSupportMeters']=min(clearances);row['terminalWorldBounds']=[wp.min(axis=0).tolist(),wp.max(axis=0).tolist()];assert min(clearances)>.029
assert all(sha(Path(n))==v for n,v in protected.items())
report=dict(status='GEOMETRY_QA_PENDING_PREVIEW',sourceHashes=protected,treeExport=result,rootPlans=rootplans,rootRadialExtension=0,parapetRootRetractionLocal=.34,parapetRootTurnRadians=-.50,selectedShortSpikes=len(spurs),detectedShortSpikes=len(seeds),minimumDeformationJacobian=float(det.min()),normalCorrections=fixed,sourceUVAndTopologyExact=True,originalTRS=evidence['native_tree_parent'],meshLocalYawDegrees=-20,unchangedSourceVertices=int((np.linalg.norm(new-old,axis=1)<1e-7).sum()),forkTargetReduction=.18,notes='Three floor roots and separate parapet corridor. No original source or Unity edits. Native support/cover review and nav regeneration still required.')
(W/'build-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
