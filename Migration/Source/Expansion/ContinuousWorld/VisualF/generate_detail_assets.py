import bpy,bmesh,math,random,json,ast
from pathlib import Path
from mathutils import Vector
SOURCE=Path(__file__).resolve().parent/'DetailAssets';SOURCE.mkdir(exist_ok=True)
ROOT=Path(__file__).resolve().parents[5]
ATLAS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/WorldSurfaceAtlas.png'
helper=ast.parse((ROOT/'Migration/Source/Expansion/ContinuousWorld/EnvironmentKit/BridgeHero/generate_bridge_hero.py').read_text())
for n in helper.body:
    if isinstance(n,ast.FunctionDef) and n.name in {'mat','mesh','bevel','block','slab'}:exec(compile(ast.Module(body=[n],type_ignores=[]),'<preserved helper>','exec'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M=[mat('CW_ChapelPavingStone',(.39,.4,.38)),mat('CW_ChapelPavingStoneLight',(.45,.45,.42)),mat('CW_ChapelJointShadow',(.17,.19,.18))]
records=[]
for variant in range(3):
    r=random.Random(1907+variant*41);parts=[];ys=[-2,-.76+r.uniform(-.1,.1),.67+r.uniform(-.13,.13),2]
    for row in range(3):
        cuts=[-2,-.68+r.uniform(-.29,.23),.69+r.uniform(-.2,.24),2]
        for k in range(3):
            ob=slab(cuts[k]+.018,cuts[k+1]-.018,ys[row]+.018,ys[row+1]-.018,3901+variant*311+row*51+k)
            parts.append(ob)
    parts.append(block('Recessed earth between broad stones',(-2,2,-2,2,-.15,-.05),18+variant,2,0,.01))
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];name='CW_BroadPaving_'+str(variant+1);ob.name=name
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    bpy.ops.export_scene.fbx(filepath=str(SOURCE/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False)
    records.append({'name':name,'slabs':9,'triangles':len(ob.data.polygons),'walkingCollider':'separate existing continuous surface'})
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'BroadPaving.blend'))
(SOURCE/'paving-manifest.json').write_text(json.dumps(records,indent=2))
# Full adapted reed source is persisted; the earlier script/FBX are never overwritten.
s=(ROOT/'Migration/Source/Expansion/ContinuousWorld/EnvironmentKit/ReedBand/generate_reed_band.py').read_text()
start=s.index('SOURCE=');end=s.index("bpy.ops.object.select_all",start)
s=s[:start]+"SOURCE=Path("+repr(str(SOURCE))+ ");OUT=SOURCE\n"+s[end:]
s=s[:s.index('scene=bpy.context.scene')]
s=s.replace('range(480)','range(300)').replace('[.005,.0042,.0011]','[.010,.0075,.002]')
s=s.replace('r.uniform(.009,.017)','r.uniform(.022,.04)').replace('r.uniform(.025,.18)','r.uniform(.10,.38)')
s=s.replace('[.009,.014,.003]','[.018,.032,.006]').replace('CW_GoldenReedBand4m','CW_ReedVolume').replace('GoldenReedBand.blend','ReedVolume.blend')
(SOURCE/'generate_reeds_adapted.py').write_text(s)
exec(compile(s,str(SOURCE/'generate_reeds_adapted.py'),'exec'))
print('VISUAL_F_DETAIL_ASSETS_READY')
