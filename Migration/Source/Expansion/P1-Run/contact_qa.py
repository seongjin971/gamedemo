import bpy,json,math,statistics
from pathlib import Path
R=Path(__file__).resolve().parent;E=R.parents[2]/'Evidence/Expansion/P1-Run'
bpy.ops.wm.open_mainfile(filepath=str(R/'prepared-01/Adventurer.blend'))
a=bpy.data.objects['TravelerRig'];m=bpy.data.objects['TravelerSkin'];s=bpy.context.scene;a.animation_data.action=bpy.data.actions['Run']
soles={side:[v.index for v in m.data.vertices if (m.matrix_world@v.co).z<.14 and ((m.matrix_world@v.co).x>0)==(side=='Left')] for side in ['Left','Right']}
samples=[];finite=True
for frame in range(1,23):
 s.frame_set(frame);bpy.context.view_layer.update();ev=m.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();verts=[ev.matrix_world@v.co for v in me.vertices]
 finite=finite and all(math.isfinite(x) for v in verts for x in v)
 samples.append({'frame':frame,'hip':list(a.matrix_world@a.pose.bones['Hips'].head),'sides':{side:{'sole':min(verts[i].z for i in inds),'ankle':list(a.matrix_world@a.pose.bones[side+'Foot'].head)} for side,inds in soles.items()}})
 ev.to_mesh_clear()
vel=[]
for side in soles:
 for x,y in zip(samples,samples[1:]):
  v=(y['sides'][side]['ankle'][1]-x['sides'][side]['ankle'][1])*30
  if max(x['sides'][side]['sole'],y['sides'][side]['sole'])<.025 and v>0:vel.append({'side':side,'frame':x['frame'],'speed':v})
r={'finiteAllMeshVerticesEveryFrame':finite,'samples':samples,'stanceSpeedSamples':vel,'stanceMedian':statistics.median(v['speed'] for v in vel) if vel else None,'flightFramesAbove3cm':[x['frame'] for x in samples if min(y['sole'] for y in x['sides'].values())>.03],'minSole':min(y['sole'] for x in samples for y in x['sides'].values()),'maxBothSolesClearance':max(min(y['sole'] for y in x['sides'].values()) for x in samples)}
(E/'run-contact-qa.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
