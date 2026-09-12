from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[4]
evidence=ROOT/'Migration/Evidence/Expansion/WeatherWorld'
def scene_signature(revision):
    p=ROOT/f'Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_{revision}.unity'
    docs={m[2]:(m[1],m[3]) for m in re.finditer(r'^--- !u!(\d+) &(-?\d+)[^\n]*\n(.*?)(?=^--- !u!|\Z)',p.read_text(encoding='utf-8'),re.M|re.S)}
    colliders={k:v for k,v in docs.items() if v[0] in {'64','65','135','136'}}
    poses={k:re.findall(r'^  m_(?:LocalPosition|LocalRotation|LocalScale|Father):.*$',body,re.M) for k,(kind,body) in docs.items() if kind=='4'}
    prefab_poses={}
    for k,(kind,body) in docs.items():
        if kind!='1001':continue
        overrides=[m[0] for m in re.finditer(r'^    - target:.*\n      propertyPath: m_(?:LocalPosition|LocalRotation|LocalScale).*\n      value:.*$',body,re.M)]
        prefab_poses[k]=(re.findall(r'^    m_TransformParent:.*$',body,re.M),overrides)
    nav=re.findall(r'^  m_NavMeshData:.*$',p.read_text(encoding='utf-8'),re.M)
    return colliders,poses,nav,prefab_poses
a=scene_signature('W04');b=scene_signature('W05')
runtime=['WorldMotor','WorldLayout','WorldCamera','WorldRunInput','WorldAnimation','WorldWeather','WorldRoofCutaway']
same_runtime={n:(evidence/f'W04/source/Runtime/{n}.cs').read_bytes()==(evidence/f'W05/source/Runtime/{n}.cs').read_bytes() for n in runtime}
common=a[1].keys() & b[1].keys()
retained_poses=all(a[1][k]==b[1][k] for k in common)
report={'W04ToW05':{'colliderComponents':len(a[0]),'collidersIdentical':a[0]==b[0],'retainedTransformCount':len(common),'retainedTransformPosesIdentical':retained_poses,'prefabTransformOverridesIdentical':a[3]==b[3],'navigationReferencesIdentical':a[2]==b[2],'movementRuntimeIdentical':same_runtime},'note':'W04 targeted 180.34m traversal remains applicable. W05 changes atmospheric particles and lighting shader early-outs; final W05 performance includes actual walking at all four representative fixtures.'}
report['passed']=all([a[0]==b[0],retained_poses,a[2]==b[2],a[3]==b[3],*same_runtime.values()])
(evidence/'W05/movement-inheritance.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
raise SystemExit(not report['passed'])
