"""Authored open-aperture Gothic modules. Blender 5.2, no Unity execution.
Source XYZ = width/depth/height, metres; FBX export Y-up/-Z-forward.
"""
import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5]
OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/Chapel'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.87
    noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=12;noise.inputs['Detail'].default_value=4
    bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.2;bump.inputs['Distance'].default_value=.025
    m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return m
M=[mat('CW_ChapelStone',(.36,.365,.33)),mat('CW_ChapelStoneLight',(.45,.445,.38)),mat('CW_ChapelMortar',(.16,.17,.15))]

def mesh(name,vs,fs,slot=0):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(M[slot])
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();return ob

def solid_polygon(name,points,y0,y1,slot=0):
    n=len(points);vs=[(x,y,z) for y in (y0,y1) for x,z in points]
    fs=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,slot)

def bevel(ob,width=.015):
    bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Weathered arris','BEVEL');mod.width=width;mod.segments=2
    bpy.ops.object.modifier_apply(modifier=mod.name)

def block(name,x0,x1,z0,z1,y0=-.22,y1=.22,seed=0,slot=0,wear=.013):
    r=random.Random(seed);vs=[]
    for x,y,z in [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]:
        vs.append((min(x1,max(x0,x+r.uniform(-wear,wear))),min(y1,max(y0,y+r.uniform(-wear,wear))),min(z1,max(z0,z+r.uniform(-wear,wear)))))
    ob=mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],slot);bevel(ob);return ob

def join(name,obs):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name=name;return obs[0]

def make_module(name,width,height,apwidth,base,apex,rise,seed):
    a=apwidth/2;spring=apex-rise;r=(a*a+rise*rise)/(2*a);c=r-a;end=math.acos(-c/r)
    def curve(t,offset=0,side=-1):
        rad=r+offset;theta=math.pi+(math.acos(-c/rad)-math.pi)*t
        x=c+rad*math.cos(theta);z=spring+rad*math.sin(theta)
        return (x if side<0 else -x,z)
    def opening_x(z):
        if z<base or z>apex:return 0
        if z<=spring:return a
        return max(0,math.sqrt(max(0,r*r-(z-spring)**2))-c)
    # Leave a small recess behind the carved frame so coplanar reveal faces never fight.
    recess=.03
    points=[(-a-recess,base-.02),(-a-recess,spring)]+[curve(i/40,recess) for i in range(1,41)]
    points +=[curve(i/40,recess,side=1) for i in reversed(range(40))]+[(a+recess,base-.02)]
    cutter=solid_polygon('True lancet aperture cutter',points,-1,1)
    # Individual weathered blocks and continuous recessed mortar backstop.
    obs=[];rng=random.Random(seed);courses=round(height/.38);course=height/courses
    for row in range(courses):
        z0=row*course+.009;z1=(row+1)*course-.009
        # Staggered bonds with nonuniform lengths; whole module stays at the stated width.
        x=-width/2;col=0
        while x<width/2-.01:
            length=(.42 if row%2 and col==0 else rng.uniform(.61,.83));right=min(width/2,x+length)
            obs.append(block('Chipped ashlar block',x+.008,right-.008,z0,z1,seed=seed+row*77+col,slot=1 if rng.random()<.13 else 0))
            x=right;col+=1
    obs.append(block('Recessed mortar core',-width/2,width/2,0,height-.025,-.17,.17,seed,2,0))
    # Cut each closed stone independently. Booleaning an overlapping multi-shell
    # masonry/core mesh can retain internal faces across the intended aperture.
    for piece in obs:
        bb=[Vector(v) for v in piece.bound_box]
        if max(v.x for v in bb)<-a or min(v.x for v in bb)>a or max(v.z for v in bb)<base or min(v.z for v in bb)>apex:continue
        bpy.context.view_layer.objects.active=piece
        mod=piece.modifiers.new('Actual open aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
    wall=join('Pierced ashlar masonry',obs)
    bpy.data.objects.remove(cutter,do_unlink=True)
    details=[wall]
    # Radial voussoirs follow both real pointed arcs, with joints and worn edges.
    for side in (-1,1):
        x0,x1=sorted((side*a,side*(a+.10)))
        details.append(block('Solid carved jamb reveal',x0,x1,base,spring,-.25,.25,seed,0,0))
        for k in range(16):
            t0=(k+.016)/16;t1=(k+1-.016)/16
            p=[curve(t0,0,side),curve(t1,0,side),curve(t1,.32,side),curve(t0,.32,side)]
            ob=solid_polygon('Carved arch voussoir',p,-.25,.25,1 if k%5==0 else 0);bevel(ob,.008);details.append(ob)
        # Jamb legs and splayed molded archivolts project within the total 0.6 m depth.
        for offset,bandwidth,depth in [(.006,.042,.296),(.08,.038,.275),(.145,.055,.29),(.235,.075,.265)]:
            for face in (-1,1):
                front=face*depth;y0,y1=sorted((front,front-face*.040))
                for k in range(20):
                    p=[curve(k/20,offset,side),curve((k+1)/20,offset,side),curve((k+1)/20,offset+bandwidth,side),curve(k/20,offset+bandwidth,side)]
                    details.append(solid_polygon('Molded archivolt',p,y0,y1,1))
                x0,x1=sorted((side*(a+offset),side*(a+offset+bandwidth)))
                details.append(block('Continuous molded jamb',x0,x1,base,spring,y0,y1,seed,1,.002))
        # Spring capital in discrete bands; positioned outside aperture.
        x0,x1=sorted((side*a,side*(a+.36)))
        for face in (-1,1):
            y0,y1=sorted((face*.285,face*.19))
            details.append(block('Spring capital',x0,x1,spring-.095,spring+.01,y0,y1,seed+side,1,.005))
    if base>0:
        details.append(block('Window sill',-a-.35,a+.35,base-.20,base,-.295,.295,seed,1,.01))
    # A shallow crenellated broken crest remains inside nominal wall bounds.
    for x in (-width/2+.32,width/2-.32):
        details.append(block('Crest coping',x-.30,x+.30,height-.16,height,-.28,.28,seed+int(x*100),1,.015))
    ob=join(name,details)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='EAR_CLIP')
    bad=[f for f in bm.faces if f.calc_area()<1e-10]
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.validate(clean_customdata=False);ob.data.update()
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(65),island_margin=.008);bpy.ops.object.mode_set(mode='OBJECT')
    # Raw UV0 spans 0..1; parent shader maps it to stone atlas quadrant.
    ob.data.calc_loop_triangles()
    bvh=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons],all_triangles=True)
    rays=[]
    for iz in range(1,15):
        z=base+(apex-base)*iz/15;half=opening_x(z)
        for frac in (-.82,-.45,0,.45,.82):
            x=half*frac;hit=bvh.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)[0]
            rays.append({'x':x,'height':z,'clear':hit is None})
    solid_tests=[]
    for x,z in [(-width*.44,height*.3),(width*.44,height*.6),(0,height-.3)]:
        hit=bvh.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)[0];solid_tests.append({'x':x,'height':z,'hit':hit is not None})
    manifest={'name':name,'width':width,'height':height,'max_depth':.60,'origin':'ground center','source_axes':'XYZ width/depth/height; +Z up',
       'fbx_axes':'+Y up/-Z forward','aperture':{'base':base,'spring':spring,'apex':apex,'width_at_base_and_legs':apwidth,'rise':rise,
           'curve_radius':r,'curve_center_offset':c,'half_width_above_spring':'sqrt(radius^2-(height-spring)^2)-center_offset'},
       'bounds_source_xyz':[[min(v.co[i] for v in ob.data.vertices) for i in range(3)],[max(v.co[i] for v in ob.data.vertices) for i in range(3)]],
       'triangles':len(ob.data.loop_triangles),'zero_area_triangles':sum(t.area<1e-10 for t in ob.data.loop_triangles),
       'all_triangular':all(len(p.vertices)==3 for p in ob.data.polygons),'material_slots':[m.name for m in ob.data.materials],
       'aperture_ray_checks':rays,'solid_wall_ray_checks':solid_tests,'aperture_all_clear':all(x['clear'] for x in rays),'solid_tests_hit':all(x['hit'] for x in solid_tests)}
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',
        apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',bake_anim=False,mesh_smooth_type='FACE',use_tspace=True)
    (SOURCE/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2));(OUT/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2))
    return ob,manifest

window,wm=make_module('CW_ChapelLancetWall',6,7,2,1.3,6.1,1.8,1551)
door,dm=make_module('CW_ChapelEntranceArch',5,6,3,0,4,1.7,2568)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'ChapelModules.blend'))
window.location=(-3.5,0,0);door.location=(3.1,0,0)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Chapel inspection');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.28,.33,.39,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
light=bpy.data.lights.new('Window inspection light','AREA');light.energy=2300;light.size=9;lo=bpy.data.objects.new('Window inspection light',light);bpy.context.collection.objects.link(lo);lo.location=(-6,-8,12);lo.rotation_euler=(Vector((0,0,3))-lo.location).to_track_quat('-Z','Y').to_euler()
floor=block('QA floor',-15,15,-.1,0,-8,8,4,2,0)
camd=bpy.data.cameras.new('Chapel inspection camera');cam=bpy.data.objects.new('Chapel inspection camera',camd);bpy.context.collection.objects.link(cam);cam.location=(11,-21,13);cam.rotation_euler=(Vector((0,0,3.4))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=15;scene.camera=cam
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/'chapel-preview.png');bpy.ops.render.render(write_still=True)
print('CHAPEL_MODULES_COMPLETE '+str({'window_clear':wm['aperture_all_clear'],'door_clear':dm['aperture_all_clear']}))
