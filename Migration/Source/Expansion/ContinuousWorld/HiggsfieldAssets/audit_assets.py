"""Audit generated FBX geometry and texture references; no Unity access."""
import bpy,json,math,hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[4]
OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/HiggsfieldAssets'
report={'passed':True,'assets':{},'scope':'FBX numeric integrity and local texture references; not Unity visual acceptance or performance'}
for mp in OUT.glob('*/manifest.json'):
    m=json.loads(mp.read_text()); result={'lods':{},'texture_references_exist':True}
    for mat in m['materials']:
        for paths in mat['texture_inputs'].values():
            for p in paths:
                if p is None or not (mp.parent/p).is_file():result['texture_references_exist']=False
    for suffix in ('','_LOD1'):
        path=mp.parent/(m['name']+suffix+'.fbx')
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        bpy.ops.import_scene.fbx(filepath=str(path))
        obs=[ob for ob in bpy.context.scene.objects if ob.type=='MESH']
        tri=0;zero=0;finite=True;alltri=True;uv=True
        for ob in obs:
            me=ob.data;me.calc_loop_triangles();tri+=len(me.loop_triangles);zero+=sum(t.area<1e-12 for t in me.loop_triangles)
            finite &= all(math.isfinite(c) for v in me.vertices for c in v.co)
            alltri &= all(len(p.vertices)==3 for p in me.polygons);uv &= bool(me.uv_layers)
        expected=m['lod1_triangles'] if suffix else sum(x['triangles'] for x in m['meshes'])
        good=tri==expected and zero==0 and finite and alltri and uv
        result['lods'][suffix or 'LOD0']={'passed':good,'triangles':tri,'zero_area_triangles':zero,'all_triangular':alltri,'finite_vertices':finite,'uvs_present':uv,
                                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        report['passed'] &= good
    report['passed'] &= result['texture_references_exist'];report['assets'][m['name']]=result
(ROOT/'.dream-loop/continuous-world/higgsfield-assets/mesh-audit.json').write_text(json.dumps(report,indent=2))
print('HF_ASSET_AUDIT_PASS='+str(report['passed']))
