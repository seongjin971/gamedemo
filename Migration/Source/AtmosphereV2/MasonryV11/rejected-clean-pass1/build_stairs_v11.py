"""Additive, individually carved stair blocks; no Unity writes."""
import bpy, bmesh, json, math, hashlib, random
from pathlib import Path
from mathutils import Vector, Quaternion

OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
SCRATCH=ROOT/'.dream-loop/unity-atmosphere-v2/masonry-v11'
SCRATCH.mkdir(parents=True,exist_ok=True)
BRIDGE=ROOT/'Unity/Vesper/Assets/Vesper/Import/unity-scene.json'
data=json.loads(BRIDGE.read_text())
STONE='08b6ee59-7da1-4fb0-bd5d-a752d5b8fa60'
FLOOR='1ba07011-f8c4-4d07-9550-6d031350c67f'
omit=[]
for node in data['nodes']:
    if node.get('distant') or not node.get('instances'):continue
    for ix,inst in enumerate(node['instances']):
        p,s=inst['position'],inst['scale'];kind=None
        if -7<p[0]<8 and -6.2<p[2]<-1.2 and 0<p[1]<3.1:
            if node['materials']==[STONE] and .23<s[1]<.31 and .12<s[2]<.23 and .5<s[0]<1:kind='riser'
            if node['materials']==[FLOOR] and .06<s[1]<.08 and .4<s[2]<.55 and .5<s[0]<1:kind='tread'
            if node['materials']==[FLOOR] and s[1]<.06 and s[2]<.09:kind='lip'
        if kind:omit.append({'nodeId':node['id'],'nodeName':node['name'],'geometry':node['geometry'],'materialId':node['materials'][0],'instanceIndex':ix,'kind':kind,**inst})
counts={k:sum(r['kind']==k for r in omit) for k in ['riser','tread','lip']}
assert counts=={'riser':90,'tread':90,'lip':98},counts
manifest={'bridge_sha256':hashlib.sha256(BRIDGE.read_bytes()).hexdigest(),'selection':'original unfiltered node.instances index, checked against node/material/position/quaternion/scale/color','counts':counts,'instances':omit,'retained':['10 dark stair supports','landing floor','cheek walls','rubble','portal','all other instances']}
(OUT/'stair-removal-manifest.json').write_text(json.dumps(manifest,indent=2))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def mat(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=.74;return m
clay=mat('Neutral stone geometry inspection',(.22,.245,.26))
before=bpy.data.collections.new('Before source assembly');bpy.context.scene.collection.children.link(before)
after=bpy.data.collections.new('After one-piece stones');bpy.context.scene.collection.children.link(after)
def place_in(ob,col):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    col.objects.link(ob)
for k,r in enumerate(omit):
    source=json.loads((ROOT/'Migration/Source/AtmosphereV2/StoneV7/runtime'/(r['geometry']+'.json')).read_text())
    pos=source['positions'];verts=[(pos[i],-pos[i+2],pos[i+1]) for i in range(0,len(pos),3)]
    inds=source['indices'];faces=[inds[i:i+3] for i in range(0,len(inds),3)]
    me=bpy.data.meshes.new('Preserved component');me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new('Before '+r['kind']+' '+str(k),me);before.objects.link(ob)
    p=r['position'];s=r['scale'];q=r['quaternion']
    ob.location=(-p[0],-p[2],p[1]);ob.scale=(s[0],s[2],s[1]);ob.rotation_mode='QUATERNION';ob.rotation_quaternion=Quaternion((q[3],q[0],q[2],-q[1]));me.materials.append(clay)

def cut(ob,points):
    bm=bmesh.new()
    for p in points:bm.verts.new(p)
    bmesh.ops.convex_hull(bm,input=list(bm.verts));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    me=bpy.data.meshes.new('Temporary chisel');bm.to_mesh(me);bm.free();tool=bpy.data.objects.new('Temporary chisel',me);after.objects.link(tool)
    bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Finite open edge fracture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)

rng=random.Random(11036);objects=[];rows=[]
treads=[r for r in omit if r['kind']=='tread']
left=min(-r['position'][0]-r['scale'][0]/2 for r in treads)
right=max(-r['position'][0]+r['scale'][0]/2 for r in treads)
for row in range(10):
    # Same total flight width. Paired joint offsets vary by row and column.
    nominal=(right-left)/9
    offsets=[0]+[(.18 if row%2 else -.14)*nominal + rng.uniform(-.065,.065) for i in range(8)]+[0]
    cuts=[left+i*nominal+offsets[i] for i in range(10)]
    ytop=(row+1)*.29+.042;zcenter=-1.75-row*.49
    rowinfo={'row':row,'unity_top':ytop,'unity_z':zcenter,'boundaries_x':cuts,'stones':[]}
    for col in range(9):
        xmin=cuts[col]+(.008 if col else 0)
        xmax=cuts[col+1]-(.008 if col<8 else 0)
        # 3cm depth variation at hidden rear edge, front kept near inherited nose.
        front=zcenter+.291;back=zcenter-.225-rng.uniform(0,.014)
        bottom=ytop-.32
        bpy.ops.mesh.primitive_cube_add(size=1,location=((xmin+xmax)/2,-(front+back)/2,(ytop+bottom)/2))
        ob=bpy.context.object;ob.name=f'Carved stair {row:02}-{col:02}';place_in(ob,after)
        ob.dimensions=(xmax-xmin,front-back,ytop-bottom);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        # Bake location for a world-space authored scene and deterministic cuts.
        bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
        bevel=ob.modifiers.new('Worn arris 4-7 mm','BEVEL');bevel.width=rng.uniform(.004,.007);bevel.segments=1
        bpy.ops.object.modifier_apply(modifier=bevel.name)
        damaged=(row*9+col)%3==1
        if damaged:
            cx=xmin+(xmax-xmin)*rng.uniform(.18,.82);half=rng.uniform(.075,.14);depth=rng.uniform(.018,.042);down=rng.uniform(.014,.037)
            # Broad chipped front nose, slanted uneven internal fracture plane.
            cut(ob,[(cx-half,-front-.025,ytop+.03),(cx+half,-front-.025,ytop+.03),(cx+half*.78,-front+depth,ytop+.03),(cx-half*.7,-front+depth*.7,ytop+.03),
                    (cx-half*.85,-front-.025,ytop-down),(cx+half*.62,-front-.025,ytop-down*.62),(cx,-front+depth*.55,ytop-.004)])
        me=ob.data;bm=bmesh.new();bm.from_mesh(me)
        # Densify actual stone planes for shallow nonuniform wear; no rounded subdivision.
        long=[e for e in bm.edges if e.calc_length()>.085]
        bmesh.ops.subdivide_edges(bm,edges=long,cuts=3,use_grid_fill=True)
        bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        # Shallow hollow in walking contact and one unequal face flake, tapering to edges.
        cx=(xmin+xmax)/2;by=-(front+back)/2
        for v in bm.verts:
            p=v.co
            if p.z>ytop-.012:
                u=(p.x-cx)/((xmax-xmin)/2);w=(p.y-by)/((front-back)/2)
                p.z-=.0025*max(0,1-u*u)*max(0,1-w*w)*(1+.4*math.sin(p.x*13+row))
            if abs(p.y+front)<.015:
                u=(p.x-(xmin+(xmax-xmin)*(.35 if col%2 else .65)))/.22;v1=(p.z-(bottom+.16))/.12
                p.y+=rng.uniform(.0015,.0045)*max(0,1-u*u-v1*v1)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
        me.materials.append(clay)
        # Hard split planes keep chisel losses readable; no inflated smooth corners.
        for p in me.polygons:p.use_smooth=False
        ob['tone']=.91+rng.random()*.13;objects.append(ob)
        rowinfo['stones'].append({'name':ob.name,'width':xmax-xmin,'nose_loss':damaged})
    rows.append(rowinfo)

scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.world.color=(.08,.08,.08)
scene.render.resolution_x=1536;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(-10,-11,12));cam=bpy.context.object;cam.rotation_euler=(Vector((-2.8,3.7,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=10.8;scene.camera=cam
for loc,energy,size in [((-5,-4,10),1500,5),((2,6,5),500,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=energy;l.data.size=size;l.rotation_euler=(Vector((-2.8,3.7,1.2))-l.location).to_track_quat('-Z','Y').to_euler()
def render(name,show_after):
    before.hide_render=show_after;after.hide_render=not show_after;scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
render('preview-before-clay.png',False);render('preview-after-clay.png',True)
pos=[];norm=[];uv=[];colors=[];inds=[];qa=[]
for ob in objects:
    me=ob.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
    qa.append({'name':ob.name,'triangles':len(me.loop_triangles),'nonmanifold_edges':nonmanifold})
    for tri in me.loop_triangles:
        for ix in tri.vertices:
            p=me.vertices[ix].co;n=tri.normal
            inds.append(len(pos)//3);pos.extend((p.x,p.z,-p.y));norm.extend((n.x,n.z,-n.y));uv.extend((p.x,-p.y));colors.extend((ob['tone'],)*3+(1,))
negative=degenerate=0
for i in range(0,len(inds),3):
    a,b,c=[Vector(pos[3*k:3*k+3]) for k in inds[i:i+3]];cross=(b-a).cross(c-a);n=Vector(norm[3*inds[i]:3*inds[i]+3])
    negative+=cross.dot(n)<0;degenerate+=cross.length<1e-10
mesh={'id':'stairs-v11','name':'One-piece worn staircase V11','positions':pos,'normals':norm,'uv':uv,'colors':colors,'indices':inds}
file=OUT/'stairs-v11-mesh.json';file.write_text(json.dumps(mesh,separators=(',',':')))
report={'mesh_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'bridge_sha256':manifest['bridge_sha256'],'triangles':len(inds)//3,'vertices':len(pos)//3,'negative_normal_dots':negative,'degenerate_triangles':degenerate,'nonmanifold_edges':sum(q['nonmanifold_edges'] for q in qa),'basis':'Unity world positions/normals (Blender x,z,-y), same triangle order; identity GameObject transform','stone_count':len(objects),'rows':rows,'objects':qa,'bounds':[[min(pos[i::3]) for i in range(3)],[max(pos[i::3]) for i in range(3)]],'removal_counts':counts,'known_limits':['Neutral Blender geometry only; native material and lighting acceptance pending.','Before clay recreates preserved V7 source components; native V8 riser replacements can have different small chips.']}
assert not negative and not degenerate and not report['nonmanifold_edges'],report
(OUT/'export-validation.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'stairs-v11.blend'))
print('STAIRS_V11_COMPLETE',len(objects),report['triangles'])
