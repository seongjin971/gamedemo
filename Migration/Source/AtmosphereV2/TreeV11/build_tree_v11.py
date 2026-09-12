"""Non-destructive Meshy TreeV11 reduction and bounded depth/root art direction.
Original GLB, downloaded images/textures, task metadata/client/PROMPT are immutable.
Blender 5.2.1: --background --threads 6 --python build_tree_v11.py
"""
import bpy,bmesh,json,math,hashlib,time
from pathlib import Path
from mathutils import Vector
import numpy as np
W=Path(__file__).resolve().parent;D=W/'derivative';D.mkdir(exist_ok=True)
SOURCE=W/'tree-v11-original.glb';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected=json.loads((W/'protected-input-hashes.json').read_text())
assert all(sha(W/n)==h for n,h in protected.items())
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(SOURCE))
obj=next(o for o in bpy.data.objects if o.type=='MESH');obj.name='TreeV11 original normalized comparison'
bpy.context.view_layer.objects.active=obj;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
def coords(o):
 p=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',p);return p.reshape((-1,3))
def assign(o,p):
 o.data.vertices.foreach_set('co',np.asarray(p,dtype=np.float32).ravel());o.data.update()
 # glTF split normals must not remain in their pre-deformation basis.
 # Recompute geometry normals while retaining UV/normal-map detail.
 if o.data.has_custom_normals:o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops))
 o.data.update()
original_p=coords(obj);rawbounds=[original_p.min(axis=0).tolist(),original_p.max(axis=0).tolist()]
lo=np.min(original_p,axis=0);hi=np.max(original_p,axis=0);span=hi-lo
root=original_p[original_p[:,2]<lo[2]+span[2]*.08];rootcenter=(root.min(axis=0)+root.max(axis=0))*.5
sx=6.3/float(span[0]);uniform=6.4/float(span[2])
p=original_p.copy();p[:,0]=(p[:,0]-rootcenter[0])*sx;p[:,1]=(p[:,1]-rootcenter[1])*uniform;p[:,2]=(p[:,2]-lo[2])*uniform-.06
assign(obj,p);del original_p,p
obj.data.calc_loop_triangles();rawtri=len(obj.data.loop_triangles)
raw=coords(obj);normal_bounds=[raw.min(axis=0).tolist(),raw.max(axis=0).tolist()];del raw
print('V11 normalized original',rawtri,normal_bounds,flush=True)

# Identical material and rig across original, reduced and art-directed variants.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=1024;scene.render.resolution_y=1024;scene.render.resolution_percentage=100;scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('Tree review neutral world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.105,.105,.105,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
scene.view_settings.view_transform='AgX';scene.render.use_persistent_data=True
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-14,3.14));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=7.35;scene.camera=camera
for location,power,color,size in [((-5,-5,9),1500,(.73,.83,1),5),((5,-3,6),1000,(1,.84,.66),4),((0,5,8),1600,(.74,.84,1),5)]:
 bpy.ops.object.light_add(type='AREA',location=location);light=bpy.context.object;light.data.energy=power;light.data.color=color;light.data.size=size;aim(light,(0,0,3.1))
views={'front':((0,-14,3.14),(0,0,3.14)),'back':((0,14,3.14),(0,0,3.14)),'left':((-14,0,3.14),(0,0,3.14)),'right':((14,0,3.14),(0,0,3.14)),'isometric':((8,-13,8),(0,0,3.05))}
def render_views(prefix):
 for label,(location,target) in views.items():
  camera.location=location;aim(camera,target);scene.render.filepath=str(D/f'{prefix}-{label}.png');bpy.ops.render.render(write_still=True)
render_views('original')

# Keep the original object in memory for exact source-surface comparison until
# decimation is complete. No voxel remesh or new bark is introduced.
candidate=obj.copy();candidate.data=obj.data.copy();candidate.name='TreeV11 reduced';bpy.context.collection.objects.link(candidate)
obj.hide_render=True;bpy.ops.object.select_all(action='DESELECT');candidate.select_set(True);bpy.context.view_layer.objects.active=candidate
print('V11 decimation START',flush=True);start=time.time()
mod=candidate.modifiers.new('150k silhouette and UV preserving collapse','DECIMATE');mod.decimate_type='COLLAPSE';mod.ratio=158000/rawtri;mod.use_collapse_triangulate=True
bpy.ops.object.modifier_apply(modifier=mod.name)
decimation_seconds=time.time()-start
print('V11 decimation END seconds',decimation_seconds,flush=True)
candidate.data.validate(clean_customdata=False);candidate.data.update();candidate.data.calc_loop_triangles()
base=coords(candidate);basebounds=[base.min(axis=0).tolist(),base.max(axis=0).tolist()]
# QEM can remove the very last tip vertex. Restore the contracted export bounds
# (height and width) without changing the authored origin or bending branches.
base[:,0]*=6.3/float(base[:,0].max()-base[:,0].min());base[:,2]=(base[:,2]-base[:,2].min())*(6.4/float(base[:,2].max()-base[:,2].min()))-.06
root=base[base[:,2]<-.06+6.4*.08];recentre=(root.min(axis=0)+root.max(axis=0))*.5;base[:,0]-=recentre[0];base[:,1]-=recentre[1]
assign(candidate,base)
for f in candidate.data.polygons:f.use_smooth=True
candidate.data.update()

def export(o,name):
 m=o.data;m.calc_loop_triangles();position=[];normal=[];uv=[];color=[];indices=[];lookup={};corners=[n.vector.copy() for n in m.corner_normals]
 skips=0;fallbacks=0;minimum=1
 for tri in m.loop_triangles:
  a,b,c=[m.vertices[i].co for i in tri.vertices];face=(b-a).cross(c-a)
  if face.length<2e-12:skips+=1;continue
  fn=face.normalized();mean=sum((corners[li] for li in tri.loops),Vector());flat=fn.dot(mean)<=0
  if flat:fallbacks+=1
  for li in (tri.loops[0],tri.loops[2],tri.loops[1]):
   p=m.vertices[m.loops[li].vertex_index].co;n=fn if flat else corners[li];po=(-p.x,p.z,-p.y);no=(-n.x,n.z,-n.y);tex=tuple(m.uv_layers.active.data[li].uv);key=po+no+tex
   if key not in lookup:lookup[key]=len(position)//3;position.extend(po);normal.extend(no);uv.extend(tex);color.extend((1,1,1,1))
   indices.append(lookup[key])
 assert 120000<=len(indices)//3<=180000
 assert all(math.isfinite(v) for a in [position,normal,uv] for v in a)
 data=dict(positions=position,normals=normal,uv=uv,colors=color,indices=indices)
 (D/(name+'.json')).write_text(json.dumps(data,separators=(',',':')))
 return dict(file=name+'.json',triangles=len(indices)//3,vertices=len(position)//3,zeroAreaDiscarded=skips,faceNormalFallbacks=fallbacks,boundsUnity=[[min(position[k::3]),max(position[k::3])] for k in range(3)],sha256=sha(D/(name+'.json')))

base_export=export(candidate,'tree-v11-base-mesh');render_views('reduced-base')
# Save only the derivative mesh and imported material, not the comparison model
# or rendering rig. Link/visibility is restored immediately for further review.
bpy.data.objects.remove(obj,do_unlink=True)
rig=[o for o in bpy.data.objects if o.type in ('CAMERA','LIGHT')]
def save_asset(filename):
 for o in rig:
  for c in list(o.users_collection):c.objects.unlink(o)
 bpy.ops.wm.save_as_mainfile(filepath=str(D/filename))
 for o in rig:bpy.context.collection.objects.link(o)
save_asset('tree-v11-reduced-base.blend')

# Bounded art direction: depth comparable with V10, and a modest root spread
# faded smoothly over the lowest 1.2m. Original surface topology and UVs remain.
art=base.copy();rootweight=np.clip(1-(art[:,2]+.06)/1.2,0,1);rootweight=rootweight*rootweight*(3-2*rootweight)
art[:,1]*=1.65*(1+.12*rootweight);art[:,0]*=1+.32*rootweight
root=art[art[:,2]<-.06+6.4*.08];artcentre=(root.min(axis=0)+root.max(axis=0))*.5;art[:,0]-=artcentre[0];art[:,1]-=artcentre[1]
assign(candidate,art);candidate.name='TreeV11 depth and root art direction'
art_export=export(candidate,'tree-v11-art-directed-mesh');render_views('art-directed')
save_asset('tree-v11-art-directed.blend')
report=dict(sourceGLBSha256=protected[SOURCE.name],originalVertices=1638506,originalTriangles=rawtri,originalBlenderBounds=rawbounds,sourceRootCentreBlender=rootcenter.tolist(),normalization=dict(height=6.4,width=6.3,bottom=-.06,rootCentreXZUnity=[0,0],heightScale=uniform,widthScale=sx),normalizedSourceBounds=normal_bounds,decimationSeconds=decimation_seconds,preRestoreReducedBounds=basebounds,base=base_export,artDirected=art_export,artDirection=dict(depthFactor=1.65,maximumRootWidthFactor=1.32,maximumRootExtraDepthFactor=1.12,rootBlendHeight=1.2),UV='Imported glTF UVMap carried through collapse; original embedded base color, normal and packed PBR maps reused',colors='Source has no vertex colors; white RGBA preserves texture color',coordinates='Blender to Unity (-x,z,-y), reverse triangle [0,2,1] once, identity model transform',originalInputsUnchanged=all(sha(W/n)==h for n,h in protected.items()),status='AWAITING_DIRECT_FOUR_VIEW_REVIEW')
(D/'build-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
