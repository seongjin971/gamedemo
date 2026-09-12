"""Four unequal rubble groups, three soil pockets and one parapet moss contact.
Only ContactV14 outputs are authored. Native world meshes import at identity.
"""
import bpy,bmesh,json,math,random,hashlib,sys
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent;ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
manifest=json.loads((OUT/'rubble-removal-manifest.json').read_text());evidence=json.loads((OUT/'world-contact-evidence.json').read_text());clusters=json.loads((OUT/'cluster-plan.json').read_text())
bridge_path=ROOT/'Unity/Vesper/Assets/Vesper/Import/unity-scene.json';bridge=json.loads(bridge_path.read_text());nodes={n['id']:n for n in bridge['nodes']}
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Contact review world');scene.render.engine='CYCLES';scene.cycles.samples=20;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=1536;scene.render.resolution_y=1024;scene.render.resolution_percentage=100;scene.world.color=(.07,.07,.07)
context=bpy.data.collections.new('Unmodified contextual root paving and parapet');scene.collection.children.link(context)
old=bpy.data.collections.new('Before 99 original offcuts');scene.collection.children.link(old)
new=bpy.data.collections.new('After retained offcuts and authored contact');scene.collection.children.link(new)
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.88;return m
stone=material('Neutral source geometry review stone',(.37,.39,.40));floor_mat=material('Paving context',(.18,.195,.20));wood=material('Tree root context',(.12,.105,.085));soilmat=material('Dark mineral soil context',(.055,.045,.033));mossmat=material('Parapet moss context',(.055,.060,.038))
def mesh_obj(name,verts,faces,col,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(mat);ob=bpy.data.objects.new(name,me);col.objects.link(ob);return ob
def native(name,d,col,mat,face_filter=None):
 p=d['positions'];idx=d['indices'];vertices=[(p[k],-p[k+2],p[k+1]) for k in range(0,len(p),3)];faces=[idx[k:k+3] for k in range(0,len(idx),3)]
 if face_filter:faces=[f for f in faces if face_filter([vertices[i] for i in f])]
 ob=mesh_obj(name,vertices,faces,col,mat)
 for f in ob.data.polygons:f.use_smooth=True
 if 'normals' in d:
  n=d['normals'];ob.data.normals_split_custom_set_from_vertices([(n[k],-n[k+2],n[k+1]) for k in range(0,len(n),3)])
 return ob
def instance(ob,i):
 p,s,q=i['position'],i['scale'],i['quaternion'];ob.location=(-p[0],-p[2],p[1]);ob.scale=(s[0],s[2],s[1]);ob.rotation_mode='QUATERNION';ob.rotation_quaternion=Quaternion((q[3],q[0],q[2],-q[1]))
def source_for(node,ix):
 i=node['instances'][ix];selected=[j for j,k in enumerate(node['instances']) if -10<=k['position'][0]<=10 and -13<=k['position'][2]<=22 and -3<=k['position'][1]<=15];j=selected.index(ix);seed=j+(j//100)*7
 if min(i['scale'])>.12 and max(i['scale'])<2.8:return json.loads((OUT.parent/'MasonryV12'/('masonry-v12-'+str(seed%6)+'.json')).read_text())
 return json.loads((OUT.parent/'StoneV7/runtime'/(node['geometry']+'.json')).read_text())
def apply_world(ob):
 matrix=ob.matrix_world.copy()
 for v in ob.data.vertices:v.co=matrix@v.co
 ob.matrix_world.identity();ob.data.update()
def clean(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),(ob.name,'not closed');assert bm.calc_volume()>1e-10,(ob.name,'volume');bm.to_mesh(ob.data);bm.free();ob.data.update()
 for f in ob.data.polygons:f.use_smooth=False
paving_data=json.loads((ROOT/evidence['paving_source']).read_text());pp=paving_data['positions'];pi=paving_data['indices'];pave_native=[Vector(pp[k:k+3]) for k in range(0,len(pp),3)];pave_faces=[pi[k:k+3] for k in range(0,len(pi),3)];pave_bvh=BVHTree.FromPolygons(pave_native,pave_faces,all_triangles=True)
def ground(x,z):
 hit=pave_bvh.ray_cast(Vector((x,2,z)),Vector((0,-1,0)),4)
 assert hit[0] is not None,('No paving support',x,z)
 return hit[0].y
native('Complete unmodified paving context',paving_data,context,floor_mat)
tree_data=json.loads((OUT.parent/'TreeV12/derivative/tree-v12-mesh.json').read_text());tree=native('Actual intact Tree V12 context',tree_data,context,wood);tree.location=(7.2,-3.7,0);tree.scale=(1.73,1.73,1.73);tree.rotation_euler.z=math.radians(evidence['combined_yaw_degrees'])
kept={(i['nodeId'],i['instanceIndex']) for i in manifest['retained_instances']}
for row in manifest['instances']+manifest['retained_instances']:
 node=nodes[row['nodeId']];ob=native('Original offcut '+row['nodeId'][:8]+' '+str(row['instanceIndex']),source_for(node,row['instanceIndex']),old,stone);instance(ob,row)
 if (row['nodeId'],row['instanceIndex']) in kept:
  copy=ob.copy();copy.data=ob.data;new.objects.link(copy)
# Only retained structural parapet stones; no wall is added to the removal set.
for node in bridge['nodes']:
 if node.get('materials')!=['08b6ee59-7da1-4fb0-bd5d-a752d5b8fa60']:continue
 for ix,i in enumerate(node.get('instances',[])):
  x,y,z=-i['position'][0],i['position'][1],i['position'][2]
  if 8.8<x<9.0 and -.1<y<1.15 and -7.8<z<7.0 and .6<min(i['scale'][0],i['scale'][2]) and max(i['scale'])<1.6:
   ob=native('Retained parapet '+node['id'][:8]+' '+str(ix),source_for(node,ix),context,stone);instance(ob,i)
support=evidence['root4_wall_contact']['support'];wall=native('Contact support query',json.loads((OUT.parent/'MasonryV12'/('masonry-v12-'+str(support['sourceVariant'])+'.json')).read_text()),context,stone);instance(wall,support);bpy.context.view_layer.update();matrix=wall.matrix_world
wv=[matrix@v.co for v in wall.data.vertices];wall.data.calc_loop_triangles();wf=[tuple(t.vertices) for t in wall.data.loop_triangles];wall_bvh=BVHTree.FromPolygons(wv,wf,all_triangles=True);wall.hide_render=True
def wall_x(y,z):
 # Blender-space X ray from the courtyard towards the parapet.
 hit=wall_bvh.ray_cast(Vector((7,-z,y)),Vector((1,0,0)),3)
 assert hit[0] is not None,('No wall support',y,z)
 return hit[0].x
made=[];piece_rows=[];rng=random.Random(14047)
offsets=[(0,0),(.42,.23),(-.39,.27),(.19,-.42),(-.39,-.34),(.60,-.17),(-.57,.49),(.13,.62)]
for cluster in clusters:
 for k,length in enumerate(cluster['lengths']):
  dx,dz=offsets[k];dx*=.83+rng.random()*.2;dz*=.83+rng.random()*.2
  cx=cluster['center_xz'][0]+dx;cz=cluster['center_xz'][1]+dz;angle=rng.uniform(-math.pi,math.pi);width=length*rng.uniform(.42,.68);height=length*rng.uniform(.12,.22)
  count=5+k%3;poly=[]
  for j in range(count):
   a=2*math.pi*j/count+rng.uniform(-.10,.10);r=rng.uniform(.86,1.08);x=math.cos(a)*length*.5*r;z=math.sin(a)*width*.5*r;poly.append((x*math.cos(angle)+z*math.sin(angle),-x*math.sin(angle)+z*math.cos(angle)))
  excess=max(cx+x for x,z in poly)-8.47
  if excess>0:cx-=excess
  supports=[ground(cx+x,cz+z) for x,z in poly];base=max(supports)-.007
  verts=[(cx+x,-cz-z,base) for x,z in poly]
  for j,(x,z) in enumerate(poly):
   h=height*(.45+.50*(x/length+.5))*(.88+.24*rng.random());verts.append((cx+x*.97,-cz-z*.97,base+max(.024,h)))
  bm=bmesh.new()
  for v in verts:bm.verts.new(v)
  bmesh.ops.convex_hull(bm,input=list(bm.verts));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));me=bpy.data.meshes.new('Angular unequal wedge');bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('Cluster '+str(cluster['id'])+' fragment '+str(k),me);new.objects.link(ob);me.materials.append(stone);ob['tone']=rng.uniform(.85,1.08);ob['color']=(ob['tone'],ob['tone'],ob['tone']);clean(ob);made.append(ob)
  piece_rows.append({'name':ob.name,'cluster':cluster['id'],'nominal_length':length,'nominal_width':width,'maximum_height':height,'center_xz':[cx,cz],'support_heights':supports,'base_y':base})
soil_objects=[];pocket_rows=[]
for row in evidence['contacts']:
 rid=row['root'];vertical=rid==4
 if vertical:contact=evidence['root4_wall_contact']['worldVertex'];center=(contact[1]+.012,contact[2]);radii=(.094,.162)
 else:
  contact=row['alternative_inner_contact']['world_vertex'] if rid==1 else row['original_world_vertex'];center=(contact[0]-(.08 if rid==1 else .035),contact[2]+.015);radii=[(.23,.32),(.31,.38),(.29,.26)][rid-1]
 count=18;outline=[]
 for j in range(count):
  a=2*math.pi*j/count;r=1+.12*math.sin(j*2.31+rid)+.065*math.sin(j*4.17+rid*.9);outline.append((math.cos(a)*radii[0]*r,math.sin(a)*radii[1]*r))
 top=[]
 for ring in [0,.34,.67,1.0]:
  indices=range(1) if ring==0 else range(count)
  for j in indices:
   du,dv=outline[j] if ring else (0,0);u,v=center[0]+du*ring,center[1]+dv*ring
   if vertical:co=(wall_x(u,v)-.005*(1+.45*(1-ring)),-v,u)
   else:
    support_y=ground(u,v);bulge=max(0,1-ring*ring);target=contact[1]+.006;h=max(support_y+.003,support_y+.003+max(0,target-support_y)*bulge);co=(u,-v,h)
   top.append(co)
 faces=[]
 for j in range(count):faces.append((0,1+j,1+(j+1)%count))
 for ring in range(2):
  start=1+ring*count;next_start=start+count
  for j in range(count):k=(j+1)%count;faces.extend([(start+j,next_start+j,next_start+k),(start+j,next_start+k,start+k)])
 perimeter=list(range(1+2*count,1+3*count));verts=list(top);bottom_start=len(verts)
 for j in perimeter:
  x,y,z=top[j];verts.append((x+.013,y,z) if vertical else (x,y,min(v[2] for v in top)-.022))
 bottom_center=len(verts);verts.append(tuple(sum(verts[bottom_start+j][a] for j in range(count))/count for a in range(3)))
 for j in range(count):k=(j+1)%count;faces.extend([(perimeter[j],bottom_start+j,bottom_start+k),(perimeter[j],bottom_start+k,perimeter[k]),(bottom_center,bottom_start+k,bottom_start+j)])
 ob=mesh_obj(('Parapet moss' if vertical else 'Root soil')+' contact '+str(rid),verts,faces,new,mossmat if vertical else soilmat);ob['color']=(.24,.26,.18) if vertical else (.27,.245,.185);clean(ob);soil_objects.append(ob);pocket_rows.append({'root':rid,'type':'vertical parapet moss' if vertical else 'horizontal mineral soil','actual_tree_vertex_world':contact,'footprint_radii':radii,'name':ob.name})
def export(objects,filename):
 positions=[];normals=[];uv=[];colors=[];indices=[];reports=[]
 for ob in objects:
  me=ob.data;me.calc_loop_triangles();start=len(indices);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);closed=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();bm.free();assert closed==0 and vol>1e-10
  points=[v.co for v in me.vertices];reports.append({'name':ob.name,'triangles':len(me.loop_triangles),'nonmanifold_edges_welded':closed,'signed_volume_m3':vol,'bounds_native':[[min((p.x,p.z,-p.y)[a] for p in points) for a in range(3)],[max((p.x,p.z,-p.y)[a] for p in points) for a in range(3)]]})
  for tri in me.loop_triangles:
   n=tri.normal;axis=max(range(3),key=lambda a:abs(n[a]))
   for vi in tri.vertices:
    p=me.vertices[vi].co;positions.extend((p.x,p.z,-p.y));normals.extend((n.x,n.z,-n.y));uv.extend([(p.y,p.z),(p.x,p.z),(p.x,p.y)][axis]);colors.extend((*ob['color'],1));indices.append(len(indices))
 d={'id':filename,'name':filename,'positions':positions,'normals':normals,'uv':uv,'colors':colors,'indices':indices};path=OUT/(filename+'.json');path.write_text(json.dumps(d,separators=(',',':')))
 return {'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangles':len(indices)//3,'objects':reports,'bounds':[[min(positions[a::3]) for a in range(3)],[max(positions[a::3]) for a in range(3)]]}
exports=[export(made,'contact-v14-rubble'),export(soil_objects,'contact-v14-deposits')]
(OUT/'build-validation.json').write_text(json.dumps({'exports':exports,'clusters':clusters,'fragments':piece_rows,'pockets':pocket_rows,'identity_transform':True,'coordinate_basis':'Native Unity world; Blender x,z,-y; same triangle order; closed bodies','retained_old_offcuts':len(kept),'removed_old_offcuts':manifest['removed_count'],'new_offcuts':len(made)},indent=2))
camera_data=bpy.data.cameras.new('Contact review camera');camera=bpy.data.objects.new('Contact review camera',camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO';camera_data.lens=45
def aim(native_focus,angle,elevation,extent):
 focus=Vector((native_focus[0],-native_focus[2],native_focus[1]));delta=Vector((-math.sin(angle)*math.cos(elevation),-math.cos(angle)*math.cos(elevation),math.sin(elevation)))*22;camera.location=focus+delta;camera.rotation_euler=(focus-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=extent
focus=Vector((6.7,0,0))
for name,position,power,size in [('Large cool studio',(-3,-2,13),1800,7),('Soft reverse fill',(10,9,8),900,6)]:
 light_data=bpy.data.lights.new(name,'AREA');light_data.energy=power;light_data.shape='DISK';light_data.size=size;light=bpy.data.objects.new(name,light_data);scene.collection.objects.link(light);light.location=position;light.rotation_euler=(focus-light.location).to_track_quat('-Z','Y').to_euler()
def render(name):
 if '--geometry-only' in sys.argv:return
 if '--contact-previews-only' in sys.argv and name.startswith('clusters-'):return
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
aim((6.6,.3,-.2),.46,.91,15.2);old.hide_render=False;new.hide_render=True;render('overview-before');old.hide_render=True;new.hide_render=False;render('overview-after')
aim((6.8,.1,-3),.25,1.02,10);old.hide_render=False;new.hide_render=True;render('clusters-before');old.hide_render=True;new.hide_render=False;render('clusters-after')
aim((7.05,.30,3.85),.65,.95,7.4);render('contacts-after')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'contact-v14.blend'));print('CONTACT_V14_COMPLETE',len(made),len(soil_objects),sum(e['triangles'] for e in exports))
