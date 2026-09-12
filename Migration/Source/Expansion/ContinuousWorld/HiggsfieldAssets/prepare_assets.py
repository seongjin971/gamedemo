"""Import original Higgsfield GLBs, preserve PBR maps, normalize pivots, export triangle FBXs.
Run Blender --background --threads 6 --python prepare_assets.py -- rock fir alder
"""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
import numpy as np
SOURCE=Path(__file__).resolve().parent
ROOT=SOURCE.parents[4]
OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/HiggsfieldAssets'
QA=ROOT/'.dream-loop/continuous-world/higgsfield-assets'
CONFIG={'rock':('CW_HF_Limestone',5.0,0),'fir':('CW_HF_AlpineFir',9.0,2),'alder':('CW_HF_RiverAlder',8.0,2),
        'fir_hunyuan':('CW_HF_AlpineFir_Hunyuan',9.0,2),'buttress':('CW_HF_GothicButtress',5.0,2)}
requested=[a for a in sys.argv[sys.argv.index('--')+1:] if a!='--no-render'] if '--' in sys.argv else list(CONFIG)

def export_fbx(path,obs):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs: ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},
        axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',
        use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=True,bake_anim=False,path_mode='RELATIVE')

def sanitize(ob):
    bm=bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='EAR_CLIP')
    bad=[f for f in bm.faces if f.calc_area()<1e-9]
    if bad: bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    bm.to_mesh(ob.data); bm.free(); ob.data.validate(clean_customdata=False); ob.data.update()

def write_rgba(name,array,dest,noncolor=True):
    height,width=array.shape[:2]
    img=bpy.data.images.new(name,width=width,height=height,alpha=True)
    if noncolor: img.colorspace_settings.name='Non-Color'
    img.pixels.foreach_set(array.astype(np.float32).ravel()); img.filepath_raw=str(dest); img.file_format='PNG'; img.save()
    return img

for key in requested:
    name,target,axis=CONFIG[key]; modelout=OUT/name; modelout.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for im in list(bpy.data.images):
        if im.name!='Render Result': bpy.data.images.remove(im)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE/(key+'.glb')))
    obs=[ob for ob in bpy.context.scene.objects if ob.type=='MESH']
    for i,ob in enumerate(obs):
        mat=ob.matrix_world.copy(); ob.parent=None; ob.matrix_world=mat
        bpy.context.view_layer.objects.active=ob; bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True); ob.name=name+('_'+str(i) if i else '')
    points=[v.co.copy() for ob in obs for v in ob.data.vertices]
    mn=Vector([min(p[i] for p in points) for i in range(3)]); mx=Vector([max(p[i] for p in points) for i in range(3)])
    scale=target/(mx[axis]-mn[axis]); center=Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z))
    for ob in obs:
        for v in ob.data.vertices: v.co=(v.co-center)*scale
        sanitize(ob)
    tex_info=[]; image_map={}
    for i,im in enumerate(list(bpy.data.images)):
        if im.name=='Render Result': continue
        # Embedded GLB image buffers are lazy; accessing pixels loads their packed data.
        pixel_count=len(im.pixels)
        if not pixel_count: continue
        path=modelout/(name+'_Texture'+str(i)+'.png'); im.filepath_raw=str(path); im.file_format='PNG'; im.save()
        image_map[im.name]=path.name; tex_info.append({'source_image':im.name,'file':path.name,'size':list(im.size),'colorspace':im.colorspace_settings.name})
    materials=[]
    for i,mat in enumerate(dict.fromkeys(m for ob in obs for m in ob.data.materials if m)):
        oldname=mat.name; mat.name=name+'_Material'+str(i); nodes=mat.node_tree.nodes
        bs=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
        slots={}
        def find_images(socket,visited=None):
            if not socket.is_linked:return []
            visited=set() if visited is None else visited; result=[]
            for link in socket.links:
                n=link.from_node
                if n in visited:continue
                visited.add(n)
                if n.type=='TEX_IMAGE' and n.image:result.append(n.image)
                else:
                    for s in n.inputs:result+=find_images(s,visited)
            return list(dict.fromkeys(result))
        if bs:
            for field in ('Base Color','Metallic','Roughness','Normal','Alpha'):
                slots[field]=[image_map.get(im.name) for im in find_images(bs.inputs[field])]
            rough_images=find_images(bs.inputs['Roughness'])
            metal_images=find_images(bs.inputs['Metallic'])
            # GLTF metallic-roughness map: G roughness, B metallic. Unity expects R metallic/A smoothness.
            if rough_images and metal_images and rough_images[0]==metal_images[0]:
                im=rough_images[0]; pix=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pix)
                pix=pix.reshape(im.size[1],im.size[0],4); packed=np.zeros_like(pix);packed[:,:,0]=pix[:,:,2];packed[:,:,3]=1-pix[:,:,1]
                dest=modelout/(name+'_MetallicSmoothness'+str(i)+'.png');write_rgba(dest.stem,packed,dest)
                slots['UnityMetallicSmoothness']=[dest.name]
        materials.append({'name':mat.name,'source_name':oldname,'texture_inputs':slots,'double_sided_recommended':key!='rock'})
    manifest={'name':name,'source_glb':key+'.glb','source_job':json.loads((SOURCE/(key+'-job.json')).read_text(encoding='utf-8-sig')),
       'normalization':{'uniform_scale':scale,'source_min':list(mn),'source_max':list(mx),'source_ground_pivot':list(center)},
       'source_axes':'+Z up','fbx_axes':'+Y up, -Z forward','materials':materials,'textures':tex_info,'meshes':[]}
    for ob in obs:
        ob.data.calc_loop_triangles(); manifest['meshes'].append({'name':ob.name,'triangles':len(ob.data.loop_triangles),
           'zero_area_triangles':sum(t.area<1e-12 for t in ob.data.loop_triangles),'uv_layers':len(ob.data.uv_layers),
           'all_triangular':all(len(p.vertices)==3 for p in ob.data.polygons)})
    manifest['bounds_source_xyz']=[[min(v.co[i] for ob in obs for v in ob.data.vertices) for i in range(3)],
                                  [max(v.co[i] for ob in obs for v in ob.data.vertices) for i in range(3)]]
    export_fbx(modelout/(name+'.fbx'),obs)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(name+'.blend')))
    # LOD1 is additive: preserve original textured geometry and export a 40% decimation copy.
    lod=[]
    for ob in obs:
        dup=ob.copy(); dup.data=ob.data.copy(); bpy.context.collection.objects.link(dup); dup.name=ob.name+'_LOD1'
        mod=dup.modifiers.new('LOD1 Decimation','DECIMATE');mod.ratio=.4
        bpy.context.view_layer.objects.active=dup;bpy.ops.object.modifier_apply(modifier=mod.name);sanitize(dup);lod.append(dup)
    export_fbx(modelout/(name+'_LOD1.fbx'),lod)
    manifest['lod1_triangles']=sum(len(ob.data.polygons) for ob in lod)
    for ob in lod:bpy.data.objects.remove(ob,do_unlink=True)
    (modelout/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    (SOURCE/(key+'-manifest.json')).write_text(json.dumps(manifest,indent=2),encoding='utf8')
    if '--no-render' in sys.argv:
        print('HF_ASSET_COMPLETE '+name);continue
    # Render true textures under neutral lighting for an asset-level quality check.
    scene=bpy.context.scene; scene.render.engine='CYCLES';scene.cycles.samples=40
    scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
    world=bpy.data.worlds.new('Neutral inspection world');scene.world=world;world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.36,.40,.46,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
    bounds=manifest['bounds_source_xyz']; h=bounds[1][2]; width=max(bounds[1][0]-bounds[0][0],bounds[1][1]-bounds[0][1]); extent=max(h,width)
    for pos,power,size in [((-extent,-extent,extent*1.8),140*extent**2,extent),((extent,extent,extent),65*extent**2,extent*.8)]:
        ld=bpy.data.lights.new('QA softbox','AREA');ld.energy=power;ld.size=size;lo=bpy.data.objects.new('QA softbox',ld);bpy.context.collection.objects.link(lo);lo.location=pos;lo.rotation_euler=(Vector((0,0,h*.4))-lo.location).to_track_quat('-Z','Y').to_euler()
    cd=bpy.data.cameras.new('QA camera');cam=bpy.data.objects.new('QA camera',cd);bpy.context.collection.objects.link(cam)
    cam.location=(extent*1.2,-extent*1.7,h*.75+extent*.45);cam.rotation_euler=(Vector((0,0,h*.45))-cam.location).to_track_quat('-Z','Y').to_euler()
    cd.type='ORTHO';cd.ortho_scale=extent*1.32;scene.camera=cam;scene.view_settings.view_transform='AgX'
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(QA/(key+'-preview.png'));bpy.ops.render.render(write_still=True)
    print('HF_ASSET_COMPLETE '+name)
