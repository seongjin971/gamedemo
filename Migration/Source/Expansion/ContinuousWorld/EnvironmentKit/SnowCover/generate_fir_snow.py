"""Snow pockets on alpha-supported curved fir sprays, in the untouched original basis."""
import bpy,bmesh,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
import numpy as np
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/SnowCover'
BASE=ROOT/'Migration/Source/Expansion/ContinuousWorld/EnvironmentKit/FoliageFir/CardedAlpineFir.blend'
PAIR=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/FoliageFir/CW_CardedAlpineFir.fbx'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(BASE),link=False) as (src,dst):dst.objects=['CW_CardedAlpineFir_Wood','CW_CardedAlpineFir_Needles']
for ob in dst.objects:bpy.context.collection.objects.link(ob)
wood,leaves=dst.objects;me=leaves.data
image=bpy.data.images.load(str(ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/FirBranches.png'),check_existing=True)
pixels=np.array(image.pixels[:],dtype=np.float32).reshape(image.size[1],image.size[0],4);h,w=pixels.shape[:2]
vertex_uv={}
for loop in me.loops:vertex_uv[loop.vertex_index]=me.uv_layers.active.data[loop.index].uv.copy()
verts=[];faces=[];r=random.Random(91247);used=0
for start in range(0,len(me.vertices)-29,30):
    cv=[me.vertices[start+i].co.copy() for i in range(30)]
    # Source main branch cards are six longitudinal rows by five folded columns.
    along=cv[5]-cv[0];across=cv[1]-cv[0];n=across.cross(along).normalized()
    if abs(n.z)<.81 or r.random()>.48 or cv[0].z>7.8:continue
    if (cv[25]-cv[0]).length<.5:continue
    grid={};cols=29;rows=37;local_count=0
    for j in range(rows):
        t=.16+.77*j/(rows-1);rt=t*5;ri=min(4,int(rt));rf=rt-ri
        for k in range(cols):
            u=.035+.93*k/(cols-1);ct=u*4;ci=min(3,int(ct));cf=ct-ci
            p=cv[ri*5+ci].lerp(cv[ri*5+ci+1],cf).lerp(cv[(ri+1)*5+ci].lerp(cv[(ri+1)*5+ci+1],cf),rf)
            uv=vertex_uv[start+ri*5+ci].lerp(vertex_uv[start+ri*5+ci+1],cf).lerp(vertex_uv[start+(ri+1)*5+ci].lerp(vertex_uv[start+(ri+1)*5+ci+1],cf),rf)
            # Alpha support uses supplied needles; branch snow never spans transparent air.
            alpha=pixels[min(h-1,max(0,int(uv.y*h))),min(w-1,max(0,int(uv.x*w))),3]
            keep=alpha>.65 and abs(u-.54)<(.36-.20*t) and math.sin(t*24+start*.04)+math.cos(u*19)>-.7
            if keep:grid[(j,k)]=len(verts);verts.append(p+Vector((0,0,.04)));local_count+=1
    for j in range(rows-1):
        for k in range(cols-1):
            keys=[(j,k),(j,k+1),(j+1,k+1),(j+1,k)]
            if all(key in grid for key in keys):faces.append(tuple(grid[key] for key in keys))
    used+=1
name='CW_CardedAlpineFir_SnowCover';mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();cap=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(cap)
bpy.ops.object.select_all(action='DESELECT');cap.select_set(True);bpy.context.view_layer.objects.active=cap
bm=bmesh.new();bm.from_mesh(mesh);loose=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=loose,context='VERTS');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
solid=cap.modifiers.new('Needle snow thickness','SOLIDIFY');solid.thickness=.075;solid.offset=1;solid.use_even_offset=False;bpy.ops.object.modifier_apply(modifier=solid.name)
rem=cap.modifiers.new('Settled small needle pillows','REMESH');rem.mode='VOXEL';rem.voxel_size=.022;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
smooth=cap.modifiers.new('Soft settled edges','SMOOTH');smooth.factor=.7;smooth.iterations=3;bpy.ops.object.modifier_apply(modifier=smooth.name)
dec=cap.modifiers.new('Practical branch snow topology','DECIMATE');dec.ratio=.055;bpy.ops.object.modifier_apply(modifier=dec.name)
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-8]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.validate(clean_customdata=False);mesh.update()
for p in mesh.polygons:p.use_smooth=True
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(65),island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
mat=bpy.data.materials.new('CW_SettledSnow');mat.use_nodes=True;nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.81,.85,.87,1);bs.inputs['Roughness'].default_value=.97;mesh.materials.append(mat)
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/WorldSurfaceAtlas.png'),check_existing=True);uv=nt.nodes.new('ShaderNodeTexCoord');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.492,.492,1);shift=nt.nodes.new('ShaderNodeVectorMath');shift.operation='ADD';shift.inputs[1].default_value=(.504,.004,0);nt.links.new(uv.outputs['UV'],scale.inputs[0]);nt.links.new(scale.outputs[0],shift.inputs[0]);nt.links.new(shift.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
def bounds(objects):
    vs=[ob.matrix_world@v.co for ob in objects for v in ob.data.vertices];return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def export(ob):
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.fbx(filepath=str(OUT/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False)
export(cap);manifest={'name':name,'paired_model':'CW_CardedAlpineFir','paired_fbx':str(PAIR.relative_to(ROOT)),'paired_fbx_sha256':hashlib.sha256(PAIR.read_bytes()).hexdigest(),'source_rock_bounds':bounds([wood,leaves]),'cap_bounds':bounds([cap]),'triangles':len(mesh.polygons),'snow_branch_groups':used,'material':'CW_SettledSnow','uv':'0..1; parent material ST selects WSA bottom-right snow','placement':'Identical wrapper transform and original pivot as paired fir, preserving -90 X root. These are sparse pockets, not full-branch blankets.'}
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(name+'-pair.blend')))
lod=cap.copy();lod.data=cap.data.copy();lod.name=name+'_LOD1';bpy.context.collection.objects.link(lod);bpy.context.view_layer.objects.active=lod;dec=lod.modifiers.new('LOD1','DECIMATE');dec.ratio=.5;bpy.ops.object.modifier_apply(modifier=dec.name)
bm=bmesh.new();bm.from_mesh(lod.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-8]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
bm.to_mesh(lod.data);bm.free();lod.data.validate(clean_customdata=False);lod.data.update();export(lod);manifest['lod1_triangles']=len(lod.data.polygons);bpy.data.objects.remove(lod,do_unlink=True)
(SOURCE/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2));(OUT/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.transparent_max_bounces=32;scene.render.resolution_x=1200;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Snow fir inspection');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.32,.38,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
for pos,power,size in [((-6,-8,13),2300,9),((4,4,9),1000,7)]:
    ld=bpy.data.lights.new('Fir softbox','AREA');ld.energy=power;ld.size=size;lo=bpy.data.objects.new('Fir softbox',ld);bpy.context.collection.objects.link(lo);lo.location=pos;lo.rotation_euler=(Vector((0,0,4))-lo.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Fir inspection camera');cam=bpy.data.objects.new('Fir inspection camera',cd);bpy.context.collection.objects.link(cam);cam.location=(12,-16,12);cam.rotation_euler=(Vector((0,0,4.3))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=11;scene.camera=cam;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/(name+'-preview.png'));bpy.ops.render.render(write_still=True);print('FIR_SNOW_COMPLETE')
