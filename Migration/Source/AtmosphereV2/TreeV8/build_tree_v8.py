"""Structural v8: continuous root collars, remeshed/fair upper wood, fork twigs."""
import bpy,bmesh,json,math,hashlib,random
import faulthandler
faulthandler.dump_traceback_later(90,repeat=True)
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
WORK=Path(__file__).resolve().parent;ROOT=next(p for p in WORK.parents if (p/'ArtSource').is_dir())
SOURCE=ROOT/'Migration/Source/AtmosphereV2/Tree/tree-v7.blend'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
source=bpy.data.objects['Sculpted bark roots and fine branches'];original_mesh=source.data
original=source.copy();original.data=source.data.copy();original.name='Preserved v7 comparison';bpy.context.collection.objects.link(original);original.hide_render=True
mesh=source.data;material=mesh.materials[0]
bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table()
remaining=set(bm.verts);components=[]
while remaining:
    seed=remaining.pop();comp=[seed.index];stack=[seed]
    while stack:
        at=stack.pop()
        for e in at.link_edges:
            n=e.other_vert(at)
            if n in remaining:remaining.remove(n);comp.append(n.index);stack.append(n)
    components.append(comp)
bm.free()
print('STAGE components',len(components),flush=True)
vuv=defaultdict(list)
for poly in mesh.polygons:
    for li in poly.loop_indices:vuv[mesh.loops[li].vertex_index].append(mesh.uv_layers.active.data[li].uv.y)
def rings_of(comp):
    rings=defaultdict(list)
    for i in comp:
        if vuv[i]:rings[round(sum(vuv[i])/len(vuv[i]),5)].append(i)
    rings=[rings[k] for k in sorted(rings)]
    if len(rings)<3 or any(len(r)<4 for r in rings):return None
    centers=[sum((mesh.vertices[i].co for i in r),Vector())/len(r) for r in rings]
    radii=[sum((mesh.vertices[i].co-c).length for i in r)/len(r) for r,c in zip(rings,centers)]
    return rings,centers,radii
major_ids=set(max(components,key=len))
root_components=[c for c in components if len(c)<1000 and min(mesh.vertices[i].co.z for i in c)<.15]
for c in root_components:major_ids.update(c)
root_tail_ids=set()
for c in root_components:
    rc=rings_of(c)
    if not rc:continue
    rr,cc,rad=rc
    for ring,center,radius in zip(rr,cc,rad):
        if radius<.025 and Vector((center.x,center.y,0)).length>.45:root_tail_ids.update(ring)

# Select eight visible terminal offshoots, distributed around the crown.
# Rebuild their actual geometry as curved, tapering, split limbs.
candidates=[]
for c in components:
    if c[0] in major_ids:continue
    rc=rings_of(c)
    if not rc:continue
    rings,centers,radii=rc
    length=sum((centers[j]-centers[j-1]).length for j in range(1,len(centers)))
    if .24<length<1.05 and .004<max(radii)<.052 and centers[0].z>1.7:
        candidates.append((max(radii)*length,c,rc))
selected=[]
for score,c,rc in sorted(candidates,key=lambda x:-x[0]):
    if all((rc[1][0]-other[2][1][0]).length>.40 for other in selected):selected.append((score,c,rc))
    if len(selected)==8:break
replaced_ids={i for _,c,_ in selected for i in c}

def subset(name,keep):
    polygons=[p for p in mesh.polygons if all(i in keep for i in p.vertices)]
    used=sorted({i for p in polygons for i in p.vertices});mapping={old:new for new,old in enumerate(used)}
    me=bpy.data.meshes.new(name);me.from_pydata([mesh.vertices[i].co for i in used],[],[[mapping[i] for i in p.vertices] for p in polygons]);me.update()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(material)
    layer=me.uv_layers.new(name='BarkUV')
    for new,old in zip(me.polygons,polygons):
        new.use_smooth=True
        for li,oldli in zip(new.loop_indices,old.loop_indices):layer.data[li].uv=mesh.uv_layers.active.data[oldli].uv
    return ob
major=subset('Continuous wood and root collars',major_ids)
fine=subset('Retained crown and distal root tips',(set(range(len(mesh.vertices)))-major_ids-replaced_ids)|root_tail_ids)
print('STAGE subsets',len(major.data.vertices),len(fine.data.vertices),flush=True)

# Broad proportional sculpt rounds the main crown hooks over branch-diameter
# distances. Stronger than v7, then remesh and surface fairing blend the joins.
fields=[
 ((-.77,.05,3.46),(.13,0,-.035),.42),
 ((-.6,.08,4.27),(.075,0,-.045),.37),
 ((-1.66,-.08,4.0),(.11,0,.02),.34),
 ((-1.90,-.15,4.77),(.07,0,.02),.28),
 ((1.12,.03,2.95),(-.08,0,-.025),.36),
 ((1.42,0,3.66),(-.065,0,-.015),.30),
 ((.95,.08,4.7),(-.055,0,.01),.27),
]
def field_delta(pos):
    delta=Vector()
    for at,shift,rad in fields:
        d=(pos-Vector(at)).length/rad
        if d<2:delta+=Vector(shift)*math.exp(-2*d*d)
    return delta
for ob in [major,fine]:
    for v in ob.data.vertices:
        if v.co.z>1.6:v.co+=field_delta(v.co)

def tube(name,centers,radii,sides=10):
    verts=[];faces=[];tex=[];previous=None;length=0
    for j,(p,r) in enumerate(zip(centers,radii)):
        tangent=(centers[min(j+1,len(centers)-1)]-centers[max(j-1,0)]).normalized()
        axis=tangent.cross(Vector((0,1,0))).normalized() if previous is None else (previous-tangent*previous.dot(tangent)).normalized()
        other=tangent.cross(axis).normalized();previous=axis
        if j:length+=(p-centers[j-1]).length
        for k in range(sides):
            a=k*math.tau/sides;shape=1+.05*math.sin(a*3+j*.18)
            verts.append(p+(axis*math.cos(a)+other*math.sin(a))*r*shape);tex.append((k/sides,length*.7))
            if j:faces.append(((j-1)*sides+k,(j-1)*sides+(k+1)%sides,j*sides+(k+1)%sides,j*sides+k))
    faces.append(tuple(reversed(range(sides))));faces.append(tuple((len(centers)-1)*sides+k for k in range(sides)))
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(material)
    layer=me.uv_layers.new(name='BarkUV')
    for p in me.polygons:
        p.use_smooth=True
        for li in p.loop_indices:layer.data[li].uv=tex[me.loops[li].vertex_index]
        if max(layer.data[li].uv.x for li in p.loop_indices)-min(layer.data[li].uv.x for li in p.loop_indices)>.8:
            for li in p.loop_indices:
                if layer.data[li].uv.x<.1:layer.data[li].uv.x+=1
    return ob

# Continuous buttresses overlap the existing roots inside the stump. Their
# inner ends climb the trunk instead of ending in cylinders against its base.
collars=[]
for c in root_components:
    rc=rings_of(c)
    if not rc:continue
    _,centers,radii=rc
    if max(radii)<.045:continue
    rootpoint=centers[min(2,len(centers)-1)];direction=Vector((rootpoint.x,rootpoint.y,0)).normalized()
    start=Vector((direction.x*.10,direction.y*.10,.58))
    end=centers[min(5,len(centers)-1)]
    pts=[];rs=[]
    for j in range(13):
        t=j/12;pts.append(start.lerp(end,t)+Vector((0,0,.06*math.sin(math.pi*t))))
        rs.append(.145*(1-t)**1.3+max(.018,radii[min(5,len(radii)-1)])*t)
    collars.append(tube('Root collar',pts,rs,16))
bpy.ops.object.select_all(action='DESELECT');major.select_set(True)
for ob in collars:ob.select_set(True)
bpy.context.view_layer.objects.active=major;bpy.ops.object.join()
print('STAGE union start',len(major.data.vertices),flush=True)
mod=major.modifiers.new('Voxel union wood roots and collars','REMESH');mod.mode='VOXEL';mod.voxel_size=.015;mod.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=mod.name)
print('STAGE union complete',len(major.data.vertices),flush=True)
mod=major.modifiers.new('Round branch and root junctions','SMOOTH');mod.factor=.72;mod.iterations=22
bpy.ops.object.modifier_apply(modifier=mod.name)
print('STAGE smooth complete',flush=True)
# Correct modest surface shrinkage without restoring the hard collar seams.
surface_normals=[v.normal.copy() for v in major.data.vertices]
for v,n in zip(major.data.vertices,surface_normals):v.co+=n*.004
major.data.update();major.data.calc_loop_triangles();raw_count=len(major.data.loop_triangles)
mod=major.modifiers.new('Continuous wood runtime surface','DECIMATE');mod.ratio=min(1,35000/raw_count)
print('STAGE decimation start',raw_count,flush=True)
bpy.ops.object.modifier_apply(modifier=mod.name)
print('STAGE decimation complete',flush=True)
if not major.data.uv_layers:major.data.uv_layers.new(name='BarkUV')
mod=major.modifiers.new('Reproject preserved bark UV','DATA_TRANSFER');mod.object=source;mod.use_loop_data=True;mod.data_types_loops={'UV'};mod.loop_mapping='POLYINTERP_NEAREST';mod.layers_uv_select_src='ALL';mod.layers_uv_select_dst='NAME'
bpy.ops.object.modifier_apply(modifier=mod.name)
print('STAGE UV transfer complete',flush=True)
for poly in major.data.polygons:
    poly.use_smooth=True
    for li in poly.loop_indices:
        p=major.data.vertices[major.data.loops[li].vertex_index].co;uvp=major.data.uv_layers.active.data[li].uv
        # Short staggered transverse breaks interrupt long parallel bark rails.
        uvp.x+=.035*math.sin(p.z*14+p.x*3)*math.sin(p.y*6+p.z*2)
        uvp.y+=.025*math.sin(p.z*11+p.y*5+p.x*7)

new_twigs=[];twig_report=[]
for idx,(_,comp,rc) in enumerate(selected):
    _,centers,radii=rc;base=centers[0]+field_delta(centers[0]);tip=centers[-1]+field_delta(centers[-1]);delta=tip-base;length=delta.length
    side=delta.normalized().cross(Vector((0,1,0))).normalized()*(-1 if idx%2 else 1)
    depth=delta.normalized().cross(side).normalized();pts=[];rs=[]
    base_r=max(radii[0],.008)
    for j in range(19):
        t=j/18
        pts.append(base+delta*t+side*(math.sin(math.pi*t)*length*.17+math.sin(t*math.tau)*length*.035)+depth*math.sin(math.pi*t)*length*.045)
        rs.append(max(.0003,base_r*(1-t)**1.25))
    new_twigs.append(tube('Curved terminal '+str(idx),pts,rs,10))
    anchor=pts[10];forkdelta=delta*.34-side*length*.24+depth*length*.055;fpts=[];frs=[]
    for j in range(12):
        t=j/11;fpts.append(anchor+forkdelta*t-side*math.sin(math.pi*t)*length*.06);frs.append(max(.00022,rs[10]*.68*(1-t)**1.3))
    new_twigs.append(tube('Split terminal '+str(idx),fpts,frs,8))
    twig_report.append({'base':list(base),'tip':list(tip),'base_radius':base_r})

bpy.ops.object.select_all(action='DESELECT')
for ob in [major,fine]+new_twigs:ob.select_set(True)
bpy.context.view_layer.objects.active=major;bpy.ops.object.join();obj=major;mesh=obj.data
obj.parent=bpy.data.objects.get('TreeRoot')
bpy.data.objects.remove(source,do_unlink=True);obj.name='Sculpted bark roots and fine branches';original.hide_render=True
mesh.validate(clean_customdata=False);mesh.update();mesh.calc_loop_triangles()
for p in mesh.polygons:p.use_smooth=True
positions=[];normals=[];uv=[];indices=[];lookup={}
for tri in mesh.loop_triangles:
    for li in (tri.loops[0],tri.loops[2],tri.loops[1]):
        p=mesh.vertices[mesh.loops[li].vertex_index].co;n=mesh.corner_normals[li].vector
        pos=(-p.x,p.z,-p.y);norm=(-n.x,n.z,-n.y);tex=tuple(mesh.uv_layers.active.data[li].uv);key=pos+norm+tex
        if key not in lookup:lookup[key]=len(positions)//3;positions.extend(pos);normals.extend(norm);uv.extend(tex)
        indices.append(lookup[key])
assert all(math.isfinite(v) for v in positions+normals+uv)
(WORK/'tree-v8-mesh.json').write_text(json.dumps({'positions':positions,'normals':normals,'uv':uv,'indices':indices},separators=(',',':')))
# Save deliverable with only the edited tree and original parent.
bpy.data.objects.remove(original,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'tree-v8.blend'))
report={'source':str(SOURCE),'source_sha256':source_hash,'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash,'mesh_vertices':len(mesh.vertices),'export_vertices':len(positions)//3,'triangles':len(indices)//3,'raw_remesh_triangles':raw_count,'root_collars_unioned':len(collars),'replaced_split_twigs':len(selected),'twigs':twig_report,'coordinate_conversion':'Blender (x,y,z) to Unity (-x,z,-y)','winding':'triangle [0,2,1]','uv':'Nearest source UV reprojection on continuous wood; cylindrical longitudinal bark on rebuilt twig tubes; exact tuple dedup retains seams','bounds_blender_min':[min(v.co[i] for v in mesh.vertices) for i in range(3)],'bounds_blender_max':[max(v.co[i] for v in mesh.vertices) for i in range(3)]}
(WORK/'tree-v8-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

# Matched asset previews. Same render rig as v7; v7 source loaded separately.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1024;scene.render.resolution_y=1024;scene.render.resolution_percentage=100;scene.world.color=(.06,.06,.06);scene.view_settings.view_transform='AgX'
def look_at(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-13,8));camera=bpy.context.object;look_at(camera,(0,0,3.05));camera.data.type='ORTHO';camera.data.ortho_scale=7.6;scene.camera=camera
for loc,power,color,size in [((-5,-5,9),1800,(.55,.72,1),5),((4,-2,5),950,(1,.68,.35),4),((0,5,7),1600,(.35,.6,1),4)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.color=color;light.data.shape='DISK';light.data.size=size;look_at(light,(0,0,3))
scene.render.filepath=str(WORK/'tree-v8-preview.png');bpy.ops.render.render(write_still=True)
obj.hide_render=True
with bpy.data.libraries.load(str(SOURCE),link=False) as (data_from,data_to):data_to.objects=['Sculpted bark roots and fine branches']
prior=data_to.objects[0];bpy.context.collection.objects.link(prior);prior.hide_render=False
scene.render.filepath=str(WORK/'tree-v7-same-light.png');bpy.ops.render.render(write_still=True)
