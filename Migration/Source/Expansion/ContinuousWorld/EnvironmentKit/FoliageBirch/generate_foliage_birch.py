"""Airy birch with real textured twig cards and a curving white-bark skeleton.
Source +Z up, FBX -Z forward/+Y up; preserve FBX root rotation in Unity.
"""
import bpy,bmesh,math,random,json,hashlib
from pathlib import Path
from mathutils import Vector
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5]
OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/FoliageBirch'
ATLAS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/BirchBranches.png'
BARK=OUT/'BirchBark.png';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
leaf=bpy.data.materials.new('CW_BirchLeaves');leaf.use_nodes=True;bs=leaf.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.92
tex=leaf.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ATLAS));leaf.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
clip=leaf.node_tree.nodes.new('ShaderNodeMath');clip.operation='GREATER_THAN';clip.inputs[1].default_value=.4;leaf.node_tree.links.new(tex.outputs['Alpha'],clip.inputs[0]);leaf.node_tree.links.new(clip.outputs[0],bs.inputs['Alpha'])
bark=bpy.data.materials.new('CW_WhiteBirchBark');bark.use_nodes=True;bs=bark.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.95
tex=bark.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(BARK));bark.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
bump=bark.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.018;bark.node_tree.links.new(tex.outputs['Color'],bump.inputs['Height']);bark.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
twig=bpy.data.materials.new('CW_BirchTwigs');twig.diffuse_color=(.16,.13,.10,1);twig.use_nodes=True;bs=twig.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.16,.13,.10,1);bs.inputs['Roughness'].default_value=.97

def obj(name,vs,fs,uvs,material):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(material)
    layer=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        for li in p.loop_indices:layer.data[li].uv=uvs[me.loops[li].vertex_index]
    return ob

def tube(vs,fs,uvs,points,radii,sides):
    base=len(vs)
    for j,p in enumerate(points):
        p=Vector(p);d=(Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])).normalized();u=d.cross(Vector((0,1,0)))
        if u.length<.05:u=d.cross(Vector((1,0,0)))
        u.normalize();v=d.cross(u).normalized()
        for k in range(sides+1):
            a=k*math.tau/sides;vs.append(p+(u*math.cos(a)+v*math.sin(a))*radii[j]*(1+.04*math.sin(k*4+j)));uvs.append((k/sides,j/(len(points)-1)))
    for j in range(len(points)-1):
        for k in range(sides):
            a=base+j*(sides+1)+k;fs.append((a,a+1,a+sides+2,a+sides+1))
    fs.append(tuple(base+k for k in reversed(range(sides))));fs.append(tuple(base+(len(points)-1)*(sides+1)+k for k in range(sides)))

def card(vs,fs,uvs,p,d,length,roll,quad):
    d=Vector(d).normalized();side=d.cross(Vector((0,0,1))).normalized();up=side.cross(d).normalized();across=side*math.cos(roll)+up*math.sin(roll)
    roots=[(.04,.33),(.02,.39),(.035,.46),(.02,.46)];tips=[(.88,.89),(.83,.86),(.85,.91),(.80,.91)]
    root=Vector(roots[quad]);delta=Vector(tips[quad])-root;direction=delta.normalized();perp=Vector((-direction.y,direction.x));base=len(vs)
    for j in range(5):
        for k in range(5):
            u=k/4;v=j/4;q=Vector((u,v))-root;t=q.dot(direction)/delta.length;s=q.dot(perp)/delta.length
            vs.append(Vector(p)+d*(length*t)+across*(length*s)+Vector((0,0,-.09*t*t-.045*abs(s))))
            uvs.append(((quad%2)*.5+.004+u*.492,(1-quad//2)*.5+.004+v*.492))
    for j in range(4):
        for k in range(4):a=base+j*5+k;fs.append((a,a+1,a+6,a+5))

def build(name,lod=False):
    r=random.Random(6631);bv=[];bf=[];bu=[];tv=[];tf=[];tu=[];lv=[];lf=[];lu=[];phantom=[];card_count=0
    trunk=[(0,0,0),(.05,-.04,1.2),(-.07,.035,2.5),(.05,.13,3.8),(.22,.10,5.1),(.30,.18,6.3),(.25,.13,7.0)]
    tube(bv,bf,bu,trunk,[.18,.16,.132,.103,.072,.043,.005],12 if not lod else 8)
    second=[(-.045,.02,2.3),(-.33,-.11,3.6),(-.60,-.05,4.8),(-.65,.15,5.85)]
    tube(bv,bf,bu,second,[.10,.076,.048,.006],9 if not lod else 6)
    branch_count=0
    for i in range(31):
        z=2.1+i*.145;a=i*2.399+r.uniform(-.15,.15);reach=(1.0+.75*math.sin((z-1.1)/6*math.pi))*r.uniform(.78,1.02)
        # Branch roots coincide with the actual curved trunk, not an assumed centerline.
        seg=next(j for j in range(len(trunk)-1) if trunk[j][2]<=z<=trunk[j+1][2]);troot=(z-trunk[seg][2])/(trunk[seg+1][2]-trunk[seg][2]);start=Vector(trunk[seg]).lerp(Vector(trunk[seg+1]),troot)
        d=Vector((math.cos(a),math.sin(a),r.uniform(.12,.30))).normalized();tip=start+d*reach+Vector((0,0,.20));mid=start.lerp(tip,.52)+Vector((0,0,.14))
        tube(bv,bf,bu,[start,mid],[.052*(1-(z-2)/7),.021],7 if not lod else 5)
        tube(tv,tf,tu,[mid,tip],[.021,.003],6 if not lod else 4);branch_count+=1
        for j,t in enumerate((.36,.60,.82,.97)):
            p=start.lerp(tip,t);a2=a+(j-1.5)*.52+r.uniform(-.17,.17);d2=Vector((math.cos(a2),math.sin(a2),r.uniform(.05,.35))).normalized();length=r.uniform(.93,1.28)*(1-.25*max(0,z-5)/2)
            twig_end=p+d2*length*.76;tube(tv,tf,tu,[p,twig_end],[.009,.0015],5 if not lod else 4)
            roll=r.uniform(-.55,.65);roll2=roll+r.uniform(.65,1.05);quad=(i+j)%4
            card(lv,lf,lu,p,d2,length,roll,quad);card_count+=1
            if (i+j)%2==0:
                if not lod:
                    card(lv,lf,lu,p+Vector((0,0,.015)),d2,length*.91,roll2,(quad+1)%4);card_count+=1
                else:card(phantom,[],[],p+Vector((0,0,.015)),d2,length*.91,roll2,(quad+1)%4)
    for tip in (Vector(trunk[-1]),Vector(second[-1])):
        for i in range(3):
            a=i*math.tau/3;d=Vector((math.cos(a)*.65,math.sin(a)*.65,.65)).normalized()
            card(lv,lf,lu,tip-Vector((0,0,.12)),d,.70,.3+i*.6,i);card_count+=1
    wood=obj(name+'_WhiteBark',bv,bf,bu,bark);twigs=obj(name+'_FineTwigs',tv,tf,tu,twig);leaves=obj(name+'_Leaves',lv,lf,lu,leaf)
    obs=[wood,twigs,leaves];points=[v.co for ob in obs for v in ob.data.vertices]+phantom
    maxxy=max(max(abs(v.x),abs(v.y)) for v in points);maxz=max(v.z for v in points);xy=2.4/maxxy;zs=7.2/maxz
    for ob in obs:
        for v in ob.data.vertices:v.co.x*=xy;v.co.y*=xy;v.co.z*=zs
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
        for p in ob.data.polygons:p.use_smooth=True
        if ob==leaves:ob.data.normals_split_custom_set_from_vertices([Vector((v.co.x*.35,v.co.y*.35,.65)).normalized() for v in ob.data.vertices])
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.context.view_layer.objects.active=wood
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False,path_mode='RELATIVE')
    manifest={'name':name,'height':7.2,'max_width':4.8,'branch_count':branch_count,'card_count':card_count,'triangles':{ob.name:len(ob.data.polygons) for ob in obs},
      'source_axes':'Z-up','fbx_axes':'Y-up/-Z-forward; preserve root X=-90 degrees','pivot':'ground center','lod':1 if lod else 0,
      'materials':{'CW_BirchLeaves':{'texture':str(ATLAS.relative_to(ROOT)),'uv':'already addresses four quadrants; no ST remap','alpha_cutoff':.4,'cull':'Off'},
        'CW_WhiteBirchBark':{'texture':str(BARK.relative_to(ROOT)),'uv':'0..1 full dedicated birch bark texture; no ST remap'},'CW_BirchTwigs':{'color':[.16,.13,.10],'roughness':.97}},
      'branch_atlas_sha256':hashlib.sha256(ATLAS.read_bytes()).hexdigest(),'bark_texture_sha256':hashlib.sha256(BARK.read_bytes()).hexdigest(),
      'bark_source_job':'f37da558-07d4-4b9d-832c-94ab5c605428','bark_credits':2}
    (SOURCE/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2));(OUT/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2))
    return obs

full=build('CW_CardedRiverBirch');low=build('CW_CardedRiverBirch_LOD1',True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'CardedRiverBirch.blend'))
for ob in low:ob.hide_render=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.transparent_max_bounces=32;scene.render.resolution_x=1300;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Birch inspection');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.28,.33,.39,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
for pos,power,size in [((-6,-8,13),2200,9),((4,4,9),1000,7)]:
    ld=bpy.data.lights.new('Birch softbox','AREA');ld.energy=power;ld.size=size;lo=bpy.data.objects.new('Birch softbox',ld);bpy.context.collection.objects.link(lo);lo.location=pos;lo.rotation_euler=(Vector((0,0,3.5))-lo.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Birch inspection camera');cam=bpy.data.objects.new('Birch inspection camera',cd);bpy.context.collection.objects.link(cam);cam.location=(12,-16,11);cam.rotation_euler=(Vector((0,0,3.6))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=9.0;scene.camera=cam;scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/'birch-preview.png');bpy.ops.render.render(write_still=True);print('CARDED_BIRCH_COMPLETE')
