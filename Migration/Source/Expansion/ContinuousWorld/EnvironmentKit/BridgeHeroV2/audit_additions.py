import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];ART=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit'
report={'passed':True,'models':{}}
items=[(SOURCE/'approach-manifest.json',ART/'BridgeHeroV2'),(SOURCE.parent/'ReedBand/CW_GoldenReedBand4m-manifest.json',ART/'ReedBand'),(SOURCE.parent/'ReedBand/CW_GoldenReedBand4m_LOD1-manifest.json',ART/'ReedBand')]
for mp,folder in items:
    m=json.loads(mp.read_text());name=m['name'];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(folder/(name+'.fbx')))
    vs=[];fs=[];tris=0;zero=0;uvunit=True;nodes=[]
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        nodes.append(ob.name);me=ob.data;me.calc_loop_triangles();tris+=len(me.loop_triangles);zero+=sum(t.area<1e-10 for t in me.loop_triangles);off=len(vs);vs.extend([ob.matrix_world@v.co for v in me.vertices]);fs.extend([[i+off for i in p.vertices] for p in me.polygons]);uvunit &= all(-1e-6<=c<=1.000001 for uv in me.uv_layers.active.data for c in uv.uv)
    bounds=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]];error=max(abs(bounds[j][i]-m['bounds_source_xyz'][j][i]) for j in range(2) for i in range(3));rays=[]
    if 'paving_cells_xy' in m:
        bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
        for x0,x1,y0,y1 in m['paving_cells_xy']:
            hit=bvh.ray_cast(Vector(((x0+x1)*.5,(y0+y1)*.5,.2)),Vector((0,0,-1)),.4)[0];rays.append(hit is not None and -.001<=hit.z<=.00801)
    passed=tris==m['triangles'] and zero==0 and all(len(f)==3 for f in fs) and uvunit and error<1e-4 and all(rays) and not any(n.endswith('_LOD1') for n in nodes)
    report['models'][name]={'passed':passed,'triangles':tris,'zero_area_triangles':zero,'explicit_triangles':all(len(f)==3 for f in fs),'uv0_in_unit_square':uvunit,'reimport_bounds_error':error,'nodes':nodes,'walking_rays':len(rays),'walking_all_safe':all(rays)};report['passed'] &= passed
(SOURCE/'additions-fbx-audit.json').write_text(json.dumps(report,indent=2));print('ADDITIONS_FBX_AUDIT_PASS='+str(report['passed']))
