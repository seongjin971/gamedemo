"""Read-only import inspection; writes new inspection evidence only."""
import bpy,json,hashlib
from pathlib import Path
W=Path(__file__).resolve().parent
originals=['creation-started.json','download-manifest.json','meshy_asset.py','preview-back.png','preview-front.png','preview-left.png','preview-right.png','PROMPT.md','reference-tree.png','request-metadata.json','task-created.json','task-status.json','texture-0-base_color.png','texture-0-metallic.png','texture-0-normal.png','texture-0-roughness.png','tree-v11-original.glb']
hashes={n:hashlib.sha256((W/n).read_bytes()).hexdigest() for n in originals};(W/'protected-input-hashes.json').write_text(json.dumps(hashes,indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(W/'tree-v11-original.glb'))
objects=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 m=o.data;m.calc_loop_triangles();coords=[o.matrix_world@v.co for v in m.vertices]
 objects.append(dict(name=o.name,vertices=len(m.vertices),triangles=len(m.loop_triangles),matrix=[list(r) for r in o.matrix_world],bounds=[[min(v[k] for v in coords),max(v[k] for v in coords)] for k in range(3)],uvLayers=[uv.name for uv in m.uv_layers],colorAttributes=[a.name for a in m.color_attributes],materials=[mat.name for mat in m.materials]))
materials=[]
for mat in bpy.data.materials:
 materials.append(dict(name=mat.name,nodes=[dict(name=n.name,type=n.type,image=n.image.name if n.type=='TEX_IMAGE' and n.image else None) for n in mat.node_tree.nodes] if mat.use_nodes else []))
report=dict(objects=objects,materials=materials,images=[dict(name=i.name,size=list(i.size),filepath=i.filepath,colorspace=i.colorspace_settings.name) for i in bpy.data.images]);(W/'original-inspection.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
