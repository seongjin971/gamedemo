"""Blender P1 derivative. Keep source GLBs and make an in-place Generic FBX.

No old asset is overwritten. Bake the original rig's evaluated poses onto its
own skeleton, preserving skin bindings and avoiding Humanoid retargeting.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'prepared-v3'; OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene; scene.render.fps=30

def load(filename):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/filename))
    objects=list(set(bpy.data.objects)-before)
    arm=next(o for o in objects if o.type=='ARMATURE')
    action=arm.animation_data.action
    return arm,action,objects

walk_arm,walk_source,walk_objects=load('walking.glb')
idle_arm,idle_source,idle_objects=load('idle-animation_glb_url.glb')

def evaluated(arm,action):
    arm.animation_data.action=action
    # GLB samples use exact 30Hz timestamps. Export a closed loop of 32 samples.
    first,last=action.frame_range
    count=round(last-first)+1
    frames=[]
    for i in range(count):
        f=first+i;scene.frame_set(int(f),subframe=f%1)
        frames.append({b.name:b.matrix_basis.copy() for b in arm.pose.bones})
    return frames, float(first), float(last)

walk_poses,first,last=evaluated(walk_arm,walk_source)
idle_poses,_,_=evaluated(idle_arm,idle_source)
# Sample toe/ankle travel in source world space for empirical stride calibration.
samples=[]
walk_arm.animation_data.action=walk_source
for i in range(len(walk_poses)):
    f=first+i;scene.frame_set(int(f),subframe=f%1)
    samples.append({name:list(walk_arm.matrix_world@walk_arm.pose.bones[name].head) for name in ('Hips','LeftFoot','RightFoot','LeftToeBase','RightToeBase')})

root0=Vector(samples[0]['Hips']);root1=Vector(samples[-1]['Hips'])
travel=Vector((root1.x-root0.x,root1.y-root0.y,0))
duration=(len(walk_poses)-1)/30
# When a source walk is already in place, estimate planted-foot backward speed.
velocities=[]
for name in ('LeftFoot','RightFoot'):
    heights=[s[name][2] for s in samples];lo=min(heights);hi=max(heights)
    for i in range(len(samples)-1):
        a=Vector(samples[i][name]); b=Vector(samples[i+1][name]);v=(b-a)*30
        if a.z<lo+(hi-lo)*.38 and v.y>0:velocities.append(v.y)
velocities.sort()
inplaceSpeed=velocities[len(velocities)//2] if velocities else 1.4
speed=travel.length/duration if travel.length>.2 else inplaceSpeed
speed=max(.7,min(2.1,speed))

# Baking takes basis matrices, so changing bone display lengths is unnecessary.
walk_arm.animation_data_clear()
for o in idle_objects:bpy.data.objects.remove(o,do_unlink=True)
mesh=next(o for o in walk_objects if o.type=='MESH' and o.vertex_groups)
for o in list(walk_objects):
    if o.type not in ('ARMATURE','MESH') or (o.type=='MESH' and not o.vertex_groups):
        bpy.data.objects.remove(o,do_unlink=True)
walk_arm.name='TravelerRig'
mesh.name='TravelerSkin'
for a in list(bpy.data.actions):bpy.data.actions.remove(a)

def bake(name,poses):
    arm=walk_arm
    arm.animation_data_create()
    action=bpy.data.actions.new(name);arm.animation_data.action=action
    root=arm.pose.bones['Hips']
    start=poses[0]['Hips'].translation.copy();finish=poses[-1]['Hips'].translation.copy()
    # Root bone basis is in the root's rest coordinate system, not world axes.
    rest=arm.data.bones['Hips'].matrix_local
    world0=rest@poses[0]['Hips'];world1=rest@poses[-1]['Hips']
    delta=world1.translation-world0.translation;delta.z=0
    for i,pose in enumerate(poses):
        for b in arm.pose.bones:
            b.rotation_mode='QUATERNION';matrix=pose[b.name].copy()
            if b.name=='Hips':
                transformed=rest@matrix
                if name=='Walk':transformed.translation-=delta*(i/max(1,len(poses)-1))
                matrix=rest.inverted()@transformed
            b.matrix_basis=matrix
            b.keyframe_insert('location',frame=i+1,group=b.name)
            b.keyframe_insert('rotation_quaternion',frame=i+1,group=b.name)
            b.keyframe_insert('scale',frame=i+1,group=b.name)
    action.use_fake_user=True
    return action

# Remove excessive lateral arm spread from the supplied walk while preserving
# its shoulder-to-elbow forward swing and its lower-body trajectory exactly.
corrected=[]
walk_arm.animation_data_clear()
for pose in walk_poses:
    for b in walk_arm.pose.bones:b.matrix_basis=pose[b.name]
    bpy.context.view_layer.update()
    for side,sign in [('Left',1),('Right',-1)]:
        upper=walk_arm.pose.bones[side+'Arm'];lower=walk_arm.pose.bones[side+'ForeArm']
        direction=lower.head-upper.head;length=direction.length
        lateral=sign*5.5
        forward=max(-length*.65,min(length*.65,direction.y*.90))
        desired=Vector((lateral,forward,-math.sqrt(max(1,length*length-lateral*lateral-forward*forward))))
        delta=direction.rotation_difference(desired)
        origin=upper.head.copy()
        upper.matrix=Matrix.Translation(origin)@delta.to_matrix().to_4x4()@Matrix.Translation(-origin)@upper.matrix
        bpy.context.view_layer.update()
    corrected.append({b.name:b.matrix_basis.copy() for b in walk_arm.pose.bones})
walk=bake('Walk',corrected)
# The library Idle has a long staggered combat stance. Author a quiet planted
# stance on the same skin instead; retain a little of its upper-body motion.
relaxed=[]
for i,source in enumerate(idle_poses):
    phase=i/max(1,len(idle_poses)-1)*math.tau
    pose={b.name:Matrix.Identity(4) for b in walk_arm.pose.bones}
    for name in ('Spine02','Spine01','Spine','neck','Head'):
        q=Quaternion().slerp(source[name].to_quaternion(),.10)
        pose[name]=q.to_matrix().to_4x4()
    for name,sign in [('LeftArm',1),('RightArm',-1)]:
        rest=walk_arm.data.bones[name].matrix_local.to_quaternion()
        global_delta=Quaternion((0,1,0),math.radians(sign*(19+math.sin(phase)*.45)))
        pose[name]=(rest.inverted()@global_delta@rest).to_matrix().to_4x4()
    relaxed.append(pose)
idle=bake('Idle',relaxed)
walk_arm.animation_data.action=idle
scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
walk_arm.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=walk_arm
bpy.ops.export_scene.fbx(filepath=str(OUT/'Adventurer.fbx'),use_selection=True,
    object_types={'ARMATURE','MESH'},add_leaf_bones=False,axis_forward='-Z',axis_up='Y',
    bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,
    bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,
    use_armature_deform_only=True,path_mode='STRIP')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Adventurer.blend'))
report={'walkSpeed':speed,'sourceForwardTravel':travel.length,'walkDuration':duration,
    'inplaceFootSpeedEstimate':inplaceSpeed,'walkSamples':len(walk_poses),'idleSamples':len(idle_poses),
    'sourceSamples':samples,'note':'Generic same-skeleton bake. Horizontal Hips drift removed; root movement owned by Unity motor. Speed from source forward drift or planted ankle travel. Idle locally authored with planted neutral legs and 10 percent source upper-body motion; source combat stance rejected.'}
(ROOT/'animation-calibration.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='sourceSamples'}))
