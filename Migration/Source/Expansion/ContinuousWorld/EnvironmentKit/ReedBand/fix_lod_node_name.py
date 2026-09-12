import bpy
from pathlib import Path
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parents[5];OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/EnvironmentKit/ReedBand'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'GoldenReedBand.blend'))
ob=bpy.data.objects.get('CW_GoldenReedBand4m_LOD1') or bpy.data.objects['CW_GoldenReedBand4m_Reduced'];ob.name='CW_GoldenReedBand4m_Reduced';ob.data.name=ob.name
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.fbx(filepath=str(OUT/'CW_GoldenReedBand4m_LOD1.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_tspace=True,mesh_smooth_type='FACE',bake_anim=False)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'GoldenReedBand.blend'));print('LOD_NODE_RENAME_COMPLETE')
