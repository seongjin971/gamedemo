"""Architecture-only additive derivatives of the existing v7 masonry sculpt."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
SOURCE=ROOT/'Migration/Source/AtmosphereV2/StoneV7/runtime/stone-v7-runtime.blend'
protected=[SOURCE,ROOT/'Migration/Source/AtmosphereV2/StoneV7/stone-v7.blend',ROOT/'ArtSource/stone-v5.blend',ROOT/'public/models/stone-v5.glb']
protected+=list((ROOT/'Migration/Source/AtmosphereV2/Stone').glob('*'))
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected if p.is_file()}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
sources=[bpy.data.objects['Masonry_Broken'],bpy.data.objects['Masonry_Quarried']]
objects=[]
for k in range(8):
    ob=sources[k%2].copy();ob.data=sources[k%2].data.copy();bpy.context.collection.objects.link(ob)
    ob.name=f'masonry-v8-{k}' if k<6 else f'facade-v8-{k-6}'
    ob.location=((k%3-1)*1.75,(k//3-1)*1.75,0);ob.scale=(1.25,1,.85) if k<6 else (1.45,.95,.72)
    ob.rotation_euler=(0,0,0);objects.append(ob)
for ob in list(bpy.data.objects):
    if ob not in objects:bpy.data.objects.remove(ob,do_unlink=True)

mat=bpy.data.materials.new('Neutral geometry clay');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.21,.24,.255,1);bs.inputs['Roughness'].default_value=.74
for ob in objects:
    ob.data.materials.clear();ob.data.materials.append(mat)
    for p in ob.data.polygons:p.material_index=0
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=48;s.world.color=(.06,.06,.06)
s.render.resolution_x=1800;s.render.resolution_y=1500;s.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(5,-9,7));cam=bpy.context.object;cam.name='QA_Camera'
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=7.1;s.camera=cam
for loc,power,size in [((-3,-4,6),1200,2),((4,0,4),550,2.5)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='QA_Light';o.data.energy=power;o.data.size=size
    o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
def render(name):s.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
render('before-inherited-masonry.png')

# (face axis, outward sign, horizontal centre, vertical centre, half width,
# half height, depth): finite angular cuts, not a uniform all-edge bevel.
cuts=[[(1,-1,-.38,.40,.24,.18,.115),(0,1,.20,-.26,.14,.16,.075)],
      [(1,-1,.40,.02,.18,.28,.110),(1,-1,-.10,.48,.25,.11,.072)],
      [(1,-1,-.25,-.46,.24,.16,.125),(0,1,-.40,.29,.18,.20,.103)],
      [(1,-1,.26,.46,.30,.15,.122),(0,-1,-.05,-.36,.17,.22,.094)],
      [(1,-1,-.46,.12,.16,.30,.126),(0,1,.18,.48,.21,.14,.102)],
      [(1,-1,.35,-.37,.23,.22,.140),(1,-1,-.33,.48,.16,.13,.105)],
      [(1,-1,-.42,.42,.24,.17,.100),(0,1,-.38,-.41,.18,.16,.075)],
      [(1,-1,.42,-.39,.23,.19,.105),(1,-1,-.25,.47,.19,.13,.080)]]

def carve(ob,spec,index):
    axis,sign,cx,cz,w,h,depth=spec;horizontal=1-axis
    # Irregular outer polygon plus three inner chisel points form a closed
    # convex volume. Its intersection leaves several unequal fracture planes.
    outline=[(-1,-.56),(-.58,-1),(.52,-.88),(1,-.33),(.83,.64),(.23,1),(-.72,.80)]
    pts=[]
    for u,v in outline:
        co=[0,0,0];co[axis]=sign*.565;co[horizontal]=cx+u*w;co[2]=cz+v*h;pts.append(co)
    for u,v,d in [(-.29,-.18,1),(.26,.17,.80),(-.08,.35,.70)]:
        co=[0,0,0];co[axis]=sign*(.50-depth*d*.62);co[horizontal]=cx+u*w;co[2]=cz+v*h;pts.append(co)
    mesh=bpy.data.meshes.new('Temporary finite chisel');bm=bmesh.new()
    for p in pts:bm.verts.new(p)
    bmesh.ops.convex_hull(bm,input=list(bm.verts));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    tool=bpy.data.objects.new('Temporary finite chisel',mesh);bpy.context.collection.objects.link(tool)
    tool.matrix_world=ob.matrix_world.copy();bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new(f'Authored edge loss {index}','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)

rows=[]
for k,ob in enumerate(objects):
    me=ob.data;bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    # Slightly asymmetric centimetre-scale concavity; no high-frequency noise.
    for v in me.vertices:
        co=v.co.copy()
        for axis in (0,1):
            other=1-axis
            if abs(co[axis])>.38:
                u=(co[other]-(.07 if k%2 else -.06))/.46;z=(co.z-(.04 if k%3 else -.07))/.46
                weight=max(0,1-u*u)*max(0,1-z*z)
                v.co[axis]-=math.copysign((.012+.002*(k%4))*weight,co[axis])
    me.update()
    # A broad planar corner spall interrupts the inherited continuous shoulder.
    # Each variant uses a different corner and chisel angle; unlike a cavity,
    # this is an open missing corner with a readable silhouette change.
    corner_specs=[(-1,1,.83,.92,.64,.205),(1,1,.62,.90,.85,.175),
                  (-1,-1,.91,.78,.70,.235),(1,1,1.10,.70,.62,.235),
                  (-1,1,.66,1.05,.87,.175),(1,-1,.75,.98,.80,.215),
                  (-1,1,.83,.92,.64,.205),(1,-1,.75,.98,.80,.215)]
    sx,sz,nx,ny,nz,loss=corner_specs[k];normal=Vector((sx*nx,-ny,sz*nz))
    distance=(nx+ny+nz)*.5-loss
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,
                          plane_co=normal*(distance/normal.length_squared),plane_no=normal,clear_outer=True,clear_inner=False)
    boundary=[e for e in bm.edges if e.is_boundary]
    if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    for j,spec in enumerate(cuts[k]):carve(ob,spec,j)
    me=ob.data;bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();me.calc_loop_triangles()
    authored_tris=len(me.loop_triangles);budget=686 if k<6 else 116
    bpy.context.view_layer.objects.active=ob
    if authored_tris>budget:
        mod=ob.modifiers.new('Runtime triangle budget','DECIMATE');mod.ratio=budget/authored_tris;mod.use_collapse_triangulate=True
        bpy.ops.object.modifier_apply(modifier=mod.name);me=ob.data
    old_bounds=[[min(v.co[a] for v in me.vertices) for a in range(3)],[max(v.co[a] for v in me.vertices) for a in range(3)]]
    for v in me.vertices:
        for a in range(3):v.co[a]=(v.co[a]-old_bounds[0][a])/(old_bounds[1][a]-old_bounds[0][a])-.5
    me.update()
    # Split sharp fracture planes and carry dominant-axis UVs onto new cut faces.
    while me.uv_layers:me.uv_layers.remove(me.uv_layers[0])
    uv=me.uv_layers.new(name='Dominant stone face UV')
    for p in me.polygons:
        axis=max(range(3),key=lambda a:abs(p.normal[a]));p.use_smooth=True;p.material_index=0
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=[(co.y+.5,co.z+.5),(co.x+.5,co.z+.5),(co.x+.5,co.y+.5)][axis]
    mod=ob.modifiers.new('Hard fracture boundaries','EDGE_SPLIT');mod.split_angle=.50
    bpy.ops.object.modifier_apply(modifier=mod.name);me=ob.data;me.update();me.calc_loop_triangles()
    pos=[];norm=[];uvs=[];inds=[];dedup={};fallback=0
    for tri in me.loop_triangles:
        ix=[]
        for li in tri.loops:
            co=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector
            if n.dot(tri.normal)<.1:n=tri.normal;fallback+=1
            t=me.uv_layers.active.data[li].uv
            key=(-co.x,co.z,-co.y,-n.x,n.z,-n.y,float(t[0]),float(t[1]))
            if key not in dedup:
                dedup[key]=len(pos)//3;pos.extend(key[:3]);norm.extend(key[3:6]);uvs.extend(key[6:])
            ix.append(dedup[key])
        inds.extend([ix[0],ix[2],ix[1]])
    data={'id':ob.name,'name':ob.name,'positions':pos,'normals':norm,'uv':uvs,'indices':inds}
    (OUT/(ob.name+'.json')).write_text(json.dumps(data,separators=(',',':')))
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    nm=sum(not e.is_manifold for e in bm.edges);bm.free()
    bounds=[[min(pos[a::3]) for a in range(3)],[max(pos[a::3]) for a in range(3)]]
    rows.append({'id':ob.name,'source':'Masonry_Broken' if k%2==0 else 'Masonry_Quarried','triangles':len(inds)//3,'vertices':len(pos)//3,
        'authored_triangles_before_budget':authored_tris,'budget':700 if k<6 else 120,'unit_bounds_exact':bounds==[[-.5]*3,[.5]*3],
        'unity_bounds':bounds,'nonmanifold_edges_welded':nm,'normal_fallback_corners':fallback,'finite':all(math.isfinite(x) for x in pos+norm+uvs),
        'edge_damage':cuts[k],'face_concavity':.012+.002*(k%4)})
render('after-masonry-v8.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'masonry-v8.blend'))
qa={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashes,
    'all_sources_preserved':all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items()),
    'export_basis':'alreadyUnity positions/normals (-x,z,-y), triangle winding (0,2,1); no object transform baked',
    'total_triangles':sum(r['triangles'] for r in rows),'meshes':rows}
(OUT/'masonry-v8-qa.json').write_text(json.dumps(qa,indent=2));print('MASONRY_V8_COMPLETE',qa['total_triangles'])
