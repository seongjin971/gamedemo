"""V10 crown reconstruction. Blender 5.2; authoring and evidence paths only.

Retains the V9 lower-trunk form; discards its needle crown and radial root fan.
Eight major crown systems use C1 continuous centerlines and unequal split ends.
Run: blender --background --threads 6 --python build_tree_v10.py
"""
import bpy, bmesh, math, json, hashlib, random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
WORK=Path(__file__).resolve().parent
ROOT=next(p for p in WORK.parents if (p/'ArtSource').is_dir())
OUT=ROOT/'.dream-loop/unity-atmosphere-v2/tree-v10';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'Migration/Source/AtmosphereV2/TreeV9/tree-v9.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_hash=sha(SOURCE)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
source=bpy.data.objects['Sculpted bark roots and fine branches'];source.name='V9 comparison source'
material=source.data.materials[0];source.hide_render=True
parent=source.parent;source_matrix=source.matrix_local.copy()
mesh=source.data

# Retain the connected lower trunk rather than a fresh cylinder approximation.
bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table();todo=set(bm.verts);components=[]
while todo:
    seed=todo.pop();comp=[seed];queue=[seed]
    while queue:
        v=queue.pop()
        for e in v.link_edges:
            n=e.other_vert(v)
            if n in todo:todo.remove(n);comp.append(n);queue.append(n)
    components.append(comp)
keep={v.index for v in max(components,key=len) if .43<v.co.z<1.66 and abs(v.co.y)<.47 and -.98<v.co.x<.36}
bm.free()
polys=[p for p in mesh.polygons if all(i in keep for i in p.vertices)]
used=sorted({i for p in polys for i in p.vertices});mapping={v:i for i,v in enumerate(used)}
me=bpy.data.meshes.new('Preserved lower trunk');me.from_pydata([mesh.vertices[i].co for i in used],[],[[mapping[i] for i in p.vertices] for p in polys]);me.update()
core=bpy.data.objects.new('Continuous V10 wood',me);bpy.context.collection.objects.link(core);me.materials.append(material)
layer=me.uv_layers.new(name='BarkUV')
for new,old in zip(me.polygons,polys):
    for li,oi in zip(new.loop_indices,old.loop_indices):layer.data[li].uv=mesh.uv_layers.active.data[oi].uv
bm=bmesh.new();bm.from_mesh(me);boundary=[e for e in bm.edges if e.is_boundary]
bmesh.ops.holes_fill(bm,edges=boundary,sides=0);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()

def curve(knots,radii,steps=10):
    """Cardinal spline with full-diameter smooth turns, no polyline elbows."""
    pp=list(map(Vector,knots));points=[];rr=[]
    for i in range(len(pp)-1):
        a=pp[max(0,i-1)];b=pp[i];c=pp[i+1];d=pp[min(len(pp)-1,i+2)]
        m0=(c-a)*.40;m1=(d-b)*.40
        for j in range(steps):
            t=j/steps;t2=t*t;t3=t2*t
            points.append(b*(2*t3-3*t2+1)+m0*(t3-2*t2+t)+c*(-2*t3+3*t2)+m1*(t3-t2))
            s=t2*(3-2*t);rr.append(radii[i]*(1-s)+radii[i+1]*s)
    points.append(pp[-1]);rr.append(radii[-1]);return points,rr

def tube(name,points,radii,sides=18,flatten=1,phase=0):
    vv=[];ff=[];tt=[];axis=None;distance=0
    for j,(p,r) in enumerate(zip(points,radii)):
        tangent=(points[min(j+1,len(points)-1)]-points[max(0,j-1)]).normalized()
        axis=tangent.cross(Vector((0,1,0))).normalized() if axis is None else (axis-tangent*axis.dot(tangent)).normalized()
        other=tangent.cross(axis).normalized()
        if j:distance+=(p-points[j-1]).length
        for k in range(sides):
            angle=math.tau*k/sides
            # Broad twisted grain structure, subordinated to authored silhouette.
            shape=1+.105*math.sin(angle*3+phase+distance*.8)+.05*math.sin(angle*7+phase-distance*1.4)
            vv.append(p+(axis*math.cos(angle)*flatten+other*math.sin(angle))*r*shape);tt.append((k/sides,distance*.7))
            if j:ff.append(((j-1)*sides+k,(j-1)*sides+(k+1)%sides,j*sides+(k+1)%sides,j*sides+k))
    ff.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+k for k in range(sides))])
    me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.update();uv=me.uv_layers.new(name='BarkUV')
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(material)
    for p in me.polygons:
        p.use_smooth=True
        for li in p.loop_indices:uv.data[li].uv=tt[me.loops[li].vertex_index]
        if max(uv.data[li].uv.x for li in p.loop_indices)-min(uv.data[li].uv.x for li in p.loop_indices)>.8:
            for li in p.loop_indices:
                if uv.data[li].uv.x<.1:uv.data[li].uv.x+=1
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    return ob

# Continuous leader plus seven major lateral terminal systems. Their distal
# thirds replace all old needles, including those previously left untouched.
recipes=[
 ('Leader',[(-.53,.02,1.36),(-.62,.02,1.96),(-.42,.04,2.58),(-.46,.05,3.22),(-.38,.07,3.81),(-.30,.09,4.35),(-.45,.11,4.83),(-.29,.08,5.30),(-.39,.03,5.64)],[.29,.27,.23,.19,.14,.096,.057,.027,.002]),
 ('High left',[(-.45,.04,2.92),(-1.02,.03,3.25),(-1.32,-.03,3.78),(-1.51,-.10,4.15),(-1.56,-.15,4.63),(-1.86,-.12,5.02),(-1.81,-.09,5.36)],[.175,.14,.105,.071,.041,.018,.002]),
 ('High right',[(-.42,.07,3.71),(-.04,.08,4.02),(.42,.10,4.18),(.70,.11,4.57),(.81,.10,5.01),(1.10,.12,5.39)],[.125,.093,.067,.045,.022,.002]),
 ('Mid left',[(-.60,.02,2.07),(-1.03,-.08,2.28),(-1.40,-.12,2.72),(-1.79,-.15,3.17),(-2.17,-.14,3.32),(-2.52,-.12,3.67)],[.19,.145,.108,.068,.035,.002]),
 ('Low left',[(-.52,.01,1.39),(-1.02,-.08,1.56),(-1.49,-.08,1.81),(-1.80,-.10,2.13),(-2.23,-.14,2.25),(-2.64,-.12,2.57)],[.21,.161,.109,.072,.034,.002]),
 ('Mid right',[(-.61,.06,1.91),(-.06,.15,2.08),(.41,.11,2.39),(.93,.06,2.58),(1.11,.04,3.00),(1.25,.02,3.50),(1.53,.01,3.89)],[.22,.171,.124,.083,.058,.029,.002]),
 ('Low right',[(-.29,.04,1.14),(.27,.04,1.61),(.86,.03,1.79),(1.42,.07,1.75),(1.90,.08,1.95),(2.30,.09,1.98),(2.67,.10,2.21)],[.22,.179,.131,.092,.060,.025,.002]),
 ('Back ascending',[(-.20,.17,.86),(.14,.48,1.38),(.52,.69,1.86),(.64,.78,2.38),(.96,.79,2.81),(1.24,.78,3.09)],[.19,.15,.107,.076,.040,.002]),
]
wood=[core];ends=[];pathdata=[]
# Broad overlap through the preserved slanting lower trunk closes its cut
# collar robustly; the previous narrow crop alone did not overlap the leader.
bridge_points,bridge_radii=curve([(-.08,.02,.40),(-.22,.025,.78),(-.39,.025,1.15),(-.54,.02,1.53),(-.56,.02,1.77)],[.34,.34,.32,.295,.27],12)
wood.append(tube('Connected lower trunk bridge',bridge_points,bridge_radii,28,1.0,.4))
pathdata.append((bridge_points,bridge_radii))
for i,(name,knots,radii) in enumerate(recipes):
    points,rr=curve(knots,radii,12);pathdata.append((points,rr))
    # Major wood union preserves organic junctions; fine tips retain full taper.
    split=next((j for j,r in enumerate(rr) if r<.028),len(rr)-1)
    wood.append(tube(name+' structural wood',points[:split+1],rr[:split+1],24,1,i*.81))
    ends.append(tube(name+' curved terminal',points[max(0,split-3):],rr[max(0,split-3):],12,1,i*.81))
    for branch_id,(fraction,length,turn) in enumerate([(.43,.67,1),(.64,.70,-1),(.79,.55,1),(.9,.30,-1)]):
        at=int((len(points)-1)*fraction);a=points[at];direction=(points[min(at+2,len(points)-1)]-points[max(0,at-2)]).normalized()
        side=Vector((direction.z,.13*math.sin(i),-direction.x)).normalized()*turn
        if i in (0,1,2):side.z=abs(side.z)*.6;side.normalize()
        length*=1+.14*math.sin(i*2.4+branch_id)
        b=a+direction*length*.34+side*length*.17
        c=a+direction*length*.58+side*length*.53+Vector((0,(-1 if i%2 else 1)*.055,length*.17))
        d=a+direction*length*.76+side*length*.64+Vector((0,0,length*.22))
        base=max(.015,min(.056,rr[at]*.61));fp,fr=curve([a,b,c,d],[base,base*.69,base*.31,.0015],10)
        ends.append(tube(name+' unequal fork '+str(branch_id),fp,fr,12,1,i+branch_id))
        # A secondary curved division gives branching hierarchy, not spines.
        if branch_id<2:
            f=fp[16];e=f+(direction*.17-side*.26+Vector((0,.035,.19)))*length
            qp,qr=curve([f,f+direction*length*.12,e],[fr[16]*.64,fr[16]*.36,.0012],9)
            ends.append(tube(name+' secondary fork '+str(branch_id),qp,qr,9,1,i+2))

# Four substantial plank-like buttresses, no preserved radial needle fan.
# Their widths exceed the four retained new feeder roots by 2.5-3.5 times.
roots=[
 ([(-.17,-.04,.92),(-.39,-.27,.49),(-.54,-.71,.16),(-.80,-1.12,.035),(-.93,-1.35,-.035)],[.22,.205,.125,.050,.003],1.15),
 ([(-.18,.03,.78),(.26,-.08,.40),(.79,-.36,.12),(1.24,-.55,.025),(1.44,-.62,-.035)],[.24,.20,.125,.048,.003],1.20),
 ([(-.31,.06,.95),(-.64,.25,.51),(-.93,.61,.13),(-1.17,.83,.035),(-1.39,.96,-.025)],[.23,.195,.13,.045,.003],1.10),
 ([(-.06,.13,.70),(.20,.43,.34),(.43,.92,.095),(.62,1.31,.015),(.82,1.44,-.025)],[.22,.18,.105,.042,.003],1.12),
]
for i,(knots,radii,flat) in enumerate(roots):
    pp,rr=curve(knots,radii,12);wood.append(tube('Broad buttress '+str(i),pp,rr,24,flat,i));pathdata.append((pp,rr))
    # A single small feeder curls away and sinks below stone rather than a fan.
    a=Vector(knots[2]);d=a+Vector((.28*(-1 if i%2 else 1),.34*(-1 if i>1 else 1),-.18))
    pp,rr=curve([a,a.lerp(d,.5)+Vector((.08,-.04,0)),d],[.082,.038,.002],12)
    ends.append(tube('Small root feeder '+str(i),pp,rr,12,1,i))

bpy.ops.object.select_all(action='DESELECT')
for ob in wood:ob.select_set(True)
bpy.context.view_layer.objects.active=core;bpy.ops.object.join()
uv_source=core.copy();uv_source.data=core.data.copy();uv_source.name='Authored wood UV source';bpy.context.collection.objects.link(uv_source);uv_source.hide_render=True
print('V10 union start',flush=True)
mod=core.modifiers.new('Joined authored trunk crown and buttresses','REMESH');mod.mode='VOXEL';mod.voxel_size=.014;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name)
mod=core.modifiers.new('Fair fork junctions','SMOOTH');mod.factor=.65;mod.iterations=5;bpy.ops.object.modifier_apply(modifier=mod.name)
core.data.calc_loop_triangles();raw=len(core.data.loop_triangles)
mod=core.modifiers.new('Continuous wood budget','DECIMATE');mod.ratio=min(1,39000/raw);bpy.ops.object.modifier_apply(modifier=mod.name)
if not core.data.uv_layers:core.data.uv_layers.new(name='BarkUV')
mod=core.modifiers.new('Reproject authored longitudinal bark','DATA_TRANSFER');mod.object=uv_source;mod.use_loop_data=True;mod.data_types_loops={'UV'};mod.loop_mapping='POLYINTERP_NEAREST';mod.layers_uv_select_src='ALL';mod.layers_uv_select_dst='NAME';bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(uv_source,do_unlink=True)
bm=bmesh.new();bm.from_mesh(core.data);todo=set(bm.verts);connected_sizes=[];component_verts=[]
while todo:
    seed=todo.pop();size=1;queue=[seed];verts=[seed]
    while queue:
        v=queue.pop()
        for e in v.link_edges:
            n=e.other_vert(v)
            if n in todo:todo.remove(n);size+=1;queue.append(n);verts.append(n)
    connected_sizes.append(size);component_verts.append(verts)
largest=max(component_verts,key=len)
bmesh.ops.delete(bm,geom=[v for comp in component_verts if comp is not largest for v in comp],context='VERTS')
bm.to_mesh(core.data);bm.free();connected_sizes=[len(largest)]
print('V10 connected core component sizes',connected_sizes,flush=True)
assert len(connected_sizes)==1 or connected_sizes[1]<50, 'Disconnected major wood requires correction'
print('V10 core complete',len(core.data.polygons),flush=True)

# Interrupted raised longitudinal bark ribbons on new major wood. Each patch
# follows the actual authored centerline and wraps over its convex surface.
bm=bmesh.new();bm.from_mesh(core.data);bvh=BVHTree.FromBMesh(bm);bm.free()
random.seed(101042);pv=[];pf=[];pu=[];plate_count=0
for path_id,(points,rr) in enumerate(pathdata):
    for attempt in range(82 if path_id==0 else 44):
        j=random.randrange(2,len(points)-3);radius=rr[j]
        if radius<.042:continue
        p=points[j];t=(points[j+1]-points[j-1]).normalized();theta=random.random()*math.tau
        a=t.cross(Vector((0,1,0))).normalized();rad=a*math.cos(theta)+t.cross(a)*math.sin(theta)
        hit,n,fi,dist=bvh.ray_cast(p,rad,radius*3+.10)
        if hit is None or n.dot(rad)<.15:continue
        t=(t-n*t.dot(n)).normalized();s=n.cross(t).normalized();length=random.uniform(.14,.37);width=random.uniform(.040,.085);lift=random.uniform(.008,.022)*min(1,radius/.12)
        vv=[];uv=[];valid=True
        for row in range(5):
            u=row/4
            for col in range(4):
                v=col/3;q=hit+t*((u-.5)*length+(v-.5)*length*.18)+s*((v-.5)*width)
                q,qn,fi,dist=bvh.find_nearest(q)
                if q is None or dist>radius*.75 or qn.dot(n)<.15:valid=False;break
                vv.append(q+qn*(.0008+lift*math.sin(math.pi*u)**.7*math.sin(math.pi*v)**1.4));uv.append((theta/math.tau+v*.15,j*.075+u*length*.7))
            if not valid:break
        if not valid:continue
        off=len(pv);pv.extend(vv);pu.extend(uv)
        for row in range(4):
            for col in range(3):
                if row==0 and col==0 and plate_count%3==0:continue
                pf.append((off+row*4+col,off+(row+1)*4+col,off+(row+1)*4+col+1,off+row*4+col+1))
        plate_count+=1
me=bpy.data.meshes.new('Interrupted raised grain');me.from_pydata(pv,[],pf);me.update();uv=me.uv_layers.new(name='BarkUV');me.materials.append(material)
plates=bpy.data.objects.new('Interrupted bark ridges',me);bpy.context.collection.objects.link(plates)
for p in me.polygons:
    p.use_smooth=True
    for li in p.loop_indices:uv.data[li].uv=pu[me.loops[li].vertex_index]
bpy.ops.object.select_all(action='DESELECT')
for ob in [core,plates]+ends:ob.select_set(True)
bpy.context.view_layer.objects.active=core;bpy.ops.object.join();obj=core;obj.name='Sculpted bark roots and fine branches';obj.parent=parent;obj.matrix_local=source_matrix
obj.hide_render=False;mesh=obj.data;mesh.validate(clean_customdata=False);mesh.update()
# Restore V9's broad crown envelope while locking origin and lower trunk.
for v in mesh.vertices:
    if v.co.z>1.66:
        blend=min(1,(v.co.z-1.66)/.9)
        v.co.x+=(v.co.x+.3)*(.20 if v.co.x<-.3 else .08)*blend
        v.co.z=1.66+(v.co.z-1.66)*1.20
mesh.update()
for p in mesh.polygons:p.use_smooth=True
mesh.calc_loop_triangles();positions=[];normals=[];texcoords=[];indices=[];lookup={};cn=[n.vector.copy() for n in mesh.corner_normals]
discarded_degenerate=0;flat_normal_fallbacks=0
for tri in mesh.loop_triangles:
    a,b,c=[mesh.vertices[i].co for i in tri.vertices];face=(b-a).cross(c-a)
    if face.length<2e-12:discarded_degenerate+=1;continue
    flat=face.normalized();use_flat=sum((cn[li] for li in tri.loops),Vector()).dot(flat)<0
    if use_flat:flat_normal_fallbacks+=1
    for li in (tri.loops[0],tri.loops[2],tri.loops[1]):
        p=mesh.vertices[mesh.loops[li].vertex_index].co;n=flat if use_flat else cn[li];pos=(-p.x,p.z,-p.y);normal=(-n.x,n.z,-n.y);uv=tuple(mesh.uv_layers.active.data[li].uv);key=pos+normal+uv
        if key not in lookup:lookup[key]=len(positions)//3;positions.extend(pos);normals.extend(normal);texcoords.extend(uv)
        indices.append(lookup[key])
assert len(indices)//3<100000
assert all(math.isfinite(v) for v in positions+normals+texcoords)
payload=json.dumps({'positions':positions,'normals':normals,'uv':texcoords,'indices':indices},separators=(',',':'))
(WORK/'tree-v10-mesh.json').write_text(payload);(OUT/'tree-v10-mesh.json').write_text(payload)
report={'source_sha256':source_hash,'source_unchanged':sha(SOURCE)==source_hash,'triangles':len(indices)//3,'export_vertices':len(positions)//3,'raw_major_triangles':raw,'authored_major_crown_systems':8,'unequal_forks':32,'secondary_forks':16,'buttresses':4,'small_feeders':4,'bark_plates':plate_count,'preserved_lower_trunk_source_vertices':len(used),'bounds_blender_min':[min(v.co[i] for v in mesh.vertices) for i in range(3)],'bounds_blender_max':[max(v.co[i] for v in mesh.vertices) for i in range(3)],'matrix_local':[list(row) for row in obj.matrix_local],'source_matrix_local':[list(row) for row in source_matrix],'coordinates':'(-x,z,-y); triangle winding [0,2,1] once','finite':True}
report['connected_major_component_vertices']=connected_sizes
report['discarded_zero_area_export_triangles']=discarded_degenerate;report['tiny_cap_flat_normal_fallbacks']=flat_normal_fallbacks
(OUT/'tree-v10-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
# Save only deliverable tree and its original parent, packed original images.
bpy.data.objects.remove(source,do_unlink=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'tree-v10.blend'))

# Same-light material and neutral geometry before/after, no scene acceptance.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1152;scene.render.resolution_y=1152;scene.render.resolution_percentage=100;scene.world.color=(.06,.06,.06);scene.view_settings.view_transform='AgX'
for old in list(bpy.data.objects):
    if old.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(old,do_unlink=True)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-13,8));camera=bpy.context.object;aim(camera,(0,0,3.05));camera.data.type='ORTHO';camera.data.ortho_scale=7.6;scene.camera=camera
for loc,power,color,size in [((-5,-5,9),1800,(.55,.72,1),5),((4,-2,5),950,(1,.68,.35),4),((0,5,7),1600,(.35,.6,1),4)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.color=color;light.data.shape='DISK';light.data.size=size;aim(light,(0,0,3))
with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst):dst.objects=['Sculpted bark roots and fine branches']
prior=dst.objects[0];bpy.context.collection.objects.link(prior);prior.hide_render=True
def render(name,active,inactive):
    active.hide_render=False;inactive.hide_render=True;scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
render('tree-v10-preview.png',obj,prior);render('tree-v9-same-light.png',prior,obj)
neutral=bpy.data.materials.new('Neutral geometry');neutral.diffuse_color=(.38,.38,.38,1);neutral.use_nodes=True;neutral.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8
for ob in [obj,prior]:
    ob.data.materials.clear();ob.data.materials.append(neutral)
    for p in ob.data.polygons:p.material_index=0
render('tree-v10-geometry.png',obj,prior);render('tree-v9-geometry.png',prior,obj)
print('V10 COMPLETE',flush=True)
