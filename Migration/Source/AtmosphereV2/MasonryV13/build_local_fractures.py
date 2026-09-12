"""Eight selected architecture overrides and localized staircase refinement."""
import bpy,bmesh,json,math,hashlib,random,sys
from mathutils import Vector,Quaternion
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
V11=ROOT/'Migration/Source/AtmosphereV2/MasonryV11';V12=ROOT/'Migration/Source/AtmosphereV2/MasonryV12'
BRIDGE=ROOT/'Unity/Vesper/Assets/Vesper/Import/unity-scene.json';bridge=json.loads(BRIDGE.read_text())
bpy.ops.wm.open_mainfile(filepath=str(V11/'stairs-v11.blend'))
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.cycles.samples=32
oldstairs=bpy.data.collections.new('V11 intact stair comparison');scene.collection.children.link(oldstairs)
stairs=bpy.data.collections['After one-piece stones'];bpy.data.collections['Before source assembly'].hide_render=True
stair_objects=sorted([o for o in stairs.objects if o.type=='MESH'],key=lambda o:o.name)
for ob in stair_objects:
    copy=ob.copy();copy.data=ob.data.copy();oldstairs.objects.link(copy)
clay=stair_objects[0].data.materials[0]
def cut(ob,points,name,solver='EXACT'):
    bm=bmesh.new()
    for p in points:bm.verts.new(p)
    bmesh.ops.convex_hull(bm,input=list(bm.verts));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();tool=bpy.data.objects.new('Temporary chisel',me);scene.collection.objects.link(tool)
    bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver=solver;mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
def clean(ob):
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();ob.data.materials.clear();ob.data.materials.append(clay)
    for f in ob.data.polygons:f.use_smooth=True;f.material_index=0
    bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Keep fracture boundaries','EDGE_SPLIT');mod.split_angle=.28;bpy.ops.object.modifier_apply(modifier=mod.name)
def components(bm):
    remaining=set(bm.verts);count=0
    while remaining:
        count+=1;todo=[remaining.pop()]
        while todo:
            v=todo.pop()
            for edge in v.link_edges:
                other=edge.other_vert(v)
                if other in remaining:remaining.remove(other);todo.append(other)
    return count
def native(name,data,col):
    p=data['positions'];n=data['normals'];idx=data['indices'];me=bpy.data.meshes.new(name);me.from_pydata([(p[i],-p[i+2],p[i+1]) for i in range(0,len(p),3)],[],[idx[i:i+3] for i in range(0,len(idx),3)]);me.update()
    for f in me.polygons:f.use_smooth=True
    me.normals_split_custom_set_from_vertices([(n[i],-n[i+2],n[i+1]) for i in range(0,len(n),3)]);me.materials.append(clay);ob=bpy.data.objects.new(name,me);col.objects.link(ob);return ob
def render(name):
    if '--geometry-only' in sys.argv:return
    if '--portal-only' in sys.argv and name.startswith('stairs-'):return
    scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
def export(objects,name,colors=False):
    p=[];n=[];uv=[];c=[];idx=[];keys={};closure=0
    for ob in objects:
        me=ob.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);closure+=sum(not e.is_manifold for e in bm.edges);bm.free()
        for tri in me.loop_triangles:
            for li in tri.loops:
                co=me.vertices[me.loops[li].vertex_index].co;normal=me.corner_normals[li].vector
                if normal.dot(tri.normal)<.05:normal=tri.normal
                axis=max(range(3),key=lambda a:abs(normal[a]));t=[(co.y,co.z),(co.x,co.z),(co.x,co.y)][axis];tone=ob.get('tone',1)
                key=(co.x,co.z,-co.y,normal.x,normal.z,-normal.y,*t,tone)
                if key not in keys:keys[key]=len(p)//3;p.extend(key[:3]);n.extend(key[3:6]);uv.extend(key[6:8]);c.extend((tone,tone,tone,1))
                idx.append(keys[key])
    d={'id':name,'name':name,'positions':p,'normals':n,'uv':uv,'indices':idx}
    if colors:d['colors']=c
    path=OUT/(name+'.json');path.write_text(json.dumps(d,separators=(',',':')))
    return {'id':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangles':len(idx)//3,'vertices':len(p)//3,'nonmanifold_edges_welded':closure,'bounds':[[min(p[a::3]) for a in range(3)],[max(p[a::3]) for a in range(3)]]}

stairs.hide_render=True;oldstairs.hide_render=False;render('stairs-before-clay.png')
stair_rows=json.loads((V11/'export-validation.json').read_text())['rows'];rng=random.Random(1341);cuts=[];volumes=[]
for ob in stair_objects:
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));original_volume=abs(bm.calc_volume());original_components=components(bm);bm.to_mesh(ob.data);bm.free();ob.data.update()
    row,col=map(int,ob.name.rsplit(' ',1)[-1].split('-'));coords=stair_rows[row]['boundaries_x'];oldlo=coords[col]+(.008 if col else 0);oldhi=coords[col+1]-(.008 if col<8 else 0)
    newlo=oldlo+(.006 if col else 0);newhi=oldhi-(.006 if col<8 else 0)
    for v in ob.data.vertices:v.co.x=newlo+(v.co.x-oldlo)/(oldhi-oldlo)*(newhi-newlo)
    if (col+row*2)%3==1:
        top=(row+1)*.29+.042;front=-1.75-row*.49+.291;cx=(newlo+newhi)/2+rng.uniform(-.045,.045);half=min((newhi-newlo)*.39,rng.uniform(.22,.29));dep=rng.uniform(.032,.047);down=rng.uniform(.025,.045)
        cut(ob,[(cx-half,-front-.006,top+.006),(cx+half,-front-.006,top+.006),(cx+half*.6,-front+dep,top+.006),(cx-half*.85,-front+dep*.72,top+.006),
                (cx-half*.67,-front-.006,top-down),(cx+half*.79,-front-.006,top-down*.63),(cx+.022,-front+dep*.64,top-.008)],'Wide unequal nose loss','MANIFOLD')
        cuts.append({'row':row,'column':col,'width':2*half,'depth':dep,'vertical_loss':down})
    clean(ob)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);volume=abs(bm.calc_volume());final_components=components(bm);bm.free();assert original_volume>0 and volume/original_volume>.90 and final_components==original_components,(ob.name,original_volume,volume,original_components,final_components)
    volumes.append({'name':ob.name,'original_volume':original_volume,'final_volume':volume,'ratio':volume/original_volume,'vertices':len(ob.data.vertices),'original_components':original_components,'final_components':final_components})
oldstairs.hide_render=True;stairs.hide_render=False;render('stairs-after-clay.png')
reports=[export(stair_objects,'stairs-v13-mesh',True)];stairs.hide_render=True

before=bpy.data.collections.new('Portal before');scene.collection.children.link(before)
after=bpy.data.collections.new('Portal after');scene.collection.children.link(after)
masters=bpy.data.collections.new('Normalized eight overrides');scene.collection.children.link(masters);masters.hide_render=True
chosen={('592370d4',412),('592370d4',415),('592370d4',452),('592370d4',455),('592370d4',459),('b8fdddbd',414),('b8fdddbd',453),('b8fdddbd',458)}
overrides=[];fracture_rng=random.Random(134113)
for node in bridge['nodes']:
    if node.get('distant') or node.get('materials')!=['08b6ee59-7da1-4fb0-bd5d-a752d5b8fa60']:continue
    selected=[(ix,i) for ix,i in enumerate(node.get('instances',[])) if -10<=i['position'][0]<=10 and -13<=i['position'][2]<=22 and -3<=i['position'][1]<=15]
    for j,(ix,inst) in enumerate(selected):
        p,s,q=inst['position'],inst['scale'],inst['quaternion'];seed=j+(j//100)*7
        if not (3<p[1]<14 and -9<p[2]<-6.4 and -4<p[0]<9 and min(s)>.12 and max(s)<2.8):continue
        d=json.loads((V12/f'masonry-v12-{seed%6}.json').read_text());old=native(f'Before {node["id"][:8]} {ix}',d,before);source=old.data
        if (node['id'][:8],ix) in chosen:
            k=len(overrides);ob=native(f'localized-masonry-v13-{k}',d,masters)
            # Broad unequal open corner loss; depth remains below 1/4 local block.
            side=-1 if k%2 else 1;normal=Vector((side*(.78+.12*(k%3)),-(.75+.08*((k+1)%3)),.62+.12*(k%2)));loss=(.19+.018*(k%4))*min(abs(x) for x in normal);distance=sum(abs(x) for x in normal)*.5-loss
            bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=normal*(distance/normal.length_squared),plane_no=normal,dist=1e-7,clear_outer=True,clear_inner=False);edges=[e for e in bm.edges if e.is_boundary];bmesh.ops.holes_fill(bm,edges=edges,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
            z=.19 if k%3 else -.04;cx=-side*.18
            cut(ob,[(cx-.16,-.506,z-.075),(cx+.13,-.506,z-.10),(cx+.18,-.506,z+.036),(cx+.025,-.506,z+.10),(cx-.18,-.506,z+.061),(cx-.022,-.464,z+.008),(cx+.057,-.472,z-.026)],'Broad shallow open face flake')
            # Open irregular corner fracture: the rejected mid-arris cut made
            # repeated C-shaped notches. This terminates at an existing top or
            # bottom corner, with unequal intercepts and a multifaceted face.
            side=-side;vertical=1 if k in (2,5) else -1
            dx=fracture_rng.uniform(.18,.245);dy=fracture_rng.uniform(.155,.237);dz=fracture_rng.uniform(.175,.244)
            def corner(u,v,w):return (side*(.506-u),-.506+v,vertical*(.506-w))
            cut(ob,[corner(0,0,0),corner(dx,0,0),corner(0,dy,0),corner(0,0,dz),
                    corner(dx*.58,dy*.15,dz*.39),corner(dx*.14,dy*.63,dz*.34)],'Unequal open corner fracture')
            clean(ob);reports.append(export([ob],ob.name));source=ob.data
            overrides.append({'nodeId':node['id'],'instanceIndex':ix,'geometry':node['geometry'],'materialId':node['materials'][0],'sourceVariant':seed%6,'replacement':ob.name+'.json',**inst})
        new=bpy.data.objects.new(old.name.replace('Before','After'),source);after.objects.link(new)
        for ob in [old,new]:ob.location=(-p[0],-p[2],p[1]);ob.scale=(s[0],s[2],s[1]);ob.rotation_mode='QUATERNION';ob.rotation_quaternion=Quaternion((q[3],q[0],q[2],-q[1]))
assert len(overrides)==8,len(overrides)
assert all(not r['nonmanifold_edges_welded'] for r in reports),reports
scene.camera.location=(-13,-5,13);focus=Vector((-2.8,7.5,8));scene.camera.rotation_euler=(focus-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=12.3
for lamp,loc,energy in zip([o for o in scene.objects if o.type=='LIGHT'],[(-6,0,14),(3,10,11)],[1500,650]):
    lamp.location=loc;lamp.data.energy=energy;lamp.data.size=4;lamp.rotation_euler=(focus-lamp.location).to_track_quat('-Z','Y').to_euler()
before.hide_render=False;after.hide_render=True;render('portal-before-clay.png');before.hide_render=True;after.hide_render=False;render('portal-after-clay.png')
manifest={'bridge_sha256':hashlib.sha256(BRIDGE.read_bytes()).hexdigest(),'identity':'original node UUID + original instanceIndex + exact transform/color/material/geometry','overrides':overrides,'scope':'Only eight listed portal pier/buttress/spandrel instances. Other V12 masonry remains unchanged.'}
(OUT/'architecture-overrides.json').write_text(json.dumps(manifest,indent=2));report={'meshes':reports,'stair_nose_losses':cuts,'stair_volumes':volumes,'stair_joint_width':.028,'stair_boundary_centers_preserved':True,'stair_outer_width_and_level_heights_preserved':True,'source_v11_mesh_sha256':hashlib.sha256((V11/'stairs-v11-mesh.json').read_bytes()).hexdigest(),'source_v12_validation_sha256':hashlib.sha256((V12/'independent-validation.json').read_bytes()).hexdigest(),'notes':['Clay assembly excludes non-instanced arch-ring mesh and trim; matching before/after context only.','No scene material, lighting or Unity files changed.']}
assert all(not r['nonmanifold_edges_welded'] for r in reports),reports
(OUT/'build-validation.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'masonry-v13.blend'));print('MASONRY_V13_COMPLETE',len(overrides),len(cuts),sum(r['triangles'] for r in reports))
