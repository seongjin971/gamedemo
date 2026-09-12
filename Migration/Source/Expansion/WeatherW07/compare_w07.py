from pathlib import Path
import re,json,sys
ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W07'
def signature(revision):
    s=(ROOT/f'Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_{revision}.unity').read_text(encoding='utf-8')
    docs={m[2]:(m[1],m[3]) for m in re.finditer(r'^--- !u!(\d+) &(-?\d+)[^\n]*\n(.*?)(?=^--- !u!|\Z)',s,re.M|re.S)}
    colliders={k:v for k,v in docs.items() if v[0] in {'64','65','135','136'}}
    poses={k:re.findall(r'^  m_(?:LocalPosition|LocalRotation|LocalScale|Father):.*$',body,re.M) for k,(kind,body) in docs.items() if kind=='4'}
    prefabs={k:(re.findall(r'^    m_TransformParent:.*$',body,re.M),[m[0] for m in re.finditer(r'^    - target:.*\n      propertyPath: m_(?:LocalPosition|LocalRotation|LocalScale).*\n      value:.*$',body,re.M)]) for k,(kind,body) in docs.items() if kind=='1001'}
    return colliders,poses,prefabs,re.findall(r'^  m_NavMeshData:.*$',s,re.M)
a,b=signature('W06'),signature('W07')
runtime={p.name:p.read_bytes()==(ROOT/'Unity/Vesper/Assets/Vesper/Expansion/WeatherWorld/Runtime'/p.name).read_bytes() for p in (E/'before-source/Runtime').glob('*.cs')}
r={'source':'W06','candidate':'W07','colliderComponents':len(a[0]),'collidersIdentical':a[0]==b[0],'originalTransforms':len(a[1]),'changedOriginalTransforms':[k for k,v in a[1].items() if b[1].get(k)!=v],'newTransforms':len(b[1])-len(a[1]),'originalPrefabTransformsPreserved':all(b[2].get(k)==v for k,v in a[2].items()),'navigationIdentical':a[3]==b[3],'originalRuntimeUnchanged':runtime}
r['passed']=r['collidersIdentical'] and not r['changedOriginalTransforms'] and r['originalPrefabTransformsPreserved'] and r['navigationIdentical'] and all(runtime.values())
out=E/'movement-preservation.json'
if out.exists():raise SystemExit('Refuse existing comparison')
out.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));sys.exit(not r['passed'])
