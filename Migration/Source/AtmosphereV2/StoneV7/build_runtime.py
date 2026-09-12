import bpy,bmesh,json,math,hashlib,shutil
from pathlib import Path
OUT=Path(__file__).resolve().parent;RUN=OUT/'runtime';RUN.mkdir(exist_ok=True)
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
report=json.loads((OUT/'stone-v7-report.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(OUT/'stone-v7.blend'))
master_hash=hashlib.sha256((OUT/'stone-v7.blend').read_bytes()).hexdigest()
shutil.copy2(OUT/'after-v7-geometry.png',RUN/'before-master.png')
rows=[]
for src in report['meshes']:
    ob=bpy.data.objects[src['name']];me=ob.data;lo,hi=src['source_blender_bounds']
    matrix=[list(row) for row in ob.matrix_world]
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(me);bm.free();me.update();me.calc_loop_triangles()
    baseline=json.loads((ROOT/'Migration/Source/AtmosphereV2/Stone'/(src['id']+'.json')).read_text())
    target=int(len(baseline['indices'])/3*1.25)
    bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Runtime preserve silhouette reduce planar interiors','DECIMATE')
    mod.ratio=target/len(me.loop_triangles);mod.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=mod.name);me=ob.data
    # Decimation may remove a single extremal point. Restore the exact fitting
    # bounds with a recorded affine correction; object matrices remain unchanged.
    before=[[min(v.co[a] for v in me.vertices) for a in range(3)],[max(v.co[a] for v in me.vertices) for a in range(3)]]
    for v in me.vertices:
        for a in range(3):v.co[a]=lo[a]+(v.co[a]-before[0][a])/(before[1][a]-before[0][a])*(hi[a]-lo[a])
    me.update()
    # Split genuinely sharp fissure/arris edges; smooth the support planes only.
    for p in me.polygons:p.use_smooth=True
    mod=ob.modifiers.new('Runtime hard fissure normals','EDGE_SPLIT');mod.split_angle=.57
    bpy.ops.object.modifier_apply(modifier=mod.name);me=ob.data;me.update();me.calc_loop_triangles()
    positions=[];normals=[];uvs=[];indices=[];dedup={};uvlayer=me.uv_layers.active
    normal_fallbacks=0;skipped_tiny=0
    for tri in me.loop_triangles:
        if tri.area<1e-13:skipped_tiny+=1;continue
        ix=[]
        for li in tri.loops:
            co=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector
            if n.dot(tri.normal)<.10:n=tri.normal;normal_fallbacks+=1
            tex=uvlayer.data[li].uv if uvlayer else (co.x,co.y)
            key=(-co.x,co.z,-co.y,-n.x,n.z,-n.y,float(tex[0]),float(tex[1]))
            if key not in dedup:
                dedup[key]=len(positions)//3;positions.extend(key[:3]);normals.extend(key[3:6]);uvs.extend(key[6:])
            ix.append(dedup[key])
        indices.extend([ix[0],ix[2],ix[1]])
    data={'id':src['id'],'name':src['name'],'positions':positions,'normals':normals,'uv':uvs,'indices':indices}
    (RUN/(src['id']+'.json')).write_text(json.dumps(data,separators=(',',':')))
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    nm=sum(not e.is_manifold for e in bm.edges);bm.free()
    after=[[min(v.co[a] for v in me.vertices) for a in range(3)],[max(v.co[a] for v in me.vertices) for a in range(3)]]
    rows.append({'name':src['name'],'id':src['id'],'triangles':len(indices)//3,'vertices':len(positions)//3,
        'baseline_triangles':len(baseline['indices'])//3,'bounds_exact':after==[lo,hi],
        'bounds_max_error':max(abs(after[i][a]-[lo,hi][i][a]) for i in range(2) for a in range(3)),
        'pre_restoration_bounds':before,'blender_bounds':after,'normal_fallback_corners':normal_fallbacks,
        'skipped_subprecision_triangles':skipped_tiny,'nonmanifold_edges_welded':nm,
        'transform_unchanged':matrix==[list(row) for row in ob.matrix_world]})
s=bpy.context.scene;s.render.filepath=str(RUN/'after-runtime.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(RUN/'stone-v7-runtime.blend'))
qa={'export_basis':report['export_basis'],'master_preserved':hashlib.sha256((OUT/'stone-v7.blend').read_bytes()).hexdigest()==master_hash,
    'total_triangles':sum(r['triangles'] for r in rows),'v6_total_triangles':sum(r['baseline_triangles'] for r in rows),
    'all_sources_preserved':all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in report['source_sha256'].items()),'meshes':rows}
(RUN/'runtime-qa.json').write_text(json.dumps(qa,indent=2));print('STONE_V7_RUNTIME_COMPLETE',qa['total_triangles'])
