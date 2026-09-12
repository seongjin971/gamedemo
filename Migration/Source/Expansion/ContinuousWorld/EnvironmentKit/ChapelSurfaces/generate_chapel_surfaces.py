"""Additive chapel surfaces. Source X=width/Y=length/Z=up, metres."""
import bpy,bmesh,math,random,json,ast
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/ChapelSurfaces';OUT.mkdir(parents=True,exist_ok=True)
ATLAS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/WorldSurfaceAtlas.png'
# Reuse only stable local construction helpers, never execute or modify the prior asset generator.
helper=ast.parse((SOURCE.parent/'BridgeHero/generate_bridge_hero.py').read_text())
for node in helper.body:
    if isinstance(node,ast.FunctionDef) and node.name in {'mat','mesh','bevel','block','slab'}:exec(compile(ast.Module(body=[node],type_ignores=[]),'<local construction helper>','exec'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M=[mat('CW_ChapelPavingStone',(.39,.385,.35)),mat('CW_ChapelPavingStoneLight',(.43,.42,.38)),mat('CW_ChapelJointShadow',(.19,.195,.18)),mat('CW_ChapelRoofSlate',(.14,.165,.175)),mat('CW_ChapelRoofSlateLight',(.19,.21,.215)),mat('CW_ChapelRoofTimber',(.115,.080,.057))]
for m in [M[5]]:
    for node in m.node_tree.nodes:
        if node.bl_idname=='ShaderNodeVectorMath' and node.operation=='ADD':node.inputs[1].default_value=(.004,.004,0)
assets=[];manifests={}
def finish(name,parts,extra):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name=name
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='EAR_CLIP');bad=[f for f in bm.faces if f.calc_area()<1e-8]
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.validate(clean_customdata=False);ob.data.update();ob.data.calc_loop_triangles()
    bounds=[[min(v.co[i] for v in ob.data.vertices) for i in range(3)],[max(v.co[i] for v in ob.data.vertices) for i in range(3)]]
    manifest={'name':name,'bounds_source_xyz':bounds,'triangles':len(ob.data.loop_triangles),'zero_area_triangles':sum(t.area<1e-10 for t in ob.data.loop_triangles),'materials':[m.name for m in ob.data.materials],'source_axes':'X width/Y length/Z up, metres','fbx_axes':'Y-up/-Z-forward; preserve root X=-90 degree conversion via world wrapper','uv':'0..1 UV0 per stone/slate/timber; apply parent atlas ST per material',**extra}
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False)
    (SOURCE/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2));(OUT/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2));assets.append(ob);manifests[name]=manifest;return ob

# Four irregular running-bond courses, each with different broad slab widths.
r=random.Random(61983);parts=[];rects=[]
rows=[-2,-1.09,-.13,.91,2]
cuts=[[-2,-.94,.16,1.13,2],[-2,-1.33,-.29,.83,2],[-2,-.81,.29,1.20,2],[-2,-1.25,-.12,.87,2]]
for j in range(4):
    for i in range(4):
        bounds=[cuts[j][i]+.012,cuts[j][i+1]-.012,rows[j]+.012,rows[j+1]-.012];ob=slab(*bounds,seed=1831+j*79+i)
        # All top-course vertices are safe at or above nominal zero, below +.008.
        for v in ob.data.vertices:
            if v.co.z>-.01:v.co.z=max(0,min(.008,v.co.z+.003))
        parts.append(ob);rects.append(bounds)
parts.append(block('Paving recessed mortar',(-2,2,-2,2,-.18,-.032),19,2,0,.004))
paving=finish('CW_ChapelPaving4m',parts,{'slab_count':16,'pivot':'nominal walking surface center, top0..+.008; parent owns collider','size_xz_unity':[4,4],'paving_cells_xy':rects})

# Roof surfaces follow continuous slope. The final short end is deliberately torn back.
def roofheight(x):return 2.32-.80*abs(x)
def end_y(x):return 3.16+.65*(.5+.5*math.sin(x*2.7+.4))
def roofpiece(name,x0,x1,y0,y1,seed,slot=3,thickness=.065):
    rr=random.Random(seed);c=[rr.uniform(.018,.055) for _ in range(4)];points=[(x0+c[0],y0),(x1-c[1],y0),(x1,y0+c[1]),(x1,y1-c[2]),(x1-c[2],y1),(x0+c[3],y1),(x0,y1-c[3]),(x0,y0+c[0])]
    lift=.045+rr.uniform(0,.014);vs=[]
    for bottom in (True,False):
        for x,y in points:vs.append((x,y,roofheight(x)+lift-(thickness if bottom else 0)))
    n=len(points);fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)]
    ob=mesh(name,vs,fs,slot);bevel(ob,.005,1);return ob
parts=[]
for sign in (-1,1):
    xs=[sign*3,sign*2.4,sign*1.8,sign*1.2,sign*.6,0]
    # Watertight thickness below the slate; ray checks exclude intentional torn end.
    outline=[(xs[0],-4),(xs[-1],-4)]+[(x,end_y(x)) for x in reversed(xs)]
    n=len(outline);vs=[(x,y,roofheight(x)-drop) for drop in (.12,0) for x,y in outline];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)]
    parts.append(mesh('Continuous pitched roof boarding',vs,fs,5))
    # Courses overlap down slope, with independent chipped slate heads and staggered joints.
    for course in range(7):
        near=course*3/7;far=min(3,(course+1)*3/7+.045);x0,x1=sorted((sign*near,sign*far));y=-4;col=0
        while y<3.8:
            width=(.31 if course%2 and col==0 else r.uniform(.57,.77));end=min(4,y+width);maxend=min(end_y(x0),end_y(x1))+.12
            if y>=maxend-.001:break
            end=min(end,maxend)
            if end-y>.12:parts.append(roofpiece('Individual chipped slate tile',x0+.005,x1-.005,y+.005,end-.005,2401+course*83+col,4 if (course+col)%6==0 else 3))
            y=end;col+=1

def beam(name,p0,p1,width,depth,seed):
    p0,p1=Vector(p0),Vector(p1);direction=p1-p0;ob=block(name,(-width/2,width/2,-depth/2,depth/2,0,direction.length),seed,5,.012,.009)
    rot=direction.to_track_quat('Z','Y').to_matrix()
    for v in ob.data.vertices:v.co=rot@v.co+p0
    return ob
for y in (-3.85,-2.4,-.8,.8,2.35,3.12):
    for sign in (-1,1):parts.append(beam('Exposed principal rafter',(sign*2.95,y,-.19),(0,y,2.20),.19,.21,int(y*30)+sign))
    if y in (-3.85,-.8,2.35):
        parts.append(beam('Heavy horizontal tie beam',(-2.94,y,-.16),(2.94,y,-.16),.22,.22,int(y*97)))
        parts.append(beam('Roof king post',(0,y,-.05),(0,y,2.20),.15,.15,int(y*61)))
for sign in (-1,1):
    parts.append(beam('Long exposed eave beam',(sign*2.88,-4,-.13),(sign*2.88,4,-.13),.22,.22,84+sign))
    for x in (sign*1.0,sign*2.1):parts.append(beam('Long underside purlin',(x,-4,roofheight(x)-.20),(x,end_y(x),roofheight(x)-.20),.13,.16,int(x*28)))
parts.append(beam('Exposed ridge beam',(0,-4,2.18),(0,3.86,2.18),.17,.20,621))
# Narrow jointed ridge caps are modeled as angular slate moldings, never above +2.4.
y=-4;k=0
while y<3.6:
    yy=min(3.72,y+.56);p=[(-.18,2.235),(-.125,2.31),(-.07,2.38),(0,2.4),(.07,2.38),(.125,2.31),(.18,2.235),(.12,2.24),(0,2.33),(-.12,2.24)];n=len(p)
    vs=[(x,length,z) for length in (y+.008,yy-.008) for x,z in p];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];parts.append(mesh('Individual pointed ridge cap',vs,fs,4));y=yy;k+=1
for ob in parts:
    for v in ob.data.vertices:v.co.x=max(-3,min(3,v.co.x))
roof=finish('CW_ChapelBrokenSlateRoof6x8m',parts,{'pivot':'eave/wall top height0, center X/Y; ridge+2.4','nominal_full_width':6,'nominal_full_length':8,'broken_end':'positive sourceY / converted Unity length axis; last .2.. .85m torn back','rain_surface':'continuous pitched underlayer across x +/-2.9, length -3.9..3.0; parent raycast collider may use actual mesh','stone_slate_ST':'WSA top-right','timber_ST':'WSA bottom-left'})

# Offcut rubble, sized as one small reusable pile with irregular block rotations.
parts=[]
for i in range(18):
    rr=random.Random(728+i*47);w=rr.uniform(.35,.81);d=rr.uniform(.3,.66);h=rr.uniform(.24,.41);x=rr.uniform(-1.03,1.03);y=rr.uniform(-.65,.65);z=(.12 if i<11 else .38)+rr.uniform(-.04,.10)
    ob=block('Weathered fallen masonry',(-w/2,w/2,-d/2,d/2,-h/2,h/2),seed=i*18,slot=1 if i%4==0 else 0,wear=.045,bev=.035)
    from mathutils import Euler
    rot=Euler((rr.uniform(-.4,.4),rr.uniform(-.4,.4),rr.uniform(-math.pi,math.pi))).to_matrix()
    for v in ob.data.vertices:v.co=rot@v.co+Vector((x,y,z))
    parts.append(ob)
vs=[v.co for ob in parts for v in ob.data.vertices];lo=Vector([min(v[i] for v in vs) for i in range(3)]);hi=Vector([max(v[i] for v in vs) for i in range(3)]);mid=(lo+hi)*.5
for ob in parts:
    for v in ob.data.vertices:v.co=Vector(((v.co.x-mid.x)*3/(hi.x-lo.x),(v.co.y-mid.y)*2/(hi.y-lo.y),(v.co.z-lo.z)*.95/(hi.z-lo.z)))
rubble=finish('CW_ChapelRubblePile3m',parts,{'pivot':'ground center','overall_size':[3,2,.95],'blocks':18})

bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'ChapelSurfaces.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Chapel surfaces inspection');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.32,.38,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
for pos,power,size in [((-6,-8,13),2400,9),((4,4,9),1300,7)]:
    ld=bpy.data.lights.new('Surface softbox','AREA');ld.energy=power;ld.size=size;ob=bpy.data.objects.new('Surface softbox',ld);bpy.context.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Surface camera');cam=bpy.data.objects.new('Surface camera',cd);bpy.context.collection.objects.link(cam);cd.type='ORTHO';scene.camera=cam;scene.view_settings.view_transform='AgX'
for ob in assets:
    for other in assets:other.hide_render=other!=ob
    center=Vector((0,0,1 if ob==roof else .1));cam.location=(10,13,11) if ob==roof else (6,-8,10);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=11 if ob==roof else (6 if ob==paving else 4.5)
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/(ob.name+'-preview.png'));bpy.ops.render.render(write_still=True)
print('CHAPEL_SURFACES_COMPLETE')
