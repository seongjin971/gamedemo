"""New road-package preservation record; never runs or replaces old baselines."""
from pathlib import Path
import datetime, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'Migration/Evidence/Expansion/LinearWorld/RoadR01'
OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='before':
    paths=set()
    for folder in ['Unity/Vesper/Builds/VesperLinearWorld_L06','Unity/Vesper/Assets/Vesper/Expansion/LinearWorld/Generated/L06']:
        paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file())
    paths.update(p for p in (ROOT/'Unity/Vesper/Assets/Vesper/Expansion/LinearWorld').rglob('*') if p.suffix in {'.cs','.shader'})
    for name in ['.gitignore','package-lock.json','PLAY_VESPER_LINEAR.cmd','PLAY_VESPER_WORLD.cmd','PLAY_VESPER_WORLD_F01.cmd','Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperLinearWorld_L06.unity','Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperLinearWorld_L06.unity.meta','Unity/Vesper/Assets/UniversalRenderPipelineGlobalSettings.asset','Unity/Vesper/Assets/Vesper/AtmosphereV2/Settings/AtmosphereURP.asset','Unity/Vesper/ProjectSettings/GraphicsSettings.asset','Unity/Vesper/ProjectSettings/ProjectSettings.asset','Migration/Evidence/Expansion/ContinuousWorld/VisualF/preservation-baseline-20260910.json','Migration/Evidence/Expansion/ContinuousWorld/VisualF/F02-uncompiled-source-manifest.json','Migration/Evidence/Expansion/LinearWorld/delivery-audit.json']:
        paths.add(ROOT/name)
    data={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}
    with (OUT/'before.json').open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
    previous=ROOT/'Migration/Evidence/Expansion/LinearWorld/L06/build-source'
    source=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/LinearWorld'
    drift=[p.relative_to(previous).as_posix() for p in previous.rglob('*') if p.is_file() and sha(p)!=sha(source/p.relative_to(previous))]
    print(json.dumps({'recorded':len(data),'sourceDriftFromL06':drift}))
else:
    data=json.loads((OUT/'before.json').read_text())
    changed=[n for n,h in data.items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
    f02=json.loads((ROOT/'Migration/Evidence/Expansion/ContinuousWorld/VisualF/F02-uncompiled-source-manifest.json').read_text())
    old_drift=[n for n,h in f02.items() if sha(ROOT/n)!=h]
    report={'timeUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checked':len(data),'changed':changed,'f02Checked':len(f02),'f02Changed':old_drift}
    with (OUT/(sys.argv[2] if len(sys.argv)>2 else 'after.json')).open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    print(json.dumps(report))
    if changed or old_drift:raise SystemExit(1)
