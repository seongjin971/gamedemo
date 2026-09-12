"""Radial 3D conifer with curved crossed cards using the supplied alpha branch atlas.
Does not modify supplied textures. Blender source + FBX only, no Unity operations.
"""
import bpy,bmesh,math,random,json,hashlib
from pathlib import Path
from mathutils import Vector
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5]
OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/FoliageFir'
ATLAS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/FirBranches.png'
BARK=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/WorldSurfaceAtlas.png'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
needle=bpy.data.materials.new('CW_FirNeedles');needle.use_nodes=True;bs=needle.node_tree.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.9;tex=needle.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ATLAS));tex.interpolation='Linear'
needle.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
clip=needle.node_tree.nodes.new('ShaderNodeMath');clip.operation='GREATER_THAN';clip.inputs[1].default_value=.35
needle.node_tree.links.new(tex.outputs['Alpha'],clip.inputs[0]);needle.node_tree.links.new(clip.outputs[0],bs.inputs['Alpha'])
bark=bpy.data.materials.new('CW_FirBark');bark.diffuse_color=(.22,.16,.12,1);bark.use_nodes=True
bs=bark.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.93
if BARK.exists():
    tex=bark.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(BARK));bark.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
else:bs.inputs['Base Color'].default_value=(.22,.16,.12,1)

def make_mesh(name,verts,faces,uvs,mat):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mat)
    layer=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        for li in p.loop_indices:layer.data[li].uv=uvs[me.loops[li].vertex_index]
    return ob

def tube(verts,faces,uvs,points,radii,sides):
    base=len(verts)
    for j,p in enumerate(points):
        p=Vector(p);d=(Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])).normalized();u=d.cross(Vector((0,1,0)))
        if u.length<.1:u=d.cross(Vector((1,0,0)))
        u.normalize();v=d.cross(u).normalized()
        for k in range(sides+1):
            a=k*math.tau/sides;q=p+(u*math.cos(a)+v*math.sin(a))*radii[j]*(1+.045*math.sin(k*4+j))
            verts.append(q);uvs.append((.025+.45*k/sides,.025+.45*j/(len(points)-1)))
    for j in range(len(points)-1):
        for k in range(sides):
            a=base+j*(sides+1)+k;faces.append((a,a+1,a+sides+2,a+sides+1))
    faces.append(tuple(base+k for k in reversed(range(sides))));faces.append(tuple(base+(len(points)-1)*(sides+1)+k for k in range(sides)))

def card(verts,faces,uvs,start,direction,length,width,roll,quad,seed):
    r=random.Random(seed);d=Vector(direction).normalized();side=Vector((-d.y,d.x,0));up=Vector((0,0,1));across=side*math.cos(roll)+up*math.sin(roll)
    roots=(.535,.515,.570,.565);root=roots[quad];base=len(verts);rows=6;cols=5
    qx=quad%2;qy=1-quad//2;inset=.004
    for j in range(rows):
        t=j/(rows-1);center=Vector(start)+d*(length*t)+up*(-.30*t*t+.13*t**6+.045*math.sin(t*math.pi))
        for k in range(cols):
            u=k/(cols-1);ac=(u-root)*width
            # Cross-section folds around the actual stem; branch tip and outer sprays droop.
            p=center+across*ac+up*(-.10*abs((u-root)*2)**1.5*math.sin(t*math.pi))
            verts.append(p);uvs.append((qx*.5+inset+u*(.5-2*inset),qy*.5+inset+t*(.5-2*inset)))
    for j in range(rows-1):
        for k in range(cols-1):
            a=base+j*cols+k;faces.append((a,a+1,a+cols+1,a+cols))

def build(name,lod=False):
    r=random.Random(4322);woodv=[];woodf=[];wooduv=[];leafv=[];leaff=[];leafuv=[]
    points=[(.045*math.sin(z*.75),.035*math.cos(z*.66),z) for z in (0,1,2.5,4,5.5,7,8.4,9)]
    tube(woodv,woodf,wooduv,points,[.23,.195,.15,.12,.085,.054,.027,.005],12 if not lod else 8)
    branch_count=0;card_count=0;normalization_points=[]
    for tier in range(15):
        z=1.15+tier*.51;reach=2.63*(1-(z/10.0)**1.25);count=7 if tier<8 else (6 if tier<12 else 4)
        for k in range(count):
            a=k*math.tau/count+tier*2.399+r.uniform(-.13,.13);d=Vector((math.cos(a),math.sin(a),0));start=Vector((.03*math.sin(z),0,z+r.uniform(-.12,.12)))
            length=reach*r.uniform(.88,1.1);tip=start+d*length+Vector((0,0,-.17));mid=start.lerp(tip,.5)+Vector((0,0,-.035))
            tube(woodv,woodf,wooduv,[start,mid,tip],[max(.012,.045*(1-z/11)),.018*(1-z/12),.002],5 if not lod else 4);branch_count+=1
            # Two rolled, curved surfaces share a real radial woody branch. No whole-tree cards.
            primary_roll=math.radians(r.uniform(-27,-12));secondary_roll=math.radians(r.uniform(36,53))
            card(leafv,leaff,leafuv,start,d,length,length*.95,primary_roll,(tier+k)%4,tier*44+k);card_count+=1
            if (tier+k)%3!=0:
                if not lod or (tier+k)%4==0:
                    card(leafv,leaff,leafuv,start+Vector((0,0,.015)),d,length*.96,length*.86,secondary_roll,(tier+k+1)%4,tier*81+k);card_count+=1
                else:
                    # Use full-resolution bounds for LOD scale, without retaining hidden geometry.
                    dummy=[];card(dummy,[],[],start+Vector((0,0,.015)),d,length*.96,length*.86,secondary_roll,(tier+k+1)%4,tier*81+k);normalization_points.extend(dummy)
    # A slender upright terminal shoot uses small crossed sprays, anchored at the true tree tip.
    for angle in (0,math.pi/2):
        d=Vector((math.cos(angle)*.1,math.sin(angle)*.1,.995))
        # Regular radial builder's across vector needs a horizontal main stem; build a bent summit manually.
        start=Vector((0,0,8.3));side=Vector((math.cos(angle),math.sin(angle),0));base=len(leafv)
        for j in range(5):
            t=j/4
            for k in range(3):
                u=k/2;leafv.append(start+Vector((0,0,.9*t))+side*((u-.565)*.45));leafuv.append((.504+u*.492,.004+t*.492))
        for j in range(4):
            for k in range(2):a=base+j*3+k;leaff.append((a,a+1,a+4,a+3))
        card_count+=1
    wood=make_mesh(name+'_Wood',woodv,woodf,wooduv,bark);leaves=make_mesh(name+'_Needles',leafv,leaff,leafuv,needle)
    # Keep the requested practical 5 m crown width and 9 m total height exactly.
    allvs=[v.co for ob in (wood,leaves) for v in ob.data.vertices]+normalization_points;maxxy=max(max(abs(v.x),abs(v.y)) for v in allvs);maxz=max(v.z for v in allvs)
    for ob in (wood,leaves):
        for v in ob.data.vertices:v.co.x*=2.5/maxxy;v.co.y*=2.5/maxxy;v.co.z*=9/maxz
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
        for p in ob.data.polygons:p.use_smooth=True
        if ob==leaves:
            # Foliage shading follows the canopy volume, avoiding obvious flat-card lighting.
            normals=[Vector((v.co.x*.45,v.co.y*.45,.75)).normalized() for v in ob.data.vertices]
            ob.data.normals_split_custom_set_from_vertices(normals)
    bpy.ops.object.select_all(action='DESELECT');wood.select_set(True);leaves.select_set(True);bpy.context.view_layer.objects.active=wood
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False,path_mode='RELATIVE')
    counts={ob.name:len(ob.data.polygons) for ob in (wood,leaves)}
    manifest={'name':name,'height':9,'max_width':5,'branch_count':branch_count,'card_count':card_count,'triangles':counts,
        'origin':'ground center','source_axes':'Z-up','fbx_axes':'Y-up/-Z-forward','materials':{'CW_FirNeedles':{'texture':str(ATLAS.relative_to(ROOT)),
          'uv':'already selects four atlas quadrants; do not remap','alpha_cutoff':.35,'cull':'Off','rendering':'opaque alpha clip, not blended transparency'},
          'CW_FirBark':{'texture':str(BARK.relative_to(ROOT)),'uv':'already selects bottom-left bark quadrant; do not remap'}},
        'texture_sha256':hashlib.sha256(ATLAS.read_bytes()).hexdigest(),'lod':1 if lod else 0,'snow':'no synthetic snow plates; parent may add location-based frost material after visual review'}
    (SOURCE/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2));(OUT/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2))
    return wood,leaves

full=build('CW_CardedAlpineFir');low=build('CW_CardedAlpineFir_LOD1',True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'CardedAlpineFir.blend'))
for ob in low:ob.hide_render=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.transparent_max_bounces=32
scene.render.resolution_x=1200;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Fir inspection world');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.32,.38,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
for pos,power,size in [((-6,-8,13),2300,9),((4,4,9),1000,7)]:
    ld=bpy.data.lights.new('Fir softbox','AREA');ld.energy=power;ld.size=size;lo=bpy.data.objects.new('Fir softbox',ld);bpy.context.collection.objects.link(lo);lo.location=pos;lo.rotation_euler=(Vector((0,0,4))-lo.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Fir inspection camera');cam=bpy.data.objects.new('Fir inspection camera',cd);bpy.context.collection.objects.link(cam);cam.location=(12,-16,12);cam.rotation_euler=(Vector((0,0,4.3))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=11;scene.camera=cam;scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/'fir-preview.png');bpy.ops.render.render(write_still=True)
print('CARDED_FIR_COMPLETE')
