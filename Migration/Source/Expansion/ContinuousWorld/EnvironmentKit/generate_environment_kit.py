"""Reproducible authored environment meshes for the additive ContinuousWorld.

Run Blender --background --python this_file.py. No external downloads, no Unity API.
Coordinates in source: metres, +Z up, +Y bridge length. FBX: -Z forward, +Y up.
"""
import bpy, bmesh, math, random, json
from pathlib import Path
from mathutils import Vector
from mathutils.noise import noise_vector

ROOT = Path(__file__).resolve().parents[5]
SOURCE = Path(__file__).resolve().parent
OUT = ROOT / 'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit'
QA = ROOT / '.dream-loop/continuous-world/assets'
OUT.mkdir(parents=True, exist_ok=True); QA.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for x in list(bpy.data.materials): bpy.data.materials.remove(x)
random.seed(11923)

def material(name, color, roughness=.82, detail=5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; bs=nt.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=roughness
    tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=detail; tex.inputs['Detail'].default_value=5
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(*[c*.62 for c in color],1)
    ramp.color_ramp.elements[1].color=(*[min(c*1.2,1) for c in color],1)
    nt.links.new(tex.outputs['Fac'],ramp.inputs[0]); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.24; bump.inputs['Distance'].default_value=.038
    nt.links.new(tex.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return m

M={
 'Rock':material('CW_Rock',(.285,.30,.285),.87,9),
 'RockLight':material('CW_RockLight',(.39,.395,.355),.89,7),
 'Crevice':material('CW_Crevice',(.115,.135,.125),.94,9),
 'Moss':material('CW_Moss',(.19,.245,.11),.97,18),
 'Stone':material('CW_Stone',(.40,.385,.32),.9,11),
 'StoneDark':material('CW_StoneDark',(.285,.285,.25),.93,10),
 'Bark':material('CW_Bark',(.16,.135,.105),.96,28),
 'Birch':material('CW_Birch',(.54,.525,.435),.96,24),
 'Leaf':material('CW_Leaf',(.17,.265,.105),.94,18),
 'LeafLight':material('CW_LeafLight',(.30,.37,.145),.94,18),
 'Reed':material('CW_Reed',(.30,.37,.14),.98,18),
 'ReedDry':material('CW_ReedDry',(.47,.39,.21),.98,18),
 'Seed':material('CW_Seed',(.185,.125,.07),1,24),
 'Pine':material('CW_Pine',(.105,.17,.125),.94,20),
 'PineTip':material('CW_PineTip',(.16,.245,.18),.96,20),
 'Snow':material('CW_Snow',(.77,.82,.84),.94,16),
}
MODELS={}

def mesh(name, verts, faces, mats, indices=None, smooth=False):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob)
    for m in mats: me.materials.append(M[m])
    for i,p in enumerate(me.polygons):
        p.material_index=indices[i] if indices else 0; p.use_smooth=smooth
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    bpy.context.view_layer.objects.active=ob; ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.016)
    bpy.ops.object.mode_set(mode='OBJECT'); ob.select_set(False)
    return ob

def bevel(ob, width=.018, segments=1):
    bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Small worn arrises','BEVEL'); mod.width=width; mod.segments=segments
    bpy.ops.object.modifier_apply(modifier=mod.name)

def join(name, obs):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs: ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]; bpy.ops.object.join()
    ob=obs[0]; ob.name=name; ob.select_set(False); return ob

def register(name, obs, notes):
    if not isinstance(obs,list): obs=[obs]
    MODELS[name]={'objects':obs,'notes':notes}

def rock(name, size, seed, moss=True):
    # A carved irregular solid: broad fracture planes and localized strata, no stacked rings.
    r=random.Random(seed); bm=bmesh.new(); bmesh.ops.create_icosphere(bm,subdivisions=4,radius=1)
    shift=Vector((seed*.071,seed*.023,seed*.041))
    for v in bm.verts:
        q=v.co.copy()
        q=Vector([math.copysign(abs(c)**.68,c) for c in q])
        coarse=noise_vector(q*1.6+shift); fine=noise_vector(q*6.4+shift)
        q+=coarse*.18+fine*.035
        # Inclined fissure carved across a limited part of the front shoulder.
        fault=q.z+.20*q.x-.05
        if q.y<-.25 and abs(fault)<.045: q.y+=.11*(1-abs(fault)/.045)
        # Local ledges terminate on the shoulder instead of encircling the rock.
        if q.x<-.3 and q.z<.55:
            phase=(q.z+.17*q.y)*5.2
            q.x+=max(0,math.cos(phase*math.tau))**12*.042
        v.co=q
    # Clip substantial pieces from three independently angled faces, filling real cut planes.
    planes=[((.83,0,0),(.96,.13,.22)),((0,.82,0),(-.16,1,.22)),((0,0,.73),(.21,-.10,1)),
            ((-.82,0,0),(-1,.13,.02)),((0,0,-.84),(0,0,-1))]
    for co,no in planes:
        result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
             dist=.0001,plane_co=Vector(co),plane_no=Vector(no),clear_outer=True,clear_inner=False)
        edges=[e for e in result['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and e.is_boundary]
        if edges: bmesh.ops.holes_fill(bm,edges=edges,sides=0)
    for v in bm.verts:
        q=v.co; v.co=((q.x+.11*q.z)*size[0]/1.85,(q.y-.06*q.z)*size[1]/1.85,(q.z+.82)*size[2]/1.62-.045)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.verts.ensure_lookup_table(); bm.verts.index_update(); bm.faces.ensure_lookup_table()
    vs=[tuple(v.co) for v in bm.verts]; fs=[tuple(v.index for v in f.verts) for f in bm.faces]
    ob=mesh(name,vs,fs,['Rock','RockLight','Crevice','Moss'])
    bm.free()
    for p in ob.data.polygons:
        p.use_smooth=len(p.vertices)==3
    bevel(ob,.008,1)
    register(name,ob,'Carved irregular stone solid, broad planar fracture faces, fine surface erosion and localized ledges. Ground pivot. Assign tileable stone texture and normal; no disconnected primitive stacks.')
    return ob

def block(name, bounds, seed, mat='Stone', wear=.025):
    x0,x1,y0,y1,z0,z1=bounds; r=random.Random(seed)
    verts=[(x+r.uniform(-wear,wear),y+r.uniform(-wear,wear),z+r.uniform(-wear,wear))
           for x,y,z in [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                         (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]]
    ob=mesh(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],[mat])
    bevel(ob,.026,1); return ob

def bridge(flat=False):
    obs=[]; r=random.Random(180)
    # Walking surface: actual shallow arch, 10 m length, clear width 5.2 m.
    def deck(y): return 0 if flat else .8*max(0,1-(y/5)**2)
    for j in range(20):
        y0=-5+j*.5+.018; y1=y0+.464
        for k in range(5):
            x0=-2.6+k*1.04+.012; x1=x0+1.016
            z0=deck(y0); z1=deck(y1)
            ob=mesh('Worn deck flag',[(x0,y0,z0-.24),(x1,y0,z0-.24),(x1,y1,z1-.24),(x0,y1,z1-.24),
                 (x0,y0,z0),(x1,y0,z0),(x1,y1,z1),(x0,y1,z1)],
                 [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],['Stone' if r.random()>.25 else 'StoneDark'])
            bevel(ob,.018,1); obs.append(ob)
    # Side walls have a real curved open arch, not a solid box under a bridge decal.
    for side in (-1,1):
        xa,xb=sorted((side*2.6,side*3.10))
        for j in range(22):
            y0=-5+j*(10/22)+.012; y1=y0+10/22-.024
            lower0=-1.60+.98*math.sqrt(max(0,1-(y0/4.55)**2))
            lower1=-1.60+.98*math.sqrt(max(0,1-(y1/4.55)**2))
            top0=deck(y0)-.13; top1=deck(y1)-.13
            ob=mesh('Radial arch masonry',[(xa,y0,lower0),(xb,y0,lower0),(xb,y1,lower1),(xa,y1,lower1),
                     (xa,y0,top0),(xb,y0,top0),(xb,y1,top1),(xa,y1,top1)],
                     [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],['StoneDark' if j%4==0 else 'Stone'])
            bevel(ob,.025); obs.append(ob)
        for j in range(15):
            y=-5+j*2/3
            # Thin continuous parapet gives a readable safe edge without hiding player.
            for course in range(2):
                z=deck(y+.32)+course*.32+.025
                obs.append(block('Parapet course',(xa,xb,y+.012,y+.644,z,z+.30),j*87+course+side,'StoneDark' if j%5==0 else 'Stone'))
            z=deck(y+.32)+.68
            obs.append(block('Coping stone',(xa-.055,xb+.055,y+.006,y+.651,z,z+.135),j+200+side,'Stone',.018))
        for y in (-4.82,4.82):
            obs.append(block('Bridge abutment',(xa-.13,xb+.13,y-.38,y+.38,-1.75,.2),int(y*100)+side,'StoneDark'))
    name='CW_StoneFootbridge_Flat12m' if flat else 'CW_StoneFootbridge'
    ob=join(name,obs)
    if flat:
        for v in ob.data.vertices: v.co.y*=1.2
    register(name,ob,'12 m along Z in Unity; 5.2 m clear width, flat walking deck at local y=0. Place at Unity y=.8 for desired world deck. Arch underside reaches -1.75 below deck; no collider included.' if flat else '10 m along Z in Unity; 5.2 m clear deck width; deck y=.8*(1-(z/5)^2), -5<=z<=5. Origin at deck end elevation. Arch underside -1.75 m; parapet top ~1.6 m at crown. Add continuous walking collider from formula; visual slab gaps are not navigation holes.')

def tube(name,points,radii,sides=8,mat='Bark'):
    vs=[]; fs=[]
    for j,p in enumerate(points):
        p=Vector(p); tangent=Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])
        tangent.normalize(); u=tangent.cross(Vector((0,1,0)))
        if u.length<.1: u=tangent.cross(Vector((1,0,0)))
        u.normalize(); v=tangent.cross(u).normalized()
        for i in range(sides):
            a=i*math.tau/sides; q=p+(u*math.cos(a)+v*math.sin(a))*radii[j]*(1+.07*math.sin(i*9+j))
            vs.append(q)
    for j in range(len(points)-1):
        for i in range(sides): fs.append((j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i))
    fs.append(tuple(reversed(range(sides)))); fs.append(tuple((len(points)-1)*sides+i for i in range(sides)))
    return mesh(name,vs,fs,[mat],smooth=True)

def leaf_geometry(vs,fs,ids,center,axis,width,length,mat,fold=.15):
    c=Vector(center); a=Vector(axis).normalized(); u=a.cross(Vector((0,0,1)))
    if u.length<.05: u=Vector((1,0,0))
    u.normalize(); n=a.cross(u).normalized(); base=len(vs)
    vs.extend([c-a*length*.5,c-a*length*.12+u*width*.5,c+a*length*.5,
               c-a*length*.12-u*width*.5,c+n*width*fold])
    fs.extend([(base,base+1,base+4),(base+1,base+2,base+4),(base+2,base+3,base+4),(base+3,base,base+4)])
    ids.extend([mat]*4)

def birch():
    r=random.Random(994); obs=[]; vs=[]; fs=[]; ids=[]
    trunk=[(0,0,0),(.06,-.05,1.5),(-.06,.04,3),(.10,.05,4.5),(.05,.12,6.2)]
    obs.append(tube('Slender birch bole',trunk,[.20,.155,.12,.073,.015],12,'Birch'))
    # Black lenticel patches and split bark are geometry, visible even without textures.
    for i in range(37):
        z=r.uniform(.25,5.6); a=r.uniform(0,math.tau); rad=.20*(1-z/7)
        p=Vector((.02+math.cos(a)*rad,math.sin(a)*rad,z)); tang=Vector((-math.sin(a),math.cos(a),0))
        w=r.uniform(.025,.10); h=r.uniform(.012,.035)
        ob=mesh('Birch lenticel',[p-tang*w,p+tang*w,p+tang*w+Vector((0,0,h)),p-tang*w+Vector((0,0,h*.7))],[(0,1,2,3)],['Bark'])
        obs.append(ob)
    for i in range(24):
        z=1.8+i*.17; a=i*2.399; length=r.uniform(1.3,2.3)*(1-.24*max(0,z-3)/3)
        start=Vector((.03,0,z)); end=Vector((math.cos(a)*length,math.sin(a)*length,z+r.uniform(.55,1.05)))
        mid=start.lerp(end,.48)+Vector((0,0,.20))
        obs.append(tube('Birch branch',[start,mid,end],[.05,.026,.006],7,'Bark'))
        for b in range(3):
            az=a+(b-1)*.8; p=mid.lerp(end,.3+b*.25); tip=p+Vector((math.cos(az)*.65,math.sin(az)*.65,.25))
            obs.append(tube('Fine twig',[p,tip],[.014,.002],5,'Bark'))
            for k in range(18):
                t=r.random(); c=p.lerp(tip,t)+Vector((r.uniform(-.36,.36),r.uniform(-.36,.36),r.uniform(-.16,.3)))
                leaf_geometry(vs,fs,ids,c,(math.cos(az+k),math.sin(az+k),r.uniform(-.1,.7)),r.uniform(.11,.17),r.uniform(.19,.30),r.randrange(2))
    obs.append(mesh('Individual folded birch leaves',vs,fs,['Leaf','LeafLight'],ids))
    ob=join('CW_RiverBirch',obs); register('CW_RiverBirch',ob,'Open canopy river birch; branched tapering trunk, dark bark lenticels, individual folded leaves. Ground origin. Leaf material should render double sided.')

def reeds(name,seed,count,grass=False):
    r=random.Random(seed); obs=[]; vs=[]; fs=[]; ids=[]
    for k in range(count):
        a=r.uniform(0,math.tau); radius=math.sqrt(r.random())*(.85 if grass else .95)
        p=Vector((math.cos(a)*radius,math.sin(a)*radius,0)); h=r.uniform(.38,.85) if grass else r.uniform(1.0,2.0)
        lean=Vector((r.uniform(-.2,.2),r.uniform(-.2,.2),0)); direction=Vector((math.cos(a+.8),math.sin(a+.8),0))
        if not grass and k%3==0:
            obs.append(tube('Reed culm',[p,p+lean*.4+Vector((0,0,h*.6)),p+lean+Vector((0,0,h))],[.013,.01,.006],5,'ReedDry'))
            if k%2==0:
                q=p+lean+Vector((0,0,h)); obs.append(tube('Cattail seed head',[q,q+Vector((0,0,.035)),q+Vector((0,0,.21)),q+Vector((0,0,.24))],[.01,.04,.036,.005],7,'Seed'))
        for j in range(3 if grass else 2):
            az=a+j*2.2; d=Vector((math.cos(az),math.sin(az),0)); side=Vector((-d.y,d.x,0)); base=len(vs)
            height=h*(.85 if grass else .72)*r.uniform(.7,1.1); spread=r.uniform(.22,.60)
            start=p+Vector((0,0,0 if grass else j*.13)); width=r.uniform(.023,.045) if grass else r.uniform(.027,.054)
            for s in range(6):
                t=s/5; c=start+d*(spread*t*t)+Vector((0,0,height*(t-.29*t*t)))
                w=width*math.sin(math.pi*(.07+.93*t))
                vs.extend([c-side*w,c+Vector((0,0,.008))*math.sin(t*math.pi),c+side*w])
            for s in range(5):
                v=base+s*3; fs.extend([(v,v+3,v+4,v+1),(v+1,v+4,v+5,v+2)]); ids.extend([k%3==0,k%3==0])
    obs.append(mesh('Curved tapered blades',vs,fs,['Reed','ReedDry'],ids))
    ob=join(name,obs); register(name,ob,'Ground centered clump. Individually curved creased ribbons and seed heads; blade materials should render double sided.')

def fir():
    r=random.Random(761); woody=[]; vs=[]; fs=[]; ids=[]; sv=[]; sf=[]; si=[]
    height=7.5
    woody.append(tube('Fir bole',[(0,0,0),(.07,0,2.5),(0,.04,5.0),(.02,.04,height)],[.24,.15,.08,.01],12,'Bark'))
    for tier in range(12):
        z=.65+tier*.54; reach=2.6*(1-z/(height+.6))
        for branch in range(7):
            a=branch*math.tau/7+tier*1.3+r.uniform(-.12,.12); d=Vector((math.cos(a),math.sin(a),0)); sideways=Vector((-d.y,d.x,0))
            start=Vector((0,0,z)); end=start+d*reach+Vector((0,0,-.13+.18*tier/12))
            woody.append(tube('Fir woody bough',[start,start.lerp(end,.55)+Vector((0,0,-.13)),end],[.047*(1-tier/15),.023,.002],5,'Bark'))
            for frond in range(7):
                t=.20+frond*.115; center=start.lerp(end,t); span=(1-t*.65)*reach*.34
                for s in (-1,1):
                    axis=(d*.5+sideways*s*.85+Vector((0,0,.11))).normalized(); length=span*r.uniform(.8,1.2)
                    leaf_geometry(vs,fs,ids,center+axis*length*.38,axis,length*.70,length*1.5,(tier+branch+frond)%4==0,.22)
                    # Fine sawtooth fringe: needle fans at the sides of every frond.
                    for needle in range(3):
                        tip=center+axis*(length*(.25+needle*.25)); spread=(d*.7+sideways*s*1.1+Vector((0,0,-.08))).normalized()
                        leaf_geometry(vs,fs,ids,tip,spread,.065,.23,r.randrange(2),.14)
                if tier<10 and (branch+tier)%4!=0 and frond==3:
                    # Separate snow mantle conforms to the bough, gently drooping edges.
                    p=center+Vector((0,0,.09)); axis=d; across=sideways
                    leng=reach*.28; wid=span*1.1; base=len(sv); n=11
                    for ring in range(3):
                        for k in range(n):
                            angle=k*math.tau/n; rr=(1,.79,.22)[ring]*(1+r.uniform(-.12,.12))
                            sv.append(p+axis*(math.cos(angle)*leng*rr)+across*(math.sin(angle)*wid*rr)+Vector((0,0,(-.015,.075,.135)[ring])))
                    for ring in range(2):
                        for k in range(n):
                            sf.append((base+ring*n+k,base+ring*n+(k+1)%n,base+(ring+1)*n+(k+1)%n,base+(ring+1)*n+k))
                    sf.append(tuple(base+2*n+k for k in range(n)))
    woody.append(mesh('Fir flat needle sprays',vs,fs,['Pine','PineTip'],ids))
    tree=join('CW_AlpineFir',woody)
    snow=mesh('CW_AlpineFir_SnowCaps',sv,sf,['Snow'],smooth=True)
    register('CW_AlpineFir',[tree,snow],'7.5 m alpine fir, irregular drooping woody boughs and serrated needle sprays. Snow caps are a separate child mesh that can be hidden for lower elevation. Pine material should render double sided.')

def waymarker():
    obs=[]
    obs.append(block('Marker plinth',(-.57,.57,-.48,.48,-.08,.25),99,'StoneDark',.07))
    obs.append(block('Marker shaft',(-.30,.30,-.24,.24,.20,2.20),102,'Stone',.055))
    # Hewn pointing cap and recessed directional cutouts.
    ob=mesh('Pointing weathered cap',[(-.65,-.30,2.17),(.65,-.30,2.17),(.93,-.30,2.42),(.65,-.30,2.65),(-.65,-.30,2.65),
                                    (-.65,.30,2.17),(.65,.30,2.17),(.93,.30,2.42),(.65,.30,2.65),(-.65,.30,2.65)],
                                    [(0,4,3,2,1),(5,6,7,8,9),(0,1,6,5),(1,2,7,6),(2,3,8,7),(3,4,9,8),(4,0,5,9)],['Stone'])
    bevel(ob,.04); obs.append(ob)
    for z in (.65,.98,1.32):
        p=[(-.13,-.279,z),(.06,-.279,z+.11),(.16,-.279,z),(.06,-.279,z-.11)]
        obs.append(mesh('Inset weathered glyph',p,[(0,1,2,3)],['Crevice']))
    ob=join('CW_StoneWaymarker',obs); register('CW_StoneWaymarker',ob,'Hewn directional stone marker, 2.65 m high, pointer along local X, ground origin.')

rock('CW_LayeredRock_A',(4.3,3.2,2.5),145)
rock('CW_LayeredRock_B',(3.4,2.6,1.7),922)
rock('CW_CliffLedge',(7.0,3.6,4.0),455,False)
rock('CW_RiverBoulder',(2.1,1.65,.85),75)
bridge(); bridge(True); reeds('CW_Reeds',773,27); reeds('CW_RiverGrass',355,35,True); birch(); fir(); waymarker()

# Export each model without changing object pivots. Unity imports material slots by CW_ name.
manifest={'version':1,'source_units':'metres','source_axes':'+Z up, +Y length','fbx_axes':'-Z forward, +Y up','models':{}}
for name,data in MODELS.items():
    bpy.ops.object.select_all(action='DESELECT'); verts=[]; triangles=0; slots=[]
    for ob in data['objects']:
        # Export only explicit valid triangles, so Unity never reinterprets a weathered ngon.
        bm=bmesh.new(); bm.from_mesh(ob.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
        bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='EAR_CLIP')
        bad=[f for f in bm.faces if f.calc_area()<1e-10]
        if bad: bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(ob.data); bm.free(); ob.data.update()
        ob.select_set(True); verts.extend([ob.matrix_world@Vector(v) for v in ob.bound_box]); ob.data.calc_loop_triangles()
        triangles+=len(ob.data.loop_triangles); slots.extend([m.name for m in ob.data.materials if m])
    bpy.context.view_layer.objects.active=data['objects'][0]
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},
        apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',
        use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=True,bake_anim=False,add_leaf_bones=False)
    mn=[min(v[i] for v in verts) for i in range(3)]; mx=[max(v[i] for v in verts) for i in range(3)]
    manifest['models'][name]={'file':name+'.fbx','triangles':triangles,'source_bounds_min':mn,'source_bounds_max':mx,
                             'size_xyz_source':[mx[i]-mn[i] for i in range(3)],'material_slots':list(dict.fromkeys(slots)),
                             'objects':[ob.name for ob in data['objects']],'notes':data['notes']}
(SOURCE/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
# Save original source before staging the contact sheet.
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'ContinuousWorld_EnvironmentKit.blend'))

# Contact sheet of the actual meshes, perspective matching an elevated game camera.
positions={'CW_LayeredRock_A':(-7,0,0),'CW_LayeredRock_B':(-3,0,0),'CW_CliffLedge':(-7,6,0),
           'CW_RiverBoulder':(-1,0,0),'CW_StoneFootbridge':(3,5,1.6),'CW_Reeds':(-8,-4,0),
           'CW_RiverGrass':(-5,-4,0),'CW_RiverBirch':(9,5,0),'CW_AlpineFir':(10,-3,0),'CW_StoneWaymarker':(-1,-4,0),'CW_StoneFootbridge_Flat12m':(3,25,1.6)}
for name,data in MODELS.items():
    for ob in data['objects']: ob.location=positions[name]
ground=block('QA floor',(-18,18,-12,18,-.16,-.11),1,'RockLight',0)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=48
scene.render.resolution_x=1800; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
scene.world.color=(.24,.27,.29)
world=scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.30,.36,.43,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
ld=bpy.data.lights.new('Soft afternoon key','AREA'); ld.energy=2800; ld.shape='DISK'; ld.size=12
lo=bpy.data.objects.new('Soft afternoon key',ld); bpy.context.collection.objects.link(lo); lo.location=(-6,-7,18)
lo.rotation_euler=(Vector((0,3,0))-lo.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('QA elevated camera'); cam=bpy.data.objects.new('QA elevated camera',camd); bpy.context.collection.objects.link(cam)
cam.location=(24,-33,28); cam.rotation_euler=(Vector((0,2,2))-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=31
scene.camera=cam; scene.view_settings.view_transform='AgX'; scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(QA/'environment-kit-contact.png'); bpy.ops.render.render(write_still=True)
print('ENVIRONMENT_KIT_COMPLETE '+str(OUT))
