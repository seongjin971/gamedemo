"""Matched actual V15 floor/Contact14/parapet context; source-only images.
Native full/zoom/glare camera parameters, plus one useful root close-up.
This is Blender material context, not a Unity shader reproduction.
"""
import bpy,json,math,os
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(W.parent/'ContactV14/contact-v14.blend'))
scene=bpy.context.scene
for o in list(bpy.data.objects):
 if o.type in ('CAMERA','LIGHT') or o.name.startswith('Actual intact Tree') or o.name.startswith('Complete unmodified paving'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(W/'tree-v16.blend'),link=False) as (a,b):b.objects=[n for n in a.objects if n.startswith('TreeV16')]
source=next(o for o in b.objects if o);materials=list(source.data.materials);bpy.data.objects.remove(source,do_unlink=True)
for m in materials:
 if not m.use_nodes:continue
 bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 for l in list(m.node_tree.links):
  if l.to_node==bs and l.to_socket.name in ('Roughness','Metallic'):m.node_tree.links.remove(l)
 bs.inputs['Roughness'].default_value=.85;bs.inputs['Metallic'].default_value=0
 # Equal current native dark wood tint; underlying photo maps and normal detail stay.
 links=[l for l in m.node_tree.links if l.to_node==bs and l.to_socket.name=='Base Color']
 if links:
  link=links[0];up=link.from_socket;m.node_tree.links.remove(link);mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.8,.8,.8,1);m.node_tree.links.new(up,mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],bs.inputs['Base Color'])
def native(name,path,mats):
 d=json.loads(path.read_text());p=d['positions'];ns=d['normals'];uv=d['uv'];ids=d['indices'];me=bpy.data.meshes.new(name);me.from_pydata([(p[i],-p[i+2],p[i+1]) for i in range(0,len(p),3)],[],[ids[i:i+3] for i in range(0,len(ids),3)]);me.update();ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob)
 for mat in mats:me.materials.append(mat)
 layer=me.uv_layers.new(name='UVMap')
 for i,l in enumerate(me.loops):layer.data[i].uv=uv[2*l.vertex_index:2*l.vertex_index+2]
 for f in me.polygons:f.use_smooth=True
 me.normals_split_custom_set_from_vertices([(ns[i],-ns[i+2],ns[i+1]) for i in range(0,len(ns),3)])
 return ob
trees=[]
for tag,path in [('before',W.parent/'TreeV12/derivative/tree-v12-mesh.json'),('after',W/'tree-v16-mesh.json')]:
 ob=native('Tree '+tag,path,materials);ob.location=(7.2,-3.7,0);ob.scale=(1.73,1.73,1.73);ob.rotation_euler.z=math.radians(-25.729577951308233);trees.append(ob)
floor_mat=bpy.data.materials.get('Paving context');native('Exact PavingV15 context',W.parent/'PavingV15/paving-v15-mesh.json',[floor_mat])
with bpy.data.libraries.load(str(W/'tree-v16-covers.blend'),link=False) as(a,b):b.objects=a.objects
covers=[o for o in b.objects if o]
for o in covers:scene.collection.objects.link(o)
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_x=1536;scene.render.resolution_y=1024;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.world.color=(.065,.075,.085)
for name,loc,power,size in [('Cool broad',(-6,-1,15),2100,7),('Soft opposing',(11,5,10),1000,6)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((7,-3,4))-o.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Exact native camera angles');cam=bpy.data.objects.new('Exact native camera angles',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
def camera(focus,angle,elev,ortho):
 f=Vector((focus[0],-focus[2],focus[1]));cam.location=f+Vector((-math.sin(angle)*math.cos(elev),-math.cos(angle)*math.cos(elev),math.sin(elev)))*42;cam.rotation_euler=(f-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=ortho*2
views=[('full',(0,2.9,.7),.46,.72,14.1/1.27),('zoom',(0,2.9,.7),.46,.72,8.8),('glare-orbit',(0,2.9,.7),1.05980349,.73530388,11.1023626),('roots',(7.0,.55,3.6),.72,.78,3.0)]
for tag,ob in zip(['before','after'],trees):
 for t in trees:t.hide_render=t!=ob
 for c in covers:c.hide_render=tag=='before'
 for name,focus,a,e,scale in views:
  if os.environ.get('TREE16_ROOT_ONLY')=='1' and name!='roots':continue
  if os.environ.get('TREE16_SKIP_ROOTS')=='1' and name=='roots':continue
  camera(focus,a,e,scale)
  if name=='glare-orbit':
   cam.location=(-27.1694241,-15.9328890,31.0741272);direction=Vector((math.sin(a)*math.cos(e),math.cos(a)*math.cos(e),-math.sin(e)));cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
  scene.render.filepath=str(W/(name+'-'+tag+'.png'));bpy.ops.render.render(write_still=True)
print('TreeV16 matched context previews complete; no source saves')
