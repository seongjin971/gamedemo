"""Additive local sculpt refinement of the v6 meshes. Run with Blender --background --python."""
import bpy, bmesh, math, json, hashlib
from pathlib import Path
from mathutils import Vector, noise

OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
SOURCE=ROOT/'Migration/Source/AtmosphereV2/Stone'
names=['Flagstone_Split','Flagstone_Spalled','Flagstone_Laminated','Flagstone_Weathered','Flagstone_Cleft','Flagstone_Granular','Flagstone_Worn','Flagstone_Branched','Masonry_Broken','Masonry_Quarried']
source_data={json.loads(p.read_text())['name']:json.loads(p.read_text()) for p in SOURCE.glob('*.json') if p.name!='stone-v6-report.json'}
preserved=[ROOT/'ArtSource/stone-v5.blend',ROOT/'public/models/stone-v5.glb']+list(SOURCE.iterdir())
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in preserved if p.is_file()}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'stone-v6.blend'))
objects=[bpy.data.objects[n] for n in names]
def bounds(me):
    return [[min(v.co[a] for v in me.vertices) for a in range(3)],[max(v.co[a] for v in me.vertices) for a in range(3)]]
def digest_transform(ob):
    return [list(row) for row in ob.matrix_world]
original_bounds={ob.name:bounds(ob.data) for ob in objects}
transforms={ob.name:digest_transform(ob) for ob in objects}
original_counts={ob.name:(len(ob.data.vertices),len(ob.data.polygons)) for ob in objects}

# Identical neutral inspection lighting and camera for both captures. No generated bump
# or directional slate textures can disguise the actual sculpt in this comparison.
mat=bpy.data.materials.new('V7 neutral stone geometry inspection');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.215,.24,1)
bs.inputs['Roughness'].default_value=.69
for ob in objects:
    ob.data.materials.clear();ob.data.materials.append(mat)
    for p in ob.data.polygons:p.material_index=0
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32
s.render.resolution_x=1500;s.render.resolution_y=1500;s.render.resolution_percentage=100
s.world.color=(.075,.075,.075)
bpy.ops.object.camera_add(location=(4,-6,8));cam=bpy.context.object;cam.name='QA_Camera'
cam.rotation_euler=(Vector((0,0,-.1))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=7.7;s.camera=cam
for loc,power,size in [((1,-3,5),1000,1.6),((-3,0,3),330,2.5)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object
    light.name='QA_Light';light.data.energy=power;light.data.size=size
    light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
def render(name):
    s.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
render('before-v6-geometry.png')

report=[]
for k,ob in enumerate(objects):
    me=ob.data;lo,hi=original_bounds[ob.name]
    # Densify the existing carved topology without smoothing away its fissures.
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=1,use_grid_fill=True)
    bm.to_mesh(me);bm.free();me.update()
    # Deliberately short unequal perimeter losses. Their support occupies ~8% of
    # the four-metre normalized perimeter, with 1-5cm inward losses at metre scale.
    chips=[(0,1,-.24+.035*(k%4),.061,.016+.004*(k%3)),
           (1,-1,.17-.043*(k%5),.077,.024+.004*(k%4)),
           (0,-1,.29-.03*(k%3),.047,.012+.004*(k%2))]
    changed=0;max_change=0.0
    for v in me.vertices:
        co=v.co.copy();x,y,z=co
        if k<8:
            # 70% removal of residual broad top relief; deep fissure walls survive.
            if z>.39:
                v.co.z=hi[2]-(hi[2]-z)*.30
            # A few compact shallow granular losses, never full-face random noise.
            if z>.40 and max(abs(x),abs(y))<.40:
                for px,py,r,depth in [(-.21+.021*k,.13,.080,.006),(.17,-.18+.013*k,.055,.004)]:
                    d=math.hypot(x-px,y-py)/r
                    if d<1:v.co.z-=depth*(1-d)**1.4
        else:
            # Compress noisy broad relief on masonry faces; retain the source's
            # asymmetric fractured corners, top split and closed topology.
            for axis in range(3):
                others=[a for a in range(3) if a!=axis]
                if abs(co[axis])>.40 and max(abs(co[a]) for a in others)<.34:
                    target=math.copysign(.478,co[axis])
                    v.co[axis]=target+(co[axis]-target)*.48
        for axis,sign,center,radius,depth in chips:
            tangent=1-axis;along=co[tangent]-center
            boundary=(hi[axis] if sign>0 else -lo[axis])
            edge_depth=boundary-sign*co[axis]
            top_weight=max(0,min(1,(z-.17)/.20))
            if abs(along)<radius and edge_depth<.12 and top_weight>0:
                # Piecewise angular brush creates a shallow planar spall with
                # unequal shoulders instead of a rounded notch or repeated bevel.
                along_weight=max(0,1-abs(along/radius))
                inward=depth*along_weight*max(0,1-edge_depth/.12)*top_weight
                v.co[axis]-=sign*inward
                v.co.z-=inward*(.75 if k<8 else .58)
        # Additional compact masonry arris losses at different face heights.
        if k>=8:
            for axis,sign,center,radius,depth in [(0,-1,.09,.10,.032),(1,1,-.18,.085,.044)]:
                edge=(hi[axis] if sign>0 else -lo[axis])-sign*co[axis]
                other=1-axis
                d=abs(z-center)/radius+abs(co[other]-(.43 if k==8 else -.42))/.13
                if d<1 and edge<.1:
                    v.co[axis]-=sign*depth*(1-d)*max(0,1-edge/.1)
        # Exact original local AABB is retained; pin only original extrema. This
        # also preserves the runtime's fitting contract and instance transforms.
        for axis in range(3):
            v.co[axis]=min(hi[axis],max(lo[axis],v.co[axis]))
            if abs(co[axis]-lo[axis])<1e-7 or abs(co[axis]-hi[axis])<1e-7:
                v.co[axis]=co[axis]
        delta=(v.co-co).length;changed+=delta>1e-8;max_change=max(max_change,delta)
    me.update()
    # Gentle top normals eliminate the regular original triangulation highlights;
    # the v5 split-edge topology keeps true fissure and cleavage boundaries sharp.
    for p in me.polygons:
        if p.normal.z>.80:p.use_smooth=True
    me.update();me.calc_loop_triangles()
    verts=[];norm=[];uv=[];inds=[];dedup={};uvlayer=me.uv_layers.active
    for tri in me.loop_triangles:
        ix=[]
        for li in tri.loops:
            co=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector
            tex=uvlayer.data[li].uv if uvlayer else (co.x,co.y)
            key=(-co.x,co.z,-co.y,-n.x,n.z,-n.y,float(tex[0]),float(tex[1]))
            if key not in dedup:
                dedup[key]=len(verts)//3;verts.extend(key[:3]);norm.extend(key[3:6]);uv.extend(key[6:])
            ix.append(dedup[key])
        inds.extend([ix[0],ix[2],ix[1]])
    data={'id':source_data[ob.name]['id'],'name':ob.name,'positions':verts,'normals':norm,'uv':uv,'indices':inds}
    (OUT/(data['id']+'.json')).write_text(json.dumps(data,separators=(',',':')))
    weld=bmesh.new();weld.from_mesh(me);bmesh.ops.remove_doubles(weld,verts=list(weld.verts),dist=.000001)
    nonmanifold=sum(not e.is_manifold for e in weld.edges);weld.free()
    exported_bounds=[[min(verts[a::3]) for a in range(3)],[max(verts[a::3]) for a in range(3)]]
    r={'id':data['id'],'name':ob.name,'source_vertices':original_counts[ob.name][0],
       'sculpt_vertices':len(me.vertices),'export_vertices':len(verts)//3,'triangles':len(inds)//3,
       'source_blender_bounds':original_bounds[ob.name],'blender_bounds':bounds(me),'unity_bounds':exported_bounds,
       'bounds_exact':bounds(me)==original_bounds[ob.name],'transform_unchanged':digest_transform(ob)==transforms[ob.name],
       'modified_vertices':changed,'maximum_vertex_delta':max_change,'nonmanifold_edges_welded':nonmanifold,
       'finite':all(math.isfinite(x) for x in verts+norm+uv),'indices_valid':min(inds)>=0 and max(inds)<len(verts)//3,
       'edge_chip_support_fraction':sum(2*c[3] for c in chips)/4,'chip_depth_unit_range':[min(c[4] for c in chips),max(c[4] for c in chips)]}
    report.append(r)
render('after-v7-geometry.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'stone-v7.blend'))
preservation={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items()}
qa={'source':'Migration/Source/AtmosphereV2/Stone/stone-v6.blend','method':'Edit inherited sculpt topology; subdivide once; flatten top relief 70%; compact angular spall brushes; original fissures retained',
    'export_basis':'alreadyUnity: Blender (x,y,z) to (-x,z,-y), normals same, triangles (0,2,1). Matches v6 exactly. No object transforms baked.',
    'source_sha256':hashes,'source_preserved':preservation,'all_sources_preserved':all(preservation.values()),
    'mesh_count':len(report),'total_triangles':sum(r['triangles'] for r in report),'meshes':report,
    'limitations':['Long directional texture ridges are a separate material concern; these exports only alter geometry.',
                    'Centimetre chip sizes assume a one-metre normalized asset; existing per-instance scaling changes physical sizes.',
                    'Blender comparison is neutral geometry QA; final Unity visual and FPS review remains required.']}
(OUT/'stone-v7-report.json').write_text(json.dumps(qa,indent=2))
print('STONE_V7_COMPLETE',json.dumps({'triangles':qa['total_triangles'],'sources_preserved':qa['all_sources_preserved']}))
