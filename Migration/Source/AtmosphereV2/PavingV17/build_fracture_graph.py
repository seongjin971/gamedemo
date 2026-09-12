"""PavingV17 adds 18 source-registered stones to preserved V16 ten. Blender 5.2, coordinated slot.
Load V16 blend. Reuse all other V16 export arrays without re-export/rounding.
"""
import bpy,bmesh,json,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent;V16=OUT.parent/'PavingV16';V14=OUT.parent/'PavingV14';PREVIEW=OUT/'previews';PREVIEW.mkdir(exist_ok=True)
SOURCE=V16/'paving-v16-mesh.json';source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert source_hash=='f812feed57a6b6e2fa3c7378caada08243c650883b5e1f33d630640dd828b7b6'
original=json.loads(SOURCE.read_text());previous=json.loads((V16/'fracture-metadata.json').read_text());meta=json.loads((V14/'hybrid-metadata.json').read_text());traces=json.loads((OUT/'trace_graph.json').read_text())
seeds={s['id']:s for s in json.loads((V14/'source_seeds.json').read_text())['slabs']};selected={t['number']:t for t in traces['stones']}
stones={int(s['name'].split('_')[1]):s for s in meta['hero_stones']};selected_names={stones[i]['name'] for i in selected}
textured=bpy.data.materials['Actual source4K Color roughness NormalGL .4'];records=[];new_objects=[];before_objects=[]
bed_tree=BVHTree.FromObject(bpy.data.objects['Continuous recessed source stonebed'],bpy.context.evaluated_depsgraph_get())
def bed_height(p):
 hit=bed_tree.ray_cast(Vector((p[0],-p[1],1)),Vector((0,0,-1)))[0]
 return float(hit.z) if hit is not None else -.0636
tile_shift=np.array([0.,0.])
def world(p):return np.array([p[0]/2048*12.4-12.4,(1-p[1]/1024)*6.2+6.2])+tile_shift
def area(poly):return sum(np.cross(a,b) for a,b in zip(poly,np.roll(poly,-1,axis=0)))*.5
def inside(p,poly):
 ans=False
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  if ((a[1]>p[1])!=(b[1]>p[1])) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:ans=not ans
 return ans
def orient(a,b,c):return float((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
def overlap(p,q):
 if any(max(p[:,k])<=min(q[:,k]) or max(q[:,k])<=min(p[:,k]) for k in [0,1]):return False
 return any(orient(a,b,c)*orient(a,b,d)<-1e-12 and orient(c,d,a)*orient(c,d,b)<-1e-12 for a,b in zip(p,np.roll(p,-1,axis=0)) for c,d in zip(q,np.roll(q,-1,axis=0))) or any(inside(x,q) for x in p) or any(inside(x,p) for x in q)
def finish(name,bm):
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=2e-6)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=2e-6)
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=2e-6)
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),(name,'nonmanifold')
 assert bm.calc_volume(signed=True)>0,(name,'negative volume')
 me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(textured)
 uv=me.uv_layers.new(name='UVMap')
 for loop in me.loops:
  p=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(p.x/12.4,-p.y/6.2)
 for f in me.polygons:f.use_smooth=False
 return ob

for number,t in selected.items():
 s=stones[number];old=bpy.data.objects[s['name']];old.hide_render=True;before_objects.append(old)
 tile_shift=np.array([0.,0.]);raw=np.array([world(p) for p in seeds[s['source_id']]['polygon']]);tile_shift=np.round((np.array(s['center'])-raw.mean(0))/np.array([12.4,6.2]))*np.array([12.4,6.2]);poly=np.array([world(p) for p in seeds[s['source_id']]['polygon']]);orientation=area(poly)
 if orientation<0:poly=poly[::-1]
 center=poly.mean(0);level=s['plane_level'];slope=np.array(t['base_tilt']);cuts=[]
 for endpoints,gain in zip(t['cuts'],t['slopes']):
  a,b=[world(p) for p in endpoints];direction=b-a;normal=np.array([-direction[1],direction[0]])/np.linalg.norm(direction);cuts.append((a,normal,gain))
 def field(p):return float(np.dot(p-center,slope)+sum(g*max(0,np.dot(p-a,n)) for a,n,g in cuts))
 # Keep cap mean near existing level and preserve global maximum height.
 samples=[field(p) for p in poly]+[field(center)];offset=level-np.mean(samples);offset=min(offset,.0095-max(samples))
 def cap(p):return offset+field(p)
 bm=bmesh.new();bottom=[bm.verts.new((p[0],-p[1],-.115)) for p in poly];top=[bm.verts.new((p[0],-p[1],0)) for p in poly]
 bm.faces.new(top[::-1]);bm.faces.new(bottom)
 for j in range(len(poly)):k=(j+1)%len(poly);bm.faces.new((bottom[j],bottom[k],top[k],top[j]))
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 # Only selected boundary segments get a single fractured chamfer. All other
 # edges retain the source's angular corner; no whole-loop inset or averaging.
 eds=[]
 for j in t['bevel_edges']:
  j%=len(poly);edge=next((e for e in bm.edges if top[j] in e.verts and top[(j+1)%len(poly)] in e.verts),None)
  if edge:eds.append(edge)
 if eds:bmesh.ops.bevel(bm,geom=eds,offset=.016 if s['subordinate'] else .029,segments=1,affect='EDGES',clamp_overlap=True,profile=.5)
 # Real constrained topology along authored fracture graph. Bisect every
 # intersected face, retaining both sides; all bodies stay connected and closed.
 for a,n,g in cuts:
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=Vector((a[0],-a[1],0)),plane_no=Vector((n[0],-n[1],0)),dist=1e-8,clear_inner=False,clear_outer=False)
 # Check extrema at actual fracture intersections too, not just raw corners.
 offset=min(offset,.0095-max(field(np.array([v.co.x,-v.co.y])) for v in bm.verts))
 for v in bm.verts:
  p=np.array([v.co.x,-v.co.y]);z=v.co.z;weight=max(0,min(1,(z+.115)/.115));v.co.z=z+cap(p)*weight
 ob=finish('V17_'+s['name'],bm);new_objects.append(ob)
 fill_count=0
 records.append({'name':s['name'],'number':number,'source_id':s['source_id'],'raw_polygon_world_xz':poly.tolist(),'cuts_source_pixels':t['cuts'],'hinge_slopes':t['slopes'],'cap_offset':offset,'cap_base_tilt':slope.tolist(),'selective_bevel_source_edges':t['bevel_edges'],'fill_count':fill_count,'trace_note':t['trace_note'],'tile_shift':tile_shift.tolist()})

# Preserve every original vertex record verbatim; old selected vertices become
# unreferenced. Remove only selected part triangle lists; append new records.
data={k:(v.copy() if isinstance(v,list) else v) for k,v in original.items()};data['id']='paving-v17-expanded-fracture-graph';data['name']='PavingV17ExpandedFractureGraph';data['indices']=[];parts=[]
for p in previous['parts']:
 if p['name'] in selected_names:continue
 start=len(data['indices']);data['indices'].extend(original['indices'][p['index_start']:p['index_start']+p['index_count']]);parts.append({'name':p['name'],'index_start':start,'index_count':p['index_count'],'original_index_start':p['index_start']})
new_start=len(data['indices'])
for ob in new_objects:
 me=ob.data;me.calc_loop_triangles();start=len(data['indices']);lookup={}
 for tri in me.loop_triangles:
  out=[]
  for li in tri.loops:
   v=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector;uv=me.uv_layers.active.data[li].uv
   key=tuple(round(float(q),9) for q in (v.x,v.z,-v.y,n.x,n.z,-n.y,uv.x,uv.y))
   if key not in lookup:
    lookup[key]=len(data['positions'])//3;data['positions'].extend(key[:3]);data['normals'].extend(key[3:6]);data['uv'].extend(key[6:]);data['colors'].extend([1,1,1,1])
   out.append(lookup[key])
  data['indices'].extend(out)
 parts.append({'name':ob.name,'index_start':start,'index_count':len(data['indices'])-start})
pp=np.array(data['positions']).reshape(-1,3);ii=np.array(data['indices']).reshape(-1,3);nn=np.array(data['normals']).reshape(-1,3);cross=np.cross(pp[ii[:,1]]-pp[ii[:,0]],pp[ii[:,2]]-pp[ii[:,0]])
dots=np.einsum('ij,ikj->ik',cross,nn[ii])
if not np.all(dots>0):
 bad=np.where(np.any(dots<=0,axis=1))[0];(OUT/'rejected-preflight.json').write_text(json.dumps([{'index':int(i),'positions':pp[ii[i]].tolist(),'cross':cross[i].tolist(),'normals':nn[ii[i]].tolist()} for i in bad],indent=2))
assert np.all(dots>0),('native winding',np.where(np.any(dots<=0,axis=1)))
assert np.all(np.linalg.norm(cross,axis=1)>1e-12),'degenerate';assert len(ii)<120000
assert np.all(np.isfinite(pp)) and np.all(np.isfinite(nn));assert np.max(abs(np.linalg.norm(nn,axis=1)-1))<1e-5
target=OUT/'paving-v17-mesh.json';target.write_text(json.dumps(data,separators=(',',':')))
report={'mesh_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_sha256':source_hash,'selected_records':records,'parts':parts,'triangles':len(ii),'vertices':len(pp),'new_index_start':new_start,'new_object_count':len(new_objects),'period':[12.4,6.2],'patch_bounds_xz':[[min(p[k] for r in records for p in r['raw_polygon_world_xz']),max(p[k] for r in records for p in r['raw_polygon_world_xz'])] for k in [0,1]],'world_bounds':[pp.min(0).tolist(),pp.max(0).tolist()],'prototype_only':False,'total_fracture_stones':28,'preserved_v16_stones':[s['number'] for s in previous['selected_records']], 'protected_tree_contact_xz':[[4.5,9.05],[1.2,6.4]],'protected_drainage_body':280,'old_vertex_prefix_preserved':all(data[k][:len(original[k])]==original[k] for k in ['positions','normals','uv','colors']),'strict_positive_triangles':len(ii),'limitations':['28-unit selected foreground expansion; remaining floor caps retain the previous method.','Internal planar continuation and height angles are authored, not measured scan fracture depth.','Original selected vertex records remain unreferenced to preserve all other indices exactly.']}
(OUT/'fracture-metadata.json').write_text(json.dumps(report,indent=2));assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.cycles.samples=16
for o in new_objects:o.hide_render=False
for o in before_objects:o.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'paving-v17.blend'))
print('PAVING_V17_BUILD_DONE',report['triangles'],report['mesh_sha256'])
