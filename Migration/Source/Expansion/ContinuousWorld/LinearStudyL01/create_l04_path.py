"""Irregular interlocking limestone paving, new Blender bundle only."""
import bpy,bmesh,math,random,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
SOURCE=Path(__file__).resolve().parent/'L04Details'
OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/LinearWorld/Art/EnvironmentKit/L04Details'
if OUT.exists():raise RuntimeError('Refuse existing bundle')
SOURCE.mkdir(exist_ok=True);OUT.mkdir(parents=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats=[]
for name,col in [('CW_ChapelPavingStone',(.38,.40,.37,1)),('CW_ChapelPavingStoneLight',(.45,.46,.42,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=col;mats.append(m)
def clip(poly,a,b):
 n=(b[0]-a[0],b[1]-a[1]);offset=(b[0]*b[0]+b[1]*b[1]-a[0]*a[0]-a[1]*a[1])/2
 def dist(p):return p[0]*n[0]+p[1]*n[1]-offset
 out=[]
 for j,p in enumerate(poly):
  q=poly[(j+1)%len(poly)];dp,dq=dist(p),dist(q)
  if dp<=0:out.append(p)
  if (dp<0)!=(dq<0):t=dp/(dp-dq);out.append((p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t))
 return out
records=[]
for variant in range(3):
 r=random.Random(7301+variant*17);seeds=[];vs=[];fs=[];slots=[]
 for row in range(7):
  for col in range(5):seeds.append((-1.75+(col+.5)*.7+r.uniform(-.20,.20),-2+(row+.5)*4/7+r.uniform(-.18,.18)))
 for index,seed in enumerate(seeds):
  poly=[(-1.75,-2),(1.75,-2),(1.75,2),(-1.75,2)]
  for other in seeds:
   if seed!=other and poly:poly=clip(poly,seed,other)
  if len(poly)<3:continue
  cx=sum(x for x,y in poly)/len(poly);cy=sum(y for x,y in poly)/len(poly)
  inset=r.uniform(.022,.045);poly=[(x+(cx-x)*inset,y+(cy-y)*inset) for x,y in poly]
  n=len(poly);base=len(vs);top=r.uniform(.004,.022)
  for level,z in [(0,-.14),(1,-.012),(2,top)]:
   for x,y in poly:vs.append((x+(cx-x)*(.045 if level==2 else 0),y+(cy-y)*(.045 if level==2 else 0),z))
  vs.append((cx,cy,top+r.uniform(.001,.015)))
  for layer in range(2):
   for j in range(n):a=base+layer*n+j;b=base+layer*n+(j+1)%n;fs.append((a,b,b+n,a+n));slots.append(index%5==0)
  for j in range(n):fs.append((base+2*n+j,base+2*n+(j+1)%n,base+3*n));slots.append(index%5==0)
 me=bpy.data.meshes.new('Worn fieldstones');me.from_pydata(vs,[],fs);me.update()
 for m in mats:me.materials.append(m)
 for p,slot in zip(me.polygons,slots):p.material_index=int(slot)
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  for li in p.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.25,v.y*.25)
 ob=bpy.data.objects.new('LinearIrregular_'+str(variant+1),me);bpy.context.collection.objects.link(ob)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(OUT/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False)
 records.append({'name':ob.name,'stones':len(seeds),'triangles':len(me.polygons),'width':3.5,'length':4})
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'IrregularPath.blend'))
(SOURCE/'manifest.json').write_text(json.dumps(records,indent=2));print('LINEAR_L04_DETAILS_COMPLETE')
