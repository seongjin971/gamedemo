import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/ChapelSurfaces'
report={'passed':True,'models':{}}
for mp in SOURCE.glob('*-manifest.json'):
    m=json.loads(mp.read_text());name=m['name'];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(OUT/(name+'.fbx')))
    vs=[];fs=[];tri=0;zero=0;uv=[];alltri=True
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        me=ob.data;me.calc_loop_triangles();tri+=len(me.loop_triangles);zero+=sum(t.area<1e-10 for t in me.loop_triangles);alltri &= all(len(p.vertices)==3 for p in me.polygons);offset=len(vs);vs.extend([ob.matrix_world@v.co for v in me.vertices]);fs.extend([[i+offset for i in p.vertices] for p in me.polygons]);uv.extend([t.uv.copy() for t in me.uv_layers.active.data])
    bounds=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]];err=max(abs(bounds[j][i]-m['bounds_source_xyz'][j][i]) for j in range(2) for i in range(3));uvunit=all(-1e-6<=c<=1.000001 for x in uv for c in x);bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);rays=[]
    if 'Paving' in name:
        for rect in m['paving_cells_xy']:
            x0,x1,y0,y1=rect
            for tx,ty in [(.25,.25),(.5,.5),(.75,.75)]:
                hit=bvh.ray_cast(Vector((x0+(x1-x0)*tx,y0+(y1-y0)*ty,.2)),Vector((0,0,-1)),.5)[0];rays.append({'hit_z':None if hit is None else hit.z,'passed':hit is not None and -.001<=hit.z<=.00801})
    if 'Roof' in name:
        for x in (-2.8,-2,-1,0,1,2,2.8):
            for y in (-3.8,-2.5,-1,0,1,2,3):
                hit=bvh.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),5)[0];expected=2.32-.8*abs(x);rays.append({'x':x,'y':y,'hit_z':None if hit is None else hit.z,'passed':hit is not None and expected-.025<=hit.z<=expected+.12})
    passed=tri==m['triangles'] and tri<20000 and zero==0 and alltri and uvunit and err<1e-4 and all(x['passed'] for x in rays)
    report['models'][name]={'passed':passed,'triangles':tri,'zero_area_triangles':zero,'all_triangular':alltri,'uv0_within_unit_square':uvunit,'bounds':bounds,'reimport_bounds_error':err,'surface_rays':rays,'all_surface_rays_pass':all(x['passed'] for x in rays)};report['passed'] &= passed
(SOURCE/'surfaces-fbx-audit.json').write_text(json.dumps(report,indent=2));print('CHAPEL_SURFACES_AUDIT_PASS='+str(report['passed']))
