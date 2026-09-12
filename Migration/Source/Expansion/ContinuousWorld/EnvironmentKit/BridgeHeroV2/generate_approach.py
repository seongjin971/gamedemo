import bpy,bmesh,math,random,json,ast
from pathlib import Path
from mathutils import Vector
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/BridgeHeroV2';ATLAS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/WorldSurfaceAtlas.png'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for node in ast.parse((SOURCE/'generate_bridge_hero_v2.py').read_text()).body:
    if isinstance(node,ast.FunctionDef) and node.name in {'mat','mesh','bevel','block','slab'}:exec(compile(ast.Module(body=[node],type_ignores=[]),'<bridge helpers>','exec'))
M=[mat('CW_BridgeStone',(.40,.39,.345)),mat('CW_BridgeStoneLight',(.44,.425,.37)),mat('CW_BridgeMortar',(.22,.225,.20))]
parts=[];rects=[];r=random.Random(12945);nx,ny=10,12;used=set()
for row in range(ny):
    for col in range(nx):
        if (col,row) in used:continue
        choices=[(2,2),(3,2),(3,3),(2,3),(2,2)];r.shuffle(choices);choices.extend([(1,2),(2,1),(1,1)])
        for cw,ch in choices:
            if col+cw<=nx and row+ch<=ny and all((x,y) not in used for x in range(col,col+cw) for y in range(row,row+ch)):break
        used.update((x,y) for x in range(col,col+cw) for y in range(row,row+ch))
        x0=-3+col*.6+.014;x1=-3+(col+cw)*.6-.014;y0=-4+row*(8/12)+.014;y1=-4+(row+ch)*(8/12)-.014
        # Ragged outer lips create a natural approach edge, without introducing walking steps.
        if col==0:x0+=r.uniform(0,.16)
        if col+cw==nx:x1-=r.uniform(0,.16)
        ob=slab(x0,x1,y0,y1,2945+row*67+col)
        for v in ob.data.vertices:
            if v.co.z>-.01:v.co.z=max(0,min(.008,v.co.z+.002))
        parts.append(ob);rects.append([x0,x1,y0,y1])
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name='CW_BridgeApproach6x8m'
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces),ngon_method='EAR_CLIP');bad=[f for f in bm.faces if f.calc_area()<1e-8]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.validate(clean_customdata=False);ob.data.update()
manifest={'name':ob.name,'triangles':len(ob.data.polygons),'nominal_size_width_length':[6,8],'bounds_source_xyz':[[min(v.co[i] for v in ob.data.vertices) for i in range(3)],[max(v.co[i] for v in ob.data.vertices) for i in range(3)]],'stone_slabs':len(parts),'paving_cells_xy':rects,'top':'0..+.008 nominal deck; chipped edges recessed, no steps; parent owns smooth collider','pivot':'nominal deck center0','uv':'0..1; calm cropped stone detail, parent WSA top-right ST','fbx_axes':'Y-up/-Z-forward, preserve -90X root'}
bpy.ops.export_scene.fbx(filepath=str(OUT/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',mesh_smooth_type='FACE',use_tspace=True,bake_anim=False)
(SOURCE/'approach-manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'approach-manifest.json').write_text(json.dumps(manifest,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'BridgeApproach6x8m.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.render.resolution_x=1300;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Approach inspection');world.use_nodes=True;scene.world=world;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.3,.35,.4,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
ld=bpy.data.lights.new('Approach softbox','AREA');ld.energy=2800;ld.size=10;lo=bpy.data.objects.new('Approach softbox',ld);bpy.context.collection.objects.link(lo);lo.location=(-8,-10,14);lo.rotation_euler=(-lo.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Approach camera');cam=bpy.data.objects.new('Approach camera',cd);bpy.context.collection.objects.link(cam);cam.location=(10,-14,19);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=10;scene.camera=cam;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(SOURCE/'approach-preview.png');bpy.ops.render.render(write_still=True);print('APPROACH_COMPLETE')
