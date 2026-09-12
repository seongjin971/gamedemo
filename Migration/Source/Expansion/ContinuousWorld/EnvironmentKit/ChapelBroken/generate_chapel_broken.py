"""Camera-safe actual broken Gothic masonry. Staged exports only; no Unity writes."""
import bpy,bmesh,math,random,json,ast
from pathlib import Path
from mathutils import Vector,Euler
from mathutils.bvhtree import BVHTree
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];OUT=SOURCE/'staged';OUT.mkdir(parents=True,exist_ok=True);ATLAS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/WorldSurfaceAtlas.png'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for node in ast.parse((SOURCE.parent/'BridgeHero/generate_bridge_hero.py').read_text()).body:
    if isinstance(node,ast.FunctionDef) and node.name in {'mat','mesh','bevel','block'}:exec(compile(ast.Module(body=[node],type_ignores=[]),'<stable local masonry helpers>','exec'))
M=[mat('CW_ChapelStone',(.34,.36,.35)),mat('CW_ChapelStoneLight',(.42,.435,.40)),mat('CW_ChapelMortar',(.18,.20,.18)),mat('CW_WetMoss',(.11,.20,.065))]
for node in M[3].node_tree.nodes:
    if node.bl_idname=='ShaderNodeVectorMath' and node.operation=='ADD':node.inputs[1].default_value=(.004,.504,0)
assets=[];reports={}
def prism(name,points,y0,y1,slot=0):
    n=len(points);vs=[(x,y,z) for y in (y0,y1) for x,z in points];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh(name,vs,fs,slot)
def clip(ob,cutter):
    bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Actual irregular fractured silhouette','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name)
    return bool(ob.data.polygons)
def finish(name,parts,extra):
    for part in parts:
        for v in part.data.vertices:v.co.z=max(0,v.co.z)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name=name
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces),ngon_method='EAR_CLIP');bad=[f for f in bm.faces if f.calc_area()<1e-8]
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.validate(clean_customdata=False);ob.data.update();ob.data.calc_loop_triangles()
    report={'name':name,'triangles':len(ob.data.loop_triangles),'zero_area_triangles':sum(t.area<1e-10 for t in ob.data.loop_triangles),'bounds_source_xyz':[[min(v.co[i] for v in ob.data.vertices) for i in range(3)],[max(v.co[i] for v in ob.data.vertices) for i in range(3)]],'materials':[m.name for m in ob.data.materials],'uv':'0..1 individual stone UV0; parent WSA stone-quadrant ST. CW_WetMoss uses moss/soil quadrant via parent existing Moss slot.','pivot':'ground center; preserve original -90X FBX root via wrapper transform','source_axes':'X width, Y wall thickness, Z height, metres',**extra}
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',mesh_smooth_type='FACE',use_tspace=True,bake_anim=False)
    (SOURCE/(name+'-manifest.json')).write_text(json.dumps(report,indent=2));(OUT/(name+'-manifest.json')).write_text(json.dumps(report,indent=2));assets.append(ob);reports[name]=report;return ob
def moss_patch(center,width,height,axis,seed):
    rr=random.Random(seed);n=9;vs=[]
    for i in range(n):
        a=i*math.tau/n;rx=width*(.5+rr.uniform(-.09,.09));ry=height*(.5+rr.uniform(-.09,.09))
        if axis=='front':vs.append((center[0]+math.cos(a)*rx,center[1]+rr.uniform(-.003,.003),center[2]+math.sin(a)*ry))
        else:vs.append((center[0]+math.cos(a)*rx,center[1]+math.sin(a)*ry,center[2]+rr.uniform(0,.012)))
    vs.append(Vector(center));fs=[(i,(i+1)%n,n) for i in range(n)]
    if axis=='front' and center[1]>0:fs=[tuple(reversed(f)) for f in fs]
    return mesh('Moss in damp broken joints',vs,fs,3)

profile=[(-3,2.8),(-2.69,2.76),(-2.53,2.36),(-2.14,2.29),(-1.98,2.48),(-1.58,1.99),(-1.23,1.83),(-.96,1.94),(-.77,1.32),(-.35,1.36),(0,.78),(.48,.75),(.68,.99),(1.14,1.09),(1.45,1.27),(1.78,.91),(2.02,.88),(2.29,.72),(2.54,.84),(2.75,.61),(3,.30),(2.86,0),(-3,0)]
cutter=prism('Wall break profile cutter',profile,-1,1);parts=[];rng=random.Random(78344);body=[]
for row in range(10):
    z0=row*.30+.007;z1=(row+1)*.30-.008;x=-3;col=0
    while x<2.99:
        end=min(3,x+(.31 if row%2 and col==0 else rng.uniform(.49,.78)))
        ob=block('Bonded fractured ashlar',(x+.007,end-.007,-.285,.285,z0,z1),seed=912+row*80+col,slot=1 if rng.random()<.18 else 0,wear=.021,bev=.016)
        if clip(ob,cutter):parts.append(ob);body.append(ob)
        else:bpy.data.objects.remove(ob,do_unlink=True)
        x=end;col+=1
coreprofile=[(x,max(0,z-.027)) for x,z in profile]
core=prism('Recessed irregular mortar core',coreprofile,-.24,.24,2);parts.append(core)
# A true partial sill and broken jamb survive in the low wall; no miniature complete arch.
for bounds,seed in [((-.94,.54,-.30,.30,.55,.69),704),((-.97,-.81,-.30,.30,.69,1.73),705),((-.77,-.69,-.30,.30,.69,1.62),706)]:
    ob=block('Remaining carved lancet sill and jamb',bounds,seed,1,.013,.017)
    if clip(ob,cutter):parts.append(ob)
    else:bpy.data.objects.remove(ob,do_unlink=True)
# Original jamb-like molding at the taller fracture end anchors the abbey silhouette.
for x0,x1,y0,y1 in [(-2.83,-2.73,-.30,-.25),(-2.70,-2.63,-.30,-.24),(-2.58,-2.50,-.30,-.25)]:
    ob=block('Broken vertical molded wall rib',(x0,x1,y0,y1,.15,2.9),820,1,.004,.008)
    if clip(ob,cutter):parts.append(ob)
    else:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(cutter,do_unlink=True)
# Sparse damp moss hugs horizontal joints and the exposed low upper shelves.
for ob in body:
    bb=[v.co for v in ob.data.vertices];x0=min(v.x for v in bb);x1=max(v.x for v in bb);z0=min(v.z for v in bb);z1=max(v.z for v in bb)
    if rng.random()<.40:
        for sign in (-1,1):parts.append(moss_patch(((x0+x1)/2,sign*.287,z0+.010),min(.5,x1-x0)*rng.uniform(.4,.9),rng.uniform(.024,.062),'front',int((x0+8)*833+sign)))
# Low rubble toe fits inside the width; shallow depth remains explicit for parent placement.
for i in range(20):
    rr=random.Random(907+i*44);w=rr.uniform(.22,.46);d=rr.uniform(.18,.35);h=rr.uniform(.16,.29);x=rr.uniform(-2.72,2.70);y=rr.choice((-1,1))*rr.uniform(.32,.43)
    ob=block('Loose fallen wall foot stone',(-w/2,w/2,-d/2,d/2,-h/2,h/2),1700+i,0,.032,.023);rot=Euler((rr.uniform(-.23,.23),rr.uniform(-.35,.35),rr.uniform(-1.1,1.1))).to_matrix()
    for v in ob.data.vertices:v.co=rot@v.co+Vector((x,y,.12))
    lowest=min(v.co.z for v in ob.data.vertices)
    for v in ob.data.vertices:v.co.z-=lowest;v.co.x=max(-3,min(3,v.co.x));v.co.y=max(-.65,min(.65,v.co.y))
    parts.append(ob)
wall=finish('CW_ChapelBrokenWall6m',parts,{'wall_body_width':6,'wall_body_thickness':.6,'height_range': [.6,2.8],'broken_profile_xz':profile,'rubble_toe_depth_max':1.3,'opening':'no complete window arch; low wall with true broken silhouette and surviving sill/jamb fragments','placement_note':'Tall left end descends toward right; rotate/mirror placement if needed. Keep central walking gap between separate instances.'})

# Clustered Gothic pier: continuous engaged shafts and bonded core, genuinely fractured top.
parts=[];toppts=[(-.50,2.74),(-.31,2.78),(-.18,3.0),(-.035,2.86),(.11,2.87),(.25,2.63),(.40,2.70),(.5,2.54),(.5,0),(-.5,0)]
cutter=prism('Pier fracture cutter',toppts,-1,1)
for row in range(7):
    ob=block('Pier central weathered course',(-.25,.25,-.25,.25,.29+row*.38,.29+(row+1)*.38-.013),3100+row,0,.015,.012)
    if clip(ob,cutter):parts.append(ob)
    else:bpy.data.objects.remove(ob,do_unlink=True)
def shaft(cx,cy,rad,z0,z1,seed):
    rr=random.Random(seed);n=10;vs=[]
    for z in (z0,z1):
        for i in range(n):a=i*math.tau/n;vs.append((cx+math.cos(a)*rad,cy+math.sin(a)*rad,z+rr.uniform(-.004,.004)))
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh('Engaged Gothic column drum',vs,fs,1 if seed%6==0 else 0)
for k,(cx,cy,rad) in enumerate([(-.245,-.245,.105),(.245,-.245,.105),(.245,.245,.105),(-.245,.245,.105),(0,-.285,.09),(.285,0,.09),(0,.285,.09),(-.285,0,.09)]):
    for row in range(6):
        ob=shaft(cx,cy,rad,.34+row*.46,.34+(row+1)*.46-.012,491+k*31+row)
        if clip(ob,cutter):parts.append(ob)
        else:bpy.data.objects.remove(ob,do_unlink=True)
for width,z0,z1 in [(.88,0,.12),(.80,.12,.20),(.72,.20,.25),(.66,.25,.32),(.71,.32,.355)]:
    parts.append(block('Carved Gothic base molding',(-width/2,width/2,-width/2,width/2,z0,z1),4021,1,.009,.01))
for z in (1.05,2.02):
    parts.append(block('Narrow shaft binding collar',(-.365,.365,-.365,.365,z,z+.058),4130,1,.006,.009))
bpy.data.objects.remove(cutter,do_unlink=True)
for i in range(9):
    rr=random.Random(5299+i*21);a=rr.uniform(0,math.tau);w=rr.uniform(.14,.26);d=rr.uniform(.12,.24);h=rr.uniform(.10,.22);ob=block('Broken pier toe fragment',(-w/2,w/2,-d/2,d/2,0,h),5980+i,0,.016,.016);rot=Euler((0,0,a)).to_matrix()
    for v in ob.data.vertices:v.co=rot@v.co+Vector((math.cos(a)*.36,math.sin(a)*.36,0));v.co.x=max(-.5,min(.5,v.co.x));v.co.y=max(-.5,min(.5,v.co.y))
    parts.append(ob)
    if i%2==0:parts.append(moss_patch((math.cos(a)*.34,math.sin(a)*.34,h+.003),.18,.13,'top',5980+i))
for z in (.18,.345):parts.append(moss_patch((-.22,-.30,z+.004),.33,.13,'top',int(z*456)))
pier=finish('CW_ChapelBrokenPier3m',parts,{'height':3,'footprint_max':[1,1],'construction':'Bonded weathered central pier with eight engaged Gothic shaft fragments, carved base bands, an irregular fractured top, moss and rubble toe.'})
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'ChapelBroken.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.render.resolution_x=1500;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Wet abbey inspection');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.24,.29,.31,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.60
for pos,power,size in [((-6,-8,10),1800,7),((4,4,7),800,6)]:
    ld=bpy.data.lights.new('Abbey cloud light','AREA');ld.energy=power;ld.size=size;lo=bpy.data.objects.new('Abbey cloud light',ld);bpy.context.collection.objects.link(lo);lo.location=pos;lo.rotation_euler=(Vector((0,0,1))-lo.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Abbey inspection camera');cam=bpy.data.objects.new('Abbey inspection camera',cd);bpy.context.collection.objects.link(cam);cd.type='ORTHO';scene.camera=cam;scene.view_settings.view_transform='AgX'
for ob in assets:
    for other in assets:other.hide_render=other!=ob
    cam.location=(8,-12,7) if ob==wall else (5,-8,4.8);cam.rotation_euler=(Vector((0,0,1.25 if ob==wall else 1.5))-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=7.4 if ob==wall else 4.8;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/(ob.name+'-preview.png'));bpy.ops.render.render(write_still=True)
print('CHAPEL_BROKEN_STAGED_COMPLETE')
