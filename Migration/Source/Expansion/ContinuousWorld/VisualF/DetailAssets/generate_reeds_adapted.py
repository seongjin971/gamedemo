"""Dense golden bank reeds: fine 3D stems and narrow drooping leaves, no rosette cards."""
import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector
SOURCE=Path('C:\\Users\\brian\\Dev\\active\\Dream Loop Astra\\Migration\\Source\\Expansion\\ContinuousWorld\\VisualF\\DetailAssets');OUT=SOURCE
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M=[]
for name,c in [('CW_GoldenReedStem',(.54,.41,.18)),('CW_GoldenReedLight',(.72,.57,.29)),('CW_DryReedLeaf',(.43,.37,.19)),('CW_ReedSeed',(.37,.26,.115))]:
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=.92;M.append(m)
verts=[];faces=[];slots=[];uvs=[];groups=[];r=random.Random(97224)
def tube(points,radii,slot):
    base=len(verts);n=3
    for j,p in enumerate(points):
        d=(points[min(j+1,len(points)-1)]-points[max(0,j-1)]).normalized();u=d.cross(Vector((0,1,0))).normalized();v=d.cross(u).normalized()
        for k in range(n):
            q=p+(u*math.cos(k*math.tau/n)+v*math.sin(k*math.tau/n))*radii[j];verts.append(q);uvs.append((k/(n-1),j/(len(points)-1)))
    for j in range(len(points)-1):
        for k in range(n):a=base+j*n+k;b=base+j*n+(k+1)%n;faces.append((a,b,b+n,a+n));slots.append(slot)
    faces.append(tuple(base+k for k in reversed(range(n))));slots.append(slot);faces.append(tuple(base+(len(points)-1)*n+k for k in range(n)));slots.append(slot)
def leaf(root,d,length,width,slot):
    base=len(verts);side=Vector((-d.y,d.x,0)).normalized()
    for j in range(3):
        t=j/2;center=root+d*(length*t)+Vector((0,0,.11*math.sin(t*math.pi)-.17*t*t));w=width*(1-t)*(.85 if j==0 else 1)
        for k in (-1,1):verts.append(center+side*w*k);uvs.append(((k+1)/2,t))
    faces.extend([(base,base+1,base+3,base+2),(base+2,base+3,base+5,base+4)]);slots.extend([slot,slot])
for i in range(300):
    vstart,fstart=len(verts),len(faces);x=r.uniform(-2,2);y=r.uniform(-.75,.75)
    # Density is continuous, while the top profile and perimeter stay organically uneven.
    h=r.uniform(.62,1.18)*(1-.12*abs(y)/.75);a=r.uniform(0,math.tau);bend=Vector((math.cos(a),math.sin(a),0))*r.uniform(.10,.38);root=Vector((x,y,0));mid=root+Vector((0,0,h*.56))+bend*.25;tip=root+Vector((0,0,h))+bend
    tube([root,mid,tip],[.010,.0075,.002],1 if i%5<2 else 0)
    for j in range(1+(i%2)):
        t=r.uniform(.28,.70);p=root.lerp(tip,t);angle=a+r.uniform(-2,2);d=Vector((math.cos(angle),math.sin(angle),.16));leaf(p,d,r.uniform(.17,.34),r.uniform(.022,.04),2 if i%3 else 1)
    if i%7==0:
        d=(tip-mid).normalized();tube([tip-d*.13,tip-d*.055,tip+d*.008],[.018,.032,.006],3)
    groups.append((vstart,len(verts),fstart,len(faces)))
lo=Vector([min(v[i] for v in verts) for i in range(3)]);hi=Vector([max(v[i] for v in verts) for i in range(3)]);mid=(lo+hi)/2
verts=[Vector(((v.x-mid.x)*4/(hi.x-lo.x),(v.y-mid.y)*1.5/(hi.y-lo.y),(v.z-lo.z)*1.2/(hi.z-lo.z))) for v in verts]
def build(name,lod=False):
    keep=[g for i,g in enumerate(groups) if not lod or i%2==0];ids={};vv=[];uu=[];ff=[];ss=[]
    for va,vb,fa,fb in keep:
        for idx in range(va,vb):ids[idx]=len(vv);vv.append(verts[idx]);uu.append(uvs[idx])
        for idx in range(fa,fb):ff.append(tuple(ids[v] for v in faces[idx]));ss.append(slots[idx])
    me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
    for mat in M:me.materials.append(mat)
    layer=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        p.material_index=ss[p.index]
        for li in p.loop_indices:layer.data[li].uv=uu[me.loops[li].vertex_index]
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-10]
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.validate(clean_customdata=False);me.update()
    if lod:ob.name=name.replace('_LOD1','_Reduced');me.name=ob.name
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False)
    manifest={'name':name,'stem_count':len(keep),'triangles':len(me.polygons),'bounds_source_xyz':[[min(v.co[i] for v in me.vertices) for i in range(3)],[max(v.co[i] for v in me.vertices) for i in range(3)]],'full_band_size':[4,1.5,1.2],'pivot':'ground center','axes':'source X=4m band length, Y=1.5m depth, Z=1.2m up; preserve imported -90X root','materials':{m.name:list(m.diffuse_color) for m in M},'material_contract':'solid authored gold/brown colors, no texture required; leaves double-sided/cull off; stems are real tubes, no alpha cards','lod':1 if lod else 0}
    (SOURCE/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2));(OUT/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2));return ob
full=build('CW_ReedVolume');low=build('CW_ReedVolume_LOD1',True);low.hide_render=True;bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'ReedVolume.blend'))
