import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from io_scene_fbx import parse_fbx
SOURCE=Path(__file__).resolve().parent;report={'passed':True,'models':{}}
for mp in SOURCE.glob('*-manifest.json'):
    m=json.loads(mp.read_text());path=SOURCE/'staged'/(m['name']+'.fbx');bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(path))
    vs=[];fs=[];zero=0;tri=0;slots={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        me=ob.data;off=len(vs);vs.extend([ob.matrix_world@v.co for v in me.vertices]);fs.extend([[off+i for i in p.vertices] for p in me.polygons]);me.calc_loop_triangles();tri+=len(me.loop_triangles);zero+=sum(t.area<1e-10 for t in me.loop_triangles)
        for p in me.polygons:
            slot=slots.setdefault(me.materials[p.material_index].name,[1e9,-1e9,1e9,-1e9])
            for li in p.loop_indices:
                u,v=me.uv_layers.active.data[li].uv;slot[0]=min(slot[0],u);slot[1]=max(slot[1],u);slot[2]=min(slot[2],v);slot[3]=max(slot[3],v)
    bounds=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]];err=max(abs(bounds[j][i]-m['bounds_source_xyz'][j][i]) for j in range(2) for i in range(3));bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);height_samples=[]
    if 'Wall' in m['name']:
        for i in range(29):
            x=-2.8+i*.2;hit=bvh.ray_cast(Vector((x,0,3.5)),Vector((0,0,-1)),4)[0];height_samples.append({'x':x,'height':None if hit is None else hit.z,'passed':hit is not None and .25<=hit.z<=2.80001})
    parsed,version=parse_fbx.parse(str(path));rots=[]
    for e in parsed.elems:
        if e.id!=b'Objects':continue
        for ob in e.elems:
            if ob.id!=b'Model':continue
            for prop in ob.elems:
                if prop.id==b'Properties70':
                    for p in prop.elems:
                        if p.id==b'P' and p.props[0]==b'Lcl Rotation':rots.append(list(p.props[4:]))
    passed=tri==m['triangles'] and zero==0 and all(len(f)==3 for f in fs) and all(math.isfinite(c) for v in vs for c in v) and all(0<=s[0]<=s[1]<=1 and 0<=s[2]<=s[3]<=1 for s in slots.values()) and err<1e-4 and all(s['passed'] for s in height_samples) and all(abs(r[0]+90)<.001 for r in rots)
    if 'Strip' in m['name']:passed &= bounds[1][2]<=.55001 and abs(bounds[1][0]-bounds[0][0]-6)<1e-4
    else:passed &= abs(bounds[1][0]-bounds[0][0]-3)<1e-4
    material_stats={}
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH':
            for p in ob.data.polygons:
                label=ob.data.materials[p.material_index].name;item=material_stats.setdefault(label,{'triangles':0,'surface_area_m2':0});item['triangles']+=1;item['surface_area_m2']+=p.area
    report['models'][m['name']]={'passed':passed,'triangles':tri,'zero_area_triangles':zero,'explicit_triangles':all(len(f)==3 for f in fs),'bounds_source_xyz':bounds,'reimport_bounds_error':err,'uv_bounds_per_material':slots,'fbx_root_rotations':rots,'material_statistics':material_stats};report['passed'] &= passed
(SOURCE/'rubble-fbx-audit.json').write_text(json.dumps(report,indent=2));print('ABBEY_RUBBLE_FBX_AUDIT_PASS='+str(report['passed']))

