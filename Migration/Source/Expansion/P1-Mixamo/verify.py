import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;E=R.parents[2]/'Evidence/Expansion/P1-Mixamo'
bpy.ops.wm.open_mainfile(filepath=str(R/'prepared-01/Adventurer.blend'))
a=bpy.data.objects['TravelerRig'];m=bpy.data.objects['TravelerSkin'];s=bpy.context.scene;report={'boneCount':len(a.data.bones),'vertexCount':len(m.data.vertices),'clips':{}}
for name in ['Walk','WalkAlternative','Idle','Stop']:
 ac=bpy.data.actions[name];a.animation_data.action=ac;start,end=map(round,ac.frame_range);poses=[];angles=[];separations=[]
 for f in range(start,end+1):
  s.frame_set(f);bpy.context.view_layer.update();poses.append({b.name:{'q':list(b.rotation_quaternion),'p':list(a.matrix_world@b.head)} for b in a.pose.bones})
  for side in ['Left','Right']:
   hip=a.pose.bones[side+'UpLeg'].head;knee=a.pose.bones[side+'Leg'].head;ankle=a.pose.bones[side+'Foot'].head;angles.append(math.degrees((hip-knee).angle(ankle-knee)))
  separations.append(poses[-1]['LeftFoot']['p'][0]-poses[-1]['RightFoot']['p'][0])
 first,last=poses[0],poses[-1]
 maxstep=max((Vector(poses[i+1][b]['p'])-Vector(poses[i][b]['p'])).length for i in range(len(poses)-1) for b in ['LeftHand','RightHand','LeftFoot','RightFoot'])
 seam=max((Vector(first[b]['p'])-Vector(last[b]['p'])).length for b in first)
 hp0=first['Hips']['p'];hp1=last['Hips']['p']
 report['clips'][name]={'frames':[start,end],'kneeInteriorAngleDegrees':[min(angles),max(angles)],'signedAnkleXSeparationMeters':[min(separations),max(separations)],'maxHandOrFootFrameStepMeters':maxstep,'endpointBoneHeadMismatchMeters':seam,'hipEndpointHorizontalDriftMeters':math.hypot(hp1[0]-hp0[0],hp1[1]-hp0[1])}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(R/'prepared-01/Adventurer.fbx'))
report['fbxRoundtrip']={'armatures':[{ 'name':o.name,'bones':len(o.data.bones)} for o in bpy.data.objects if o.type=='ARMATURE'],'meshes':[{ 'name':o.name,'vertices':len(o.data.vertices)} for o in bpy.data.objects if o.type=='MESH'],'actions':[{ 'name':ac.name,'frames':list(ac.frame_range)} for ac in bpy.data.actions]}
(E/'source-numeric-qa.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
