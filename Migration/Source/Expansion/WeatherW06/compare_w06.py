from pathlib import Path
import re,json,sys
ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W06'
def signature(revision):
    s=(ROOT/f'Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_{revision}.unity').read_text(encoding='utf-8')
    docs={m[2]:(m[1],m[3]) for m in re.finditer(r'^--- !u!(\d+) &(-?\d+)[^\n]*\n(.*?)(?=^--- !u!|\Z)',s,re.M|re.S)}
    colliders={k:v for k,v in docs.items() if v[0] in {'64','65','135','136'}}
    poses={k:re.findall(r'^  m_(?:LocalPosition|LocalRotation|LocalScale|Father):.*$',body,re.M) for k,(kind,body) in docs.items() if kind=='4'}
    prefabs={}
    for k,(kind,body) in docs.items():
        if kind!='1001':continue
        prefabs[k]=(re.findall(r'^    m_TransformParent:.*$',body,re.M),[m[0] for m in re.finditer(r'^    - target:.*\n      propertyPath: m_(?:LocalPosition|LocalRotation|LocalScale).*\n      value:.*$',body,re.M)])
    return colliders,poses,prefabs,re.findall(r'^  m_NavMeshData:.*$',s,re.M)
a,b=signature('W05'),signature('W06')
runtime=['WorldMotor','WorldLayout','WorldCamera','WorldRunInput','WorldAnimation','WorldWeather','WorldRoofCutaway']
r={'source':'W05','candidate':'W06','colliderComponents':len(a[0]),'collidersIdentical':a[0]==b[0],'transformCount':len(a[1]),'allTransformsIdentical':a[1]==b[1],'prefabTransformsIdentical':a[2]==b[2],'navigationIdentical':a[3]==b[3],'movementRuntimeIdentical':{n:(E/f'before-source/Runtime/{n}.cs').read_bytes()==(E/f'source/Runtime/{n}.cs').read_bytes() for n in runtime}}
r['passed']=all([*r['movementRuntimeIdentical'].values(),r['collidersIdentical'],r['allTransformsIdentical'],r['prefabTransformsIdentical'],r['navigationIdentical']])
out=E/'movement-preservation.json'
if out.exists():raise SystemExit('Refuse to overwrite movement comparison')
out.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));sys.exit(not r['passed'])
