"""Run in background Blender against the exported source .blend; writes numeric QA only."""
import bpy, math, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
SOURCE=Path(__file__).resolve().parent
OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'ContinuousWorld_EnvironmentKit.blend'))
manifest=json.loads((SOURCE/'manifest.json').read_text())
report={'models':{},'passed':True,'scope':'mesh integrity and FBX roundtrip only; not Unity visual or performance acceptance'}
for name,entry in manifest['models'].items():
    checks=[]; tris=0
    for objname in entry['objects']:
        ob=bpy.data.objects[objname]; me=ob.data; me.calc_loop_triangles(); tris+=len(me.loop_triangles)
        small=sum(t.area<1e-10 for t in me.loop_triangles)
        finite=all(math.isfinite(c) for v in me.vertices for c in v.co)
        uv=bool(me.uv_layers) and all(math.isfinite(c) for u in me.uv_layers.active.data for c in u.uv)
        checks.append({'object':objname,'triangles':len(me.loop_triangles),'zero_area_triangles':small,'finite_vertices':finite,'finite_uvs':uv})
    good=tris==entry['triangles'] and all(x['finite_vertices'] and x['finite_uvs'] and x['zero_area_triangles']==0 for x in checks)
    report['models'][name]={'passed':good,'source':checks}; report['passed'] &= good
for name,entry in manifest['models'].items():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(OUT/entry['file']))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    triangles=0
    for ob in meshes: ob.data.calc_loop_triangles(); triangles+=len(ob.data.loop_triangles)
    good=triangles==entry['triangles'] and len(meshes)==len(entry['objects'])
    report['models'][name]['fbx_roundtrip']={'passed':good,'triangles':triangles,'mesh_objects':len(meshes)}
    report['passed'] &= good
(ROOT/'.dream-loop/continuous-world/assets/mesh-audit.json').write_text(json.dumps(report,indent=2))
print('ENVIRONMENT_KIT_AUDIT_PASS='+str(report['passed']))
