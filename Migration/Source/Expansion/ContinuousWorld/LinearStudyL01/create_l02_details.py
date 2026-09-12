"""New authored Blender geometry; originals are read-only helpers, never executed."""
import bpy,bmesh,math,random,json,ast
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[5]
SOURCE=Path(__file__).resolve().parent/'L02Details'
OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/LinearWorld/Art/EnvironmentKit/L02Details'
if OUT.exists():raise RuntimeError('Refuse existing detail bundle')
SOURCE.mkdir(exist_ok=True);OUT.mkdir(parents=True)
ATLAS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/WorldSurfaceAtlas.png'
helper=ast.parse((ROOT/'Migration/Source/Expansion/ContinuousWorld/EnvironmentKit/BridgeHero/generate_bridge_hero.py').read_text())
for n in helper.body:
    if isinstance(n,ast.FunctionDef) and n.name in {'mat','mesh','bevel','block','slab'}:exec(compile(ast.Module(body=[n],type_ignores=[]),'<read-only helper>','exec'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M=[mat('CW_ChapelPavingStone',(.39,.4,.38)),mat('CW_ChapelPavingStoneLight',(.45,.45,.42)),mat('CW_ChapelJointShadow',(.17,.19,.18))]
records=[]
def export(parts,name):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name=name
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False)
    records.append({'name':name,'triangles':len(ob.data.polygons),'walkingCollider':'separate continuous ground'})
    return ob
for variant in range(3):
    r=random.Random(4831+variant*83);parts=[]
    for row in range(5):
        y0=-2+row*.8;y1=y0+.8;cuts=[-1.8,-.64+r.uniform(-.22,.2),.63+r.uniform(-.2,.22),1.8]
        for col in range(3):
            inset=r.uniform(.025,.16) if col in (0,2) else .02
            ob=slab(cuts[col]+inset,cuts[col+1]-.025,y0+.022,y1-.02,8311+variant*101+row*7+col)
            # The edge stones tilt down into soil; center retains stable travel clearance.
            for v in ob.data.vertices:v.co.z-=max(0,abs(v.co.x)-1.1)*r.uniform(.015,.07)
            parts.append(ob)
    export(parts,'LinearPaving_'+str(variant+1))
for variant in range(3):
    r=random.Random(129+variant*83);parts=[]
    for k in range(17):
        x=r.uniform(-1.65,1.65);y=r.uniform(-1.8,1.8);w=r.uniform(.20,.56);h=r.uniform(.24,.69)
        ob=slab(x-w/2,x+w/2,y-h/2,y+h/2,4200+variant*31+k)
        for v in ob.data.vertices:v.co.z-=.012+abs(x)*.005
        parts.append(ob)
    export(parts,'LinearFieldstone_'+str(variant+1))
M=[mat('CW_LinearGrassOlive',(.25,.34,.12)),mat('CW_LinearGrassLight',(.34,.40,.17)),mat('CW_LinearGrassDry',(.38,.34,.17))]
for variant in range(2):
    r=random.Random(9601+variant);parts=[]
    for group in range(3):
        vs=[];fs=[]
        for k in range(46):
            a=r.uniform(0,math.tau);rad=math.sqrt(r.random())*.42;x=math.cos(a)*rad;y=math.sin(a)*rad
            length=r.uniform(.20,.62);bend=r.uniform(.12,.35);width=r.uniform(.012,.032);angle=r.uniform(0,math.tau);dx,dy=math.cos(angle),math.sin(angle);base=len(vs)
            for j in range(4):
                t=j/3;cx=x+dx*bend*t*t;cy=y+dy*bend*t*t;z=length*t-.11*t*t
                for s in (-1,1):vs.append((cx-dy*width*(1-t)*s,cy+dx*width*(1-t)*s,z))
            for j in range(3):b=base+j*2;fs.extend([(b,b+1,b+3),(b,b+3,b+2)])
        parts.append(mesh('Curved meadow blades',vs,fs,group,False))
    export(parts,'LinearGrass_'+str(variant+1))
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'LinearGroundDetails.blend'))
(SOURCE/'manifest.json').write_text(json.dumps(records,indent=2))
print('LINEAR_L02_DETAILS_COMPLETE')
