"""Additive fractured abbey rubble; export to staged, never directly to Assets."""
import bpy,bmesh,math,random,json,ast
from pathlib import Path
from mathutils import Vector,Euler
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];OUT=SOURCE/'staged';OUT.mkdir(parents=True,exist_ok=True)
ATLAS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/WorldSurfaceAtlas.png'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for node in ast.parse((SOURCE.parent/'BridgeHero/generate_bridge_hero.py').read_text()).body:
    if isinstance(node,ast.FunctionDef) and node.name in {'mat','mesh','bevel'}:exec(compile(ast.Module(body=[node],type_ignores=[]),'<stable helpers>','exec'))
M=[mat('ChapelRubbleStone',(.24,.26,.25)),mat('ChapelMoss',(.105,.16,.055))]
# Preview uses the quieter generated limestone; parent owns runtime binding.
stone_map=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/LimestoneSurface.png'
for node in M[0].node_tree.nodes:
    if node.bl_idname=='ShaderNodeTexImage' and stone_map.exists():node.image=bpy.data.images.load(str(stone_map),check_existing=True)
    if node.bl_idname=='ShaderNodeVectorMath' and node.operation=='MULTIPLY':node.inputs[1].default_value=(1,1,1)
    if node.bl_idname=='ShaderNodeVectorMath' and node.operation=='ADD':node.inputs[1].default_value=(0,0,0)
for node in M[1].node_tree.nodes:
    if node.bl_idname=='ShaderNodeVectorMath' and node.operation=='ADD':node.inputs[1].default_value=(.004,.504,0)
assets=[];reports={}
def clip_polyhedron(faces,normal,d):
    """Intersect convex planar polygon faces with a plane; build sorted cap explicitly."""
    n=Vector(normal).normalized();new=[];cross=[]
    for face in faces:
        p=[]
        for a,b in zip(face,face[1:]+face[:1]):
            da=a.dot(n)-d;db=b.dot(n)-d
            if da<=1e-8:p.append(a)
            if (da<0 and db>0) or (da>0 and db<0):
                q=a+(b-a)*(da/(da-db));p.append(q);cross.append(q)
        if len(p)>=3:new.append(p)
    unique=[]
    for p in cross:
        if not any((p-q).length<1e-6 for q in unique):unique.append(p)
    if len(unique)>=3:
        center=sum(unique,Vector())/len(unique);u=n.cross(Vector((0,0,1)))
        if u.length<.1:u=n.cross(Vector((0,1,0)))
        u.normalize();v=n.cross(u);unique.sort(key=lambda p:math.atan2((p-center).dot(v),(p-center).dot(u)));new.append(unique)
    return new
def moss_on_face(ob,poly,rr):
    coords=[ob.data.vertices[i].co.copy() for i in poly.vertices];center=sum(coords,Vector())/len(coords);normal=poly.normal.copy();u=(coords[0]-center).normalized();v=normal.cross(u).normalized()
    # Connected angular growth reaches a chosen facet edge/crevice, never isolated circular spots.
    toward=(coords[rr.randrange(len(coords))]-center).normalized();limit=rr.uniform(.02,.20)*max((p-center).length for p in coords);boundary=[]
    for a,b in zip(coords,coords[1:]+coords[:1]):
        da=(a-center).dot(toward)-limit;db=(b-center).dot(toward)-limit
        if da>=0:boundary.append(a)
        if da*db<0:boundary.append(a+(b-a)*(da/(da-db)))
    if len(boundary)<3:return None
    patchcenter=sum(boundary,Vector())/len(boundary);edge=[]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):
        for k in range(3):edge.append((a+(b-a)*(k/3)).lerp(patchcenter,rr.uniform(.035,.20)))
    n=len(edge);vs=[patchcenter+normal*.015];rings=[]
    for ring in (.48,1):
        ids=[]
        for p in edge:
            ids.append(len(vs));vs.append(patchcenter.lerp(p,ring)+normal*rr.uniform(.002,.018)*(1-ring*.55))
        rings.append(ids)
    fs=[(0,rings[0][i],rings[0][(i+1)%n]) for i in range(n)]
    for i in range(n):fs.append((rings[0][i],rings[1][i],rings[1][(i+1)%n],rings[0][(i+1)%n]))
    return mesh('Moss cushion on upward fracture',vs,fs,1)
def chunk(position,size,seed,tilt=.4,moss_chance=.53):
    rr=random.Random(seed);w,d,h=size
    vs=[Vector((x,y,z)) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces=[[vs[i] for i in f] for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]
    # Large planar fractures remove corners; additional shallow chips break repeated box silhouettes.
    for k in range(rr.randint(5,8)):
        n=Vector((rr.choice((-1,1))*rr.uniform(.3,1),rr.choice((-1,1))*rr.uniform(.3,1),rr.uniform(-.85,.9))).normalized()
        faces=clip_polyhedron(faces,n,rr.uniform(.85,1.17))
    faces=clip_polyhedron(faces,Vector((rr.uniform(-.32,.32),rr.uniform(-.25,.25),1)),rr.uniform(.69,.92))
    verts=[];fs=[]
    for face in faces:
        ids=[]
        for p in face:
            match=next((i for i,q in enumerate(verts) if (p-q).length<1e-6),None)
            if match is None:match=len(verts);verts.append(p)
            ids.append(match)
        fs.append(ids)
    rot=Euler((rr.uniform(-tilt,tilt),rr.uniform(-tilt,tilt),rr.uniform(-math.pi,math.pi))).to_matrix()
    verts=[rot@Vector((p.x*w/2,p.y*d/2,p.z*h/2)) for p in verts];zmin=min(p.z for p in verts)
    verts=[p+Vector((position[0],position[1],position[2]-zmin)) for p in verts]
    ob=mesh('Individually fractured limestone chunk',verts,fs,0);bevel(ob,min(w,d,h)*rr.uniform(.025,.053),1)
    parts=[ob];ob.data.update()
    for poly in list(ob.data.polygons):
        if poly.normal.z>.56 and poly.area>.005 and rr.random()<moss_chance:
            m=moss_on_face(ob,poly,rr)
            if m:parts.append(m)
    return parts
def finish(name,parts,construction):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name=name
    bb=[[min(v.co[i] for v in ob.data.vertices) for i in range(3)],[max(v.co[i] for v in ob.data.vertices) for i in range(3)]];width=6 if 'Strip' in name else 3;center=[(bb[0][i]+bb[1][i])*.5 for i in range(2)];zs=min(1,.55/(bb[1][2]-bb[0][2])) if 'Strip' in name else 1
    for v in ob.data.vertices:v.co.x=(v.co.x-center[0])*width/(bb[1][0]-bb[0][0]);v.co.y-=center[1];v.co.z=(v.co.z-bb[0][2])*zs
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces),ngon_method='EAR_CLIP');bad=[f for f in bm.faces if f.calc_area()<1e-9]
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.validate(clean_customdata=False);ob.data.update();ob.data.calc_loop_triangles()
    bounds=[[min(v.co[i] for v in ob.data.vertices) for i in range(3)],[max(v.co[i] for v in ob.data.vertices) for i in range(3)]]
    report={'name':name,'triangles':len(ob.data.loop_triangles),'zero_area_triangles':sum(t.area<1e-10 for t in ob.data.loop_triangles),'bounds_source_xyz':bounds,'bounds_unity_width_height_depth':[bounds[1][0]-bounds[0][0],bounds[1][2]-bounds[0][2],bounds[1][1]-bounds[0][1]],'materials':[m.name for m in ob.data.materials],'uv':'UV0 0..1 per chunk. ChapelRubbleStone: parent atlas stone quadrant ST OR full LimestoneSurface. ChapelMoss: parent supplied moss material; UV0 0..1.','pivot':'ground center; Blender X width Y depth Z up in metres. FBX root -90 degrees X; preserve root in wrapper.','construction':construction,'physics':'Decorative only. Parent owns walking collision and keeps path clear.'}
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',mesh_smooth_type='FACE',use_tspace=True,bake_anim=False)
    (OUT/(name+'-manifest.json')).write_text(json.dumps(report,indent=2));(SOURCE/(name+'-manifest.json')).write_text(json.dumps(report,indent=2));assets.append(ob);reports[name]=report
    return ob
# Broad broken pieces form offset overlapping pockets, with a sparse chip feather at the walk-facing edge.
parts=[];rr=random.Random(28109)
for i in range(79):
    x=rr.uniform(-2.65,2.65);y=rr.uniform(-.30,.30)+.1*math.sin(x*2.2);w=rr.uniform(.26,.65);d=rr.uniform(.22,.49);h=rr.uniform(.13,.31)
    base=.14 if i%9==0 and abs(y)<.22 else rr.uniform(0,.07)
    parts+=chunk((x,y,base),(w,d,h),11309+i*41,tilt=.28)
for i in range(57):
    x=rr.uniform(-2.86,2.86);y=rr.choice((-1,1))*rr.uniform(.31,.58);w=rr.uniform(.12,.26)
    parts+=chunk((x,y,0),(w,rr.uniform(.10,.23),rr.uniform(.05,.15)),81309+i*41,tilt=.45,moss_chance=.35)
strip=finish('CW_AbbeyRubbleStrip6m',parts,'136 distinct plane-clipped angular limestone chunks with chamfered fracture arrises, irregular low overlapping pockets and smaller peripheral chips; small moss cushions hug selected upward facets, leaving most broken stone exposed.')
# Loose compact mound with large lower fragments, shallow middle crown and fine outer offcuts.
parts=[];rr=random.Random(87442)
for i in range(91):
    a=rr.uniform(0,math.tau);rad=math.sqrt(rr.random());x=math.cos(a)*rad*1.19;y=math.sin(a)*rad*.78;w=rr.uniform(.22,.65);d=rr.uniform(.17,.47);h=rr.uniform(.13,.33)
    base=max(0,.34*(1-rad)**.7+rr.uniform(-.06,.07))
    parts+=chunk((x,y,base),(w,d,h),57319+i*37,tilt=.42)
for i in range(33):
    a=rr.uniform(0,math.tau);rad=rr.uniform(.82,1);w=rr.uniform(.12,.25)
    parts+=chunk((math.cos(a)*rad*1.32,math.sin(a)*rad*.91,0),(w,w*rr.uniform(.55,.9),w*.45),88391+i*31,tilt=.5,moss_chance=.25)
mound=finish('CW_AbbeyRubbleMound3m',parts,'124 distinct angular fragments in a shallow scattered mound. No smooth balls, regular brick grid, or all-green rock surfaces.')
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'AbbeyRubbleV2.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=28;scene.render.resolution_x=1350;scene.render.resolution_y=900;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Overcast abbey');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.29,.34,.36,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
for pos,power,size in [((-4,-5,9),1100,6),((4,5,6),450,5)]:
    ld=bpy.data.lights.new('Cloud lighting','AREA');ld.energy=power;ld.size=size;lo=bpy.data.objects.new('Cloud lighting',ld);bpy.context.collection.objects.link(lo);lo.location=pos;lo.rotation_euler=(Vector((0,0,0))-lo.location).to_track_quat('-Z','Y').to_euler()
groundmat=bpy.data.materials.new('Preview damp ground');groundmat.diffuse_color=(.11,.125,.105,1);groundmat.use_nodes=True;groundmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.11,.125,.105,1);groundmat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.013));ground=bpy.context.object;ground.data.materials.append(groundmat)
cd=bpy.data.cameras.new('Inspection');cam=bpy.data.objects.new('Inspection',cd);bpy.context.collection.objects.link(cam);cd.type='ORTHO';scene.camera=cam;scene.view_settings.view_transform='AgX'
for ob in assets:
    for other in assets:other.hide_render=other!=ob
    cam.location=(5,-8,7);cam.rotation_euler=(Vector((0,0,.17))-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=6.8 if ob==strip else 4.0;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/(ob.name+'-preview.png'));bpy.ops.render.render(write_still=True)
print('ABBEY_RUBBLE_STAGED_COMPLETE '+json.dumps({k: {'triangles':v['triangles'],'bounds':v['bounds_source_xyz']} for k,v in reports.items()}))
