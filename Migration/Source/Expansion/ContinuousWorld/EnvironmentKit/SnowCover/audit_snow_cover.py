import bpy,json,math,hashlib
from pathlib import Path
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/SnowCover'
report={'passed':True,'models':{}}
for mp in SOURCE.glob('*-manifest.json'):
    m=json.loads(mp.read_text());pair=ROOT/m['paired_fbx'];pair_unchanged=hashlib.sha256(pair.read_bytes()).hexdigest()==m['paired_fbx_sha256']
    for suffix,key in [('', 'triangles'),('_LOD1','lod1_triangles')]:
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);name=m['name']+suffix;bpy.ops.import_scene.fbx(filepath=str(OUT/(name+'.fbx')))
        tris=0;zero=0;finite=True;alltri=True;uv=True;bounds=[];uvs=[]
        for ob in bpy.context.scene.objects:
            if ob.type!='MESH':continue
            me=ob.data;me.calc_loop_triangles();tris+=len(me.loop_triangles);zero+=sum(t.area<1e-10 for t in me.loop_triangles);finite &= all(math.isfinite(c) for v in me.vertices for c in v.co);alltri &= all(len(p.vertices)==3 for p in me.polygons);uv &= bool(me.uv_layers)
            bounds.extend([ob.matrix_world@v.co for v in me.vertices]);uvs.extend([x.uv.copy() for x in me.uv_layers.active.data])
        measured=[[min(v[i] for v in bounds) for i in range(3)],[max(v[i] for v in bounds) for i in range(3)]]
        alignment_error=max(abs(measured[j][i]-m['cap_bounds'][j][i]) for j in range(2) for i in range(3))
        # Reimport returns original Blender basis. LOD simplification may soften extremities.
        within_bounds=alignment_error<(.0001 if not suffix else .12)
        uvbounds=[[min(v[i] for v in uvs) for i in range(2)],[max(v[i] for v in uvs) for i in range(2)]]
        uvunit=all(-1e-6<=c<=1.000001 for vv in uvbounds for c in vv)
        rock=m['source_rock_bounds'];overhang=max(max(rock[0][i]-measured[0][i],measured[1][i]-rock[1][i]) for i in range(3))
        passed=tris==m[key] and zero==0 and finite and alltri and uv and uvunit and pair_unchanged and within_bounds and overhang<.25
        report['models'][name]={'passed':passed,'triangles':tris,'zero_area_triangles':zero,'finite':finite,'all_triangular':alltri,'uv_bounds':uvbounds,'blender_world_bounds':measured,'reimport_bounds_error':alignment_error,'maximum_bounds_overhang':overhang,'paired_fbx_sha256_unchanged':pair_unchanged}
        report['passed'] &= passed
(SOURCE/'snow-fbx-audit.json').write_text(json.dumps(report,indent=2));print('SNOW_FBX_AUDIT_PASS='+str(report['passed']))
