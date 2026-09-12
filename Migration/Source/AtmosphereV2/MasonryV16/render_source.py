"""Blender source comparison at the actual Unity full camera; no Unity writes."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Quaternion
OUT=Path(__file__).resolve().parent;ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir());SRC=OUT.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=1536;s.render.resolution_y=1024;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Neutral masonry context');s.world.color=(.075,.085,.10)
def collection(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);return c
context=collection('Preserved source context');before=collection('Before candidate52 masonry');after=collection('After MasonryV16');allobjects=[]
def mat(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.82;return m
clay=mat('Neutral clay',(.33,.36,.38));wood=mat('Retained tree context',(.095,.078,.065));floor=mat('Retained paving context',(.23,.25,.26));rock=mat('Existing licensed Rock05',(.32,.34,.35))
nodes=rock.node_tree.nodes;links=rock.node_tree.links;p=nodes.get('Principled BSDF');uv=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=.60;links.new(uv.outputs['UV'],mapping.inputs[0])
texroot=ROOT/'Unity/Vesper/Assets/Vesper/AtmosphereV2/Textures'
for file,socket,space in [('rock_05_diff_2k.png','Base Color','sRGB'),('rock_05_rough_2k.png','Roughness','Non-Color')]:
 t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(texroot/file),check_existing=True);t.image.colorspace_settings.name=space;links.new(mapping.outputs[0],t.inputs['Vector']);links.new(t.outputs['Color'],p.inputs[socket])
t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(texroot/'rock_05_nor_gl_2k.png'),check_existing=True);t.image.colorspace_settings.name='Non-Color';nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=1.2;links.new(mapping.outputs[0],t.inputs['Vector']);links.new(t.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs[0],p.inputs['Normal'])
normalmat=bpy.data.materials.new('Unlit geometry normals');normalmat.use_nodes=True;nn=normalmat.node_tree.nodes;ll=normalmat.node_tree.links;nn.clear();o=nn.new('ShaderNodeOutputMaterial');em=nn.new('ShaderNodeEmission');geo=nn.new('ShaderNodeNewGeometry');mul=nn.new('ShaderNodeVectorMath');mul.operation='MULTIPLY_ADD';mul.inputs[1].default_value=(.5,.5,.5);mul.inputs[2].default_value=(.5,.5,.5);ll.new(geo.outputs['Normal'],mul.inputs[0]);ll.new(mul.outputs['Vector'],em.inputs['Color']);ll.new(em.outputs[0],o.inputs['Surface'])
cache={}
def native(name,d,col,material=clay,shared=None):
 if shared and shared in cache:me=cache[shared]
 else:
  pos=d['positions'];idx=d['indices'];me=bpy.data.meshes.new(name);me.from_pydata([(pos[k],-pos[k+2],pos[k+1]) for k in range(0,len(pos),3)],[],[idx[k:k+3] for k in range(0,len(idx),3)]);me.update()
  for f in me.polygons:f.use_smooth=True
  if d.get('normals'):
   n=d['normals'];me.normals_split_custom_set_from_vertices([(n[k],-n[k+2],n[k+1]) for k in range(0,len(n),3)])
  uv=d.get('uv');layer=me.uv_layers.new(name='Source metre UV')
  if uv:
   for loop in me.loops:layer.data[loop.index].uv=uv[loop.vertex_index*2:loop.vertex_index*2+2]
  if shared:cache[shared]=me
 ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.data.materials.clear();ob.data.materials.append(material);allobjects.append(ob);return ob
def instance(ob,i):
 p,sc,q=i['position'],i['scale'],i['quaternion'];ob.location=(-p[0],-p[2],p[1]);ob.scale=(sc[0],sc[2],sc[1]);ob.rotation_mode='QUATERNION';ob.rotation_quaternion=Quaternion((q[3],q[0],q[2],-q[1]))
bridge=read(ROOT/'Unity/Vesper/Assets/Vesper/Import/unity-scene.json')
heroes=read(OUT/'hero-overrides.json')['overrides'];heroids={(r['nodeId'],r['instanceIndex']):r for r in heroes}
fa=read(OUT/'facade-removal-manifest.json')['instances'];faids={(r['nodeId'],r['instanceIndex']) for r in fa}
old13=read(SRC/'MasonryV13/architecture-overrides.json')['overrides'];oldids={(r['nodeId'],r['instanceIndex']):r for r in old13}
stairomit={(r['nodeId'],r['instanceIndex']) for r in read(SRC/'MasonryV11/stair-removal-manifest.json')['instances']}
contactomit={(r['nodeId'],r['instanceIndex']) for r in read(SRC/'ContactV14/rubble-removal-manifest.json')['instances']}
variants=[read(SRC/f'MasonryV12/masonry-v12-{j}.json') for j in range(6)];count=0
for n in bridge['nodes']:
 path=SRC/'StoneV7/runtime'/(n.get('geometry','')+'.json')
 if n.get('distant') or not n.get('instances') or not path.exists():continue
 source=read(path);selected=[(ix,i) for ix,i in enumerate(n['instances']) if -10<=i['position'][0]<=10 and -13<=i['position'][2]<=22 and -3.6<=i['position'][1]<=15]
 originalselected=[ix for ix,i in enumerate(n['instances']) if -10<=i['position'][0]<=10 and -13<=i['position'][2]<=22 and -3<=i['position'][1]<=15]
 for ix,i in selected:
  ident=(n['id'],ix);p,sc=i['position'],i['scale']
  if ident in stairomit or ident in contactomit:continue
  if n['materials'][0]=='1ba07011-f8c4-4d07-9550-6d031350c67f' and p[1]<.2:continue
  if ix in originalselected:
   j=originalselected.index(ix);seed=j+(j//100)*7
  else:seed=[k for k in range(len(n['instances'])) if k not in originalselected].index(ix)
  data=variants[seed%6] if min(sc)>.12 and max(sc)<2.8 else source
  key=f'V12-{seed%6}' if data is not source else n['geometry']
  if ident in oldids:data=read(SRC/'MasonryV13'/oldids[ident]['replacement']);key=oldids[ident]['replacement']
  col=before if ident in heroids or ident in faids else context
  ob=native(f'Bridge {n["id"][:8]} {ix}',data,col,shared=key);instance(ob,i);count+=1
  if ident in heroids:
   ob=native(f'New lower hero {ix}',read(OUT/heroids[ident]['replacement']),after);instance(ob,i)
native('Before exact V13 stairs',read(SRC/'MasonryV13/stairs-v13-mesh.json'),before)
native('After half rebuilt flight',read(OUT/'stairs-v16-mesh.json'),after)
native('After right running bond',read(OUT/'facade-v16-mesh.json'),after)
native('Unchanged actual PavingV15',read(SRC/'PavingV15/paving-v15-mesh.json'),context,floor)
tree=native('Unchanged actual TreeV12',read(SRC/'TreeV12/derivative/tree-v12-mesh.json'),context,wood);tree.scale=(1.73,)*3;tree.location=(7.2,-3.7,0);tree.rotation_euler[2]=math.radians(-25.7295779513)
for part in ('rubble','deposits'):native('Unchanged ContactV14 '+part,read(SRC/f'ContactV14/contact-v14-{part}.json'),context,clay)
cd=bpy.data.cameras.new('Unity52 full camera');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);s.camera=cam;cd.type='ORTHO';cd.ortho_scale=(14.1/1.27)*2*1.5
focus=Vector((0,-.7,2.9));a=.46;e=.72;cam.location=focus+Vector((-math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))*42;cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler()
cam.scale.x=-1 # Match Unity's handed camera basis without mirroring source geometry.
for name,loc,power,size in [('Large directional clay key',(-12,-1,18),2500,7),('Soft reverse', (8,10,14),1800,9)]:
 light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;ob=bpy.data.objects.new(name,light);s.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((-3,3,2))-ob.location).to_track_quat('-Z','Y').to_euler()
def render(filename):
 s.render.filepath=str(OUT/filename);bpy.ops.render.render(write_still=True)
def pair(mode):
 s.view_layers[0].material_override=normalmat if mode=='normal' else (clay if mode=='clay' else None)
 if mode=='material':
  bpy.context.view_layer.update()
  for ob in context.objects.values():
   if ob.data.materials and ob.data.materials[0] not in (wood,floor):ob.data.materials.clear();ob.data.materials.append(rock)
  for ob in list(before.objects.values())+list(after.objects.values()):
   ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(rock)
   matrix=ob.matrix_world;normalmatrix=matrix.to_3x3().inverted().transposed();layer=ob.data.uv_layers.active
   for poly in ob.data.polygons:
    bn=(normalmatrix@poly.normal).normalized();nn=(bn.x,bn.z,-bn.y);axis=max(range(3),key=lambda k:abs(nn[k]))
    for li in poly.loop_indices:
     bp=matrix@ob.data.vertices[ob.data.loops[li].vertex_index].co;pp=(bp.x,bp.z,-bp.y)
     layer.data[li].uv=[(pp[2],pp[1]),(pp[0],pp[2]),(pp[0],pp[1])][axis]
 for label in ['before','after']:
  if '--after-only' in sys.argv and label=='before' and mode!='material':continue
  before.hide_render=label!='before';after.hide_render=label!='after';render(f'full-{mode}-{label}.png')
if '--material-only' not in sys.argv:
 pair('normal');pair('clay')
pair('material')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'masonry-v16-context.blend'))
if '--crops' in sys.argv:
 s.render.use_border=True;s.render.use_crop_to_border=True
 for name,rect in [('stairs',(750,1175,340,660)),('hero',(655,1280,220,690)),('facade',(965,1410,490,970))]:
  x0,x1,y0,y1=rect;s.render.border_min_x=x0/1536;s.render.border_max_x=x1/1536;s.render.border_min_y=1-y1/1024;s.render.border_max_y=1-y0/1024
  for label in ('before','after'):
   before.hide_render=label!='before';after.hide_render=label!='after';render(f'{name}-material-{label}.png')
 s.render.use_border=False;s.render.use_crop_to_border=False
(OUT/'render-context.json').write_text(json.dumps({'camera':'Native full candidate52 projection; 1536x1024','bridge_instances':count,'tree':'Complete unchanged V12','paving':'Complete unchanged V15','limits':['Source clay/material comparison, not Unity render.','Lighting is matched between before/after but is not the Unity HDR environment.','Non-instanced arch rings, fire effects and character are excluded.','Deep vertical shaft context uses preserved source geometry; replacement facade rows are explicit.'],'renders':['full-'+m+'-'+v+'.png' for m in ('normal','clay','material') for v in ('before','after')]},indent=2));print('MASONRY_V16_RENDER_COMPLETE',count)
