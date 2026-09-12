"""V12 bounded anatomy refinement of immutable V11 textured derivative.
Blender 5.2.1 --background --threads 3 --python build_tree_v12.py.
"""
import bpy,json,math,hashlib,ast,os
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
import numpy as np
W=Path(__file__).resolve().parent;S=W.parent/'TreeV11';D=W/'derivative';D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected={p.relative_to(S).as_posix():sha(p) for p in S.rglob('*') if p.is_file()}
(W/'protected-v11-hashes.json').write_text(json.dumps(protected,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(S/'derivative/tree-v11-art-directed.blend'))
for o in list(bpy.data.objects):
 if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
o=next(o for o in bpy.data.objects if o.type=='MESH');o.name='TreeV12 anatomical refinement'
m=o.data
# Reuse only independent export/coordinate functions; never execute V11 build.
tree=ast.parse((S/'build_tree_v11.py').read_text());selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('coords','assign','export')]
exec(compile(ast.Module(body=selected,type_ignores=[]),'v11_functions','exec'))
original=coords(o);p=original.astype(np.float64).copy();m.calc_loop_triangles();originalUV=[tuple(t.uv) for t in m.uv_layers.active.data]
# X/Z centreline control points are chosen from the actual front view. Shrink
# perpendicular cross-sections, not limb length; fade both end caps and border.
paths=[('lower_left',[(-.10,1.75),(-.65,2.22),(-1.06,2.35),(-1.62,2.10),(-2.00,2.25)],.38),('lower_right',[(.38,1.62),(.89,1.80),(1.35,2.00),(1.81,2.28),(2.30,2.27)],.36),('upper_right',[(.14,3.13),(.66,3.57),(1.01,4.12),(1.38,4.28),(1.80,4.52)],.39),('upper_left',[(-.05,3.48),(-.32,3.97),(-.60,4.16),(-1.16,4.06),(-1.68,4.30)],.35)]
def smooth(a):a=np.clip(a,0,1);return a*a*(3-2*a)
def fork_warp(q):
 p=q.copy()
 xz=p[:,[0,2]];totalDelta=np.zeros_like(p);best=np.zeros(len(p));pathstats=[];sumWeight=np.zeros(len(p))
 def smooth(a):a=np.clip(a,0,1);return a*a*(3-2*a)
 for name,points,radius in paths:
  points=np.array(points);dist=np.full(len(p),999.);near=np.zeros((len(p),2));tangent=np.zeros((len(p),2));progress=np.zeros(len(p));lengths=np.linalg.norm(np.diff(points,axis=0),axis=1);cum=np.r_[0,np.cumsum(lengths)]
  for j,(a,b) in enumerate(zip(points[:-1],points[1:])):
   v=b-a;t=np.clip(((xz-a)*v).sum(axis=1)/(v*v).sum(),0,1);q=a+t[:,None]*v;dd=np.linalg.norm(xz-q,axis=1);take=dd<dist;near[take]=q[take];dist[take]=dd[take];tangent[take]=v/np.linalg.norm(v);progress[take]=(cum[j]+t[take]*lengths[j])/cum[-1]
  weight=smooth((radius-dist)/(.35*radius))*smooth(progress/.18)*smooth((1-progress)/.24)
  # Only the broad surface zone; depth outliers smoothly attenuate.
  weight*=smooth((.95-np.abs(p[:,1]))/.25)
  delta=np.zeros_like(p);delta[:,[0,2]]=(near-xz)*.18*weight[:,None];delta[:,1]=-p[:,1]*.18*weight
  totalDelta+=delta;sumWeight+=weight;best=np.maximum(best,weight)
  pathstats.append(dict(name=name,maxCrossSectionReduction=.18,vertices=int((weight>.01).sum())))
 p+=totalDelta/np.maximum(1,sumWeight)[:,None]
 return p,best,pathstats
p,best,pathstats=fork_warp(p)
# Find short convex protrusions on broad limbs by multi-ring surface relaxation.
# Coincident seam vertices share a unique-position adjacency, preventing UV cracks.
rounded=np.round(original,6);unique,inv=np.unique(rounded,axis=0,return_inverse=True);u=np.zeros_like(unique);count=np.bincount(inv);np.add.at(u,inv,p);u/=count[:,None]
edges=np.array([[e.vertices[0],e.vertices[1]] for e in m.edges]);edges=inv[edges];edges=edges[edges[:,0]!=edges[:,1]];edges=np.unique(np.sort(edges,axis=1),axis=0);aa=np.r_[edges[:,0],edges[:,1]];bb=np.r_[edges[:,1],edges[:,0]];degree=np.bincount(aa,minlength=len(u));relax=u.copy()
for _ in range(36):
 accum=np.zeros_like(u);np.add.at(accum,aa,relax[bb]);avg=accum/np.maximum(degree,1)[:,None];relax=.55*relax+.45*avg
norm=np.zeros((len(m.vertices),3),np.float32);m.vertices.foreach_get('normal',norm.ravel());un=np.zeros_like(u);np.add.at(un,inv,norm);un/=np.maximum(np.linalg.norm(un,axis=1),1e-9)[:,None]
res=u-relax;prominence=(res*un).sum(axis=1);bulk=np.zeros(len(u));np.maximum.at(bulk,inv,best)
kdt=KDTree(len(u))
for i,q in enumerate(u):kdt.insert(Vector(q),i)
kdt.balance();seeds=[]
for i in np.argsort(prominence)[::-1]:
 if prominence[i]<.025:break
 if bulk[i]<.15 or not 1.8<u[i,2]<4.8:continue
 if any(np.linalg.norm(u[i]-u[j])<.24 for j in seeds):continue
 seeds.append(int(i))
# One third of isolated convex spur sites, distributed by prominence ranking.
chosen=seeds[::3];spatialSpurs=[]
for i in chosen:
 vector=-res[i]*.75;vector*=min(1,.055/max(np.linalg.norm(vector),1e-8));spatialSpurs.append((u[i].copy(),vector))
def spike_warp(q):
 result=q.copy()
 for center,vector in spatialSpurs:
  distance=np.linalg.norm(q-center,axis=1);weight=np.clip(1-(distance/.30)**2,0,1)**3
  result+=weight[:,None]*vector
 return result
p=spike_warp(p)
# Four unequal root corridors preserve surface flow. Intervening fringe sinks,
# and final radial quarter of dominant roots buries below the review plane z=0.
rootdirs=[(-2.60,.35),(-.90,.30),(.45,.32),(2.15,.40)]
def root_warp(q):
 p=q.copy()
 r=np.linalg.norm(p[:,:2],axis=1);theta=np.arctan2(p[:,1],p[:,0]);rootWeight=smooth((1.35-p[:,2])/1.05)
 dominant=np.zeros(len(p))
 for angle,width in rootdirs:
  diff=np.arctan2(np.sin(theta-angle),np.cos(theta-angle));dominant=np.maximum(dominant,np.exp(-.5*(diff/width)**2))
 outer=smooth((r-.30)/.65);between=(1-dominant)*outer*rootWeight
 # Unfold the original steep foot into four lower, longer buttress corridors.
 extension=1+.35*dominant*outer*rootWeight
 p[:,:2]*=extension[:,None]
 p[:,2]*=1-.35*dominant*outer*rootWeight
 p[:,2]-=.55*between
 # Selected root ridges stay proud before their last quarter disappears.
 p[:,2]+=.08*dominant*outer*rootWeight*(1-smooth((r-1.08)/.25))
 terminal=smooth((r-1.08)/.30)*rootWeight
 p[:,2]-=.25*terminal
 return p
p=root_warp(p)
# Preserve original global scale/origin and every upper-crown tip; no recenter.
# Spatially continuous fields act equally across coincident UV/source islands.
# Check deformation Jacobian, which distinguishes actual volume inversion from
# a valid face rotating >90 degrees relative to its old sliver normal.
def full_warp(q):return root_warp(spike_warp(fork_warp(q)[0]))
probe=original.astype(np.float64);jac=np.empty((len(probe),3,3));epsilon=1e-4
for axis in range(3):
 off=np.zeros_like(probe);off[:,axis]=epsilon;jac[:,:,axis]=(full_warp(probe+off)-full_warp(probe-off))/(2*epsilon)
determinants=np.linalg.det(jac);assert determinants.min()>.03,float(determinants.min())
assign(o,p)
# Match exceptional triangle normal sanitation in the saved Blender surface too.
def correct_normals(mesh):
 mesh.calc_loop_triangles();cn=[x.vector.copy() for x in mesh.corner_normals];fixed=0
 for t in mesh.loop_triangles:
  a,b,c=[mesh.vertices[i].co for i in t.vertices];fn=(b-a).cross(c-a).normalized();mean=sum((cn[i] for i in t.loops),Vector())
  if fn.dot(mean)<=.03:
   # Minimal hemisphere projection retains smooth shading instead of creating
   # a hard flat triangle on tiny inherited folds.
   amount=max(0,-fn.dot(mean)/3)+.03
   for i in t.loops:cn[i]=(cn[i]+fn*amount).normalized()
   if fn.dot(sum((cn[i] for i in t.loops),Vector()))<=0:
    for i in t.loops:cn[i]=fn.copy()
   fixed+=1
 mesh.normals_split_custom_set(cn);mesh.update();return fixed
fixed=correct_normals(m)
assert originalUV==[tuple(t.uv) for t in m.uv_layers.active.data]
result=export(o,'tree-v12-mesh');print('EXPORT',result,flush=True)
# Save asset before adding any review floor, camera, or lights.
bpy.ops.wm.save_as_mainfile(filepath=str(D/'tree-v12.blend'))
# Matched before/after clean textured rig. Matte material change here is preview
# only and applied equally; root retains Unity material authority.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.resolution_x=1152;scene.render.resolution_y=1152;scene.render.resolution_percentage=100;scene.render.use_persistent_data=True;scene.view_settings.view_transform='AgX'
scene.world=bpy.data.worlds.new('Neutral');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.09,.09,.09,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.55
for mat in m.materials:
 bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 for link in list(mat.node_tree.links):
  if link.to_node==bs and link.to_socket.name=='Roughness':mat.node_tree.links.remove(link)
 bs.inputs['Roughness'].default_value=.82
before=o.copy();before.data=o.data.copy();bpy.context.collection.objects.link(before);before.name='V11 before reference';assign(before,original);correct_normals(before.data);before.hide_render=True

def aim(obj,t):obj.rotation_euler=(Vector(t)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=7.5;scene.camera=cam
for loc,power,size in [((-5,-6,9),1700,5),((5,-3,6),800,4),((0,5,8),1200,5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);li=bpy.context.object;li.data.energy=power;li.data.size=size;aim(li,(0,0,3))
bpy.ops.mesh.primitive_cube_add(size=2,location=(0,0,-2));bpy.context.object.scale=(100,100,2);floor=bpy.context.object;floor.name='Review ground only';mat=bpy.data.materials.new('Neutral ground');mat.diffuse_color=(.085,.09,.095,1);floor.data.materials.append(mat)
views={'front':((0,-14,3.14),(0,0,3.14),7.5),'arc-left':((-7,-12,14),(0,0,3),7.7),'arc-right':((7,-12,14),(0,0,3),7.7),'roots':((4,-7,5),(0,0,.65),3.7)}
for tag,obj in [('before',before),('after',o)]:
 if tag=='before' and os.environ.get('TREE_V12_SKIP_BEFORE')=='1':continue
 before.hide_render=tag!='before';o.hide_render=tag!='after'
 for name,(loc,target,scale) in views.items():
  if os.environ.get('TREE_V12_ROOTS_ONLY')=='1' and name!='roots':continue
  cam.location=loc;cam.data.ortho_scale=scale;aim(cam,target);scene.render.filepath=str(D/f'{tag}-{name}.png');bpy.ops.render.render(write_still=True)
report=dict(source=str(S/'derivative/tree-v11-art-directed.blend'),sourceSHA=protected['derivative/tree-v11-art-directed.blend'],export=result,forkRegions=pathstats,detectedConvexSpurSites=len(seeds),selectedSpurSites=len(chosen),selectedSpurCoordinates=[u[i].tolist() for i in chosen],rootDirectionsRadians=rootdirs,rootTerminalBurialStartRadius=1.08,rootTerminalBurialEndRadius=1.38,rootTerminalBurialMax=.25,interRootFringeMaxSink=.55,rootMaxRadialExtension=.35,rootMaxVerticalCompression=.35,minimumDeformationJacobian=float(determinants.min()),jacobianProbeCount=len(probe),spatialSpurMaxTranslation=.055,sourceTopologyUnchanged=True,sourceUVExact=True,blenderNormalFaceCorrections=fixed,originalBounds=[original.min(axis=0).tolist(),original.max(axis=0).tolist()],finalBounds=[p.min(axis=0).tolist(),p.max(axis=0).tolist()],unchangedVertices=int((np.linalg.norm(p-original,axis=1)<1e-7).sum()),protectedV11Unchanged=all(sha(S/n)==h for n,h in protected.items()),status='AWAITING_DIRECT_REVIEW')
(D/'build-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
