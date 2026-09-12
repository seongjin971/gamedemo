"""Separate settled-snow meshes derived from actual upward-facing rock surfaces.
Original rock objects, normals and PBR textures are never saved over or exported.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5]
OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/SnowCover';OUT.mkdir(parents=True,exist_ok=True)
ATLAS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/WorldSurfaceAtlas.png'
PAIRS=[('CW_HF_Limestone','CW_HF_Limestone_SnowCover',ROOT/'Migration/Source/Expansion/ContinuousWorld/HiggsfieldAssets/CW_HF_Limestone.blend',ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/HiggsfieldAssets/CW_HF_Limestone/CW_HF_Limestone.fbx'),
       ('CW_LayeredRock_A','CW_LayeredRock_A_SnowCover',ROOT/'Migration/Source/Expansion/ContinuousWorld/EnvironmentKit/ContinuousWorld_EnvironmentKit.blend',ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/CW_LayeredRock_A.fbx')]

def make_mat():
    m=bpy.data.materials.new('CW_SettledSnow');m.use_nodes=True;m.diffuse_color=(.81,.85,.87,1);nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.97
    tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ATLAS),check_existing=True);uv=nt.nodes.new('ShaderNodeTexCoord')
    scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.492,.492,1);shift=nt.nodes.new('ShaderNodeVectorMath');shift.operation='ADD';shift.inputs[1].default_value=(.504,.004,0)
    nt.links.new(uv.outputs['UV'],scale.inputs[0]);nt.links.new(scale.outputs[0],shift.inputs[0]);nt.links.new(shift.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.10;bump.inputs['Distance'].default_value=.009;nt.links.new(tex.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal']);return m

for base_name,name,blendpath,fbxpath in PAIRS:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    with bpy.data.libraries.load(str(blendpath),link=False) as (src,dst):dst.objects=[base_name]
    base=dst.objects[0];bpy.context.collection.objects.link(base)
    # Source files were saved before staging previews; pivot and normalized units are retained.
    source_bounds=[[min((base.matrix_world@v.co)[i] for v in base.data.vertices) for i in range(3)],[max((base.matrix_world@v.co)[i] for v in base.data.vertices) for i in range(3)]]
    bm=bmesh.new();bm.from_mesh(base.data);bmesh.ops.transform(bm,matrix=base.matrix_world,verts=list(bm.verts));bm.faces.ensure_lookup_table();bm.verts.ensure_lookup_table();bm.normal_update()
    bvh=BVHTree.FromBMesh(bm);top=source_bounds[1][2]+1;up={};exposed={}
    for f in bm.faces:
        c=f.calc_center_median();hit=bvh.ray_cast(Vector((c.x,c.y,top)),Vector((0,0,-1)),top-source_bounds[0][2]+1)[0]
        exposed[f]=hit is not None and abs(hit.z-c.z)<.045
        threshold=.47+.055*math.sin(c.x*3.4+c.y*1.9)
        up[f]=f.normal.z>threshold and exposed[f]
    chosen={f for f in bm.faces if up[f]}
    # Soft snow spreads slightly past perfectly horizontal faces, avoiding hard polygon masks.
    for _ in range(2):
        grown=set(chosen)
        for f in chosen:
            for e in f.edges:
                for n in e.link_faces:
                    if n.normal.z>.20 and exposed[n]:grown.add(n)
        chosen=grown
    # Keep coherent settled shelves; discard tiny isolated specks or snow on grass tips.
    pending=set(chosen);components=[]
    while pending:
        seed=pending.pop();group={seed};queue=[seed]
        while queue:
            f=queue.pop()
            for e in f.edges:
                for n in e.link_faces:
                    if n in pending:pending.remove(n);group.add(n);queue.append(n)
        if sum(f.calc_area() for f in group)>=.055:components.append(group)
    chosen=set().union(*components) if components else set();assert chosen,'No snow shelves selected'
    ids={};verts=[];faces=[]
    for f in chosen:
        face=[]
        for v in f.verts:
            if v not in ids:ids[v]=len(verts);verts.append(v.co.copy())
            face.append(ids[v])
        faces.append(face)
    bm.free();me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();cap=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(cap)
    cap.data.materials.append(make_mat());bpy.ops.object.select_all(action='DESELECT');cap.select_set(True);bpy.context.view_layer.objects.active=cap
    # Consolidate micronormal noise while retaining the actual fractured shelf outline.
    dec=cap.modifiers.new('Snow shelf simplification','DECIMATE');dec.ratio=.32 if len(me.polygons)>4000 else .82;bpy.ops.object.modifier_apply(modifier=dec.name)
    smooth=cap.modifiers.new('Settled surface smoothing','SMOOTH');smooth.factor=.52;smooth.iterations=3;bpy.ops.object.modifier_apply(modifier=smooth.name)
    # Project the softened sheet onto the source surface with a small air-free contact offset.
    shrink=cap.modifiers.new('Conform to original rock','SHRINKWRAP');shrink.target=base;shrink.wrap_method='NEAREST_SURFACEPOINT';shrink.offset=.012;bpy.ops.object.modifier_apply(modifier=shrink.name)
    # Modulate thickness gently over space, then close with real rounded volume.
    for v in cap.data.vertices:v.co.z+=.022+.012*math.sin(v.co.x*2.1+v.co.y*.8)
    depth=.16 if base_name=='CW_HF_Limestone' else .12
    solid=cap.modifiers.new('Settled snow depth','SOLIDIFY');solid.thickness=depth;solid.offset=1;solid.use_even_offset=False;bpy.ops.object.modifier_apply(modifier=solid.name)
    remesh=cap.modifiers.new('Coherent softly settled snow volume','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.046 if base_name=='CW_HF_Limestone' else .032;remesh.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth=cap.modifiers.new('Round melted snow lips','SMOOTH');smooth.factor=.85;smooth.iterations=7;bpy.ops.object.modifier_apply(modifier=smooth.name)
    dec=cap.modifiers.new('Practical snow topology','DECIMATE');dec.ratio=.18;bpy.ops.object.modifier_apply(modifier=dec.name)
    bm=bmesh.new();bm.from_mesh(cap.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='EAR_CLIP')
    bad=[f for f in bm.faces if f.calc_area()<1e-10]
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cap.data);bm.free();cap.data.validate(clean_customdata=False);cap.data.update()
    for p in cap.data.polygons:p.use_smooth=True
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(65),island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT');cap.data.calc_loop_triangles()
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False)
    manifest={'name':name,'paired_model':base_name,'paired_fbx':str(fbxpath.relative_to(ROOT)),'paired_fbx_sha256':hashlib.sha256(fbxpath.read_bytes()).hexdigest(),
       'source_axes':'Z-up; same normalized source coordinates and pivot as paired model','fbx_axes':'Y-up/-Z-forward; root X=-90 degrees',
       'placement':'Instantiate rock and cap under identical world wrapper transforms; preserve each imported FBX root conversion. Do not rotate twice by parenting cap beneath an already converted mesh node.',
       'source_rock_bounds':source_bounds,'cap_bounds':[[min(v.co[i] for v in cap.data.vertices) for i in range(3)],[max(v.co[i] for v in cap.data.vertices) for i in range(3)]],
       'selected_shelf_components':len(components),'triangles':len(cap.data.loop_triangles),'zero_area_triangles':sum(t.area<1e-10 for t in cap.data.loop_triangles),
       'material':'CW_SettledSnow','uv':'0..1 UV0; parent material ST selects WSA bottom-right snow quadrant','nominal_snow_depth':depth}
    (SOURCE/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2));(OUT/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(name+'-pair.blend')))
    # Optional cap-only LOD: original cap remains unchanged.
    lod=cap.copy();lod.data=cap.data.copy();bpy.context.collection.objects.link(lod);lod.name=name+'_LOD1';bpy.context.view_layer.objects.active=lod
    mod=lod.modifiers.new('Snow cap LOD1','DECIMATE');mod.ratio=.5;bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(lod.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-10]
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    bm.to_mesh(lod.data);bm.free();lod.data.validate(clean_customdata=False);lod.data.update();bpy.ops.object.select_all(action='DESELECT');lod.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(OUT/(lod.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False)
    manifest['lod1_triangles']=len(lod.data.polygons);(SOURCE/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2));(OUT/(name+'-manifest.json')).write_text(json.dumps(manifest,indent=2));bpy.data.objects.remove(lod,do_unlink=True)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.render.resolution_x=1300;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
    world=bpy.data.worlds.new('Snow inspection');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.30,.36,.43,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
    dims=Vector(source_bounds[1])-Vector(source_bounds[0]);extent=max(dims);height=dims.z
    for pos,power,size in [((-extent,-extent,extent*1.7),130*extent*extent,extent),((extent,extent,extent),65*extent*extent,extent)]:
        ld=bpy.data.lights.new('Snow softbox','AREA');ld.energy=power;ld.size=size;lo=bpy.data.objects.new('Snow softbox',ld);bpy.context.collection.objects.link(lo);lo.location=pos;lo.rotation_euler=(Vector((0,0,height*.45))-lo.location).to_track_quat('-Z','Y').to_euler()
    cd=bpy.data.cameras.new('Snow inspection camera');cam=bpy.data.objects.new('Snow inspection camera',cd);bpy.context.collection.objects.link(cam);cam.location=(extent*1.2,-extent*1.7,height*.7+extent*.55);cam.rotation_euler=(Vector((0,0,height*.45))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=extent*1.38;scene.camera=cam;scene.view_settings.view_transform='AgX'
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/(name+'-preview.png'));bpy.ops.render.render(write_still=True);print('SNOW_COVER_COMPLETE '+name)
