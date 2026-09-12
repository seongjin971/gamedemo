"""Blender authored whole-ground paving; no source edits or Unity integration.
blender --background --threads 6 --python build_paving_v10.py
"""
import bpy, bmesh, json, math, random, hashlib, statistics
from pathlib import Path
from mathutils import Vector, Quaternion, noise

OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
EVIDENCE=ROOT/'.dream-loop/unity-atmosphere-v2/paving-v10'
EVIDENCE.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'Unity/Vesper/Assets/Vesper/Import/unity-scene.json'
V7=ROOT/'Migration/Source/AtmosphereV2/StoneV7/runtime'
FLOOR='1ba07011-f8c4-4d07-9550-6d031350c67f'
SEED=102706
rng=random.Random(SEED)
bridge=json.loads(SOURCE.read_text())
sources=[SOURCE]+list(V7.glob('*.json'))
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
geos={p.stem:json.loads(p.read_text()) for p in V7.glob('*.json') if 'positions' in json.loads(p.read_text())}
selected=[]
for node in bridge['nodes']:
    if node['distant'] or node['materials']!=[FLOOR] or node['geometry'] not in geos:continue
    visible=[(k,i) for k,i in enumerate(node['instances']) if -10<=i['position'][0]<=10 and -13<=i['position'][2]<=22 and -3<=i['position'][1]<=15]
    for index,(original_index,i) in enumerate(visible):
        if i['position'][1]<.2:selected.append((node,index,original_index,i))
assert len(selected)==430
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
before=bpy.data.collections.new('BEFORE actual V7 ground');bpy.context.scene.collection.children.link(before)
after=bpy.data.collections.new('AFTER authored unequal paving');bpy.context.scene.collection.children.link(after)

mat=bpy.data.materials.new('Neutral stone inspection vertex tone');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.68
attr=mat.node_tree.nodes.new('ShaderNodeVertexColor');attr.layer_name='StoneTone'
mix=mat.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.18,.205,.22,1)
mat.node_tree.links.new(attr.outputs['Color'],mix.inputs[1]);mat.node_tree.links.new(mix.outputs[0],bs.inputs['Base Color'])

def mesh_object(name,verts,faces,collection,color):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);collection.objects.link(ob);me.materials.append(mat)
    col=me.color_attributes.new(name='StoneTone',type='FLOAT_COLOR',domain='POINT')
    for datum in col.data:datum.color=(*color,1)
    return ob

actual_points=[];rows={};top_heights=[];selection_manifest=[]
for node,index,original_index,i in selected:
    geo=geos[node['geometry']];p=i['position'];sc=list(i['scale']);sc[0]*=1.075;sc[2]*=1.075
    q=i['quaternion'];q=Quaternion((q[3],q[0],-q[1],-q[2]));pos=Vector((-p[0],p[1],p[2]))
    seed=index+(index//100)*7
    if seed%3==0 and abs(pos.x)<7.8 and pos.z>0:
        sc[0]*=.93;pos.x+=math.sin(seed*7.31)*.035;pos.z+=math.cos(seed*3.7)*.018
        q=q@Quaternion((0,1,0),math.radians(math.sin(seed)*1.8))
    verts=[];world=[]
    for k in range(0,len(geo['positions']),3):
        co=geo['positions'][k:k+3];v=q@Vector(tuple(co[a]*sc[a] for a in range(3)))+pos
        world.append(tuple(v));verts.append((v.x,-v.z,v.y))
    actual_points.extend(world);top=max(v[1] for v in world);top_heights.append(top)
    faces=[(geo['indices'][k],geo['indices'][k+2],geo['indices'][k+1]) for k in range(0,len(geo['indices']),3)]
    mesh_object('Before '+str(len(selection_manifest)),verts,faces,before,i['color'])
    bounds=[[min(v[a] for v in world) for a in range(3)],[max(v[a] for v in world) for a in range(3)]]
    row=round(p[2],3);rows.setdefault(row,[]).append(bounds)
    selection_manifest.append({'node_id':node['id'],'geometry_id':node['geometry'],'original_instance_index':original_index,'selected_instance_index':index,'existing_world_bounds':bounds,'top':top})

aabb=[[min(v[a] for v in actual_points) for a in range(3)],[max(v[a] for v in actual_points) for a in range(3)]]
mean_color=[statistics.mean(i['color'][a] for _,_,_,i in selected) for a in range(3)]
TOP=statistics.median(top_heights);BOTTOM=TOP-.125
MINX,MAXX=aabb[0][0],aabb[1][0];MINZ,MAXZ=aabb[0][2],aabb[1][2]
stones=[];stats={'large_slabs':0,'fracture_divisions':0,'chipped_stones':0,'t_junction_layout':True}

def add_stone(poly,kind):
    # Input is counterclockwise in Unity's X/Z plane. Use reversed Blender Y.
    area=sum(poly[j][0]*poly[(j+1)%len(poly)][1]-poly[(j+1)%len(poly)][0]*poly[j][1] for j in range(len(poly)))
    if area<0:poly=list(reversed(poly))
    # Unequal quarried corner cuts. Straight intermediate boundary knots remain.
    clipped=[]
    for j,p in enumerate(poly):
        prev=Vector(poly[j-1]);cur=Vector(p);nxt=Vector(poly[(j+1)%len(poly)])
        incoming=cur-prev;outgoing=nxt-cur
        if incoming.length>.08 and outgoing.length>.08 and incoming.normalized().dot(outgoing.normalized())<.55 and rng.random()<.58:
            a=min(incoming.length*.14,rng.uniform(.022,.065));b=min(outgoing.length*.14,rng.uniform(.025,.075))
            clipped.extend([tuple(cur-incoming.normalized()*a),tuple(cur+outgoing.normalized()*b)])
        else:clipped.append(p)
    poly=clipped
    cx=sum(p[0] for p in poly)/len(poly);cz=sum(p[1] for p in poly)/len(poly)
    # Restrained shared joints and localized chipped arrises, no deep gutters.
    gap=rng.uniform(.012,.020);perimeter=[]
    for j,a in enumerate(poly):
        b=poly[(j+1)%len(poly)];dist=math.dist(a,b);cuts=max(1,math.ceil(dist/.22))
        for k in range(cuts):
            t=k/cuts;x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t
            dv=Vector((cx-x,cz-z));dv.normalize();perimeter.append((x+dv.x*gap,z+dv.y*gap))
    n=len(perimeter);chip_center=rng.randrange(n);chip_depth=rng.uniform(.015,.038) if len(stones)%3==0 else 0
    if chip_depth:stats['chipped_stones']+=1
    height=TOP+rng.uniform(-.006,.006);verts=[]
    # Four rings: buried side, lower arris, chisel bevel, mineral face.
    for ring in range(4):
        for j,(x,z) in enumerate(perimeter):
            dv=Vector((cx-x,cz-z));dv.normalize()
            distance=min((j-chip_center)%n,(chip_center-j)%n)
            chip=chip_depth*max(0,1-distance/1.8)
            inset=(chip*.45,.001+chip*.60,.010+chip,.040+chip)[ring]
            xx=x+dv.x*inset;zz=z+dv.y*inset
            zzheight=(BOTTOM,height-.019,height-.004-chip*.34,height)[ring]
            if ring>=2:
                zzheight+=noise.noise_vector(Vector((xx*12.5,zz*12.5,len(stones)*.197)))[0]*.0028
            verts.append((xx,-zz,zzheight))
    # Sculpt mineral face across two internal rings: 1-3 mm grain plus selected
    # small shallow pits, never long scored lines or deep gouges.
    for fraction in (.64,.29):
        for x,z in perimeter:
            xx=cx+(x-cx)*fraction;zz=cz+(z-cz)*fraction
            relief=noise.noise_vector(Vector((xx*13.5,zz*13.5,len(stones)*.313)))[0]*.003
            if len(stones)%4==0:
                d=math.hypot(xx-cx-.13,zz-cz+.10)
                relief-=max(0,1-d/.10)*.004
            verts.append((xx,-zz,height+relief))
    center=len(verts);verts.append((cx,-cz,height+noise.noise_vector(Vector((cx*8,cz*8,.3)))[1]*.001))
    faces=[]
    for ring in range(3):
        for j in range(n):faces.append((ring*n+j,ring*n+(j+1)%n,(ring+1)*n+(j+1)%n,(ring+1)*n+j))
    for ring in (3,4):
        for j in range(n):faces.append((ring*n+j,ring*n+(j+1)%n,(ring+1)*n+(j+1)%n,(ring+1)*n+j))
    for j in range(n):faces.append((5*n+j,5*n+(j+1)%n,center))
    faces.append(tuple(range(n-1,-1,-1)))
    tone=rng.uniform(.935,1.065);color=[c*tone for c in mean_color]
    ob=mesh_object('Paving_%03d_%s'%(len(stones),kind),verts,faces,after,color)
    # Recalculate the closed sculpt's real geometry normals. Top remains gently
    # interpolated while the narrow chisel facets and side walls retain hardness.
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    for f in ob.data.polygons:f.use_smooth=f.normal.z>.85
    ob.data.update();stones.append({'object':ob,'polygon_xz':poly,'kind':kind,'color':color,'top':height,'chip_depth':chip_depth})

# Whole front courtyard retains its world envelope and walk level. Two thirds
# of the masonry is squared coursed paving; unequal boundary polylines break
# full-width rails and row-local staggered cuts create true T junctions.
FRONT=min(b[0][2] for b in rows[-1.07])
zlevels=[FRONT]
while zlevels[-1]<MAXZ-.5:zlevels.append(min(MAXZ,zlevels[-1]+rng.uniform(.81,1.09)))
if zlevels[-1]!=MAXZ:zlevels[-1]=MAXZ
knots=[MINX+(MAXX-MINX)*k/12 for k in range(13)]
boundaries=[]
for j,z in enumerate(zlevels):boundaries.append([(x,z+(rng.uniform(-.12,.12) if j not in (0,len(zlevels)-1) and k not in (0,12) else 0)) for k,x in enumerate(knots)])

def edge_points(boundary,a,b):
    def val(x):
        for k in range(len(boundary)-1):
            p,q=boundary[k:k+2]
            if p[0]-1e-6<=x<=q[0]+1e-6:return p[1]+(q[1]-p[1])*(x-p[0])/(q[0]-p[0])
        return boundary[-1][1]
    return [(a,val(a))]+[p for p in boundary if a+1e-6<p[0]<b-1e-6]+[(b,val(b))]

merges=[]
for j in range(2,len(zlevels)-2,4):
    lo=rng.uniform(MINX+1,MAXX-2.7);hi=lo+rng.uniform(1.10,1.38)
    merges.append((j,lo,hi));stats['large_slabs']+=1
    add_stone(edge_points(boundaries[j],lo,hi)+list(reversed(edge_points(boundaries[j+2],lo,hi))),'two_course_slab')
stats['two_course_merged_slabs']=len(merges)
for j in range(len(zlevels)-1):
    cuts=[MINX]
    while cuts[-1]<MAXX-.7:
        width=rng.uniform(1.03,1.45)
        if rng.random()<.085:width*=1.48;stats['large_slabs']+=1
        cuts.append(min(MAXX,cuts[-1]+width))
    if cuts[-1]!=MAXX:cuts[-1]=MAXX
    row_merges=[(lo,hi) for row,lo,hi in merges if j in (row,row+1)]
    for lo,hi in row_merges:cuts=sorted([x for x in cuts if not lo-.19<x<hi+.19]+[lo,hi])
    uppercuts=list(cuts)
    for k in range(1,len(cuts)-1):
        if any(abs(cuts[k]-edge)<1e-6 for m in row_merges for edge in m):continue
        if k%3!=0:uppercuts[k]+=rng.uniform(-.10,.10)
    for k in range(len(cuts)-1):
        a,b=cuts[k:k+2]
        if any(lo-1e-6<=a and b<=hi+1e-6 for lo,hi in row_merges):continue
        if b-a<.035:continue
        ua,ub=uppercuts[k:k+2]
        lower=edge_points(boundaries[j],a,b);upper=edge_points(boundaries[j+1],ua,ub)
        if rng.random()<.10 and b-a>1.15:
            # Unequal oblique cleave: two naturally squared angular fragments.
            x1=a+(b-a)*rng.uniform(.36,.57);x2=a+(b-a)*rng.uniform(.48,.68)
            add_stone(edge_points(boundaries[j],a,x1)+list(reversed(edge_points(boundaries[j+1],ua,x2))),'fracture_A')
            add_stone(edge_points(boundaries[j],x1,b)+list(reversed(edge_points(boundaries[j+1],x2,ub))),'fracture_B');stats['fracture_divisions']+=1
        else:add_stone(lower+list(reversed(upper)),'coursed')

# Rear side aisles: source row footprint intervals are unioned only across
# overlapping inherited tiles; large missing patches and the stair void survive.
rear_footprints=[]
for z,boxes in sorted(rows.items()):
    if z>=-1.1:continue
    intervals=[]
    for box in sorted(boxes,key=lambda b:b[0][0]):
        lo,hi=box[0][0],box[1][0]
        if intervals and lo<=intervals[-1][1]+.04:intervals[-1][1]=max(intervals[-1][1],hi)
        else:intervals.append([lo,hi])
    za=min(b[0][2] for b in boxes);zb=min(FRONT,max(b[1][2] for b in boxes))
    for lo,hi in intervals:
        rear_footprints.append([lo,hi,za,zb]);count=max(1,round((hi-lo)/1.35));cuts=[lo]+[lo+(hi-lo)*k/count+rng.uniform(-.10,.10) for k in range(1,count)]+[hi]
        for k in range(count):add_stone([(cuts[k],za),(cuts[k+1],za),(cuts[k+1],zb),(cuts[k],zb)],'rear_aisle')

# Identical oblique full-floor and near-ground previews, no surface textures.
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
s.render.resolution_x=1300;s.render.resolution_y=1500;s.render.resolution_percentage=100
s.world.color=(.09,.09,.09)
bpy.ops.object.camera_add(location=(-19,-28,32));cam=bpy.context.object;s.camera=cam
cam.rotation_euler=(Vector((0,-5,-.04))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=37
for loc,power,size in [((-8,-1,14),3500,7),((8,-14,12),1800,8)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.size=size;light.rotation_euler=(Vector((0,-5,0))-light.location).to_track_quat('-Z','Y').to_euler()
for is_after,name in [(False,'before-v7'),(True,'after-v10')]:
    before.hide_render=is_after;after.hide_render=not is_after
    s.render.filepath=str(EVIDENCE/(name+'-full.png'));bpy.ops.render.render(write_still=True)
    cam.data.ortho_scale=10;cam.location=(-4,-14,9);cam.rotation_euler=(Vector((0,-8,0))-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.resolution_x=1400;s.render.resolution_y=1000
    s.render.filepath=str(EVIDENCE/(name+'-close.png'));bpy.ops.render.render(write_still=True)
    cam.data.ortho_scale=37;cam.location=(-19,-28,32);cam.rotation_euler=(Vector((0,-5,-.04))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_x=1300;s.render.resolution_y=1500

positions=[];normals=[];uv=[];indices=[];colors=[];mesh_reports=[];degenerate_skipped=0;triangle_areas=[]
for stone in stones:
    ob=stone['object'];me=ob.data;me.calc_loop_triangles();dedup={};start=len(indices)
    for tri in me.loop_triangles:
        corners=[me.vertices[vi].co for vi in tri.vertices]
        area=(corners[1]-corners[0]).cross(corners[2]-corners[0]).length*.5
        if area<1e-10:degenerate_skipped+=1;continue
        triangle_areas.append(area)
        face=[]
        for li in tri.loops:
            v=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector
            key=(v.x,v.z,-v.y,n.x,n.z,-n.y,v.x*.72,-v.y*.72)
            if key not in dedup:
                dedup[key]=len(positions)//3;positions.extend(key[:3]);normals.extend(key[3:6]);uv.extend(key[6:]);colors.extend((*stone['color'],1))
            face.append(dedup[key])
        # Axis mapping is a proper rotation. Preserve Blender winding so face
        # cross products agree with normals, matching working StoneV7 native JSON.
        indices.extend((face[0],face[1],face[2]))
    bm=bmesh.new();bm.from_mesh(me);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
    mesh_reports.append({k:v for k,v in stone.items() if k!='object'}|{'name':ob.name,'triangles':(len(indices)-start)//3,'nonmanifold_edges':nonmanifold})

data={'id':'paving-v10-whole-ground','name':'PavingV10WholeGround','alreadyUnity':True,'positions':positions,'normals':normals,'uv':uv,'indices':indices,'colors':colors}
(OUT/'paving-v10-mesh.json').write_text(json.dumps(data,separators=(',',':')))
normal_lengths=[math.sqrt(sum(normals[k+a]**2 for a in range(3))) for k in range(0,len(normals),3)]
qa={'seed':SEED,'source_sha256':hashes,'source_preserved':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items()},
    'replacement_predicate':"!node.distant && node.materials[0] == '"+FLOOR+"' && source StoneV7/runtime geometry exists && instance.position.x in [-10,10] && instance.position.z in [-13,22] && instance.position.y in [-3,0.2)",
    'source_instance_count':len(selected),'selection':selection_manifest,'source_world_bounds':aabb,
    'source_top_height_min_median_max':[min(top_heights),TOP,max(top_heights)],'authored_nominal_top':TOP,
    'front_envelope_xz':[MINX,MAXX,FRONT,MAXZ],'rear_row_envelopes_xz':rear_footprints,
    'footprint_note':'Main courtyard outer envelope and rear source row segment envelopes retained. Old internal tile gaps are repaved. Staircase void and missing rear tiles retained. No stairs or upper landing selected.',
    'export_basis':'Unity native world space at identity. Blender (x,y,z) -> (x,z,-y), a proper rotation; preserve triangle order and rotate normals identically. Cross(edge1,edge2) dot average normals must be positive, matching working StoneV7. colors = RGBA float array, constant per stone; uv = world XZ * .72.',
    'statistics':stats,'stone_count':len(stones),'triangles':len(indices)//3,'vertices':len(positions)//3,
    'world_bounds':[[min(positions[a::3]) for a in range(3)],[max(positions[a::3]) for a in range(3)]],
    'normal_length_min_max':[min(normal_lengths),max(normal_lengths)],'finite':all(math.isfinite(v) for v in positions+normals+uv+colors),
    'minimum_triangle_area':min(triangle_areas),'degenerate_export_triangles':0,'zero_area_tessellation_triangles_omitted':degenerate_skipped,
    'valid_indices':min(indices)>=0 and max(indices)<len(positions)//3,'closed_stones':all(m['nonmanifold_edges']==0 for m in mesh_reports),'stones':mesh_reports,
    'limitations':['Neutral Blender previews prove changed paving geometry only. Unity lighting, water, camera, navigation and FPS require parent integration review.','Rear aisles preserve source mask shape; front repaving uses exact source outer AABB envelope, not every old scalloped perimeter indentation.']}
assert qa['triangles']<140000 and qa['finite'] and qa['valid_indices'] and qa['closed_stones'] and qa['world_bounds'][1][1]<-.004
(OUT/'paving-v10-report.json').write_text(json.dumps(qa,indent=2))
import runpy
runpy.run_path(str(OUT/'validate_export.py'),run_name='__main__')
before.hide_viewport=True;before.hide_render=True;after.hide_viewport=False;after.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'paving-v10.blend'))
print('PAVING_V10_COMPLETE',json.dumps({k:qa[k] for k in ['stone_count','triangles','vertices','closed_stones','source_world_bounds','source_top_height_min_median_max']}))
