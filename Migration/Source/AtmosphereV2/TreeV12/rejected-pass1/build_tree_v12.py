"""V12 bounded anatomy refinement of immutable V11 textured derivative.
Blender 5.2.1 --background --threads 3 --python build_tree_v12.py.
"""
import bpy,json,math,hashlib,ast
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
import numpy as np
W=Path(__file__).resolve().parent;S=W.parent/'TreeV11';D=W/'derivative';D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected={str(p.relative_to(S)):sha(p) for p in S.rglob('*') if p.is_file()}
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
xz=p[:,[0,2]];totalDelta=np.zeros_like(p);best=np.zeros(len(p));pathstats=[]
def smooth(a):a=np.clip(a,0,1);return a*a*(3-2*a)
for name,points,radius in paths:
 points=np.array(points);dist=np.full(len(p),999.);near=np.zeros((len(p),2));tangent=np.zeros((len(p),2));progress=np.zeros(len(p));lengths=np.linalg.norm(np.diff(points,axis=0),axis=1);cum=np.r_[0,np.cumsum(lengths)]
 for j,(a,b) in enumerate(zip(points[:-1],points[1:])):
  v=b-a;t=np.clip(((xz-a)*v).sum(axis=1)/(v*v).sum(),0,1);q=a+t[:,None]*v;dd=np.linalg.norm(xz-q,axis=1);take=dd<dist;near[take]=q[take];dist[take]=dd[take];tangent[take]=v/np.linalg.norm(v);progress[take]=(cum[j]+t[take]*lengths[j])/cum[-1]
 weight=smooth((radius-dist)/(.35*radius))*smooth(progress/.18)*smooth((1-progress)/.24)
 # Only the broad surface zone; depth outliers smoothly attenuate.
 weight*=smooth((.95-np.abs(p[:,1]))/.25)
 delta=np.zeros_like(p);delta[:,[0,2]]=(near-xz)*.18*weight[:,None];delta[:,1]=-p[:,1]*.18*weight
 take=weight>best;totalDelta[take]=delta[take];best[take]=weight[take]
 pathstats.append(dict(name=name,maxCrossSectionReduction=.18,vertices=int((weight>.01).sum())))
p+=totalDelta
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
chosen=seeds[::3];spikeWeight=np.zeros(len(u))
for i in chosen:
 for co,j,dist in kdt.find_range(Vector(u[i]),.22):spikeWeight[j]=max(spikeWeight[j],float(smooth((.22-dist)/.15)))
# Retract convex relief only; concave furrows and unselected ridges remain.
local=spikeWeight*np.clip(prominence/.025,0,1)*.92;u-=res*local[:,None];p=u[inv]
# Four unequal root corridors preserve surface flow. Intervening fringe sinks,
# and final radial quarter of dominant roots buries below the review plane z=0.
r=np.linalg.norm(p[:,:2],axis=1);theta=np.arctan2(p[:,1],p[:,0]);rootWeight=smooth((.95-p[:,2])/.65)
rootdirs=[(-2.60,.35),(-.90,.30),(.45,.32),(2.15,.40)];dominant=np.zeros(len(p))
for angle,width in rootdirs:
 diff=np.arctan2(np.sin(theta-angle),np.cos(theta-angle));dominant=np.maximum(dominant,np.exp(-.5*(diff/width)**2))
outer=smooth((r-.48)/.73);between=(1-dominant)*outer*rootWeight
p[:,2]-=.36*between
terminal=smooth((r-.97)/.30)*rootWeight
p[:,2]-=.32*terminal
# Preserve original global scale/origin and every upper-crown tip; no recenter.
assign(o,p)
# Match exceptional triangle normal sanitation in the saved Blender surface too.
m.calc_loop_triangles();cn=[x.vector.copy() for x in m.corner_normals];fixed=0
for t in m.loop_triangles:
 a,b,c=[m.vertices[i].co for i in t.vertices];fn=(b-a).cross(c-a).normalized()
 if fn.dot(sum((cn[i] for i in t.loops),Vector()))<=0:
  for i in t.loops:cn[i]=fn.copy()
  fixed+=1
m.normals_split_custom_set(cn);m.update()
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
before=o.copy();before.data=o.data.copy();bpy.context.collection.objects.link(before);before.name='V11 before reference';assign(before,original);before.hide_render=True

def aim(obj,t):obj.rotation_euler=(Vector(t)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=7.5;scene.camera=cam
for loc,power,size in [((-5,-6,9),1700,5),((5,-3,6),800,4),((0,5,8),1200,5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);li=bpy.context.object;li.data.energy=power;li.data.size=size;aim(li,(0,0,3))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));floor=bpy.context.object;floor.name='Review ground only';mat=bpy.data.materials.new('Neutral ground');mat.diffuse_color=(.085,.09,.095,1);floor.data.materials.append(mat)
views={'front':((0,-14,3.14),(0,0,3.14),7.5),'arc-left':((-7,-12,14),(0,0,3),7.7),'arc-right':((7,-12,14),(0,0,3),7.7),'roots':((4,-7,5),(0,0,.65),3.7)}
for tag,obj in [('before',before),('after',o)]:
 before.hide_render=tag!='before';o.hide_render=tag!='after'
 for name,(loc,target,scale) in views.items():
  cam.location=loc;cam.data.ortho_scale=scale;aim(cam,target);scene.render.filepath=str(D/f'{tag}-{name}.png');bpy.ops.render.render(write_still=True)
report=dict(source=str(S/'derivative/tree-v11-art-directed.blend'),sourceSHA=protected['derivative/tree-v11-art-directed.blend'],export=result,forkRegions=pathstats,detectedConvexSpurSites=len(seeds),selectedSpurSites=len(chosen),selectedSpurCoordinates=[u[i].tolist() for i in chosen],rootDirectionsRadians=rootdirs,rootTerminalBurialStartRadius=.97,rootTerminalBurialEndRadius=1.27,rootTerminalBurialMax=.32,interRootFringeMaxSink=.36,sourceTopologyUnchanged=True,sourceUVExact=True,blenderNormalFaceCorrections=fixed,originalBounds=[original.min(axis=0).tolist(),original.max(axis=0).tolist()],finalBounds=[p.min(axis=0).tolist(),p.max(axis=0).tolist()],unchangedVertices=int((np.linalg.norm(p-original,axis=1)<1e-7).sum()),protectedV11Unchanged=all(sha(S/n)==h for n,h in protected.items()),status='AWAITING_DIRECT_REVIEW')
(D/'build-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
