"""Flat 14 m hero bridge with staggered mixed-size paving and real arched soffit.
Blender XYZ = width/length/up, metres; preserve exported FBX X=-90 conversion.
"""
import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5]
OUT=SOURCE/'staged';OUT.mkdir(parents=True,exist_ok=True)
ATLAS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/WorldSurfaceAtlas.png'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.88
    if ATLAS.exists():
        tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ATLAS),check_existing=True)
        uv=nt.nodes.new('ShaderNodeTexCoord');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.492,.492,1)
        shift=nt.nodes.new('ShaderNodeVectorMath');shift.operation='ADD';shift.inputs[1].default_value=(.504,.504,0)
        nt.links.new(uv.outputs['UV'],scale.inputs[0]);nt.links.new(scale.outputs['Vector'],shift.inputs[0]);nt.links.new(shift.outputs['Vector'],tx.inputs['Vector'])
        mult=nt.nodes.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[2].default_value=(*[c/.40 for c in color],1)
        nt.links.new(tx.outputs['Color'],mult.inputs[1]);nt.links.new(mult.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.065;bump.inputs['Distance'].default_value=.016;nt.links.new(tx.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    else:bs.inputs['Base Color'].default_value=(*color,1)
    return m
M=[mat('CW_BridgeStone',(.40,.39,.345)),mat('CW_BridgeStoneLight',(.44,.425,.37)),mat('CW_BridgeMortar',(.22,.225,.20))]
objects=[];paving=[]

def mesh(name,vs,fs,slot=0,unwrap=True):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(M[slot])
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    if unwrap:
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
    return ob

def bevel(ob,width=.018,segments=1):
    bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Chipped weathered arris','BEVEL');mod.width=width;mod.segments=segments;bpy.ops.object.modifier_apply(modifier=mod.name)

def block(name,bounds,seed,slot=0,wear=.018,bev=.018):
    x0,x1,y0,y1,z0,z1=bounds;r=random.Random(seed);vs=[]
    for x,y,z in [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]:
        vs.append((min(x1,max(x0,x+r.uniform(-wear,wear))),min(y1,max(y0,y+r.uniform(-wear,wear))),min(z1,max(z0,z+r.uniform(-wear,wear)))))
    ob=mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],slot);bevel(ob,bev);return ob

def slab(x0,x1,y0,y1,seed):
    r=random.Random(seed);w=x1-x0;l=y1-y0;cuts=[r.uniform(.028,.095) for _ in range(4)]
    # Eight broken corners plus irregular edge nicks, all confined to the original cell.
    p=[(x0+cuts[0],y0),(x1-cuts[1],y0),(x1,y0+cuts[1]),(x1,y1-cuts[2]),(x1-cuts[2],y1),(x0+cuts[3],y1),(x0,y1-cuts[3]),(x0,y0+cuts[0])]
    if seed%3==0:
        p.insert(3,(x1-r.uniform(.018,.045),y0+l*.53))
    center=Vector(((x0+x1)/2,(y0+y1)/2));vs=[];n=len(p)
    for level in range(3):
        for x,y in p:
            q=Vector((x,y));z=-.16 if level==0 else (-.022 if level==1 else r.uniform(-.003,.004))
            if level==2:q=q.lerp(center,.025)
            vs.append((q.x,q.y,z))
    vs.append((center.x+r.uniform(-.05,.05),center.y+r.uniform(-.05,.05),r.uniform(.001,.008)))
    fs=[tuple(reversed(range(n)))]
    for layer in range(2):
        for i in range(n):a=layer*n+i;b=layer*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    fs.extend((2*n+i,2*n+(i+1)%n,3*n) for i in range(n))
    ob=mesh('Irregular broad flagstone',vs,fs,1 if seed%5==0 else 0,False)
    uv=ob.data.uv_layers.new(name='UVMap');turn=seed%4
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co;u=(v.x-x0)/w;v2=(v.y-y0)/l
            for _ in range(turn):u,v2=v2,1-u
            uv.data[li].uv=(.25+.46*u,.25+.46*v2)
    return ob

# Mixed-size rectangular bonding on a fine planning grid. No continuous plank rows.
r=random.Random(2941);used=set();nx,ny=8,24;slab_rects=[]
for row in range(ny):
    for col in range(nx):
        if (col,row) in used:continue
        candidates=[(2,2),(3,2),(2,3),(3,3),(2,4),(3,2),(2,2),(1,2)]
        r.shuffle(candidates);candidates.extend([(1,1)])
        for cw,ch in candidates:
            if col+cw<=nx and row+ch<=ny and all((x,y) not in used for x in range(col,col+cw) for y in range(row,row+ch)):break
        used.update((x,y) for x in range(col,col+cw) for y in range(row,row+ch))
        x0=-2.6+col*.65+.010;x1=-2.6+(col+cw)*.65-.010;y0=-7+row*(14/24)+.010;y1=-7+(row+ch)*(14/24)-.010
        ob=slab(x0,x1,y0,y1,2941+row*61+col);objects.append(ob);paving.append(ob);slab_rects.append([x0,x1,y0,y1])
# Recessed continuous deck core: purely visual, parent owns smooth walking collider.
objects.append(block('Recessed continuous deck',(-2.62,2.62,-7,7,-.16,-.032),123,2,0,.009))

def arch(t,outer=False):
    a=-math.pi/2+math.pi*t;return ((6.68 if outer else 6.4)*math.sin(a),-3.0+(2.99 if outer else 2.82)*math.cos(a))
def extrude_yz(name,points,x0,x1,slot=0):
    n=len(points);vs=[(x,y,z) for x in (x0,x1) for y,z in points];fs=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,slot)

# One continuous real barrel vault, recessed behind the radial face voussoirs.
lower=[(arch(i/48)[0],arch(i/48)[1]+.018) for i in range(49)]
core=extrude_yz('Continuous arched vault core',lower+[(6.4,-.15),(-6.4,-.15)],-3.14,3.14,2);objects.append(core)
for sign in (-1,1):
    a0,a1=sorted((sign*2.62,sign*3.25))
    for k in range(26):
        t0=(k+.008)/26;t1=(k+1-.008)/26
        p=[arch(t0),arch(t1),arch(t1,True),arch(t0,True)]
        ob=extrude_yz('Radial voussoir',p,a0,a1,1 if k%6==0 else 0);bevel(ob,.011);objects.append(ob)
    # Spandrel ashlar: trim each piece against the arch extrados before joining.
    cutpoints=[(-7,-3),(7,-3),(7,-3.0),(6.68,-3.0)]+[arch(i/40,True) for i in reversed(range(41))]+[(-7,-3.0)]
    cutter=extrude_yz('Spandrel cutter',cutpoints,-4,4,2)
    y=-7;row=0
    while row<9:
        z0=-3.0+row*.33+.006;z1=z0+.318;y=-7;col=0
        while y<6.99:
            length=(.55 if row%2 and col==0 else r.uniform(.84,1.25));end=min(7,y+length)
            ob=block('Fitted spandrel course',(a0+.012,a1-.035,y+.008,end-.008,z0,z1),seed=sign*33+row*111+col,slot=0)
            bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Cut to actual arch extrados','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name)
            if len(ob.data.polygons):objects.append(ob)
            else:bpy.data.objects.remove(ob,do_unlink=True)
            y=end;col+=1
        row+=1
    bpy.data.objects.remove(cutter,do_unlink=True)
    # Thick parapets: genuinely bonded courses and oversized individual coping stones.
    wallx0,wallx1=sorted((sign*2.66,sign*3.20))
    for row in range(3):
        y=-7;col=0
        while y<6.99:
            length=(.40 if row%2 and col==0 else r.uniform(.72,1.06));end=min(7,y+length)
            objects.append(block('Bonded parapet course',(wallx0,wallx1,y+.008,end-.008,row*.285+.01,(row+1)*.285-.01),2201+row*76+col,1 if col%9==0 else 0))
            y=end;col+=1
    # Recessed dark core prevents daylight leaking through mortar joints.
    objects.append(block('Parapet mortar core',(wallx0+.025,wallx1-.025,-7,7,-.02,.825),seed=80,slot=2,wear=0,bev=.004))
    y=-7;col=0
    while y<6.99:
        end=min(7,y+r.uniform(.75,1.05));objects.append(block('Heavy worn coping',(a0,a1,y+.007,end-.007,.84,1.015+r.uniform(-.007,.005)),371+col,1,.016,.028));y=end;col+=1
    # Stout end piers remain completely outside the 5.2 m walking clear width.
    for endsign in (-1,1):
        cy=endsign*6.67;y0=max(-7,cy-.33);y1=min(7,cy+.33)
        for row in range(4):
            objects.append(block('Terminal pier ashlar',(a0+.025,a1-.025,y0+.012,y1-.012,row*.30,(row+1)*.30-.012),410+row+endsign,0,.015))
        objects.append(block('Terminal pier cap',(a0,a1,y0,y1,1.19,1.34),410+endsign,1,.014,.025))
# Full-width bank abutments anchor the ends, preserving the actual central opening.
for y0,y1 in [(-7,-6.4),(6.4,7)]:objects.append(block('Bank abutment core',(-3.14,3.14,y0,y1,-3.02,-.17),seed=int(y0*99),slot=2,wear=0,bev=.008))

deck_max=max(v.co.z for ob in paving for v in ob.data.vertices)
bpy.ops.object.select_all(action='DESELECT')
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bridge=objects[0];bridge.name='CW_StoneBridgeHeroV3_14m'
bm=bmesh.new();bm.from_mesh(bridge.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='EAR_CLIP')
bad=[f for f in bm.faces if f.calc_area()<1e-10]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(bridge.data);bm.free();bridge.data.validate(clean_customdata=False);bridge.data.update();bridge.data.calc_loop_triangles()
bvh=BVHTree.FromPolygons([v.co for v in bridge.data.vertices],[list(p.vertices) for p in bridge.data.polygons],all_triangles=True)
under=[]
for y in (-4,-2,0,2,4):
    crown=-3.0+2.82*math.sqrt(1-(y/6.4)**2)
    for dz in (-.15,-.4):
        z=crown+dz;under.append({'length_axis':y,'height':z,'clear':bvh.ray_cast(Vector((-4,y,z)),Vector((1,0,0)),8)[0] is None})
walk=[]
for x in (-2.4,-1.2,0,1.2,2.4):
    for y in (-6.8,-5,-3,-1,1,3,5,6.8):
        hit=bvh.ray_cast(Vector((x,y,.2)),Vector((0,0,-1)),.5)[0];walk.append({'x':x,'length_axis':y,'surface_height':None if hit is None else hit.z,'safe':hit is not None and -.05<=hit.z<=.015})
manifest={'name':bridge.name,'length':14,'arch_clear_span':12.8,'arch_crown_below_deck':.18,'arch_spring_below_deck':3.0,'clear_width':5.2,'full_width':6.5,'deck_max_height':deck_max,'walking_top_contract':'0 nominal; all paving <= +0.008, no steps; parent smooth collider',
 'bounds_source_xyz':[[min(v.co[i] for v in bridge.data.vertices) for i in range(3)],[max(v.co[i] for v in bridge.data.vertices) for i in range(3)]],
 'source_axes':'X width, Y length, Z up','fbx_axes':'Y-up/-Z-forward; root X=-90 degrees MUST be preserved by wrapper placement','pivot':'deck center at nominal height0',
 'triangles':len(bridge.data.loop_triangles),'zero_area_triangles':sum(t.area<1e-10 for t in bridge.data.loop_triangles),'stone_slabs':len(slab_rects),
 'uv':'each stone UV0 within0..1; parent may map to stone atlas quadrant via material ST','materials':[m.name for m in bridge.data.materials],
 'arch_open_ray_checks':under,'arch_all_clear':all(x['clear'] for x in under),'walking_ray_checks':walk,'walking_all_safe':all(x['safe'] for x in walk)}
assert manifest['triangles']<30000,manifest['triangles']
assert manifest['arch_all_clear'] and manifest['walking_all_safe'],manifest
bpy.ops.export_scene.fbx(filepath=str(OUT/(bridge.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',mesh_smooth_type='FACE',use_tspace=True,bake_anim=False)
(SOURCE/'structural-manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'StoneBridgeHeroV3_14m.blend'))

print("STRUCTURAL_BRIDGE_V3_STAGED_COMPLETE", manifest["triangles"])
