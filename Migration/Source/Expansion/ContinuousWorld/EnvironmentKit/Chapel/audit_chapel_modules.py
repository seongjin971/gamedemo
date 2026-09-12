import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/Chapel'
report={'passed':True,'models':{}}
for p in SOURCE.glob('*-manifest.json'):
    m=json.loads(p.read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(OUT/(m['name']+'.fbx')))
    obs=[ob for ob in bpy.context.scene.objects if ob.type=='MESH'];vs=[];fs=[];zero=0;tri=0;uv=True
    for ob in obs:
        off=len(vs);vs.extend([ob.matrix_world@v.co for v in ob.data.vertices]);fs.extend([[off+i for i in p.vertices] for p in ob.data.polygons]);ob.data.calc_loop_triangles()
        tri+=len(ob.data.loop_triangles);zero+=sum(t.area<1e-10 for t in ob.data.loop_triangles);uv &= bool(ob.data.uv_layers)
    bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
    clear=all(bvh.ray_cast(Vector((r['x'],-1,r['height'])),Vector((0,1,0)),2)[0] is None for r in m['aperture_ray_checks'])
    solid=all(bvh.ray_cast(Vector((r['x'],-1,r['height'])),Vector((0,1,0)),2)[0] is not None for r in m['solid_wall_ray_checks'])
    passed=tri==m['triangles'] and zero==0 and uv and clear and solid and all(len(f)==3 for f in fs)
    report['models'][m['name']]={'passed':passed,'triangles':tri,'zero_area_triangles':zero,'uvs_present':uv,'all_triangular':all(len(f)==3 for f in fs),
        'open_aperture_rays':len(m['aperture_ray_checks']),'open_aperture_all_clear':clear,'solid_wall_rays_hit':solid}
    report['passed'] &= passed
(SOURCE/'fbx-aperture-audit.json').write_text(json.dumps(report,indent=2));print('CHAPEL_FBX_AUDIT_PASS='+str(report['passed']))
