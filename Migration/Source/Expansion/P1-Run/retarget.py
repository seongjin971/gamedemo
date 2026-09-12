import bpy,json,math,hashlib,statistics
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'prepared-01';OUT.mkdir(exist_ok=True)
EVID=ROOT.parents[2]/'Evidence/Expansion/P1-Run';EVID.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT.parent/'P1-Mixamo/prepared-01/Adventurer.blend'))
scene=bpy.context.scene;scene.render.fps=30
arm=bpy.data.objects['TravelerRig'];mesh=bpy.data.objects['TravelerSkin'];arm.animation_data_clear()
for a in list(bpy.data.actions):
 if a.name not in ['Idle','Walk']:bpy.data.actions.remove(a)
for b in arm.pose.bones:b.matrix_basis=Matrix.Identity(4);b.rotation_mode='QUATERNION'
bpy.context.view_layer.update()
mapnames={'Spine02':'Spine','Spine01':'Spine1','Spine':'Spine2','neck':'Neck'}
children={}
for side in ['Left','Right']:
 for a,b in [('Shoulder','Arm'),('Arm','ForeArm'),('ForeArm','Hand'),('UpLeg','Leg'),('Leg','Foot'),('Foot','ToeBase')]:children[side+a]=side+b
restQ={b.name:(arm.matrix_world@b.matrix_local).to_quaternion() for b in arm.data.bones}
worldQ=arm.matrix_world.to_quaternion()
restLocal={b.name:(b.parent.matrix_local.inverted()@b.matrix_local).to_quaternion() if b.parent else b.matrix_local.to_quaternion() for b in arm.data.bones}
report={'source':'Official Mixamo FBX downloads; target existing P1 prepared-v3 mesh and Generic rig','provenance':{},'materialChanges':'none','clips':{},'targetHeightMeters':1.7794589996,'retarget':'World-space source rotations with anatomical rest-direction correction; target bind matrices, vertices, UVs and weights preserved. Horizontal Hips trend removed. Grounding uses sole vertices. No IK or Humanoid remap.'}
# Preserve digest of mesh/UV/weights/rest rig before retarget.
def signature():
 d={'vertices':[tuple(v.co) for v in mesh.data.vertices],'uvs':[[tuple(x.uv) for x in l.data] for l in mesh.data.uv_layers],'weights':[[(g.group,g.weight) for g in v.groups] for v in mesh.data.vertices],'bones':[(b.name,b.parent.name if b.parent else None,[list(r) for r in b.matrix_local]) for b in arm.data.bones],'materials':[m.name if m else None for m in mesh.data.materials]}
 return hashlib.sha256(json.dumps(d).encode()).hexdigest()
original=signature()
def action_signature(action):
 curves=[]
 for layer in action.layers:
  for strip in layer.strips:
   for slot in action.slots:
    bag=strip.channelbag(slot,ensure=False)
    if bag:
     for fc in bag.fcurves:
      curves.append([fc.data_path,fc.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation] for k in fc.keyframe_points]])
 return hashlib.sha256(json.dumps(curves).encode()).hexdigest()
retained_before={n:action_signature(bpy.data.actions[n]) for n in ['Idle','Walk']}
previous=json.loads((ROOT.parent/'P1-Mixamo/prepared-01/calibration.json').read_text())
report['clips']={n:previous['clips'][n] for n in ['Idle','Walk']}
report['source']='Official Mixamo Running With Intention; target delivered P1-Mixamo prepared-01'
report['retarget']='Anatomical world-space retarget preserving original bind, skin, and Idle/Walk action curves. Horizontal Hips drift removed. Constant whole-cycle ground offset retains hip bob and flight; no per-frame grounding.'
report['sourceBlendSha256']=hashlib.sha256((ROOT.parent/'P1-Mixamo/prepared-01/Adventurer.blend').read_bytes()).hexdigest()

sole=[v.index for v in mesh.data.vertices if (mesh.matrix_world@v.co).z<.14]
for clip,filename in [('Run','Running-With-Intention.fbx')]:
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(ROOT/filename));new=list(set(bpy.data.objects)-before)
 src=next(o for o in new if o.type=='ARMATURE');action=src.animation_data.action
 names={b.name.split(':')[-1]:b.name for b in src.data.bones}
 first,last=action.frame_range;count=round(last-first)+1
 srcRest={n:(src.matrix_world@src.data.bones[s].matrix_local).to_quaternion() for n,s in names.items()}
 align={}
 for b in arm.data.bones:
  n=mapnames.get(b.name,b.name)
  if n not in names:continue
  delta=Quaternion()
  if b.name in children:
   td=arm.matrix_world.to_3x3()@(arm.data.bones[children[b.name]].head_local-b.head_local)
   sc=mapnames.get(children[b.name],children[b.name]);sd=src.matrix_world.to_3x3()@(src.data.bones[names[sc]].head_local-src.data.bones[names[n]].head_local)
   delta=td.rotation_difference(sd)
  elif b.name.endswith('Hand') or b.name.endswith('ToeBase'):
   td=arm.matrix_world.to_3x3()@(b.tail_local-b.head_local)
   sb=src.data.bones[names[n]];sd=src.matrix_world.to_3x3()@(sb.tail_local-sb.head_local)
   delta=td.rotation_difference(sd)
  align[b.name]=srcRest[n].inverted()@delta@restQ[b.name]
 # Scale bob/travel by average leg lengths, retaining source cadence.
 def leglen(obj,lookup):
  return statistics.mean(sum(((obj.matrix_world@(obj.data.bones[lookup[s+x]].head_local))-(obj.matrix_world@(obj.data.bones[lookup[s+y]].head_local))).length for x,y in [('UpLeg','Leg'),('Leg','Foot')]) for s in ['Left','Right'])
 ratio=leglen(arm,{b.name:b.name for b in arm.data.bones})/leglen(src,names)
 data=[]
 for i in range(count):
  scene.frame_set(round(first)+i);bpy.context.view_layer.update()
  data.append({'q':{b.name:(src.matrix_world@src.pose.bones[names[mapnames.get(b.name,b.name)]].matrix).to_quaternion()@align[b.name] for b in arm.data.bones if b.name in align},'root':src.matrix_world@src.pose.bones[names['Hips']].head,'feet':{s:src.matrix_world@src.pose.bones[names[s+'Foot']].head for s in ['Left','Right']}})
 for o in new:bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.actions.remove(action)
 root0=data[0]['root'];rootEnd=data[-1]['root'];drift=rootEnd-root0;drift.z=0
 duration=(count-1)/30
 for b in arm.pose.bones:b.matrix_basis=Matrix.Identity(4)
 arm.animation_data_create();dst=bpy.data.actions.new(clip);arm.animation_data.action=dst;dst.use_fake_user=True
 poses=[];footSamples=[];mins=[];soleSamples=[]
 soleSides={side:[v for v in sole if ((mesh.matrix_world@mesh.data.vertices[v].co).x>0)==(side=='Left')] for side in ['Left','Right']}
 for i,sample in enumerate(data):
  frame=i+1;scene.frame_set(frame)
  # Convert desired world orientations to local pose quaternions without changing bind translations.
  globalQs={}
  for b in arm.pose.bones:
   if b.name in sample['q']:q=worldQ.inverted()@sample['q'][b.name]
   else:q=globalQs[b.parent.name]@restLocal[b.name] if b.parent else restQ[b.name]
   globalQs[b.name]=q
   parent=globalQs[b.parent.name] if b.parent else Quaternion()
   b.rotation_quaternion=restLocal[b.name].inverted()@parent.inverted()@q
   b.location=(0,0,0);b.scale=(1,1,1)
  disp=sample['root']-root0-drift*(i/max(1,count-1));disp*=ratio
  if clip=='Stop':disp.x=0;disp.y=0
  # target Hips rest is the anchor; source vertical displacement retains cadence.
  root=arm.pose.bones['Hips'];root.location=arm.data.bones['Hips'].matrix_local.to_3x3().inverted()@(arm.matrix_world.to_3x3().inverted()@disp)
  bpy.context.view_layer.update()
  dg=bpy.context.evaluated_depsgraph_get();ev=mesh.evaluated_get(dg);me=ev.to_mesh()
  minz=min((ev.matrix_world@me.vertices[v].co).z for v in sole)
  soleSamples.append({side:min((ev.matrix_world@me.vertices[v].co).z for v in inds) for side,inds in soleSides.items()});ev.to_mesh_clear()
  poses.append({b.name:(b.location.copy(),b.rotation_quaternion.copy()) for b in arm.pose.bones})
  footSamples.append({s:list(arm.matrix_world@arm.pose.bones[s+'Foot'].head) for s in ['Left','Right']})
  mins.append(minz)
 # One constant vertical correction over the entire cycle retains natural flight.
 correction=.008-min(mins)
 localLift=arm.data.bones['Hips'].matrix_local.to_3x3().inverted()@(arm.matrix_world.to_3x3().inverted()@Vector((0,0,correction)))
 for pose in poses:
  pose['Hips']=(pose['Hips'][0]+localLift,pose['Hips'][1])
 for sample in footSamples:
  for side in sample:sample[side][2]+=correction
 for sample in soleSamples:
  for side in sample:sample[side]+=correction
 rawEndpoint=max((poses[-1][n][1].rotation_difference(poses[0][n][1])).angle for n in poses[0])
 poses[-1]=poses[0]
 report['grounding']={'method':'constant cycle-wide vertical offset; hip vertical displacement retained','offsetMeters':correction,'rawMinimumSoleRange': [min(mins),max(mins)],'expectedSoleRange':[.008,max(mins)+correction],'rawEndpointRotationDifferenceRadians':rawEndpoint}
 for i,pose in enumerate(poses):
  for b in arm.pose.bones:
   b.location,b.rotation_quaternion=pose[b.name]
   b.keyframe_insert('location',frame=i+1,group=b.name);b.keyframe_insert('rotation_quaternion',frame=i+1,group=b.name)
 velocities=[]
 for side in ['Left','Right']:
  heights=[f[side][2] for f in footSamples];lo=min(heights);hi=max(heights)
  for i in range(count-1):
   dy=(footSamples[i+1][side][1]-footSamples[i][side][1])*30
   if max(soleSamples[i][side],soleSamples[i+1][side])<.025 and dy>.1:velocities.append(dy)
 measured=statistics.median(velocities) if velocities else 0
 rootSpeed=drift.length/duration*ratio
 speed=measured if measured>0 else rootSpeed
 report['clips'][clip]={'file':filename,'frames':count,'fps':30,'duration':duration,'loop':clip!='Stop','runSpeed':speed,'targetPlantedFootSpeed':measured,'scaledSourceRootSpeed':rootSpeed,'sourceRootTravelMeters':drift.length,'proportionRatio':ratio,'groundCorrectionRange':[min(mins),max(mins)],'footSamples':footSamples,'soleSamples':soleSamples,'stanceCalibration':{'method':'median positive backward ankle velocity only where both ends of sample have boot sole below 0.025m','sampleCount':len(velocities),'samples':velocities,'thresholdMeters':.025},'nativeStrideMeters':speed*duration}
 report['provenance'][filename]={'provider':'mixamo.com','sha256':hashlib.sha256((ROOT/filename).read_bytes()).hexdigest(),'downloadSettings':'FBX Binary 30 fps, With Skin, no keyframe reduction; In Place false, Mirror false, Overdrive 50, Character Arm Space 50; UI 22 frames'}
 print('CLIP_READY',clip,count,speed,flush=True)
report['selection']='Run added from Running With Intention; retained Idle and Walk are identical to delivered P1-Mixamo. Unused Stop and WalkAlternative omitted from this derivative only.'
report['walkSpeed']=previous['walkSpeed'];report['runSpeed']=report['clips']['Run']['runSpeed']
report['preservation']={'before':original,'after':signature(),'match':original==signature(),'retainedActionBefore':retained_before,'retainedActionAfter':{n:action_signature(bpy.data.actions[n]) for n in ['Idle','Walk']}}
report['preservation']['retainedActionsMatch']=report['preservation']['retainedActionBefore']==report['preservation']['retainedActionAfter']
# Correlate signed leg swing across whole cycles to align left/right support phases.
def phase_curve(name):
 ac=bpy.data.actions[name];arm.animation_data.action=ac
 result=[]
 for i in range(200):
  frame=float(ac.frame_range[0])+(float(ac.frame_range[1])-float(ac.frame_range[0]))*i/200
  scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
  result.append((arm.matrix_world@arm.pose.bones['LeftFoot'].head).y-(arm.matrix_world@arm.pose.bones['RightFoot'].head).y)
 avg=statistics.mean(result);std=statistics.pstdev(result)
 return [(v-avg)/std for v in result]
walkCurve=phase_curve('Walk');runCurve=phase_curve('Run')
scores=[sum(walkCurve[i]*runCurve[(i+k)%200] for i in range(200))/200 for k in range(200)]
shift=max(range(200),key=lambda k:scores[k])
report['runPhaseOffset']=shift/200
report['phaseAlignment']={'apply':'runNormalizedPhase = (walkNormalizedPhase + runPhaseOffset) % 1','method':'whole-cycle cross correlation of LeftFoot.y minus RightFoot.y in target world space','correlation':scores[shift],'samples':200}
report['runtimeCalibration']={'visualScale':1.8,'walkMotorMetersPerSecond':2.25,'runMotorMetersPerSecond':4.5,'walkPlaybackRate':2.25/(report['walkSpeed']*1.8),'runPlaybackRate':4.5/(report['runSpeed']*1.8)}
assert report['preservation']['match'] and report['preservation']['retainedActionsMatch']
arm.animation_data.action=bpy.data.actions['Idle'];scene.frame_start=1;scene.frame_end=299;scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(filepath=str(OUT/'Adventurer.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,axis_forward='-Z',axis_up='Y',bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,use_armature_deform_only=True,path_mode='STRIP')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Adventurer.blend'))
(OUT/'calibration.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('DONE',report['walkSpeed'],report['preservation'],flush=True)
