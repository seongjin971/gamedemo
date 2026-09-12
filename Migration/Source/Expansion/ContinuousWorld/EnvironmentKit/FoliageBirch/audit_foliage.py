import bpy,json,math
from pathlib import Path
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];BASE=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit'
report={'passed':True,'models':{}}
for folder in ('FoliageFir','FoliageBirch'):
    for mp in (BASE/folder).glob('*-manifest.json'):
        m=json.loads(mp.read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(mp.parent/(m['name']+'.fbx')))
        tris=0;zero=0;finite=True;alltri=True;uv=True;slots={};bounds=[]
        for ob in bpy.context.scene.objects:
            if ob.type!='MESH':continue
            me=ob.data;me.calc_loop_triangles();tris+=len(me.loop_triangles);zero+=sum(t.area<1e-10 for t in me.loop_triangles);finite &= all(math.isfinite(c) for v in me.vertices for c in v.co);alltri &= all(len(p.vertices)==3 for p in me.polygons);uv &= bool(me.uv_layers)
            bounds.extend([ob.matrix_world@v.co for v in me.vertices])
            for p in me.polygons:
                key=me.materials[p.material_index].name;slot=slots.setdefault(key,[1e9,-1e9,1e9,-1e9])
                for i in p.loop_indices:
                    u,v=me.uv_layers.active.data[i].uv;slot[0]=min(slot[0],u);slot[1]=max(slot[1],u);slot[2]=min(slot[2],v);slot[3]=max(slot[3],v)
        expected=sum(m['triangles'].values());passed=tris==expected and zero==0 and finite and alltri and uv
        report['models'][m['name']]={'passed':passed,'triangles':tris,'zero_area_triangles':zero,'finite':finite,'all_triangular':alltri,'uvs':uv,'uv_bounds_per_material_umin_umax_vmin_vmax':slots,
            'blender_world_bounds':[[min(v[i] for v in bounds) for i in range(3)],[max(v[i] for v in bounds) for i in range(3)]]};report['passed'] &= passed
(SOURCE/'foliage-fbx-audit.json').write_text(json.dumps(report,indent=2));print('FOLIAGE_FBX_AUDIT_PASS='+str(report['passed']))
