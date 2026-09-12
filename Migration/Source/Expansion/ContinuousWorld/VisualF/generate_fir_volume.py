"""Authored twig-level conifers; existing generated branch atlas stays byte-identical.
Creates new source/FBX only. Unity import and visual adoption are separate.
"""
import bpy,bmesh,math,random,json,ast,hashlib
from pathlib import Path
from mathutils import Vector
SOURCE=Path(__file__).resolve().parent/'FirVolume';SOURCE.mkdir(exist_ok=True)
ROOT=Path(__file__).resolve().parents[5]
ATLAS=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Textures/FirBranches.png'
old=ROOT/'Migration/Source/Expansion/ContinuousWorld/EnvironmentKit/FoliageFir/generate_foliage_fir.py'
# Reuse reviewed mesh/UV helpers, never execute the old generation entry point.
tree=ast.parse(old.read_text())
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in {'make_mesh','tube','card'}:
        code=ast.unparse(node)
        if node.name=='card':
            code=code.replace('rows = 6','rows = 3').replace('cols = 5','cols = 3')
            code=code.replace('-0.3 * t * t + 0.13 * t ** 6 + 0.045 * math.sin(t * math.pi)','length * (-0.11 * t * t + 0.045 * t ** 6 + 0.02 * math.sin(t * math.pi))')
        exec(code)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
needle=bpy.data.materials.new('CW_FirNeedles');needle.use_nodes=True
bs=needle.node_tree.nodes.get('Principled BSDF');tex=needle.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ATLAS))
needle.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);needle.node_tree.links.new(tex.outputs['Alpha'],bs.inputs['Alpha']);bs.inputs['Roughness'].default_value=.87
bark=bpy.data.materials.new('CW_FirBark');bark.diffuse_color=(.22,.17,.13,1)
snow=bpy.data.materials.new('CW_Snow');snow.diffuse_color=(.82,.87,.9,1)
manifest=[]
for variant in range(2):
    r=random.Random(5407+variant*61);wv=[];wf=[];wu=[];lv=[];lf=[];lu=[];sv=[];sf=[];su=[]
    tube(wv,wf,wu,[(.03*math.sin(z),0,z) for z in [0,1.5,3,4.5,6,7.5,9]],[.19,.15,.12,.09,.065,.034,.004],8)
    branches=0;sprays=0
    for tier in range(13):
        z=1.25+tier*.55;reach=2.35*(1-(z/9.5)**1.25);count=6 if tier<9 else 4
        for k in range(count):
            a=k*math.tau/count+tier*2.399+r.uniform(-.2,.2);d=Vector((math.cos(a),math.sin(a),0));side=Vector((-d.y,d.x,0))
            start=Vector((0,0,z+r.uniform(-.12,.12)));length=reach*r.uniform(.84,1.14)
            tip=start+d*length+Vector((0,0,-.15));tube(wv,wf,wu,[start,start.lerp(tip,.55),tip],[.032,.016,.002],4);branches+=1
            for j in range(4):
                fraction=.2+j*.23;anchor=start+d*length*fraction+Vector((0,0,-.13*fraction))
                for sign in [-1,1]:
                    td=(d*.6+side*sign*.8+Vector((0,0,r.uniform(-.2,.1)))).normalized()
                    tl=max(.18,length*(.46-.06*j));end=anchor+td*tl
                    tube(wv,wf,wu,[anchor,end],[.009,.0015],3)
                    card(lv,lf,lu,anchor,td,tl,tl*.90,math.radians(r.uniform(-40,55)),(tier+k+j)%4,variant*9000+tier*77+k*9+j)
                    # Twig sprays have several orientations; there is no branch-sized plane.
                    card(lv,lf,lu,anchor+td*tl*.25,td,tl*.72,tl*.55,math.radians(r.uniform(65,110)),(tier+k+j+1)%4,variant*3000+tier*91+k+j)
                    sprays+=2
                    if (tier+k+j+variant)%3!=0:
                        # Closed narrow snow mass along this woody twig, with an irregular rim.
                        center=anchor+td*tl*.48+Vector((0,0,.035));across=Vector((-td.y,td.x,0)).normalized();base=len(sv);n=7
                        for ring in range(3):
                            rr=[1,.82,.12][ring];height=[0,.075,.11][ring]*r.uniform(.7,1.2)
                            for q in range(n):
                                angle=math.tau*q/n;v=center+td*(math.cos(angle)*tl*.38*rr)+across*(math.sin(angle)*tl*.105*rr)+Vector((0,0,height))
                                sv.append(v);su.append((v.x*.3,v.y*.3))
                        for ring in range(2):
                            for q in range(n):sf.append((base+ring*n+q,base+ring*n+(q+1)%n,base+(ring+1)*n+(q+1)%n,base+(ring+1)*n+q))
                        sf.append(tuple(base+2*n+q for q in range(n)))
            card(lv,lf,lu,start+d*length*.68,d,max(.2,length*.42),max(.12,length*.28),.25,(tier+k)%4,tier*171+k)
    name='CW_FirVolume_'+str(variant+1)
    obs=[make_mesh(name+'_Wood',wv,wf,wu,bark),make_mesh(name+'_Needles',lv,lf,lu,needle),make_mesh(name+'_Snow',sv,sf,su,snow)]
    for ob in obs:
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
        for face in ob.data.polygons:face.use_smooth=True
        if ob.name.endswith('_Needles'):
            ob.data.normals_split_custom_set_from_vertices([Vector((v.co.x*.3,v.co.y*.3,.85)).normalized() for v in ob.data.vertices])
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    bpy.ops.export_scene.fbx(filepath=str(SOURCE/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False)
    manifest.append({'name':name,'branches':branches,'twigSprays':sprays,'triangles':{o.name:len(o.data.polygons) for o in obs},'assetAdoption':'pending actual Unity comparison','existingTextureSha256':hashlib.sha256(ATLAS.read_bytes()).hexdigest(),'newGenerationCredits':0})
    for ob in obs:ob.hide_render=variant==0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'FirVolume.blend'))
(SOURCE/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest))
