"""V9 authored bark relief, irregular buttresses and curved fine terminal rebuild."""
import bpy,bmesh,json,math,hashlib,random
from collections import defaultdict
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.noise import noise
WORK=Path(__file__).resolve().parent;ROOT=next(p for p in WORK.parents if (p/"ArtSource").is_dir())
SOURCE=ROOT/'Migration/Source/AtmosphereV2/TreeV8/tree-v8.blend'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
source=next(o for o in bpy.data.objects if o.type=='MESH');source.name='V8 source preserved';mesh=source.data;material=mesh.materials[0]
bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table();unseen=set(bm.verts);components=[]
while unseen:
    seed=unseen.pop();comp=[seed.index];queue=[seed]
    while queue:
        at=queue.pop()
        for e in at.link_edges:
            n=e.other_vert(at)
            if n in unseen:unseen.remove(n);comp.append(n.index);queue.append(n)
    components.append(comp)
bm.free();major_ids=set(max(components,key=len));vertexuv=defaultdict(list)
for poly in mesh.polygons:
    for li in poly.loop_indices:vertexuv[mesh.loops[li].vertex_index].append(mesh.uv_layers.active.data[li].uv.y)
def rings_of(comp):
    rings=defaultdict(list)
    for i in comp:
        if vertexuv[i]:rings[round(sum(vertexuv[i])/len(vertexuv[i]),5)].append(i)
    rings=[rings[k] for k in sorted(rings)]
    if len(rings)<3 or any(len(r)<4 for r in rings):return None
    centers=[sum((mesh.vertices[i].co for i in r),Vector())/len(r) for r in rings]
    radii=[sum((mesh.vertices[i].co-c).length for i in r)/len(r) for r,c in zip(rings,centers)]
    return rings,centers,radii
candidates=[]
for comp in components:
    if comp[0] in major_ids:continue
    rc=rings_of(comp)
    if not rc:continue
    _,cc,rs=rc;length=sum((cc[j]-cc[j-1]).length for j in range(1,len(cc)))
    straight=(cc[-1]-cc[0]).length/max(length,.0001)
    if .17<length<.85 and .002<max(rs)<.024 and cc[0].z>1.8 and straight>.7:
        candidates.append((max(rs)*length*straight,comp,rc))
selected=[]
for item in sorted(candidates,key=lambda x:-x[0]):
    if all((item[2][1][0]-other[2][1][0]).length>.25 for other in selected):selected.append(item)
    if len(selected)==8:break
replaced={i for _,comp,_ in selected for i in comp}
taper_positions={};tapered_thick_terminals=0
for comp in components:
    if comp[0] in major_ids or any(i in replaced for i in comp):continue
    rc=rings_of(comp)
    if not rc:continue
    rings,centers,radii=rc
    if not (.024<max(radii)<.075 and min(c.z for c in centers)>1.65):continue
    for j,(ring,center) in enumerate(zip(rings,centers)):
        progress=j/max(1,len(rings)-1);tail=max(0,(progress-.72)/.28)
        factor=1-.50*tail*tail*(3-2*tail)
        for i in ring:taper_positions[i]=center+(mesh.vertices[i].co-center)*factor
    tapered_thick_terminals+=1
def subset(name,keep):
    pp=[p for p in mesh.polygons if all(i in keep for i in p.vertices)]
    used=sorted({i for p in pp for i in p.vertices});mapping={v:i for i,v in enumerate(used)}
    me=bpy.data.meshes.new(name);me.from_pydata([taper_positions.get(i,mesh.vertices[i].co) for i in used],[],[[mapping[v] for v in p.vertices] for p in pp]);me.update()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(material);uv=me.uv_layers.new(name='BarkUV')
    for new,old in zip(me.polygons,pp):
        new.use_smooth=True
        for li,oldli in zip(new.loop_indices,old.loop_indices):uv.data[li].uv=mesh.uv_layers.active.data[oldli].uv
    return ob
major=subset('Sculpted main wood',major_ids)
fine=subset('Retained fine tips and roots',set(range(len(mesh.vertices)))-major_ids-replaced)

def tube(name,points,radii,sides=14,flatten=1,phase=0):
    vertices=[];faces=[];uvs=[];previous=None;distance=0
    for j,(p,r) in enumerate(zip(points,radii)):
        t=(points[min(j+1,len(points)-1)]-points[max(0,j-1)]).normalized()
        a=t.cross(Vector((0,1,0))).normalized() if previous is None else (previous-t*previous.dot(t)).normalized()
        b=t.cross(a).normalized();previous=a
        if j:distance+=(p-points[j-1]).length
        for k in range(sides):
            angle=math.tau*k/sides
            asym=1+.11*math.sin(angle*3+phase+j*.16)+.055*math.cos(angle*5-phase+j*.08)
            vertices.append(p+(a*math.cos(angle)*flatten+b*math.sin(angle))*r*asym);uvs.append((k/sides,distance*.7))
            if j:faces.append(((j-1)*sides+k,(j-1)*sides+(k+1)%sides,j*sides+(k+1)%sides,j*sides+k))
    faces.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+k for k in range(sides))])
    me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(material);uv=me.uv_layers.new(name='BarkUV')
    for p in me.polygons:
        p.use_smooth=True
        for li in p.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
        if max(uv.data[li].uv.x for li in p.loop_indices)-min(uv.data[li].uv.x for li in p.loop_indices)>.8:
            for li in p.loop_indices:
                if uv.data[li].uv.x<.1:uv.data[li].uv.x+=1
    return ob
def bezier(a,b,c,d,t):return a*(1-t)**3+b*3*(1-t)**2*t+c*3*(1-t)*t*t+d*t**3

# Four individually directed, asymmetric buttresses override the uniform fan.
# Broad inner flares climb the trunk; their ends stay within the current fan.
buttress_recipes=[
 ((-.10,-.02,.75),(-.50,-.35,.43),(-.63,-.90,.10),(-.78,-1.20,.015),.23,1.30),
 ((.03,.06,.61),(.48,.22,.31),(.83,.52,.05),(1.16,.69,.009),.20,1.42),
 ((-.20,.05,.78),(-.55,.36,.38),(-.89,.73,.06),(-1.11,.90,.005),.245,1.15),
 ((.02,-.05,.56),(.38,-.18,.23),(.91,-.45,.04),(1.27,-.56,.009),.18,1.30),
]
buttresses=[]
for idx,(a,b,c,d,r,w) in enumerate(buttress_recipes):
    a,b,c,d=map(Vector,(a,b,c,d));pp=[];rr=[]
    for j in range(25):
        t=j/24;pp.append(bezier(a,b,c,d,t));rr.append(max(.002,r*(1-t)**1.25))
    buttresses.append(tube('Irregular buttress '+str(idx),pp,rr,24,w,idx*1.7))

# Replace three upper elbows with broad fair cross-sections. A spatial field
# changes their bend over a full local diameter and is shared by attached tips.
elbows=[((-.64,.05,3.44),(.12,0,.025),.48),((-1.56,-.07,4.00),(.11,0,.055),.40),((1.05,.03,2.96),(-.105,.005,.025),.40)]
def bend_delta(p):
    delta=Vector()
    for at,shift,radius in elbows:
        d=(p-Vector(at)).length/radius
        if d<2.2:delta+=Vector(shift)*math.exp(-1.6*d*d)
    return delta
for ob in (major,fine):
    for v in ob.data.vertices:
        if v.co.z>1.6:v.co+=bend_delta(v.co)

bpy.ops.object.select_all(action='DESELECT');major.select_set(True)
for ob in buttresses:ob.select_set(True)
bpy.context.view_layer.objects.active=major;bpy.ops.object.join()
print('V9 union start',flush=True)
mod=major.modifiers.new('Continuous irregular buttresses','REMESH');mod.mode='VOXEL';mod.voxel_size=.013;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name)
mod=major.modifiers.new('Fair continuous upper forks','SMOOTH');mod.factor=.62;mod.iterations=10;bpy.ops.object.modifier_apply(modifier=mod.name)
major.data.calc_loop_triangles();raw=len(major.data.loop_triangles)
mod=major.modifiers.new('Main wood budget','DECIMATE');mod.ratio=min(1,38000/raw);bpy.ops.object.modifier_apply(modifier=mod.name)
if not major.data.uv_layers:major.data.uv_layers.new(name='BarkUV')
mod=major.modifiers.new('Reproject existing bark','DATA_TRANSFER');mod.object=source;mod.use_loop_data=True;mod.data_types_loops={'UV'};mod.loop_mapping='POLYINTERP_NEAREST';mod.layers_uv_select_src='ALL';mod.layers_uv_select_dst='NAME';bpy.ops.object.modifier_apply(modifier=mod.name)
print('V9 main wood',len(major.data.polygons),flush=True)

# Geometry relief, not just a normal map: irregular scaly raised bark on the
# hero trunk and long limb faces. Project each plate vertex onto the real wood.
# Short unequal ends expose transverse breaks between longitudinal strips.
paths=[
 ([(-.1,0,.55),(-.52,.03,1.3),(-.65,.04,1.93),(-.39,.04,2.55),(-.48,.04,3.05),(-.43,.05,3.75),(-.43,.06,4.4)],[.32,.31,.26,.22,.18,.13,.07]),
 ([(-.57,.03,1.3),(-1.0,-.07,1.53),(-1.52,-.04,1.72),(-1.73,-.06,2.04),(-2.18,-.1,2.16)],[.22,.16,.11,.065,.025]),
 ([(-.67,.06,1.9),(-.14,.17,2.06),(.37,.1,2.42),(.83,.05,2.5),(.97,.03,2.97),(1.09,.025,3.4)],[.23,.19,.15,.11,.07,.04]),
 ([(-.49,.04,3.0),(-1.03,.04,3.25),(-1.28,-.025,3.68),(-1.49,-.075,4.02),(-1.53,-.12,4.4)],[.16,.13,.095,.065,.035]),
 ([(-.43,.05,3.79),(-.09,.06,4.08),(.33,.11,4.11),(.61,.11,4.47),(.9,.08,4.7)],[.12,.09,.065,.035,.018]),
 ([(-.21,.04,.9),(-.08,.35,1.3),(.15,.64,1.64),(.45,.85,2.04),(.32,1.02,2.47)],[.22,.17,.12,.07,.035]),
 ([(.82,.06,2.48),(1.39,.07,2.48),(1.82,.09,2.67),(2.15,.02,2.64)],[.09,.065,.044,.025]),
]
for a,b,c,d,r,w in buttress_recipes:
    a,b,c,d=map(Vector,(a,b,c,d))
    paths.append(([tuple(bezier(a,b,c,d,t)) for t in (0,.25,.5,.75,1)],[r,max(.025,r*.70),max(.018,r*.42),max(.008,r*.16),.002]))
major.data.calc_loop_triangles()
bm=bmesh.new();bm.from_mesh(major.data);bvh=BVHTree.FromBMesh(bm);bm.free()
plateverts=[];platefaces=[];plateuv=[];random.seed(9049);plate_count=0
def sample_path(pts,rs,t):
    i=min(len(pts)-2,int(t));f=t-i
    return Vector(pts[i]).lerp(Vector(pts[i+1]),f),rs[i]*(1-f)+rs[i+1]*f,(Vector(pts[i+1])-Vector(pts[i])).normalized()
for path_id,(pts,rs) in enumerate(paths):
    for attempt in range(125 if path_id==0 else 70):
        t=random.uniform(.05,len(pts)-1.05);center,radius,tangent=sample_path(pts,rs,t)
        if radius<.032:continue
        theta=random.random()*math.tau
        a=tangent.cross(Vector((0,1,0))).normalized();b=tangent.cross(a).normalized();radial=a*math.cos(theta)+b*math.sin(theta)
        hit,normal,face,distance=bvh.ray_cast(center,radial,radius*3+.12)
        if hit is None or normal.dot(radial)<.25:continue
        # Unequal plate widths and offsets avoid parallel machine-cut rails.
        width=min(radius*.48,random.uniform(.040,.093));length=random.uniform(.14,.34)*(1 if path_id==0 else .85)
        tangent=(tangent-normal*tangent.dot(normal)).normalized();lateral=normal.cross(tangent).normalized()
        local=[];localuv=[];valid=True;lift=random.uniform(.014,.030)*(min(1,radius/.10))
        skew=random.uniform(-.32,.32)
        for j in range(5):
            u=j/4
            for k in range(4):
                v=k/3;offset=tangent*((u-.5)*length+(v-.5)*skew*length)+lateral*((v-.5)*width)
                point,n,fi,dist=bvh.find_nearest(hit+offset)
                if point is None or dist>radius*.75 or n.dot(normal)<.15:valid=False;break
                # Asymmetric crest; broken ends, narrow transverse seam shadow.
                crest=math.sin(math.pi*v)**1.5*math.sin(math.pi*u)**.55
                raised=lift*crest*(.75+.25*math.sin(u*7+theta))
                local.append(point+n*(.001+raised));localuv.append((v*.23+theta/math.tau,u*length*.7+t*.35))
            if not valid:break
        if not valid:continue
        start=len(plateverts);plateverts.extend(local);plateuv.extend(localuv)
        for j in range(4):
            for k in range(3):
                # One uneven missing corner on selected plates breaks ends.
                if j==3 and k==0 and plate_count%3==0:continue
                platefaces.append((start+j*4+k,start+(j+1)*4+k,start+(j+1)*4+k+1,start+j*4+k+1))
        plate_count+=1
platesmesh=bpy.data.meshes.new('Interrupted raised bark plates');platesmesh.from_pydata(plateverts,[],platefaces);platesmesh.update();plates=bpy.data.objects.new('Interrupted raised bark plates',platesmesh);bpy.context.collection.objects.link(plates);platesmesh.materials.append(material);uvlayer=platesmesh.uv_layers.new(name='BarkUV')
for poly in platesmesh.polygons:
    poly.use_smooth=True
    for li in poly.loop_indices:uvlayer.data[li].uv=plateuv[platesmesh.loops[li].vertex_index]

# Eight actual fine-needle replacements, unlike V8's thicker-end selection.
twigs=[];twig_notes=[]
for idx,(_,comp,rc) in enumerate(selected):
    _,cc,rs=rc;base=cc[0]+bend_delta(cc[0]);tip=cc[-1]+bend_delta(cc[-1]);delta=tip-base;length=delta.length
    side=delta.normalized().cross(Vector((0,1,0))).normalized()*(-1 if idx%2 else 1)
    a=base;b=base+delta*.32+side*length*.19;c=base+delta*.72-side*length*.12;d=tip
    points=[bezier(a,b,c,d,j/20) for j in range(21)];radius=max(rs[0],.0085)
    radii=[max(.00032,radius*(1-j/20)**1.15) for j in range(21)]
    twigs.append(tube('Curved fine offshoot '+str(idx),points,radii,10,1,idx))
    start=points[11];end=start+delta*.33-side*length*.3
    fork=[bezier(start,start+delta*.15,start+delta*.23-side*length*.22,end,j/13) for j in range(14)]
    twigs.append(tube('Fine offshoot split '+str(idx),fork,[max(.0002,radii[11]*.68*(1-j/13)**1.2) for j in range(14)],8,1,idx+.7))
    twig_notes.append({'base':list(base),'tip':list(tip),'radius':radius})

bpy.ops.object.select_all(action='DESELECT')
for ob in [major,fine,plates]+twigs:ob.select_set(True)
bpy.context.view_layer.objects.active=major;bpy.ops.object.join();obj=major;obj.parent=bpy.data.objects.get('TreeRoot');bpy.data.objects.remove(source,do_unlink=True);obj.name='Sculpted bark roots and fine branches';mesh=obj.data
mesh.validate(clean_customdata=False);mesh.update()
for p in mesh.polygons:p.use_smooth=True
mesh.calc_loop_triangles();positions=[];normals=[];uv=[];indices=[];lookup={};corner_normals=[n.vector.copy() for n in mesh.corner_normals]
for tri in mesh.loop_triangles:
    for li in (tri.loops[0],tri.loops[2],tri.loops[1]):
        p=mesh.vertices[mesh.loops[li].vertex_index].co;n=corner_normals[li];pos=(-p.x,p.z,-p.y);norm=(-n.x,n.z,-n.y);tex=tuple(mesh.uv_layers.active.data[li].uv);key=pos+norm+tex
        if key not in lookup:lookup[key]=len(positions)//3;positions.extend(pos);normals.extend(norm);uv.extend(tex)
        indices.append(lookup[key])
assert len(indices)//3<80000
assert all(math.isfinite(v) for v in positions+normals+uv)
(WORK/'tree-v9-mesh.json').write_text(json.dumps({'positions':positions,'normals':normals,'uv':uv,'indices':indices},separators=(',',':')))
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'tree-v9.blend'))
report={'source':str(SOURCE),'source_sha256':source_hash,'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash,'mesh_vertices':len(mesh.vertices),'export_vertices':len(positions)//3,'triangles':len(indices)//3,'delta_triangles_vs_v8':len(indices)//3-51654,'raised_bark_plates':plate_count,'sculpted_buttresses':4,'replaced_fine_split_offshoots':len(selected),'fine_offshoots':twig_notes,'coordinates':'Blender (x,y,z) -> Unity (-x,z,-y); reversed winding [0,2,1]','uv':'Reprojected native bark on remeshed wood; longitudinal UV on bark plates and twigs; exact tuple dedup preserves UV seams','bounds_blender_min':[min(v.co[i] for v in mesh.vertices) for i in range(3)],'bounds_blender_max':[max(v.co[i] for v in mesh.vertices) for i in range(3)]}
(WORK/'tree-v9-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)

scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1280;scene.render.resolution_y=1280;scene.render.resolution_percentage=100;scene.world.color=(.06,.06,.06);scene.view_settings.view_transform='AgX'
def look_at(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-13,8));camera=bpy.context.object;look_at(camera,(0,0,3.05));camera.data.type='ORTHO';camera.data.ortho_scale=7.6;scene.camera=camera
for loc,power,color,size in [((-5,-5,9),1800,(.55,.72,1),5),((4,-2,5),950,(1,.68,.35),4),((0,5,7),1600,(.35,.6,1),4)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.color=color;light.data.shape='DISK';light.data.size=size;look_at(light,(0,0,3))
scene.render.filepath=str(WORK/'tree-v9-preview.png');bpy.ops.render.render(write_still=True)
obj.hide_render=True
with bpy.data.libraries.load(str(SOURCE),link=False) as (data_from,data_to):data_to.objects=[name for name in data_from.objects if 'Sculpted bark' in name]
prior=data_to.objects[0];bpy.context.collection.objects.link(prior);prior.hide_render=False
scene.render.filepath=str(WORK/'tree-v8-same-light.png');bpy.ops.render.render(write_still=True)
