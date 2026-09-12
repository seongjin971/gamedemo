"""Blender 5.x: captured heightfield source, identity Unity export, neutral previews.
Run: blender --background --threads 6 --python build_heightfield_v11.py
Writes only PavingV11. Original maps, V10 and Unity are read-only.
"""
import bpy, json, math, hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'ArtSource').is_dir())
V10=OUT.parent/'PavingV10'
PERIOD=(4.6,2.3); TOP=-.0236; AMPLITUDE=.04; WATER=-.004
report=json.loads((V10/'paving-v10-report.json').read_text())
old=json.loads((V10/'paving-v10-mesh.json').read_text())
source_paths=[V10/'paving-v10-mesh.json',V10/'paving-v10-report.json']+list((OUT/'maps').glob('*.png'))
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
oldp=np.array(old['positions'],dtype=np.float64).reshape(-1,3)
lo=oldp.min(axis=0);hi=oldp.max(axis=0)
# Keep the V10 front envelope and rear row-union mask. Clip only 5-8mm of
# inherited bevel margin at global edges to exactly preserve native V10 AABB.
rects=[]
for x0,x1,z0,z1 in [report['front_envelope_xz']]+report['rear_row_envelopes_xz']:
    rects.append([max(x0,float(lo[0])),min(x1,float(hi[0])),max(z0,float(lo[2])),min(z1,float(hi[2]))])

def axes_and_mask(step):
    xs=np.unique(np.r_[np.linspace(lo[0],hi[0],math.ceil((hi[0]-lo[0])/step)+1),[r[i] for r in rects for i in (0,1)]])
    zs=np.unique(np.r_[np.linspace(lo[2],hi[2],math.ceil((hi[2]-lo[2])/step)+1),[r[i] for r in rects for i in (2,3)]])
    xx,zz=np.meshgrid((xs[:-1]+xs[1:])/2,(zs[:-1]+zs[1:])/2)
    mask=np.zeros(xx.shape,dtype=bool)
    for a,b,c,d in rects:mask|=(xx>=a)&(xx<=b)&(zz>=c)&(zz<=d)
    return xs,zs,mask

step=.075
while True:
    xs,zs,mask=axes_and_mask(step)
    if int(mask.sum())*2<=158000:break
    step+=.001
rows,cols=np.nonzero(mask)
grid=np.arange(len(xs)*len(zs)).reshape(len(zs),len(xs))
a=grid[rows,cols];b=grid[rows,cols+1];c=grid[rows+1,cols+1];d=grid[rows+1,cols]
# Unity +Y face cross product. Blender axis rotation preserves this ordering.
faces_grid=np.stack((np.stack((a,d,b),1),np.stack((b,d,c),1)),1).reshape(-1,3)
used,inv=np.unique(faces_grid,return_inverse=True)
faces=inv.reshape(-1,3)
x=xs[used%len(xs)];z=zs[used//len(xs)]
uv=np.stack((x/PERIOD[0],z/PERIOD[1]),1)

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
height=bpy.data.images.load(str(OUT/'maps/Tiles130_4K-PNG_Displacement.png'),check_existing=True)
height.colorspace_settings.name='Non-Color'
w,h=height.size
pixels=np.empty(w*h*4,dtype=np.float32);height.pixels.foreach_get(pixels)
pixels=pixels.reshape(h,w,4)[:,:,0]
# Image.pixels has bottom-left origin. This matches exported UV and Blender's
# image texture lookup. Use texel-centered bilinear repeat, no per-row phase.
px=(uv[:,0]%1)*w-.5;py=(uv[:,1]%1)*h-.5
ix=np.floor(px).astype(int);iy=np.floor(py).astype(int);fx=px-ix;fy=py-iy
hh=(pixels[iy%h,ix%w]*(1-fx)*(1-fy)+pixels[iy%h,(ix+1)%w]*fx*(1-fy)+pixels[(iy+1)%h,ix%w]*(1-fx)*fy+pixels[(iy+1)%h,(ix+1)%w]*fx*fy)
y=TOP+AMPLITUDE*(hh-1.0)
world=np.stack((x,y,z),1)
blender=np.stack((x,-z,y),1)
mesh=bpy.data.meshes.new('Captured heightfield boundary conforming grid')
mesh.from_pydata(blender.tolist(),[],faces.tolist());mesh.update()
ob=bpy.data.objects.new('PavingV11CapturedHeightfield',mesh);bpy.context.collection.objects.link(ob)
uv_layer=mesh.uv_layers.new(name='UVMap')
for loop in mesh.loops:uv_layer.data[loop.index].uv=uv[loop.vertex_index]
for f in mesh.polygons:f.use_smooth=True
mesh.update()

def material(name,use_texture):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
    bs=n.get('Principled BSDF');bs.inputs['Roughness'].default_value=.7
    if not use_texture:bs.inputs['Base Color'].default_value=(.20,.22,.23,1);return m
    for channel,socket in [('Color','Base Color'),('Roughness','Roughness')]:
        im=bpy.data.images.load(str(OUT/f'maps/Tiles130_4K-PNG_{channel}.png'),check_existing=True)
        im.colorspace_settings.name='sRGB' if channel=='Color' else 'Non-Color'
        tex=n.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Linear';tex.extension='REPEAT';l.new(tex.outputs['Color'],bs.inputs[socket])
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'maps/Tiles130_4K-PNG_NormalGL.png'),check_existing=True);tex.image.colorspace_settings.name='Non-Color'
    tex.extension='REPEAT';normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.45
    l.new(tex.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs['Normal'],bs.inputs['Normal'])
    return m

texturemat=material('Original Tiles130 4K maps; normal strength 0.45',True)
neutral=material('Neutral geometry comparison',False)
mesh.materials.append(texturemat)

# Export geometry-derived unit vertex normals. No pixel normal is baked here.
bn=np.array([tuple(v.normal) for v in mesh.vertices],dtype=np.float64)
normals=np.stack((bn[:,0],bn[:,2],-bn[:,1]),1)
data={'id':'paving-v11-captured-heightfield','name':'PavingV11CapturedHeightfield','alreadyUnity':True,
      'positions':world.round(9).reshape(-1).tolist(),'normals':normals.round(9).reshape(-1).tolist(),
      'uv':uv.round(9).reshape(-1).tolist(),'indices':faces.reshape(-1).tolist(),'colors':[1.0]*(len(world)*4)}
(OUT/'paving-v11-mesh.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf8')
area=float((np.diff(zs)[:,None]*np.diff(xs)[None,:]*mask).sum())
meta={'source_asset':'ambientCG Tiles130','source_dimensions_m':[2.3,1.15],'art_scale':2.0,'period_m':list(PERIOD),
 'uv_formula':'u=UnityWorldX/4.6; v=UnityWorldZ/2.3; continuous unbounded; no per-row offsets',
 'height_formula':'Y=-0.0236+0.040*(bilinearRepeat(Displacement,uv)-1); no scene-wide normalization',
 'height_amplitude_m':AMPLITUDE,'height_amplitude_is_measured':False,'maximum_height_cap_m':TOP,'water_plane_y_m':WATER,
 'normal_contract':'unit vertex normals derived from displaced geometry; source NormalGL remains separate tangent-space detail',
 'normal_map_preview_strength':.45,'normal_map_preview_note':'4K NormalGL only in textured preview. Geometry export contains no texture normals.',
 'vertices':len(world),'triangles':len(faces),'grid_base_step_m':step,'grid_note':'Uniform base lattice plus exact mask-boundary coordinates; no displaced UV phase boundaries.',
 'world_bounds':[world.min(0).tolist(),world.max(0).tolist()],'v10_world_bounds':[lo.tolist(),hi.tolist()],
 'coverage_rectangles_xz':rects,'coverage_area_m2':area,'coverage_note':'Union of V10 front and 19 rear rectangles, clipped to actual V10 outer XZ AABB. Rear staircase void and missing patches preserved; internal stone joints become continuous filled stonebed.',
 'surface_topology':'Open heightfield surface with outer and inherited hole boundaries; no underside or new stair/upper-landing geometry.',
 'source_sha256':hashes,'source_preserved':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in hashes.items()},
 'mesh_sha256':hashlib.sha256((OUT/'paving-v11-mesh.json').read_bytes()).hexdigest()}
(OUT/'heightfield-metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf8')

# Existing V10 source shown under identical neutral inspection lighting/camera.
oldmesh=bpy.data.meshes.new('V10 preserved comparison source')
oldmesh.from_pydata(np.stack((oldp[:,0],-oldp[:,2],oldp[:,1]),1).tolist(),[],np.array(old['indices']).reshape(-1,3).tolist());oldmesh.update()
oldob=bpy.data.objects.new('BEFORE V10 same camera',oldmesh);bpy.context.collection.objects.link(oldob);oldmesh.materials.append(neutral)
for p in oldmesh.polygons:p.use_smooth=True
oldob.hide_render=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.world.color=(.14,.14,.14);scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(-4,-14,9));camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO'
for loc,power,size in [((-8,-1,14),5000,7),((8,-14,12),2300,8)]:
    bpy.ops.object.light_add(type='AREA',location=loc);li=bpy.context.object;li.data.energy=power;li.data.size=size;li.rotation_euler=(Vector((0,-5,0))-li.location).to_track_quat('-Z','Y').to_euler()
evidence=OUT/'previews';evidence.mkdir(exist_ok=True)
for view,location,target,scale in [('full',(-19,-28,32),(0,-5,0),37),('close',(-4,-14,7),(0,-8,0),9)]:
    camera.location=location;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    for kind in ['before-v10-neutral','after-v11-neutral','after-v11-textured']:
        oldob.hide_render=not kind.startswith('before');ob.hide_render=kind.startswith('before')
        mesh.materials[0]=texturemat if kind.endswith('textured') else neutral
        scene.render.filepath=str(evidence/f'{kind}-{view}.png');bpy.ops.render.render(write_still=True)
oldob.hide_render=True;oldob.hide_viewport=True;ob.hide_render=False;mesh.materials[0]=texturemat
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'paving-v11.blend'))
print('PAVING_V11_BUILD_DONE',json.dumps({k:meta[k] for k in ['vertices','triangles','world_bounds','coverage_area_m2','grid_base_step_m','mesh_sha256']}))
