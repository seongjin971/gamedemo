import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from io_scene_fbx import parse_fbx
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/BridgeHeroV2'
m=json.loads((SOURCE/'manifest.json').read_text());path=OUT/(m['name']+'.fbx')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(path))
vs=[];fs=[];zero=0;tris=0;slots={}
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    me=ob.data;off=len(vs);vs.extend([ob.matrix_world@v.co for v in me.vertices]);fs.extend([[off+i for i in p.vertices] for p in me.polygons]);me.calc_loop_triangles();tris+=len(me.loop_triangles);zero+=sum(t.area<1e-10 for t in me.loop_triangles)
    for p in me.polygons:
        slot=slots.setdefault(me.materials[p.material_index].name,[1e9,-1e9,1e9,-1e9])
        for li in p.loop_indices:
            u,v=me.uv_layers.active.data[li].uv;slot[0]=min(slot[0],u);slot[1]=max(slot[1],u);slot[2]=min(slot[2],v);slot[3]=max(slot[3],v)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
under=all(bvh.ray_cast(Vector((-4,r['length_axis'],r['height'])),Vector((1,0,0)),8)[0] is None for r in m['arch_open_ray_checks'])
walk=[]
for r in m['walking_ray_checks']:
    hit=bvh.ray_cast(Vector((r['x'],r['length_axis'],.2)),Vector((0,0,-1)),.5)[0];walk.append(hit is not None and -.05<=hit.z<=.015)
parsed,ver=parse_fbx.parse(str(path));transforms=[]
for e in parsed.elems:
    if e.id!=b'Objects':continue
    for ob in e.elems:
        if ob.id!=b'Model':continue
        for prop in ob.elems:
            if prop.id==b'Properties70':
                for p in prop.elems:
                    if p.id==b'P' and p.props[0]==b'Lcl Rotation':transforms.append(list(p.props[4:]))
report={'passed':tris==m['triangles'] and zero==0 and under and all(walk) and all(len(f)==3 for f in fs) and all(0<=s[0]<=s[1]<=1 and 0<=s[2]<=s[3]<=1 for s in slots.values()),
 'triangles':tris,'zero_area_triangles':zero,'all_triangular':all(len(f)==3 for f in fs),'arch_open_rays':len(m['arch_open_ray_checks']),'arch_all_clear':under,'walk_rays':len(walk),'walk_all_safe':all(walk),
 'uv_bounds_umin_umax_vmin_vmax':slots,'raw_fbx_rotations':transforms,'bounds_source_xyz':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]}
(SOURCE/'fbx-audit.json').write_text(json.dumps(report,indent=2));print('HERO_BRIDGE_FBX_AUDIT_PASS='+str(report['passed']))
