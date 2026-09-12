import bpy,math,ast
from pathlib import Path
from mathutils import Vector
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];ART=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'FirSnowV2-pairs.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.transparent_max_bounces=32;scene.render.resolution_x=760;scene.render.resolution_y=920;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.view_settings.view_transform='Standard'
atlas=bpy.data.images.load(str(ART/'Textures/FirBranches.png'),check_existing=True)
for node in ast.parse((SOURCE/'generate_fir_snow_v2.py').read_text()).body:
    if isinstance(node,ast.FunctionDef) and node.name in {'emission','render'}:exec(compile(ast.Module(body=[node],type_ignores=[]),'<same segmentation renderer>','exec'))
leafmask=emission('Actual view mask needles',(0,1,0),True);woodmask=emission('Actual view mask wood',(0,1,0));snowmask=emission('Actual view mask snow',(1,1,1))
for ob in scene.objects:
    if ob.type=='MESH':
        ob.data.materials.clear();ob.data.materials.append(leafmask if 'Needles' in ob.name else woodmask if 'Wood' in ob.name else snowmask)
cd=bpy.data.cameras.new('Actual Unity angle diagnostic');cam=bpy.data.objects.new('Actual Unity angle diagnostic',cd);bpy.context.collection.objects.link(cam);cd.type='ORTHO';cd.ortho_scale=11;scene.camera=cam
target=Vector((0,0,4.3));cam.location=target+Vector((math.sin(.46)*math.cos(.72),-math.cos(.46)*math.cos(.72),math.sin(.72)))*30;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
render('fir-v2-actual-angle-coverage-mask.png')
for ob in scene.objects:
    if ob.type=='MESH':ob.hide_render=not ('_LOD1' in ob.name or '_Reduced' in ob.name)
render('fir-v2-lod1-actual-angle-coverage-mask.png')
print('ACTUAL_ANGLE_MASK_COMPLETE')
