import bpy,json,math,hashlib,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from io_scene_fbx import parse_fbx
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];report={};original=SOURCE.parent/'BridgeHeroV2/StoneBridgeHeroV2_14m.blend'
def above_signature(path,name):
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=[name]
    ob=dst.objects[0];triangles=[]
    for p in ob.data.polygons:
        vs=[ob.data.vertices[i].co for i in p.vertices]
        if max(v.z for v in vs)>=0:triangles.append(b''.join(sorted(struct.pack('fff',*v) for v in vs)))
    result={'triangle_count':len(triangles),'sha256':hashlib.sha256(b''.join(sorted(triangles))).hexdigest()};bpy.data.objects.remove(ob,do_unlink=True);return result
report['original_v2_above_deck']=above_signature(original,'CW_StoneBridgeHeroV2_14m');report['new_v3_above_deck']=above_signature(SOURCE/'StoneBridgeHeroV3_14m.blend','CW_StoneBridgeHeroV3_14m');report['above_deck_source_triangles_bit_exact']=report['original_v2_above_deck']==report['new_v3_above_deck']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);path=SOURCE/'staged/CW_StoneBridgeHeroV3_14m.fbx';bpy.ops.import_scene.fbx(filepath=str(path));m=json.loads((SOURCE/'structural-manifest.json').read_text())
vs=[];fs=[];zero=0;tri=0;uvs={}
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    me=ob.data;off=len(vs);vs.extend([ob.matrix_world@v.co for v in me.vertices]);fs.extend([[off+i for i in p.vertices] for p in me.polygons]);me.calc_loop_triangles();tri+=len(me.loop_triangles);zero+=sum(t.area<1e-10 for t in me.loop_triangles)
    for p in me.polygons:
        bounds=uvs.setdefault(me.materials[p.material_index].name,[1,0,1,0])
        for li in p.loop_indices:
            u,v=me.uv_layers.active.data[li].uv;bounds[0]=min(bounds[0],u);bounds[1]=max(bounds[1],u);bounds[2]=min(bounds[2],v);bounds[3]=max(bounds[3],v)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);slices=[]
for z in (-.35,-.6,-1,-1.5,-2,-2.6):
    half=6.4*math.sqrt(1-((z+3)/2.82)**2);inside=[]
    for i in range(101):
        y=half*.98*(-1+2*i/100);inside.append(bvh.ray_cast(Vector((-4,y,z)),Vector((1,0,0)),8)[0] is None)
    outside=[]
    for side in (-1,1):
        for fraction in (.15,.35,.60,.85):
            y=side*(half+(7-half)*fraction);outside.append(bvh.ray_cast(Vector((-4,y,z)),Vector((1,0,0)),8)[0] is not None)
    slices.append({'source_height':z,'analytic_clear_span':half*2,'inside_clear':sum(inside),'inside_test_count':len(inside),'outside_opaque':sum(outside),'outside_test_count':len(outside),'passed':all(inside) and all(outside)})
walk=[]
for r in m['walking_ray_checks']:
    hit=bvh.ray_cast(Vector((r['x'],r['length_axis'],.2)),Vector((0,0,-1)),.5)[0];walk.append(hit is not None and -.05<=hit.z<=.015)
parsed,_=parse_fbx.parse(str(path));rots=[]
for e in parsed.elems:
    if e.id==b'Objects':
        for ob in e.elems:
            if ob.id==b'Model':
                for p in ob.elems:
                    if p.id==b'Properties70':
                        for row in p.elems:
                            if row.id==b'P' and row.props[0]==b'Lcl Rotation':rots.append(list(row.props[4:]))
bounds=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]];err=max(abs(bounds[j][i]-m['bounds_source_xyz'][j][i]) for j in range(2) for i in range(3))
report.update({'triangles':tri,'zero_area_triangles':zero,'all_explicit_triangles':all(len(f)==3 for f in fs),'uv_bounds':uvs,'root_rotations':rots,'bounds_source_xyz':bounds,'reimport_bounds_error':err,'dense_intrados_slices':slices,'walking_ray_count':len(walk),'walking_all_safe':all(walk),'passed':report['above_deck_source_triangles_bit_exact'] and tri==m['triangles'] and zero==0 and all(len(f)==3 for f in fs) and all(0<=b[0]<=b[1]<=1 and 0<=b[2]<=b[3]<=1 for b in uvs.values()) and all(s['passed'] for s in slices) and all(walk) and err<1e-4 and all(abs(r[0]+90)<.001 for r in rots)})
(SOURCE/'structural-fbx-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
