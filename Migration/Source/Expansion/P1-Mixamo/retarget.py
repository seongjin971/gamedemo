import bpy,json,math,hashlib,statistics
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'prepared-01';OUT.mkdir(exist_ok=True)
EVID=ROOT.parents[2]/'Evidence/Expansion/P1-Mixamo';EVID.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT.parent/'P1/prepared-v3/Adventurer.blend'))
scene=bpy.context.scene;scene.render.fps=30
arm=bpy.data.objects['TravelerRig'];mesh=bpy.data.objects['TravelerSkin'];arm.animation_data_clear()
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
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
sole=[v.index for v in mesh.data.vertices if (mesh.matrix_world@v.co).z<.14]
for clip,filename in [('WalkAlternative','Unarmed-Walk-Forward.fbx'),('Walk','Walking-Swagger.fbx'),('Idle','Breathing-Idle.fbx'),('Stop','Stop-Walking.fbx')]:
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
 poses=[];footSamples=[];mins=[]
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
  minz=min((ev.matrix_world@me.vertices[v].co).z for v in sole);ev.to_mesh_clear()
  # Place lowest boot sole at ground, leaving source knee bend and airborne foot height.
  lift=Vector((0,0,.008-minz));root.location+=arm.data.bones['Hips'].matrix_local.to_3x3().inverted()@(arm.matrix_world.to_3x3().inverted()@lift)
  bpy.context.view_layer.update()
  poses.append({b.name:(b.location.copy(),b.rotation_quaternion.copy()) for b in arm.pose.bones})
  footSamples.append({s:list(arm.matrix_world@arm.pose.bones[s+'Foot'].head) for s in ['Left','Right']})
  mins.append(minz)
 # Closed loops avoid exporter seam. Blend final 4 idle samples gently into initial pose.
 if clip in ['Walk','WalkAlternative','Idle']:
  poses[-1]=poses[0]
  if clip=='Idle':
   for j in range(1,13):
    k=len(poses)-1-j;w=(13-j)/13
    poses[k]={n:(loc.lerp(poses[0][n][0],w),q.slerp(poses[0][n][1],w)) for n,(loc,q) in poses[k].items()}
 for i,pose in enumerate(poses):
  for b in arm.pose.bones:
   b.location,b.rotation_quaternion=pose[b.name]
   b.keyframe_insert('location',frame=i+1,group=b.name);b.keyframe_insert('rotation_quaternion',frame=i+1,group=b.name)
 velocities=[]
 for side in ['Left','Right']:
  heights=[f[side][2] for f in footSamples];lo=min(heights);hi=max(heights)
  for i in range(count-1):
   dy=(footSamples[i+1][side][1]-footSamples[i][side][1])*30
   if heights[i]<lo+(hi-lo)*.35 and dy>.1:velocities.append(dy)
 measured=statistics.median(velocities) if velocities else 0
 rootSpeed=drift.length/duration*ratio
 speed=measured if measured>0 else rootSpeed
 report['clips'][clip]={'file':filename,'frames':count,'fps':30,'duration':duration,'loop':clip!='Stop','walkSpeed':speed,'targetPlantedFootSpeed':measured,'scaledSourceRootSpeed':rootSpeed,'sourceRootTravelMeters':drift.length,'proportionRatio':ratio,'groundCorrectionRange':[min(mins),max(mins)],'footSamples':footSamples}
 report['provenance'][filename]={'provider':'mixamo.com','sha256':hashlib.sha256((ROOT/filename).read_bytes()).hexdigest(),'downloadSettings':'FBX Binary 30 fps; fresh X Bot downloads with skin except prior Unarmed Walk Forward without skin'}
 print('CLIP_READY',clip,count,speed,flush=True)
report['selection']='Walking-Swagger chosen over Unarmed-Walk-Forward: upright torso, relaxed upper arms, clearer heel-to-toe stride. Native pace calibrated from planted target foot backward travel, not merely source root displacement.'
report['walkSpeed']=report['clips']['Walk']['walkSpeed'];report['preservation']={'before':original,'after':signature(),'match':original==signature()}
arm.animation_data.action=bpy.data.actions['Idle'];scene.frame_start=1;scene.frame_end=299;scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(filepath=str(OUT/'Adventurer.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,axis_forward='-Z',axis_up='Y',bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,use_armature_deform_only=True,path_mode='STRIP')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Adventurer.blend'))
(OUT/'calibration.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('DONE',report['walkSpeed'],report['preservation'],flush=True)
