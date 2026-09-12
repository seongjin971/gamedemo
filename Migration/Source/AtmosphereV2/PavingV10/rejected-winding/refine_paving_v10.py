"""Preserve V10 layout; hand-authored shallow cleavage topology via Blender CDT.
Run after build_paving_v10.py. Source is frozen pass2-preserved/paving-v10.blend.
"""
import bpy,bmesh,math,json,random,hashlib,sys
from pathlib import Path
from mathutils import Vector,noise
from mathutils.geometry import delaunay_2d_cdt
OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
EV=ROOT/'.dream-loop/unity-atmosphere-v2/paving-v10'
FROZEN=OUT/'pass2-preserved'
bpy.ops.wm.open_mainfile(filepath=str(FROZEN/'paving-v10.blend'))
report=json.loads((FROZEN/'paving-v10-report.json').read_text())
sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in FROZEN.iterdir() if p.is_file()}
coll=bpy.data.collections['AFTER authored unequal paving']
objects=sorted([o for o in coll.objects if o.type=='MESH'],key=lambda o:o.name)
s=bpy.context.scene;s.cycles.samples=24

def preview(prefix):
    cam=s.camera;cam.data.ortho_scale=37;cam.location=(-19,-28,32);cam.rotation_euler=(Vector((0,-5,-.04))-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.resolution_x=1300;s.render.resolution_y=1500;s.render.filepath=str(EV/(prefix+'-full.png'));bpy.ops.render.render(write_still=True)
    cam.data.ortho_scale=10;cam.location=(-4,-14,9);cam.rotation_euler=(Vector((0,-8,0))-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.filepath=str(EV/(prefix+'-close.png'));bpy.ops.render.render(write_still=True)

if '--skip-before' not in sys.argv:preview('before-v10-pass2')
stats={'fractured_stones':0,'eroded_edge_stones':0,'delamination_stones':0}
sculpt=[]

def inside(pt,poly):
    x,y=pt;value=False
    for k,a in enumerate(poly):
        b=poly[k-1]
        if (a.y>y)!=(b.y>y) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:value=not value
    return value

def distance(pt,a,b):
    ab=b-a;t=max(0,min(1,(pt-a).dot(ab)/ab.length_squared));return (pt-(a+ab*t)).length,t

for idx,ob in enumerate(objects):
    rng=random.Random(91371+idx*419)
    old=ob.data;n=(len(old.vertices)-1)//6;assert len(old.vertices)==6*n+1
    verts=[v.co.copy() for v in old.vertices[:4*n]]
    center=old.vertices[-1].co.copy();c2=Vector((center.x,center.y));baseheight=center.z
    col=tuple(old.color_attributes['StoneTone'].data[0].color)
    perimeter=[Vector((v.x,v.y)) for v in verts[3*n:4*n]]
    edge_idx=rng.randrange(n)
    eroded=idx%2==0
    if eroded:
        stats['eroded_edge_stones']+=1
        for ring in range(4):
            for j in range(n):
                # One broad planar spall, with an unequal second shoulder only
                # on selected stones. The rest of each perimeter stays quiet.
                d=min((j-edge_idx)%n,(edge_idx-j)%n)
                weight=max(0,1-d/2.15)
                loss=(.027+.018*(idx%5)/4)*weight
                inward=(c2-Vector((verts[ring*n+j].x,verts[ring*n+j].y))).normalized()
                factor=(.18,.6,1,1.2)[ring]
                verts[ring*n+j].x+=inward.x*loss*factor;verts[ring*n+j].y+=inward.y*loss*factor
                if ring>=1:verts[ring*n+j].z-=loss*(.15,.22,.36,.48)[ring]
        perimeter=[Vector((v.x,v.y)) for v in verts[3*n:4*n]]
    coords=list(perimeter);constraints=[(j,(j+1)%n) for j in range(n)];channels=[]
    is_fractured=idx%3==0
    if is_fractured:
        stats['fractured_stones']+=1
        start=perimeter[edge_idx].lerp(c2,.08)
        tip=start.lerp(c2,rng.uniform(.45,.75))
        axis=(tip-start).normalized();side=Vector((-axis.y,axis.x))
        path=[start.lerp(tip,t)+side*(math.sin(t*math.pi)*rng.uniform(-.028,.028)) for t in (0,.24,.53,.79,1)]
        widths=[rng.uniform(.014,.022) for _ in path];depth=rng.uniform(.012,.026)
        channels.append((path,widths,depth))
        if idx%12==0:
            fork=path[2];forktip=fork+axis*.16+side*rng.choice((-1,1))*.19
            if inside(forktip,perimeter):channels.append(([fork,fork.lerp(forktip,.55),forktip],[.014,.012,.008],depth*.65))
        for path,widths,depth in channels:
            strands=[[],[],[]]
            for j,p in enumerate(path):
                axis=(path[min(j+1,len(path)-1)]-path[max(0,j-1)]).normalized();normal=Vector((-axis.y,axis.x))
                for strand,offset in enumerate((-1,0,1)):
                    point=p+normal*widths[j]*offset*1.55
                    if not inside(point,perimeter):point=point.lerp(c2,.045)
                    strands[strand].append(len(coords));coords.append(point)
            for strand in strands:constraints.extend(zip(strand,strand[1:]))
    # Sparse cap tessellation supports actual mineral planes without noisy dents.
    for j in range(16):
        point=Vector((rng.uniform(min(p.x for p in perimeter),max(p.x for p in perimeter)),rng.uniform(min(p.y for p in perimeter),max(p.y for p in perimeter))))
        if inside(point,perimeter) and min((point-p).length for p in perimeter)>.06:coords.append(point)
    flake=None
    if idx%7==0:
        stats['delamination_stones']+=1;flake=(c2+Vector((.14,-.07)),rng.uniform(.12,.19),rng.uniform(.003,.007))
        for j in range(7):
            angle=j*math.tau/7;pt=flake[0]+Vector((math.cos(angle),math.sin(angle)))*flake[1]*rng.uniform(.8,1.15)
            if inside(pt,perimeter):coords.append(pt)
    vv,ee,ff,orig,_,_=delaunay_2d_cdt(coords,constraints,[list(reversed(range(n)))],1,1e-7,True)
    mapping={}
    for j,p in enumerate(vv):
        boundary=next((k for k in orig[j] if k<n),None)
        if boundary is not None:mapping[j]=3*n+boundary;continue
        # Quiet fine facets around a real chiseled fissure profile.
        height=baseheight+noise.noise_vector(Vector((p.x*9.7,p.y*9.7,idx*.317)))[0]*.0027
        if flake:
            dd=(p-flake[0]).length/flake[1]
            if dd<1:height-=flake[2]*(.4+.6*max(0,1-dd))
        relief=0
        for path,widths,depth in channels:
            for k in range(len(path)-1):
                dd,t=distance(p,path[k],path[k+1]);width=widths[k]*(1-t)+widths[k+1]*t
                along=(k+t)/(len(path)-1);taper=max(0,min(1,(1-along)*4))
                # Narrow irregular floor and steep planar banks; depth ≤26mm.
                strength=max(0,1-dd/(width*1.5))
                relief=max(relief,depth*taper*strength**.58)
        height-=relief
        mapping[j]=len(verts);verts.append(Vector((p.x,p.y,height)))
    faces=[]
    for ring in range(3):
        for j in range(n):faces.append((ring*n+j,ring*n+(j+1)%n,(ring+1)*n+(j+1)%n,(ring+1)*n+j))
    faces.append(tuple(range(n-1,-1,-1)))
    faces.extend(tuple(mapping[k] for k in f) for f in ff)
    me=bpy.data.meshes.new(ob.name+' fractured');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me)
    # Constrained intersection can omit a tiny corner triangle at a near-collinear
    # chisel shoulder. Seal only actual boundary loops, then recheck the solid.
    boundary_edges=[e for e in bm.edges if e.is_boundary]
    if boundary_edges:bmesh.ops.holes_fill(bm,edges=boundary_edges,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    me.materials.append(old.materials[0]);colors=me.color_attributes.new(name='StoneTone',type='FLOAT_COLOR',domain='POINT')
    for v in colors.data:v.color=col
    # Preserve crisp fracture-bank planes while quiet stone faces shade gently.
    for face in me.polygons:face.use_smooth=face.normal.z>.97
    ob.data=me;bpy.data.meshes.remove(old)
    bm=bmesh.new();bm.from_mesh(me);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
    assert nonmanifold==0,(ob.name,nonmanifold)
    sculpt.append({'name':ob.name,'eroded_edge':eroded,'fractured':is_fractured,'channel_count':len(channels),'maximum_channel_depth':max([d for _,_,d in channels],default=0),'nonmanifold_edges':nonmanifold})

preview('after-v10-fractured')
pos=[];norm=[];uv=[];colors=[];indices=[];areas=[];skipped=0
for ob in objects:
    me=ob.data;me.calc_loop_triangles();dedup={};tone=tuple(me.color_attributes['StoneTone'].data[0].color);first_index=len(indices)
    for tri in me.loop_triangles:
        a,b,c=[me.vertices[k].co for k in tri.vertices];area=(b-a).cross(c-a).length*.5
        if area<1e-10:skipped+=1;continue
        areas.append(area);face=[]
        for li in tri.loops:
            v=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector;key=(v.x,v.z,-v.y,n.x,n.z,-n.y,v.x*.72,-v.y*.72)
            if key not in dedup:dedup[key]=len(pos)//3;pos.extend(key[:3]);norm.extend(key[3:6]);uv.extend(key[6:]);colors.extend(tone)
            face.append(dedup[key])
        indices.extend((face[0],face[2],face[1]))
    for item in report['stones']:
        if item['name']==ob.name:item['triangles']=(len(indices)-first_index)//3
data={'id':'paving-v10-whole-ground','name':'PavingV10WholeGroundFractured','alreadyUnity':True,'positions':pos,'normals':norm,'uv':uv,'indices':indices,'colors':colors}
(OUT/'paving-v10-mesh.json').write_text(json.dumps(data,separators=(',',':')))
normal_lengths=[math.sqrt(sum(norm[k+a]**2 for a in range(3))) for k in range(0,len(norm),3)]
report.update({'refinement':'Preserved pass2 layout; modeled constrained cleavage banks and floors plus selected broad edge spalls, no material changes',
    'refinement_source_sha256':sources,'refinement_sources_preserved':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in sources.items()},
    'refinement_statistics':stats,'refinement_stones':sculpt,'triangles':len(indices)//3,'vertices':len(pos)//3,
    'world_bounds':[[min(pos[a::3]) for a in range(3)],[max(pos[a::3]) for a in range(3)]],'normal_length_min_max':[min(normal_lengths),max(normal_lengths)],
    'finite':all(math.isfinite(v) for v in pos+norm+uv+colors),'valid_indices':min(indices)>=0 and max(indices)<len(pos)//3,
    'minimum_triangle_area':min(areas),'zero_area_tessellation_triangles_omitted':skipped,'degenerate_export_triangles':0,'closed_stones':all(x['nonmanifold_edges']==0 for x in sculpt)})
assert report['triangles']<140000 and report['finite'] and report['valid_indices'] and report['closed_stones'] and report['world_bounds'][1][1]<-.004
(OUT/'paving-v10-report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'paving-v10.blend'))
print('PAVING_FRACTURED_COMPLETE',json.dumps({k:report[k] for k in ['triangles','vertices','world_bounds','refinement_statistics','closed_stones']}))
