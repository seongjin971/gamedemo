"""Conservative mesh sculpt of the preserved Blender asset, with local JSON export.

No browser or Unity assets are written. Root coordinates and UV loops are retained.
"""
import bpy, bmesh, json, math, hashlib
from pathlib import Path
from collections import defaultdict
from mathutils import Vector

WORK=Path(__file__).resolve().parent
ROOT=next(p for p in WORK.parents if (p/'ArtSource').is_dir())
SOURCE=ROOT/'ArtSource/tree-v6.blend'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
obj=bpy.data.objects['Sculpted bark roots and fine branches']
mesh=obj.data
original=[v.co.copy() for v in mesh.vertices]
original_uv=[tuple(d.uv) for d in mesh.uv_layers.active.data]

# Build the stable mesh topology components. The continuous unioned wood is
# separate from the original tube-built fine limbs and exposed roots.
bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table()
remaining=set(bm.verts);components=[]
while remaining:
    seed=remaining.pop();component=[seed];stack=[seed]
    while stack:
        at=stack.pop()
        for edge in at.link_edges:
            nxt=edge.other_vert(at)
            if nxt in remaining:
                remaining.remove(nxt);component.append(nxt);stack.append(nxt)
    components.append([v.index for v in component])
bm.free()

# Broad, localized proportional editing rounds the visibly angular upper
# elbows. Each displacement is shared by parent wood and attached twigs.
# No lower trunk/root vertex (z <= 1.65) is affected.
elbows=[
 ((-.77,.05,3.46),(-.63,.035,3.02),(-.56,.055,3.81),.32,.42),
 ((-.6,.08,4.27),(-.56,.055,3.81),(-.31,.03,4.68),.32,.40),
 ((-.47,.04,5.08),(-.31,.03,4.68),(-.26,.07,5.52),.28,.34),
 ((-1.34,-.03,3.68),(-1.07,.05,3.2),(-1.68,-.08,3.97),.26,.35),
 ((-1.68,-.08,3.97),(-1.34,-.03,3.68),(-1.58,-.13,4.4),.32,.33),
 ((-1.58,-.13,4.4),(-1.68,-.08,3.97),(-1.93,-.15,4.76),.27,.31),
 ((-1.93,-.15,4.76),(-1.58,-.13,4.4),(-1.82,-.13,5.18),.28,.32),
 ((1.14,.03,2.93),(.85,.05,2.48),(1.04,.03,3.29),.30,.36),
 ((1.04,.03,3.29),(1.14,.03,2.93),(1.45,0,3.67),.25,.34),
 ((1.45,0,3.67),(1.04,.03,3.29),(1.4,-.01,4.02),.28,.30),
 ((.33,.11,4.08),(-.1,.06,4.08),(.59,.11,4.48),.26,.32),
 ((.98,.08,4.7),(.59,.11,4.48),(.87,.11,5.08),.28,.30),
 ((.87,.11,5.08),(.98,.08,4.7),(1.1,.1,5.41),.24,.28),
]
fields=[]
for at,before,after,amount,radius in elbows:
    center=Vector(at)
    fields.append((center,((Vector(before)+Vector(after))*.5-center)*amount,radius))
for vertex in mesh.vertices:
    pos=vertex.co.copy()
    if pos.z<=1.65:continue
    delta=Vector((0,0,0))
    for center,shift,radius in fields:
        d=(pos-center).length/radius
        if d<2.3:delta+=shift*math.exp(-2*d*d)
    vertex.co+=delta

# Ring IDs survive in longitudinal UVs on the retained original tube meshes.
# Fair the centerlines (not the bark surface), then parallel-transport each
# ring, retaining its irregular cross-section and per-corner UV coordinates.
vertex_v=defaultdict(list)
for polygon in mesh.polygons:
    for li in polygon.loop_indices:
        vertex_v[mesh.loops[li].vertex_index].append(mesh.uv_layers.active.data[li].uv.y)
edited_components=0;edited_rings=0;max_fine_center_displacement=0
for comp in components:
    if len(comp)>1000 or min(original[i].z for i in comp)<1.65:continue
    rings=defaultdict(list)
    for i in comp:
        vals=vertex_v[i]
        if not vals:continue
        rings[round(sum(vals)/len(vals),5)].append(i)
    ordered=[rings[k] for k in sorted(rings)]
    if len(ordered)<4 or any(len(r)<4 for r in ordered):continue
    centers=[sum((mesh.vertices[i].co for i in ring),Vector())/len(ring) for ring in ordered]
    radii=[sum((mesh.vertices[i].co-center).length for i in ring)/len(ring) for ring,center in zip(ordered,centers)]
    if max(radii)>.065:continue
    target=[c.copy() for c in centers]
    for iteration in range(5):
        previous=[c.copy() for c in target]
        for j in range(1,len(target)-1):
            t=j/(len(target)-1)
            # Root two rings remain almost locked to prevent collar gaps.
            strength=.42*min(1,t*7)
            target[j]=previous[j].lerp((previous[j-1]+previous[j+1])*.5,strength)
    distance=[0.0]
    for j in range(1,len(target)):distance.append(distance[-1]+(target[j]-target[j-1]).length)
    total=distance[-1]
    for j,(ring,center,newcenter) in enumerate(zip(ordered,centers,target)):
        old_t=(centers[min(j+1,len(centers)-1)]-centers[max(j-1,0)]).normalized()
        new_t=(target[min(j+1,len(target)-1)]-target[max(j-1,0)]).normalized()
        rotation=old_t.rotation_difference(new_t)
        t=distance[j]/max(total,1e-6)
        # A smooth terminal taper preserves base radius and contact.
        terminal=max(0,(t-.62)/.38)
        scale=1-.32*terminal*terminal*(3-2*terminal)
        for i in ring:mesh.vertices[i].co=newcenter+(rotation@(mesh.vertices[i].co-center))*scale
        max_fine_center_displacement=max(max_fine_center_displacement,(newcenter-center).length)
    edited_components+=1;edited_rings+=len(ordered)
mesh.update()
for polygon in mesh.polygons:polygon.use_smooth=True
mesh.calc_loop_triangles()

# Deduplicate exact position/normal/UV tuples, retaining seam split vertices.
# Unity conversion reflects X, so triangle winding is reversed.
positions=[];normals=[];uv=[];indices=[]
lookup={}
corners=mesh.corner_normals
for tri in mesh.loop_triangles:
    for li in (tri.loops[0],tri.loops[2],tri.loops[1]):
        point=mesh.vertices[mesh.loops[li].vertex_index].co
        normal=corners[li].vector
        pos=(-point.x,point.z,-point.y);norm=(-normal.x,normal.z,-normal.y)
        tex=tuple(mesh.uv_layers.active.data[li].uv);key=pos+norm+tex
        if key not in lookup:
            lookup[key]=len(positions)//3
            positions.extend(pos);normals.extend(norm);uv.extend(tex)
        indices.append(lookup[key])
assert all(math.isfinite(x) for x in positions+normals+uv)
assert original_uv==[tuple(d.uv) for d in mesh.uv_layers.active.data]
assert all(vertex.co==original[vertex.index] for vertex in mesh.vertices if original[vertex.index].z<=1.65)
(WORK/'tree-v7-mesh.json').write_text(json.dumps({'positions':positions,'normals':normals,'uv':uv,'indices':indices},separators=(',',':')))
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'tree-v7.blend'))
report={
 'source':str(SOURCE),'source_sha256':source_hash,'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash,
 'mesh_vertices':len(mesh.vertices),'export_vertices':len(positions)//3,'indices':len(indices),'triangles':len(mesh.loop_triangles),
 'coordinate_conversion':'Blender (x,y,z) to Unity (-x,z,-y)',
 'winding':'triangle corners [0,2,1], reversed for X reflection',
 'export_deduplication':'exact position + corner normal + UV tuple; seams preserved',
 'uv_corners_preserved':True,'root_and_lower_trunk_exact_below_z':1.65,
 'proportional_elbows':len(elbows),'faired_fine_components':edited_components,'faired_fine_rings':edited_rings,
 'max_fine_center_shift':max_fine_center_displacement,
 'maximum_vertex_displacement':max((v.co-original[v.index]).length for v in mesh.vertices),
 'bounds_blender_min':[min(v.co[i] for v in mesh.vertices) for i in range(3)],
 'bounds_blender_max':[max(v.co[i] for v in mesh.vertices) for i in range(3)],
 'limitation':'Conservative structural smoothing preserves the existing branching design. It does not replace the trunk silhouette or establish native Unity visual acceptance.'
}
(WORK/'tree-v7-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))

# Repeatable isolated Blender before/after evidence, with the same camera,
# material and illumination. Render setup is deliberately not saved in asset.
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1024;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
scene.world.color=(.06,.06,.06)
scene.view_settings.view_transform='AgX'
def look_at(o,point):o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-13,8));camera=bpy.context.object;look_at(camera,(0,0,3.05))
camera.data.type='ORTHO';camera.data.ortho_scale=7.6;scene.camera=camera
for location,power,color,size in [((-5,-5,9),1800,(.55,.72,1),5),((4,-2,5),950,(1,.68,.35),4),((0,5,7),1600,(.35,.6,1),4)]:
    bpy.ops.object.light_add(type='AREA',location=location)
    light=bpy.context.object;light.data.energy=power;light.data.color=color;light.data.shape='DISK';light.data.size=size;look_at(light,(0,0,3))
scene.render.film_transparent=False
scene.render.filepath=str(WORK/'tree-v7-preview.png');bpy.ops.render.render(write_still=True)
edited=[v.co.copy() for v in mesh.vertices]
for v,p in zip(mesh.vertices,original):v.co=p
mesh.update()
scene.render.filepath=str(WORK/'tree-v6-same-light.png');bpy.ops.render.render(write_still=True)
for v,p in zip(mesh.vertices,edited):v.co=p
mesh.update()
