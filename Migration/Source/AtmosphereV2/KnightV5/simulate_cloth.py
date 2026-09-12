"""Physics-authored heavy-wool cape. Run in Blender 5.2.1, background, 6 threads."""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent
ROOT=next(r for r in W.parents if (r/'Migration/Source/AtmosphereV2/Knight').is_dir())
S=ROOT/'Migration/Source/AtmosphereV2/Knight';SRC=S/'knight-v3.blend';J=S/'knight-v3-unity-meshes.json'
bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene
original=bpy.data.objects['Heavy folded crimson cape'];matrix=original.matrix_world.copy();materials=list(original.data.materials)
original.hide_render=True
verts=[];rest=[];faces=[];C=45;R=43
for j in range(R):
 t=j/(R-1)
 for i in range(C):
  s=i/(C-1)*2-1
  # Smooth initial surface and wide relaxed sewing pattern, no authored grooves.
  width=.17+.205*t
  y=.023+.33*t+.024*math.sin(s*math.pi*.75+.5)*math.sin(math.pi*t)
  z=-.97*t+.008*t*t*s
  verts.append((s*width+.025*t*t,y,z))
  rest.append((s*(.205+.180*t),.02,-1.005*t+.020*t*t*s))
for j in range(R-1):
 for i in range(C-1):faces.append((j*C+i,j*C+i+1,(j+1)*C+i+1,(j+1)*C+i))
m=bpy.data.meshes.new('Wool sewing pattern simulation cage');m.from_pydata(verts,[],faces);m.update()
cloth=bpy.data.objects.new('TEMP physics cape',m);scene.collection.objects.link(cloth);cloth.matrix_world=matrix
for mat in materials:m.materials.append(mat)
for p in m.polygons:p.use_smooth=True
uv=m.uv_layers.new(name='UVMap')
for p in m.polygons:
 for li in p.loop_indices:
  vi=m.loops[li].vertex_index;uv.data[li].uv=(vi%C/(C-1),vi//C/(R-1))
cloth.shape_key_add(name='Gathered initial surface');rk=cloth.shape_key_add(name='Relaxed broad wool pattern')
for v,p in zip(rk.data,rest):v.co=p
rk.value=0
pin=cloth.vertex_groups.new(name='Pinned shoulder seam');pin.add(list(range(C)),1.0,'REPLACE')
cm=cloth.modifiers.new('Heavy wool cloth simulation','CLOTH');st=cm.settings
st.quality=12;st.mass=.42;st.air_damping=6;st.tension_stiffness=35;st.compression_stiffness=35;st.shear_stiffness=16;st.bending_stiffness=3;st.bending_damping=3
st.vertex_group_mass=pin.name;st.pin_stiffness=1;st.rest_shape_key=rk
co=cm.collision_settings;co.use_collision=True;co.distance_min=.006;co.collision_quality=6;co.use_self_collision=True;co.self_distance_min=.006;co.self_friction=8
proxies=[]
for name,center,radii in [('torso',(0,-.11,-.22),(.215,.145,.30)),('hips',(.015,-.095,-.49),(.185,.15,.18)),('left thigh',(-.075,-.12,-.72),(.08,.11,.22)),('right thigh',(.075,-.12,-.72),(.08,.11,.22))]:
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=matrix@Vector(center));p=bpy.context.object;p.name='TEMP collision '+name;p.scale=radii
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 p.modifiers.new('Collision','COLLISION');p.collision.thickness_outer=.007;p.collision.cloth_friction=8;p.hide_render=True;proxies.append(p)
# Wind gives the existing gently trailing broad placement a physical cause.
bpy.ops.object.effector_add(type='WIND',location=(0,-2,1),rotation=(-math.pi/2,0,0));wind=bpy.context.object;wind.name='TEMP steady trailing air';wind.field.strength=900;wind.field.noise=.0
scene.gravity=(0,0,-9.81);scene.frame_start=1;scene.frame_end=140;scene.render.fps=30
cm.point_cache.frame_start=1;cm.point_cache.frame_end=140
scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(W/'cloth-v5-authoring.blend'))
samples=[]
for frame in range(1,141):
 scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();ev=cloth.evaluated_get(deps)
 # Reading evaluated geometry forces each sequential simulation step.
 me=ev.to_mesh();ps=[tuple(v.co) for v in me.vertices];ev.to_mesh_clear()
 if frame%20==0:
  b=[[min(p[k] for p in ps),max(p[k] for p in ps)] for k in range(3)]
  samples.append(dict(frame=frame,bounds=b));print('SIM_FRAME',frame,b,flush=True)
 if frame==130:previous=ps
settled=ps
max_last_motion=max((Vector(p)-Vector(q)).length for p,q in zip(settled,previous))
(W/'simulation-report.json').write_text(json.dumps(dict(frames=140,vertices=len(settled),gravity=list(scene.gravity),windStrength=wind.field.strength,restPattern='wide relaxed trapezoid, physically gathered to narrow pinned seam',clothSettings=dict(mass=st.mass,bending=st.bending_stiffness,quality=st.quality),maxDisplacementLast10Frames=max_last_motion,samples=samples),indent=2))
(W/'settled-cage.json').write_text(json.dumps(dict(vertices=settled,faces=faces,C=C,R=R)))
print('SIMULATION_DONE',max_last_motion,flush=True)
