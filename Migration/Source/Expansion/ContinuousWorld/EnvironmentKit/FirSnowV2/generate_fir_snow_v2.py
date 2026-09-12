"""Branch-supported fir snow V2. Stage only; untouched original paired tree assets."""
import bpy,bmesh,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
import numpy as np
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];OUT=SOURCE/'staged';OUT.mkdir(parents=True,exist_ok=True)
ART=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art';BASE=ROOT/'Migration/Source/Expansion/ContinuousWorld/EnvironmentKit/FoliageFir/CardedAlpineFir.blend'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
names=['CW_CardedAlpineFir_Wood','CW_CardedAlpineFir_Needles','CW_CardedAlpineFir_LOD1_Wood','CW_CardedAlpineFir_LOD1_Needles']
with bpy.data.libraries.load(str(BASE),link=False) as (src,dst):dst.objects=names
for ob in dst.objects:bpy.context.collection.objects.link(ob)
wood,leaves,woodlow,leaveslow=dst.objects
atlas=bpy.data.images.load(str(ART/'Textures/FirBranches.png'),check_existing=True);pixels=np.array(atlas.pixels[:],dtype=np.float32).reshape(atlas.size[1],atlas.size[0],4);ih,iw=pixels.shape[:2]
snow=bpy.data.materials.new('CW_SettledSnow');snow.use_nodes=True;bs=snow.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.96
tx=snow.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ART/'Textures/SnowSurface.png'),check_existing=True);snow.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
reports={};caps=[]
def clean(ob):
    me=ob.data;bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces),ngon_method='EAR_CLIP');bad=[f for f in bm.faces if f.calc_area()<1e-9]
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.validate(clean_customdata=False);me.update()
def make_cap(leaf,name,target):
    me=leaf.data;vertex_uv={loop.vertex_index:me.uv_layers.active.data[loop.index].uv.copy() for loop in me.loops};verts=[];faces=[];selected=0;supports=[]
    for start in range(0,len(me.vertices)-30,30):
        cv=[me.vertices[start+i].co.copy() for i in range(30)];normal=(cv[1]-cv[0]).cross(cv[5]-cv[0]).normalized()
        if abs(normal.z)<.55:continue
        seed=int((cv[0].x+10)*997+(cv[0].y+10)*731+(cv[0].z+10)*431);rr=random.Random(seed)
        if abs(normal.z)<.81 and rr.random()<.36:continue
        cols,rows=31,43;positions={};alphas=np.zeros((rows,cols),dtype=bool)
        phase=rr.uniform(0,math.tau)
        for j in range(rows):
            t=.13+.80*j/(rows-1);rt=t*5;ri=min(4,int(rt));rf=rt-ri
            for k in range(cols):
                u=.045+.91*k/(cols-1);ct=u*4;ci=min(3,int(ct));cf=ct-ci
                p=cv[ri*5+ci].lerp(cv[ri*5+ci+1],cf).lerp(cv[(ri+1)*5+ci].lerp(cv[(ri+1)*5+ci+1],cf),rf)
                uv=vertex_uv[start+ri*5+ci].lerp(vertex_uv[start+ri*5+ci+1],cf).lerp(vertex_uv[start+(ri+1)*5+ci].lerp(vertex_uv[start+(ri+1)*5+ci+1],cf),rf)
                alpha=pixels[min(ih-1,max(0,int(uv.y*ih))),min(iw-1,max(0,int(uv.x*iw))),3]
                positions[(j,k)]=(p,u,t)
                alphas[j,k]=alpha>.46
        # Close only single-grid needle gaps, preserving the spray's branching outline.
        filled=alphas.copy()
        for j in range(1,rows-1):
            for k in range(1,cols-1):
                if alphas[j-1:j+2,k-1:k+2].sum()>=6:filled[j,k]=True
        grid={};offset=rr.uniform(.075,.115)
        for (j,k),(p,u,t) in positions.items():
            band=abs(u-.52)<(.34-.09*t)
            intermittent=math.sin(t*18+phase)+.42*math.cos(u*24+phase)>-.02
            if filled[j,k] and band and intermittent:
                grid[(j,k)]=len(verts);verts.append(p+Vector((0,0,offset+.018*math.sin(t*9+u*7))))
        added=0
        for j in range(rows-1):
            for k in range(cols-1):
                keys=[(j,k),(j,k+1),(j+1,k+1),(j+1,k)];valid=[grid[key] for key in keys if key in grid]
                if len(valid)>=3:faces.append(valid);added+=1
        if added:selected+=1;supports.append({'source_first_vertex':start,'upward_normal_abs_z':abs(normal.z),'patch_offset_m':offset,'retained_cells':added})
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();cap=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(cap);bpy.ops.object.select_all(action='DESELECT');cap.select_set(True);bpy.context.view_layer.objects.active=cap;clean(cap)
    so=cap.modifiers.new('Settled supported branch thickness','SOLIDIFY');so.thickness=.072;so.offset=1;so.use_even_offset=False;bpy.ops.object.modifier_apply(modifier=so.name)
    rem=cap.modifiers.new('Small connected needle snow ridges','REMESH');rem.mode='VOXEL';rem.voxel_size=.026;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
    sm=cap.modifiers.new('Rounded settling','SMOOTH');sm.factor=.65;sm.iterations=3;bpy.ops.object.modifier_apply(modifier=sm.name)
    me.calc_loop_triangles();dec=cap.modifiers.new('Practical triangle budget','DECIMATE');dec.ratio=min(1,target/max(1,len(me.loop_triangles)));bpy.ops.object.modifier_apply(modifier=dec.name);clean(cap)
    for p in me.polygons:p.use_smooth=True
    me.materials.append(snow);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(65),island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
    filename=name+'.fbx';exportname=name.replace('_LOD1','_Reduced');cap.name=exportname
    bpy.ops.export_scene.fbx(filepath=str(OUT/filename),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',mesh_smooth_type='FACE',use_tspace=True,bake_anim=False)
    bound=[[min(v.co[i] for v in me.vertices) for i in range(3)],[max(v.co[i] for v in me.vertices) for i in range(3)]];paired='CW_CardedAlpineFir'+('_LOD1' if '_LOD1' in name else '')
    report={'name':name,'exported_node':exportname,'triangles':len(me.polygons),'zero_area_triangles':sum(p.area<1e-10 for p in me.polygons),'bounds_source_xyz':bound,'materials':['CW_SettledSnow'],'paired_model':paired,'paired_fbx_sha256':hashlib.sha256((ART/'EnvironmentKit/FoliageFir'/(paired+'.fbx')).read_bytes()).hexdigest(),'supported_spray_count':selected,'source_sprays':supports,'placement':'Identical parent wrapper pos/scale/yaw as paired tree; preserve each FBX root -90 X. Cap-only derivative; original fir unchanged.','uv':'0..1 UV0; parent WSA snow quadrant ST or full SnowSurface identity ST.','diagnosis':'V1 selected only 33 sprays, narrowed alpha support, and sat close below crossed needle cards. V2 increases supported upper-spray coverage, closes only tiny alpha gaps, and uses 7.5-11.5 cm upper offsets plus settled thickness.'}
    (SOURCE/(name+'-manifest.json')).write_text(json.dumps(report,indent=2));(OUT/(name+'-manifest.json')).write_text(json.dumps(report,indent=2));reports[name]=report;caps.append(cap);return cap
full=make_cap(leaves,'CW_CardedAlpineFir_SnowCoverV2',14000);low=make_cap(leaveslow,'CW_CardedAlpineFir_SnowCoverV2_LOD1',7200)
for ob in (woodlow,leaveslow,low):ob.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'FirSnowV2-pairs.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.transparent_max_bounces=32;scene.render.resolution_x=950;scene.render.resolution_y=1150;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Snow fir inspection');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.32,.38,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.70
for pos,power,size in [((-6,-8,13),1900,8),((4,4,9),700,6)]:
    ld=bpy.data.lights.new('Fir softbox','AREA');ld.energy=power;ld.size=size;lo=bpy.data.objects.new('Fir softbox',ld);bpy.context.collection.objects.link(lo);lo.location=pos;lo.rotation_euler=(Vector((0,0,4))-lo.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Fir inspection camera');cam=bpy.data.objects.new('Fir inspection camera',cd);bpy.context.collection.objects.link(cam);cd.type='ORTHO';cd.ortho_scale=11;scene.camera=cam;scene.view_settings.view_transform='AgX';cam.location=(12,-16,17.6);cam.rotation_euler=(Vector((0,0,4.3))-cam.location).to_track_quat('-Z','Y').to_euler()
def render(name):scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/name);bpy.ops.render.render(write_still=True)
render('fir-v2-paired-preview.png')
for ob in (wood,leaves,full):ob.hide_render=True
for ob in (woodlow,leaveslow,low):ob.hide_render=False
render('fir-v2-lod1-paired-preview.png')
# Flat emission segmentation establishes controlled projected visible snow fraction.
def emission(name,color,alpha=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*color,1)
    if alpha:
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=atlas;cut=nt.nodes.new('ShaderNodeMath');cut.operation='GREATER_THAN';cut.inputs[1].default_value=.35;nt.links.new(tex.outputs['Alpha'],cut.inputs[0]);tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(cut.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(e.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
    else:nt.links.new(e.outputs[0],out.inputs[0])
    return m
leafmask=emission('Mask needles',(0,1,0),True);woodmask=emission('Mask wood',(0,1,0));snowmask=emission('Mask snow',(1,1,1))
for ob in (leaves,leaveslow):ob.data.materials.clear();ob.data.materials.append(leafmask)
for ob in (wood,woodlow):ob.data.materials.clear();ob.data.materials.append(woodmask)
for ob in caps:ob.data.materials.clear();ob.data.materials.append(snowmask)
scene.render.film_transparent=True;scene.view_settings.view_transform='Standard';scene.cycles.samples=8
render('fir-v2-lod1-coverage-mask.png')
for ob in (woodlow,leaveslow,low):ob.hide_render=True
for ob in (wood,leaves,full):ob.hide_render=False
render('fir-v2-coverage-mask.png')
print('FIR_SNOW_V2_STAGED_COMPLETE '+json.dumps({k:{'triangles':v['triangles'],'sprays':v['supported_spray_count']} for k,v in reports.items()}))
