"""Upright-faced, locally fractured architecture. Additive source only."""
import bpy,bmesh,math,json,hashlib,random
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
SCRATCH=ROOT/'.dream-loop/unity-atmosphere-v2/masonry-v12';SCRATCH.mkdir(parents=True,exist_ok=True)
V8=ROOT/'Migration/Source/AtmosphereV2/MasonryV8'
sourcehash={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in V8.iterdir() if p.is_file()}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Consistent neutral clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.21,.24,.255,1);bs.inputs['Roughness'].default_value=.77
master=bpy.data.collections.new('Authored normalized stones');bpy.context.scene.collection.children.link(master)
old=bpy.data.collections.new('Preserved V8 comparison');bpy.context.scene.collection.children.link(old)
objects=[];oldobjects=[]
def put_collection(ob,col):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    col.objects.link(ob)
def cleanup_mesh(me):
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
def cut(ob,points,name):
    bm=bmesh.new()
    for p in points:bm.verts.new(p)
    bmesh.ops.convex_hull(bm,input=list(bm.verts));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free()
    tool=bpy.data.objects.new('Temporary '+name,me);master.objects.link(tool);bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
def face_pit(ob,cx,cz,w,h,depth,k):
    # Uneven fractured mineral loss; outer rim lies outside front face.
    outline=[(-1,-.25),(-.52,-1),(.31,-.83),(1,-.19),(.63,.78),(-.15,1),(-.78,.62)]
    points=[(cx+u*w,-.506,cz+v*h) for u,v in outline]
    points += [(cx-w*.24,-.5+depth,cz+h*.13),(cx+w*.26,-.5+depth*.68,cz-h*.18)]
    cut(ob,points,'Angular mineral spall '+str(k))

pitlayouts=[ [(-.26,.11,.10,.073,.021),(.18,-.19,.064,.088,.017)],
             [(.15,.18,.15,.069,.024)],
             [(-.12,-.13,.095,.12,.028),(.27,.05,.057,.071,.019),(-.29,.27,.046,.061,.014)],
             [(.22,-.18,.13,.078,.021),(-.17,.15,.065,.11,.018)],
             [(-.20,.07,.18,.073,.027),(.21,.28,.075,.06,.021),(.25,-.20,.046,.061,.017),(-.22,-.30,.052,.033,.012)],
             [(.06,-.12,.11,.093,.026),(-.25,.22,.063,.066,.018)],
             [(-.22,.15,.15,.091,.026)], [(.23,-.13,.16,.092,.028)] ]
for k in range(8):
    original='masonry-v8-'+str(k) if k<6 else 'facade-v8-'+str(k-6)
    new='masonry-v12-'+str(k) if k<6 else 'facade-v12-'+str(k-6)
    d=json.loads((V8/(original+'.json')).read_text());p=d['positions'];ix=d['indices']
    me=bpy.data.meshes.new(original);me.from_pydata([(p[i],-p[i+2],p[i+1]) for i in range(0,len(p),3)],[],[ix[i:i+3] for i in range(0,len(ix),3)]);me.update()
    for face in me.polygons:face.use_smooth=True
    nn=d['normals'];me.normals_split_custom_set_from_vertices([(nn[i],-nn[i+2],nn[i+1]) for i in range(0,len(nn),3)])
    before=bpy.data.objects.new(original,me);old.objects.link(before);me.materials.append(mat);oldobjects.append(before)
    # Keep the useful fractured V8 body, but collapse its overly broad shoulder
    # toward the axis-aligned face planes. This monotonically preserves topology
    # and local ordering: at abs .4 the old 10cm belt becomes 1.7cm, and at .45
    # the old 5cm shoulder becomes 2.85mm. Inner fracture pockets remain intact.
    me=bpy.data.meshes.new(new);me.from_pydata([(p[i],-p[i+2],p[i+1]) for i in range(0,len(p),3)],[],[ix[i:i+3] for i in range(0,len(ix),3)]);me.update()
    ob=bpy.data.objects.new(new,me);master.objects.link(ob);bpy.context.view_layer.objects.active=ob
    cleanup_mesh(ob.data)
    for v in ob.data.vertices:
        original_co=v.co.copy()
        for axis in range(3):
            value=original_co[axis];a=abs(value)
            if a>.20:
                t=min(1,(a-.20)/.30)
                projected=math.copysign(.50-.30*(1-t)**2.6,value)
                others=[j for j in range(3) if j!=axis]
                edge=max(abs(original_co[j]) for j in others)
                e=max(0,min(1,(edge-.20)/.22));weight=.20+.80*e*e*(3-2*e)
                v.co[axis]=value+(projected-value)*weight
    cleanup_mesh(ob.data)
    if k in [2,5]:
        # Only two hero variants: broad open upper corner, at most 1/4 depth.
        sign=-1 if k==2 else 1;n=Vector((sign*1.0,-.92,.81));distance=(1+.92+.81)*.5-.235
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=n*(distance/n.length_squared),plane_no=n,dist=1e-7,clear_outer=True,clear_inner=False)
        boundary=[e for e in bm.edges if e.is_boundary];bmesh.ops.holes_fill(bm,edges=boundary,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
    else:
        # Finite top-front arris loss; most of the arris remains upright.
        cx=[-.24,.22,0,-.13,.27,0,-.26,.22][k];half=.13 if k<6 else .18;depth=.026+.003*(k%3)
        cut(ob,[(cx-half,-.508,.508),(cx+half,-.508,.508),(cx+half*.8,-.5+depth,.508),(cx-half*.7,-.5+depth*.74,.508),
                (cx-half*.84,-.508,.46),(cx+half*.68,-.508,.477),(cx,-.5+depth*.42,.492)],'Local broken upper arris')
    # Existing V8 pits survive the monotone reshape. Add only one shallow
    # mineral patch on selected quiet variants, not a regular field of holes.
    if k in [1,4,6,7]:face_pit(ob,*pitlayouts[k][0],0)
    if k<6:
        # Several unequal open edge losses, never a full perimeter chamfer.
        cx=.25 if k%2==0 else -.26;half=.09+.012*(k%3)
        cut(ob,[(cx-half,-.508,.508),(cx+half,-.508,.508),(cx+half*.54,-.463,.508),(cx-half*.65,-.477,.508),
                (cx-half*.71,-.508,.474),(cx+half*.82,-.508,.481),(cx+.018,-.482,.479)],'Second discontinuous top-edge loss')
        cx=-.11+.037*k;half=.13 if k%2 else .095
        cut(ob,[(cx-half,-.508,-.508),(cx+half,-.508,-.508),(cx+half*.7,-.471,-.508),(cx-half*.85,-.484,-.508),
                (cx-half*.48,-.508,-.470),(cx+half*.8,-.508,-.477),(cx,-.484,-.482)],'Unequal bottom-contact loss')
    # Selected side corner loss interrupts a second arris without girdling block.
    if k in [0,3,4]:
        side=-1 if k==3 else 1;z=-.16 if k==4 else .17
        cut(ob,[(side*.508,-.508,z-.16),(side*.508,-.508,z+.16),(side*.459,-.508,z+.08),
                (side*.508,-.459,z-.09),(side*.474,-.477,z+.015)],'Unequal side arris spall')
    cleanup_mesh(ob.data);ob.data.calc_loop_triangles();authored=len(ob.data.loop_triangles);budget=800 if k<6 else 180
    if authored>budget:
        bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Runtime silhouette budget','DECIMATE');mod.ratio=budget/authored;mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    cleanup_mesh(ob.data)
    # Decimation can overshoot planar boundaries by a few 1e-5 units. Clamp
    # only that numerical overshoot; do not globally rescale authored damage.
    for v in ob.data.vertices:
        for axis in range(3):
            value=max(-.5,min(.5,v.co[axis]))
            v.co[axis]=math.copysign(.5,value) if abs(value)>.4999 else value
    for axis in range(3):
        low=min(ob.data.vertices,key=lambda v:v.co[axis]);high=max(ob.data.vertices,key=lambda v:v.co[axis])
        assert abs(low.co[axis]+.5)<.002 and abs(high.co[axis]-.5)<.002
        low.co[axis]=-.5;high.co[axis]=.5
    ob.data.update()
    # Exact bounds remain naturally on untouched portions; fail rather than stretch.
    bounds=[[min(v.co[a] for v in ob.data.vertices) for a in range(3)],[max(v.co[a] for v in ob.data.vertices) for a in range(3)]]
    assert bounds==[[-.5]*3,[.5]*3],bounds
    ob.data.materials.clear();ob.data.materials.append(mat)
    for p in ob.data.polygons:p.material_index=0;p.use_smooth=True
    bpy.context.view_layer.objects.active=ob;sharp=ob.modifiers.new('Hard fracture boundaries','EDGE_SPLIT');sharp.split_angle=.30;bpy.ops.object.modifier_apply(modifier=sharp.name)
    ob['authored_triangles']=authored;ob['budget']=budget;objects.append(ob)

scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.world.color=(.07,.07,.07)
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=1536;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(4,-7,4.6));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=5.5;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
for loc,energy,size in [((-3,-4,6),1200,2.5),((4,2,3),300,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=energy;l.data.size=size;l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()
def render(path):scene.render.filepath=str(OUT/path);bpy.ops.render.render(write_still=True)
for k in range(8):
    pos=((k%3-1)*1.65,(k//3-1)*1.4,0)
    for ob in [objects[k],oldobjects[k]]:ob.location=pos;ob.scale=(1.25,1,.75)
old.hide_render=True;render('variants-after-clay.png');old.hide_render=False;master.hide_render=True;render('variants-before-clay.png')
wall_old=bpy.data.collections.new('Old wall assembly');scene.collection.children.link(wall_old)
wall_new=bpy.data.collections.new('New wall assembly');scene.collection.children.link(wall_new)
for row in range(5):
    for col in range(6):
        k=(row*5+col)%6
        for source,collection in [(objects[k],wall_new),(oldobjects[k],wall_old)]:
            ob=source.copy();ob.data=source.data;collection.objects.link(ob);ob.location=((col-2.5)*1.04+(row%2)*.22,0,(row-2)*.48);ob.scale=(1,.68,.455)
cam.location=(5.4,-10,4);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=7.8
old.hide_render=True;master.hide_render=True;wall_new.hide_render=True;render('wall-before-clay.png');wall_new.hide_render=False;wall_old.hide_render=True;render('wall-after-clay.png')
rows=[]
for ob in objects:
    me=ob.data;me.calc_loop_triangles();pos=[];norm=[];uv=[];inds=[];dedup={}
    for tri in me.loop_triangles:
        for li in tri.loops:
            p=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector
            if n.dot(tri.normal)<.05:n=tri.normal
            axis=max(range(3),key=lambda a:abs(n[a]));t=[(p.y+.5,p.z+.5),(p.x+.5,p.z+.5),(p.x+.5,p.y+.5)][axis]
            key=(p.x,p.z,-p.y,n.x,n.z,-n.y,*t)
            if key not in dedup:dedup[key]=len(pos)//3;pos.extend(key[:3]);norm.extend(key[3:6]);uv.extend(key[6:])
            inds.append(dedup[key])
    d={'id':ob.name,'name':ob.name,'positions':pos,'normals':norm,'uv':uv,'indices':inds};path=OUT/(ob.name+'.json');path.write_text(json.dumps(d,separators=(',',':')))
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
    rows.append({'id':ob.name,'triangles':len(inds)//3,'vertices':len(pos)//3,'authored_triangles':ob['authored_triangles'],'budget':ob['budget'],'nonmanifold_edges_welded':nonmanifold,'bounds':[[min(pos[a::3]) for a in range(3)],[max(pos[a::3]) for a in range(3)]],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
assert all(not r['nonmanifold_edges_welded'] for r in rows),rows
qa={'method':'Upright face planes, finite angular mineral losses, two broad open corner fractures, no continuous bevel shoulder','source_v8_hashes':sourcehash,'all_sources_preserved':all(hashlib.sha256((V8/p).read_bytes()).hexdigest()==h for p,h in sourcehash.items()),'basis':'Unity native (Blender x,z,-y), triangle order retained, no inspection transforms baked','meshes':rows}
(OUT/'build-validation.json').write_text(json.dumps(qa,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'masonry-v12.blend'));print('MASONRY_V12_COMPLETE',sum(r['triangles'] for r in rows))
