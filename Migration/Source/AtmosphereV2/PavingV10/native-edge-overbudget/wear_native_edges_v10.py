"""Native34 correction: broad unequal erosion in outlines, preserved slab layout.
blender --background --threads 6 --python wear_native_edges_v10.py
"""
import bpy,bmesh,json,math,random,hashlib,runpy,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
EV=ROOT/'.dream-loop/unity-atmosphere-v2/paving-v10'
FROZEN=OUT/'native34-preserved'
bpy.ops.wm.open_mainfile(filepath=str(FROZEN/'paving-v10.blend'))
report=json.loads((FROZEN/'paving-v10-report.json').read_text())
source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in FROZEN.iterdir() if p.is_file()}
objects=sorted([o for o in bpy.data.collections['AFTER authored unequal paving'].objects if o.type=='MESH'],key=lambda o:o.name)
s=bpy.context.scene;s.cycles.samples=24
def preview(prefix):
    cam=s.camera;cam.data.ortho_scale=37;cam.location=(-19,-28,32);cam.rotation_euler=(Vector((0,-5,-.04))-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.resolution_x=1300;s.render.resolution_y=1500;s.render.filepath=str(EV/(prefix+'-full.png'));bpy.ops.render.render(write_still=True)
    cam.data.ortho_scale=10;cam.location=(-4,-14,9);cam.rotation_euler=(Vector((0,-8,0))-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.filepath=str(EV/(prefix+'-close.png'));bpy.ops.render.render(write_still=True)
if '--skip-before' not in sys.argv:preview('before-native34-edges')

def inside(pt,poly):
    x,y=pt;state=False
    for j,a in enumerate(poly):
        b=poly[j-1]
        if (a.y>y)!=(b.y>y) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:state=not state
    return state

def crosses_outline(a,b,poly):
    def cross(x,y):return x.x*y.y-x.y*y.x
    ab=b-a
    for j,c in enumerate(poly):
        d=poly[j-1];cd=d-c;den=cross(ab,cd)
        if abs(den)<1e-10:continue
        t=cross(c-a,cd)/den;u=cross(c-a,ab)/den
        if 1e-5<t<1-1e-5 and -1e-6<=u<=1+1e-6:return True
    return False

sculpt=[]
for idx,ob in enumerate(objects):
    rng=random.Random(88739+idx*617);old=ob.data
    bottom=min(v.co.z for v in old.vertices);n=0
    for v in old.vertices:
        if abs(v.co.z-bottom)>1e-6:break
        n+=1
    assert 6<=n<80,(ob.name,n)
    base=[Vector((v.co.x,v.co.y)) for v in old.vertices[:n]]
    c=sum(base,Vector((0,0)))/n
    bm=bmesh.new();bm.from_mesh(old);bvh=BVHTree.FromBMesh(bm)
    median_top=sorted(v.co.z for v in old.vertices[3*n:])[len(old.vertices[3*n:])//2]
    def surface(pt):
        hit,_,_,_=bvh.ray_cast(Vector((pt.x,pt.y,.3)),Vector((0,0,-1)),1)
        return hit.z if hit is not None else median_top
    # Select long nearly-straight spans, then cut angular unequal shoulders and
    # a flat recessed shelf. Two or three broad losses replace uninterrupted
    # machined arrises, rather than sprinkling bumps around the whole perimeter.
    candidates=[]
    for j in range(n-2):
        a,b,d=base[j:j+3];u=b-a;v=d-b
        if u.length>.065 and v.length>.065 and u.normalized().dot(v.normalized())>.96 and (d-a).length>.24:candidates.append(j)
    rng.shuffle(candidates);chosen=[]
    for j in candidates:
        if all(abs(j-k)>3 for k in chosen):chosen.append(j)
        if len(chosen)>=(2 if idx%3==0 else 3):break
    recesses={j:rng.uniform(.022,.041) for j in chosen}
    outline=[];depths=[];supports=[];j=0
    while j<n:
        if j in recesses:
            a,d=base[j],base[j+2];length=(d-a).length;depth=recesses[j]
            outline.append(a);depths.append(0)
            for t,strength in [(rng.uniform(.10,.17),0),(rng.uniform(.23,.32),1),(rng.uniform(.67,.76),rng.uniform(.71,.94)),(rng.uniform(.88,.95),0)]:
                outline.append(a.lerp(d,t));depths.append(depth*strength)
            supports.append({'length':length,'depth':depth});j+=2
        else:outline.append(base[j]);depths.append(0);j+=1
    # A limited subset loses a larger corner. This preserves rectangular plan
    # logic while removing the strongest showroom-perfect corner intersections.
    corner_loss=0
    if idx%4==0:
        best=max(range(len(outline)),key=lambda k:1-(outline[k]-outline[k-1]).normalized().dot((outline[(k+1)%len(outline)]-outline[k]).normalized()))
        corner_loss=rng.uniform(.027,.047)
        depths[best]=max(depths[best],corner_loss)
        for off in (-1,1):depths[(best+off)%len(outline)]=max(depths[(best+off)%len(outline)],corner_loss*.35)
    m=len(outline);verts=[];toppts=[]
    for ring in range(4):
        for j,p in enumerate(outline):
            inward=(c-p).normalized();loss=depths[j]
            inset=(loss*.13,loss*.50+.002,loss*.82+.006,loss+.018)[ring]
            xy=p+inward*inset
            if ring==0:z=bottom
            else:
                z=surface(xy)-(.026,.012,.002)[ring-1]
                if ring==3:z-=loss*.30
            verts.append(Vector((xy.x,xy.y,z)))
            if ring==3:toppts.append(xy)
    coords=list(toppts);heights=[v.z for v in verts[3*m:]];constraints=[(j,(j+1)%m) for j in range(m)];old_to_input={}
    # Keep all inherited internal fracture vertices and their constraints. Only
    # the perimeter band is rebuilt, so the prior flat stratified face survives.
    for v in old.vertices[3*n:]:
        pt=Vector((v.co.x,v.co.y))
        if inside(pt,toppts) and min((pt-p).length for p in toppts)>.001:
            old_to_input[v.index]=len(coords);coords.append(pt);heights.append(v.co.z)
    for e in old.edges:
        a,b=e.vertices
        if a in old_to_input and b in old_to_input:
            aa,bb=old_to_input[a],old_to_input[b]
            if not crosses_outline(coords[aa],coords[bb],toppts):constraints.append((aa,bb))
    vv,ee,ff,orig,_,_=delaunay_2d_cdt(coords,constraints,[list(reversed(range(m)))],1,1e-7,True)
    mapping={}
    for j,pt in enumerate(vv):
        rim=next((k for k in orig[j] if k<m),None)
        if rim is not None:mapping[j]=3*m+rim;continue
        source=next(iter(orig[j]),None);height=heights[source] if source is not None else surface(pt)
        mapping[j]=len(verts);verts.append(Vector((pt.x,pt.y,height)))
    faces=[]
    for ring in range(3):
        for j in range(m):faces.append((ring*m+j,ring*m+(j+1)%m,(ring+1)*m+(j+1)%m,(ring+1)*m+j))
    faces.append(tuple(range(m-1,-1,-1)));faces.extend(tuple(mapping[k] for k in f) for f in ff)
    me=bpy.data.meshes.new(ob.name+' broad erosion');me.from_pydata(verts,[],faces);me.update()
    check=bmesh.new();check.from_mesh(me);bmesh.ops.remove_doubles(check,verts=list(check.verts),dist=.000001);bound=[e for e in check.edges if e.is_boundary]
    if bound:bmesh.ops.holes_fill(check,edges=bound,sides=0)
    bmesh.ops.recalc_face_normals(check,faces=list(check.faces));check.to_mesh(me);check.free();me.update()
    tone=tuple(old.color_attributes['StoneTone'].data[0].color);me.materials.append(old.materials[0]);color=me.color_attributes.new(name='StoneTone',type='FLOAT_COLOR',domain='POINT')
    for datum in color.data:datum.color=tone
    for face in me.polygons:face.use_smooth=face.normal.z>.97
    ob.data=me;bpy.data.meshes.remove(old);bm.free()
    check=bmesh.new();check.from_mesh(me);nonmanifold=sum(not e.is_manifold for e in check.edges);check.free();assert nonmanifold==0,(ob.name,nonmanifold)
    sculpt.append({'name':ob.name,'edge_recesses':supports,'corner_loss':corner_loss,'nonmanifold_edges':nonmanifold,'inherited_cap_vertices_preserved':len(old_to_input)})

preview('after-native34-worn-edges')
pos=[];norm=[];uv=[];colors=[];indices=[];areas=[];skipped=0
for ob in objects:
    me=ob.data;me.calc_loop_triangles();dedup={};tone=tuple(me.color_attributes['StoneTone'].data[0].color);first=len(indices)
    for tri in me.loop_triangles:
        a,b,c=[me.vertices[k].co for k in tri.vertices];area=(b-a).cross(c-a).length*.5
        if area<1e-10:skipped+=1;continue
        areas.append(area);face=[]
        for li in tri.loops:
            v=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector;key=(v.x,v.z,-v.y,n.x,n.z,-n.y,v.x*.72,-v.y*.72)
            if key not in dedup:dedup[key]=len(pos)//3;pos.extend(key[:3]);norm.extend(key[3:6]);uv.extend(key[6:]);colors.extend(tone)
            face.append(dedup[key])
        indices.extend(face)
    for item in report['stones']:
        if item['name']==ob.name:item['triangles']=(len(indices)-first)//3
data={'id':'paving-v10-whole-ground','name':'PavingV10WholeGroundWornEdges','alreadyUnity':True,'positions':pos,'normals':norm,'uv':uv,'indices':indices,'colors':colors}
(OUT/'paving-v10-mesh.json').write_text(json.dumps(data,separators=(',',':')))
report.update({'native_edge_refinement':'Candidate34-targeted broad uneven outline recesses; retained slab layout and internal cap fractures',
    'native34_source_sha256':source_hashes,'native34_sources_preserved':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in source_hashes.items()},
    'native_edge_sculpt':sculpt,'triangles':len(indices)//3,'vertices':len(pos)//3,'world_bounds':[[min(pos[a::3]) for a in range(3)],[max(pos[a::3]) for a in range(3)]],
    'minimum_triangle_area':min(areas),'zero_area_tessellation_triangles_omitted':skipped,'degenerate_export_triangles':0,'closed_stones':all(x['nonmanifold_edges']==0 for x in sculpt)})
assert report['triangles']<140000 and report['world_bounds'][1][1]<-.004
(OUT/'paving-v10-report.json').write_text(json.dumps(report,indent=2))
runpy.run_path(str(OUT/'validate_export.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'paving-v10.blend'))
print('PAVING_NATIVE_EDGE_COMPLETE',json.dumps({k:report[k] for k in ['triangles','vertices','world_bounds','closed_stones']}))
