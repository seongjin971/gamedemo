import bpy, math, json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'ArtSource').is_dir())
bpy.ops.wm.open_mainfile(filepath=str(root/'ArtSource/stone-v5.blend'))
names=['Flagstone_Split','Flagstone_Spalled','Flagstone_Laminated','Flagstone_Weathered','Flagstone_Cleft','Flagstone_Granular','Flagstone_Worn','Flagstone_Branched','Masonry_Broken','Masonry_Quarried']
ids=['740f8589-aea6-4e9f-831f-6adbdb49ada3','f01cf337-cea7-42b3-b142-24f2fc145766','639f340b-3b93-4211-a7ff-cd35c89a1f9f','4bf543ce-10f0-4018-88ca-18754deeeb53','b761423f-facb-4ef9-9d08-71d49f2eb0d8','4bbd6673-eca6-49ea-bb85-529da237542a','7a2d80e2-5804-4629-8fcd-a6045025c7c6','c9afbeaf-3585-4c29-a0e1-fcd500940346','7b9ce760-2f47-40f1-98d7-6b4e0aadc2e5','30387f49-1a6e-42e9-80e4-01b8c8c559c1']
report=[]
for k,name in enumerate(names):
 ob=bpy.data.objects[name];me=ob.data
 for v in me.vertices:
  x,y,z=v.co
  if k<8:
   if z>.39:v.co.z=.455+(z-.455)*.32
   # Broad asymmetric missing corner, rather than rounded edge along every side.
   sx=1 if k%2 else -1;sy=1 if k%3 else -1
   d=x*sx+y*sy
   if d>.81:
    amount=(d-.81)*.52
    v.co.x-=sx*amount;v.co.y-=sy*amount
   # Keep a flat quarried face; add two shallow planar cleavage regions.
   if z>.38:
    v.co.z-=max(0,min(.032,(x*math.cos(k)-y*math.sin(k)-.1)*.065))
  else:
   # A wide spall across one projecting corner of each masonry variant.
   sx=1 if k%2 else -1
   d=x*sx+y*.55+z*.45
   if d>.62:
    amount=(d-.62)*.40
    v.co.x-=sx*amount;v.co.y-=amount*.55;v.co.z-=amount*.45
 me.update();me.calc_loop_triangles()
 for p in me.polygons:
  # Flat split stone strata; retain existing smoothness for tiny bevels.
  if k<8 and p.normal.z>.75:p.use_smooth=False
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
 data={'id':ids[k],'name':name,'positions':verts,'normals':norm,'uv':uv,'indices':inds}
 (out/(ids[k]+'.json')).write_text(json.dumps(data,separators=(',',':')))
 report.append({'name':name,'vertices':len(verts)//3,'triangles':len(inds)//3})
bpy.ops.wm.save_as_mainfile(filepath=str(out/'stone-v6.blend'))
(out/'stone-v6-report.json').write_text(json.dumps(report,indent=2))
