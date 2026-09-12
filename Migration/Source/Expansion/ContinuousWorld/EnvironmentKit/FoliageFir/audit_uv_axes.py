import bpy,json,math
from pathlib import Path
from mathutils import Vector
from io_scene_fbx import parse_fbx
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5]
BASE=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit'
report={}
paths=list(BASE.glob('*.fbx'))+list((BASE/'Chapel').glob('*.fbx'))+list((BASE/'FoliageFir').glob('*.fbx'))
for path in paths:
    parsed,ver=parse_fbx.parse(str(path));raw=[]
    for e in parsed.elems:
        if e.id!=b'Objects':continue
        for model in e.elems:
            if model.id!=b'Model':continue
            props={}
            for child in model.elems:
                if child.id!=b'Properties70':continue
                for p in child.elems:
                    if p.id==b'P' and p.props[0] in (b'Lcl Rotation',b'Lcl Scaling',b'Lcl Translation'):
                        props[p.props[0].decode()]=list(p.props[4:])
            raw.append({'name':str(model.props[1]),'transform':props})
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(path))
    slots={};tris=0;zero=0;bounds=[]
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        me=ob.data;me.calc_loop_triangles();tris+=len(me.loop_triangles);zero+=sum(t.area<1e-10 for t in me.loop_triangles)
        bounds.extend([ob.matrix_world@v.co for v in me.vertices])
        for p in me.polygons:
            name=me.materials[p.material_index].name if me.materials else 'none';slot=slots.setdefault(name,{'u_min':float('inf'),'u_max':-float('inf'),'v_min':float('inf'),'v_max':-float('inf')})
            for i in p.loop_indices:
                u,v=me.uv_layers.active.data[i].uv;slot['u_min']=min(slot['u_min'],u);slot['u_max']=max(slot['u_max'],u);slot['v_min']=min(slot['v_min'],v);slot['v_max']=max(slot['v_max'],v)
    report[path.stem]={'raw_fbx_models':raw,'materials':slots,'triangles':tris,'zero_area_triangles':zero,
         'blender_world_bounds':[[min(v[i] for v in bounds) for i in range(3)],[max(v[i] for v in bounds) for i in range(3)]]}
(SOURCE/'uv-axis-audit.json').write_text(json.dumps(report,indent=2));print('UV_AXIS_AUDIT_COMPLETE')
