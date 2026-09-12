"""Small physical slab/soil covers on actual Paving15 support, world-space export.
Runs only after TreeV16 tree geometry passes. Contact14 stays unmodified.
"""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
pave=json.loads((W.parent/'PavingV15/paving-v15-mesh.json').read_text());p=pave['positions'];idx=pave['indices'];pv=[p[i:i+3] for i in range(0,len(p),3)];bvh=BVHTree.FromPolygons(pv,[idx[i:i+3] for i in range(0,len(idx),3)],all_triangles=True)
def ground(x,z):
 h=bvh.ray_cast(Vector((x,2,z)),Vector((0,-1,0)),4)[0]
 assert h is not None,(x,z,'No exact floor support')
 return h.y
yaw=math.radians(-25.729577951308233);cs,sn=math.cos(yaw),math.sin(yaw)
def rootpoint(angle,r,k):
 # Matches full terminal narrowing/turn of build_tree_v16.py.
 if k==3:r-=.34;angle-=.50
 nx,nz=-r*math.cos(angle),-r*math.sin(angle)
 return (7.2+1.73*(cs*nx+sn*nz),3.7+1.73*(-sn*nx+cs*nz))
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
stone=mat('Reuse existing Rock05 stone in Unity',(.29,.30,.31));soil=mat('Reuse existing mineral grain with dark earth tint',(.052,.039,.027))
objects=[];rows=[]
def body(name,center,angle,length,width,height,material,color):
 cx,cz=center;shape=[(-.50,-.33),(-.29,-.52),(.23,-.43),(.51,-.14),(.41,.41),(-.15,.50),(-.45,.13)];co=[]
 for u,v in shape:
  dx=u*length;dz=v*width;co.append((cx+math.cos(angle)*dx+math.sin(angle)*dz,cz-math.sin(angle)*dx+math.cos(angle)*dz))
 supports=[ground(x,z) for x,z in co];base=max(supports)-.008
 verts=[(x,-z,support-.008) for (x,z),support in zip(co,supports)]
 for j,(x,z) in enumerate(co):verts.append((cx+(x-cx)*.94,-cz-(z-cz)*.94,base+height*(.75+.22*math.sin(j*1.8+len(objects)))))
 n=len(co);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(material)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume()>1e-9 and all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free();ob['color']=color;objects.append(ob)
 rows.append(dict(name=name,centerWorldXZ=center,actualFloorSupportMinMax=[min(supports),max(supports)],baseWorldY=base,nominalLength=length,nominalWidth=width,nominalHeight=height))
for k,(angle,end) in enumerate(zip([-2.6,-.9,.45,2.15],[1.76,1.60,1.73,1.75])):
 center=rootpoint(angle,end*.93,k)
 # The parapet is already the physical large cover; do not pile another slab
 # against it. Only the three floor roots receive new fractured covers.
 if k<3:
  body('TreeV16 root '+str(k+1)+' broken slab cover',center,angle+yaw,.56 if k==1 else .47,.39 if k==1 else .34,.065,stone,(.79,.81,.82))
  direction=(center[0]-7.2,center[1]-3.7);mag=math.hypot(*direction);side=(-direction[1]/mag,direction[0]/mag)
  soilcenter=(center[0]+side[0]*.15-direction[0]/mag*.12,center[1]+side[1]*.15-direction[1]/mag*.12)
  body('TreeV16 root '+str(k+1)+' entry earth',soilcenter,angle+yaw,.58,.42,.035,soil,(.19,.145,.105))
def export(which,name):
 pos=[];normal=[];uv=[];color=[];ids=[];parts=[]
 for ob in which:
  start=len(ids);m=ob.data;m.calc_loop_triangles()
  for tri in m.loop_triangles:
   n=tri.normal
   for vi in tri.vertices:
    p=m.vertices[vi].co;pos.extend((p.x,p.z,-p.y));normal.extend((n.x,n.z,-n.y));uv.extend((p.x,-p.y));color.extend((*ob['color'],1));ids.append(len(ids))
  parts.append(dict(name=ob.name,indexStart=start,indexCount=len(ids)-start))
 d=dict(name=name,id=name,positions=pos,normals=normal,uv=uv,colors=color,indices=ids);path=W/(name+'.json');path.write_text(json.dumps(d,separators=(',',':')));return dict(file=path.name,parts=parts,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),triangles=len(ids)//3)
exports=[export([o for o in objects if 'slab' in o.name],'tree-v16-covers'),export([o for o in objects if 'earth' in o.name],'tree-v16-soil')]
bpy.ops.wm.save_as_mainfile(filepath=str(W/'tree-v16-covers.blend'))
report=dict(worldSpaceIdentity=True,coordinateBasis='Native Unity world x,y,z. Blender x,z,-y conversion preserves orientation; no extra reflection.',sourcePaving='PavingV15',pieces=rows,exports=exports,contact14Preserved=True,possibleOverlap='Existing Root soil contact 1/2/3 deposits are retained in preview. Small overlap is intentional layering; no original IDs requested for removal. Review for double ledges in native view.',parapetCover='Existing actual parapet stones cover root4. No floating horizontal cover outside the floor.')
(W/'covers-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
