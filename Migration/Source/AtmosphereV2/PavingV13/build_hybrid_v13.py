"""V13 contiguous source-matched foreground slabs over a captured stonebed. Blender 5.2.
No Unity or prior source writes. Six-thread build, only after render slot clear.
"""
import bpy,bmesh,json,math,hashlib,random,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;V11=OUT.parent/'PavingV11';MAPS=V11/'maps'
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
PREVIEW=OUT/'previews';PREVIEW.mkdir(exist_ok=True)
rng=random.Random(130045)
prior=json.loads((OUT.parent/'PavingV12/paving-v12-mesh.json').read_text());oldmeta=json.loads((V11/'heightfield-metadata.json').read_text())
rects=oldmeta['coverage_rectangles_xz'];bounds=oldmeta['world_bounds'];PERIOD=(9.2,4.6)
sourcepaths=[OUT.parent/'PavingV12/paving-v12-mesh.json',V11/'paving-v11-mesh.json',V11/'heightfield-metadata.json',OUT/'source_seeds.json']+list(MAPS.glob('*.png'))
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sourcepaths}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
arrays={}
def image_array(channel):
 im=bpy.data.images.load(str(MAPS/f'Tiles130_4K-PNG_{channel}.png'),check_existing=True);im.colorspace_settings.name='Non-Color';w,h=im.size
 arr=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(arr);return arr.reshape(h,w,4)[:,:,0]
height=image_array('Displacement');ao=image_array('AmbientOcclusion')
def sample(arr,u,v):
 h,w=arr.shape;px=(np.asarray(u)%1)*w-.5;py=(np.asarray(v)%1)*h-.5;ix=np.floor(px).astype(int);iy=np.floor(py).astype(int);fx=px-ix;fy=py-iy
 return arr[iy%h,ix%w]*(1-fx)*(1-fy)+arr[iy%h,(ix+1)%w]*fx*(1-fy)+arr[(iy+1)%h,ix%w]*(1-fx)*fy+arr[(iy+1)%h,(ix+1)%w]*fx*fy
def inside(x,z,poly):
 ans=np.zeros(np.asarray(x).shape,dtype=bool)
 for p,q in zip(poly,np.roll(poly,-1,axis=0)):
  ans^=((p[1]>z)!=(q[1]>z))&(x<(q[0]-p[0])*(z-p[1])/(q[1]-p[1]+1e-30)+p[0])
 return ans
def distance(x,z,poly):
 out=np.full(np.asarray(x).shape,np.inf)
 for p,q in zip(poly,np.roll(poly,-1,axis=0)):
  e=q-p;t=np.clip(((x-p[0])*e[0]+(z-p[1])*e[1])/np.dot(e,e),0,1)
  out=np.minimum(out,np.sqrt((x-p[0]-t*e[0])**2+(z-p[1]-t*e[1])**2))
 return out

guides=json.loads((OUT/'source_seeds.json').read_text())['slabs'];templates=[]
for g in guides:
 raw=np.array(g['polygon'],float)/[2048,1024];raw[:,1]=1-raw[:,1]
 raw*=PERIOD;points=[]
 for j,(a,b) in enumerate(zip(raw,np.roll(raw,-1,axis=0))):
  edge=b-a;n=np.array([-edge[1],edge[0]])/np.linalg.norm(edge)
  steps=max(2,math.ceil(np.linalg.norm(edge)/.19))
  for k in range(steps):
   p=a+(b-a)*k/steps
   # Source-guided contour snap: 2.5cm maximum, broad low-frequency polygon
   # remains authoritative; no unrestricted watershed of every small crack.
   shifts=np.linspace(-.025,.025,11);poss=p[None,:]+shifts[:,None]*n
   u,v=poss[:,0]/PERIOD[0],poss[:,1]/PERIOD[1]
   grad=abs(sample(height,u+.002,v)-sample(height,u-.002,v))+abs(sample(height,u,v+.002)-sample(height,u,v-.002))
   score=(1-sample(ao,u,v))+.45*grad-.07*(shifts/.025)**2
   chosen=int(np.argmax(score));points.append(p+shifts[chosen]*n*.45)
 poly=np.array(points)
 # Reduce alternating pixel extrema with one restrained contour-only average.
 poly=.7*poly+.15*np.roll(poly,1,axis=0)+.15*np.roll(poly,-1,axis=0)
 if sum(np.cross(poly[j],poly[(j+1)%len(poly)]) for j in range(len(poly)))<0:poly=poly[::-1]
 templates.append({'id':g['id'],'poly':poly,'center':poly.mean(0),'subordinate':g.get('subordinate',False)})

# Full foreground coverage, exact rectangular clip; rear masked bed preserved.
def clip(poly,axis,value,sign):
 out=[]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  ia=sign*(a[axis]-value)>=-1e-10;ib=sign*(b[axis]-value)>=-1e-10
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*(value-a[axis])/(b[axis]-a[axis]))
 return np.array(out)
def area(poly):
 return abs(sum(np.cross(a,b) for a,b in zip(poly,np.roll(poly,-1,axis=0))))*.5 if len(poly)>2 else 0
def clean(poly):
 out=[]
 for p in poly:
  if not out or np.linalg.norm(p-out[-1])>.025:out.append(p)
 if len(out)>1 and np.linalg.norm(out[0]-out[-1])<.025:out.pop()
 changed=True
 while changed and len(out)>3:
  changed=False
  for j in range(len(out)):
   if abs(np.cross(out[j]-out[j-1],out[(j+1)%len(out)]-out[j]))<1e-10:
    out.pop(j);changed=True;break
 return np.array(out)
def kernel_center(poly):
 # Kernel intersection guarantees radial cap rings lie inside a concave outline.
 ker=np.array([[-100.,-100.],[100.,-100.],[100.,100.],[-100.,100.]])
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  out=[];edge=b-a
  for c,d in zip(ker,np.roll(ker,-1,axis=0)):
   fc=np.cross(edge,c-a);fd=np.cross(edge,d-a);ic=fc>=-1e-9;idd=fd>=-1e-9
   if ic:out.append(c)
   if ic!=idd:out.append(c+(d-c)*fc/(fc-fd))
  ker=np.array(out)
  if len(ker)<3:return None
 return ker.mean(0)
def triangulate(poly):
 # Ear clipping only for non-star-shaped photo outlines; each resulting polygon
 # receives the same source id/plane, so no artificial inter-fragment crack.
 ids=list(range(len(poly)));out=[]
 while len(ids)>3:
  found=False
  for j in range(len(ids)):
   a,b,c=ids[j-1],ids[j],ids[(j+1)%len(ids)];pa,pb,pc=poly[[a,b,c]]
   if np.cross(pb-pa,pc-pb)<=1e-9:continue
   if any(inside(np.array([poly[k,0]]),np.array([poly[k,1]]),np.array([pa,pb,pc]))[0] for k in ids if k not in (a,b,c)):continue
   out.append(poly[[a,b,c]]);ids.pop(j);found=True;break
  assert found,'invalid source polygon'
 out.append(poly[ids]);return out
a=.46;e=.72
selected=[];skipped=[]
for tx in (-1,0):
 for tz in range(-1,5):
  for t in templates:
   shift=np.array([tx*PERIOD[0],tz*PERIOD[1]]);poly=t['poly']+shift
   for axis,value,sign in [(0,bounds[0][0],1),(0,bounds[1][0],-1),(1,rects[0][2],1),(1,bounds[1][2],-1)]:
    if len(poly)<3:break
    poly=clip(poly,axis,value,sign)
   poly=clean(poly)
   if area(poly)<.035:continue
   # Retain one actual source unit, not an ear-clipped collection of slabs.
   center=poly.mean(0)
   selected.append({'template':t,'shift':shift,'poly':poly,'center':center,'screen':None,'area':area(poly)})
assert len(selected)>300,len(selected)

def make_mat(name,textured):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
 bs.inputs['Roughness'].default_value=.72;bs.inputs['Base Color'].default_value=(.18,.205,.22,1)
 if textured:
  for ch,sock in [('Color','Base Color'),('Roughness','Roughness')]:
   im=bpy.data.images.load(str(MAPS/f'Tiles130_4K-PNG_{ch}.png'),check_existing=True);im.colorspace_settings.name='sRGB' if ch=='Color' else 'Non-Color';tex=n.new('ShaderNodeTexImage');tex.image=im;l.new(tex.outputs['Color'],bs.inputs[sock])
  tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(MAPS/'Tiles130_4K-PNG_NormalGL.png'),check_existing=True);tex.image.colorspace_settings.name='Non-Color';nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.4;l.new(tex.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],bs.inputs['Normal'])
 return m
neutral=make_mat('Neutral geometry only',False);textured=make_mat('Actual source4K Color roughness NormalGL .4',True)
objects=[];stone_reports=[]
def make_object(name,verts,faces):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(textured);return ob

for i,s in enumerate(selected):
 source=s['poly'];center=s['center'];scale=np.array([1.0,1.0])
 # No local shrink: adjacent source stones remain in their original positions.
 poly=center+(source-center)*scale;s['final_poly']=poly;s['scale']=scale
 # Roots/water integration: some tops exposed, others submerged. These are
 # explicit art-directed planes, not measured scan elevations.
 subordinate=s['template']['subordinate']
 level=([-.024,-.019,-.014,-.010][i%4] if subordinate else [-.022,-.016,-.009,-.003,.002,-.010][i%6])
 tilt=np.array([rng.uniform(-.006,.006),rng.uniform(-.006,.006)])
 hvals=sample(height,source[:,0]/PERIOD[0],source[:,1]/PERIOD[1]);fit=np.linalg.lstsq(np.c_[source-center,np.ones(len(source))],hvals,rcond=None)[0]
 def uv_for(x,z):
  orig=center+(np.array([x,z])-center)/scale;return orig/np.array(PERIOD)
 def cap_y(x,z):
  orig=center+(np.array([x,z])-center)/scale;hv=float(sample(height,orig[0]/PERIOD[0],orig[1]/PERIOD[1]));res=np.clip(.04*(hv-np.dot(np.r_[orig-center,1],fit)),-.0028,.0028)
  return float(level+np.dot(np.array([x,z])-center,tilt)+res)
 n=len(poly);verts=[]
 inset=[]
 for j,p in enumerate(poly):
  prev=p-poly[(j-1)%n];nxt=poly[(j+1)%n]-p
  prev/=np.linalg.norm(prev);nxt/=np.linalg.norm(nxt)
  npv=np.array([-prev[1],prev[0]]);nnx=np.array([-nxt[1],nxt[0]])
  direction=npv+nnx;direction/=np.linalg.norm(direction)
  width=((.018+.012*(.5+.5*math.sin(j/n*math.tau*2+i))) if subordinate else (.032+.020*(.5+.5*math.sin(j/n*math.tau*2+i))))/max(.6,float(np.dot(direction,npv)))
  inset.append(direction*width)
 inset=np.array(inset);inset_scale=1.0
 for attempt in range(9):
  top_ring=poly+inset*inset_scale
  try:
   assert np.all(inside(top_ring[:,0],top_ring[:,1],poly))
   # Every bevel strip quad must stay convex in XZ, so either triangle
   # diagonal has positive projected area rather than a folded tiny wedge.
   for j in range(n):
    quad=np.array([poly[j],poly[(j+1)%n],top_ring[(j+1)%n],top_ring[j]])
    assert all(np.cross(quad[(k+1)%4]-quad[k],quad[(k+2)%4]-quad[(k+1)%4])>1e-12 for k in range(4))
   captris=triangulate(top_ring)
   assert abs(sum(area(t) for t in captris)-area(top_ring))<1e-7
   break
  except AssertionError as exc:
   failure_reason=str(exc);inset_scale*=.5
 else:
  (OUT/'inset-failure.json').write_text(json.dumps({'id':s['template']['id'],'shift':s['shift'].tolist(),'polygon':poly.tolist(),'inset':inset.tolist(),'top':top_ring.tolist(),'reason':failure_reason}))
  raise AssertionError(('untriangulatable source inset',s['template']['id']))
 for ring in range(3):
  for j,p in enumerate(poly):
   q=top_ring[j] if ring==2 else p
   depth=(.013+.006*(.5+.5*math.sin(j/n*math.tau+i))) if subordinate else (.021+.009*(.5+.5*math.sin(j/n*math.tau+i)))
   yy=-.115 if ring==0 else cap_y(*q)-(depth if ring==1 else 0)
   verts.append((q[0],-q[1],yy))
 # Ear-clipped cap and bottom handle actual concave source contours. One
 # centroid sample per cap triangle retains scan residual without a radial
 # visibility-kernel assumption or skinny-edge recursive subdivision.
 top_ring=np.array([[v[0],-v[1]] for v in verts[2*n:3*n]])
 captris=triangulate(top_ring);bottomtris=triangulate(poly)
 top_lookup={tuple(p):j+2*n for j,p in enumerate(top_ring)}
 bot_lookup={tuple(p):j for j,p in enumerate(poly)}
 faces=[]
 for ring in range(2):
  for j in range(n):faces.append((ring*n+j,ring*n+(j+1)%n,(ring+1)*n+(j+1)%n,(ring+1)*n+j))
 for tri in captris:
  pt=tri.mean(0);ci=len(verts);verts.append((pt[0],-pt[1],cap_y(*pt)))
  ids=[top_lookup[tuple(p)] for p in tri]
  faces.extend([(ids[k],ids[(k+1)%3],ci) for k in range(3)])
 for tri in bottomtris:faces.append(tuple(bot_lookup[tuple(p)] for p in tri[::-1]))
 ob=make_object(f'HeroScanSlab_{i:02d}_{s["template"]["id"]}',verts,faces);me=ob.data
 bm=bmesh.new();bm.from_mesh(me)
 bmesh.ops.triangulate(bm,faces=list(bm.faces))
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nonmanifold=sum(not ed.is_manifold for ed in bm.edges);bm.to_mesh(me);bm.free();me.update()
 projected_top=0.
 for f in me.polygons:
  aa,bb,cc=[me.vertices[k].co for k in f.vertices]
  projected_top+=max(0.,(bb-aa).cross(cc-aa).z*.5)
 assert abs(projected_top-area(poly))<1e-5,('folded source body',s['template']['id'],projected_top,area(poly))
 uvlay=me.uv_layers.new(name='UVMap')
 for loop in me.loops:
  co=me.vertices[loop.vertex_index].co;uvlay.data[loop.index].uv=uv_for(co.x,-co.y)
 for face in me.polygons:face.use_smooth=False
 objects.append(ob)
 stone_reports.append({'name':ob.name,'source_id':s['template']['id'],'source_polygon_world_xz':source.tolist(),'polygon_world_xz':poly.tolist(),'cap_polygon_world_xz':top_ring.tolist(),'cap_area_m2':area(top_ring),'inset_scale':inset_scale,'center':center.tolist(),'scale':scale.tolist(),'plane_level':level,'plane_slope_xz':tilt.tolist(),'source_uv_formula':'((worldXZ-center)/scale+center)/[9.2,4.6]','closed_nonmanifold_edges':nonmanifold,'screen_center':s['screen'],'roughness_bias_suggestion':round(rng.uniform(-.06,.06),3)})

# Continuous underlying scan bed, lower sampling density away from hero edges.
step=.205;xs=np.unique(np.r_[np.linspace(bounds[0][0],bounds[1][0],math.ceil((bounds[1][0]-bounds[0][0])/step)+1),[r[i] for r in rects for i in (0,1)]])
zs=np.unique(np.r_[np.linspace(bounds[0][2],bounds[1][2],math.ceil((bounds[1][2]-bounds[0][2])/step)+1),[r[i] for r in rects for i in (2,3)]])
xx,zz=np.meshgrid((xs[:-1]+xs[1:])/2,(zs[:-1]+zs[1:])/2);mask=np.zeros(xx.shape,dtype=bool)
for aa,bb,cc,dd in rects:mask|=(xx>=aa)&(xx<=bb)&(zz>=cc)&(zz<=dd)
rr,cc=np.nonzero(mask);grid=np.arange(len(xs)*len(zs)).reshape(len(zs),len(xs));aa=grid[rr,cc];bb=grid[rr,cc+1];dd=grid[rr+1,cc];ee=grid[rr+1,cc+1]
fi=np.stack((np.stack((aa,dd,bb),1),np.stack((bb,dd,ee),1)),1).reshape(-1,3);used,inv=np.unique(fi,return_inverse=True)
x=xs[used%len(xs)];z=zs[used//len(xs)];y=-.0236+.04*(sample(height,x/9.2,z/4.6)-1)
for s in selected:
 poly=s['final_poly'];near=(x>=poly[:,0].min()-.16)&(x<=poly[:,0].max()+.16)&(z>=poly[:,1].min()-.16)&(z<=poly[:,1].max()+.16)
 ids=np.nonzero(near)[0];dist=distance(x[ids],z[ids],poly);isin=inside(x[ids],z[ids],poly);weight=np.where(isin,1,np.clip(1-dist/.13,0,1));weight=weight*weight*(3-2*weight)
 y[ids]=y[ids]*(1-weight)+np.minimum(y[ids],-.0636)*weight
bed=make_object('Continuous recessed source stonebed',np.stack((x,-z,y),1).tolist(),inv.reshape(-1,3).tolist());uvlay=bed.data.uv_layers.new(name='UVMap')
for loop in bed.data.loops:
 co=bed.data.vertices[loop.vertex_index].co;uvlay.data[loop.index].uv=(co.x/9.2,-co.y/4.6)
for face in bed.data.polygons:face.use_smooth=True
objects.insert(0,bed)

# Loop normals preserve the actual bevel-plane distinction, all colors white.
pos=[];norm=[];uv=[];indices=[];colors=[];parts=[]
for ob in objects:
 me=ob.data;me.calc_loop_triangles();me.update();dedup={};start=len(indices)
 for tri in me.loop_triangles:
  face=[]
  for li in tri.loops:
   v=me.vertices[me.loops[li].vertex_index].co;nn=me.corner_normals[li].vector;tex=me.uv_layers.active.data[li].uv;key=tuple(round(q,9) for q in (v.x,v.z,-v.y,nn.x,nn.z,-nn.y,tex.x,tex.y))
   if key not in dedup:dedup[key]=len(pos)//3;pos.extend(key[:3]);norm.extend(key[3:6]);uv.extend(key[6:]);colors.extend((1.,1.,1.,1.))
   face.append(dedup[key])
  indices.extend(face)
 parts.append({'name':ob.name,'index_start':start,'index_count':len(indices)-start})
data={'id':'paving-v13-hybrid-scan-slabs','name':'PavingV13HybridScanSlabs','alreadyUnity':True,'positions':pos,'normals':norm,'uv':uv,'indices':indices,'colors':colors}
assert len(indices)//3<160000,len(indices)//3
pp=np.array(pos).reshape(-1,3);nn=np.array(norm).reshape(-1,3);ii=np.array(indices).reshape(-1,3)
cross=np.cross(pp[ii[:,1]]-pp[ii[:,0]],pp[ii[:,2]]-pp[ii[:,0]])
dots=np.sum(cross*nn[ii].sum(1),axis=1)
assert np.all(dots>0),('face-normal disagreements',int(np.sum(dots<=0)))
assert np.all(np.linalg.norm(cross,axis=1)>2e-12),'degenerate geometry'
assert all(s['closed_nonmanifold_edges']==0 for s in stone_reports),'nonclosed source stone'
(OUT/'paving-v13-mesh.json').write_text(json.dumps(data,separators=(',',':')))
report={'hero_stones':stone_reports,'hero_count':len(stone_reports),'source_contour_count':len(templates),'skipped_contours':skipped,'foreground_body_area_m2':sum(s['area'] for s in selected),'foreground_area_m2':(rects[0][1]-rects[0][0])*(rects[0][3]-rects[0][2]),'parts':parts,'triangles':len(indices)//3,'vertices':len(pos)//3,'coverage_rectangles_xz':rects,'water_y':-.004,'world_bounds':[[min(pos[a::3]) for a in range(3)],[max(pos[a::3]) for a in range(3)]],'source_sha256':hashes,'sources_preserved':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items()},'mesh_sha256':hashlib.sha256((OUT/'paving-v13-mesh.json').read_bytes()).hexdigest(),'height_note':'Source40mm amplitude retained in bed; hero caps use independent art-directed planes, some above water, plus bounded2.8mm scan residual. Not vertical measurements.','uv_note':'Bed worldXZ/[9.2,4.6]; each hero uses its documented inverse source attachment transform. Use exported UV; never shader world UV on hero stones.','limitations':['AO-guided contours are manually identified source regions, not guaranteed semantic auto-segmentation.','Fine source cracks and full-map repeated courses remain in continuous bed.','Root integrates native roughness, illumination and independent pools.']}
(OUT/'hybrid-metadata.json').write_text(json.dumps(report,indent=2))
oldp=np.array(prior['positions']).reshape(-1,3);oldob=make_object('BEFORE V12 preserved',np.stack((oldp[:,0],-oldp[:,2],oldp[:,1]),1).tolist(),np.array(prior['indices']).reshape(-1,3).tolist());uvlay=oldob.data.uv_layers.new(name='UVMap');olduv=np.array(prior['uv']).reshape(-1,2)
for loop in oldob.data.loops:uvlay.data[loop.index].uv=olduv[loop.vertex_index]
for face in oldob.data.polygons:face.use_smooth=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.world.color=(.10,.10,.10)
scene.render.resolution_x=1536;scene.render.resolution_y=1024;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO'
for loc,power,size in [((-8,-1,10),2800,5),((7,-12,8),1300,6)]:
 bpy.ops.object.light_add(type='AREA',location=loc);li=bpy.context.object;li.data.energy=power;li.data.size=size;li.rotation_euler=(Vector((0,-6,0))-li.location).to_track_quat('-Z','Y').to_euler()
if '--geometry-only' in sys.argv:
 oldob.hide_render=True;oldob.hide_viewport=True
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'paving-v13.blend'))
 print('PAVING_V13_GEOMETRY_DONE',report['triangles'],report['vertices'],report['mesh_sha256'])
 bpy.ops.wm.quit_blender()
 raise SystemExit(0)
for view,target,width in [('native-ground',(0,-.7,2.9),33.3070866),('close',(0,-8,0),13.0)]:
 target=Vector(target);camera.location=target+Vector((-math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))*42;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=width
 for kind in ['before-v12-neutral','after-v13-neutral','after-v13-textured']:
  before=kind.startswith('before');oldob.hide_render=not before;oldob.data.materials[0]=neutral
  for ob in objects:ob.hide_render=before;ob.data.materials[0]=textured if kind.endswith('textured') else neutral
  scene.render.filepath=str(PREVIEW/f'{kind}-{view}.png');bpy.ops.render.render(write_still=True)
oldob.hide_render=True;oldob.hide_viewport=True
for ob in objects:ob.hide_render=False;ob.data.materials[0]=textured
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'paving-v13.blend'))
print('PAVING_V13_DONE',report['triangles'],report['vertices'],report['mesh_sha256'])
