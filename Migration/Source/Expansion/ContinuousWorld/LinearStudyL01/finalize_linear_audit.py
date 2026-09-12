from pathlib import Path
import datetime, hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[5]
OUT = ROOT / 'Migration/Evidence/Expansion/LinearWorld'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old = ROOT / 'Migration/Evidence/Expansion/ContinuousWorld/VisualF'
baseline = json.loads((old/'preservation-baseline-20260910.json').read_text(encoding='utf-8-sig'))
f02 = json.loads((old/'F02-uncompiled-source-manifest.json').read_text(encoding='utf-8-sig'))
critical = {n:h for n,h in baseline.items() if n in {
    '.gitignore','package-lock.json','PLAY_VESPER_WORLD.cmd',
    'Unity/Vesper/Assets/UniversalRenderPipelineGlobalSettings.asset',
    'Unity/Vesper/Assets/Vesper/AtmosphereV2/Settings/AtmosphereURP.asset',
    'Unity/Vesper/ProjectSettings/GraphicsSettings.asset',
    'Unity/Vesper/ProjectSettings/ProjectAuditorSettings.asset',
    'Unity/Vesper/ProjectSettings/ProjectSettings.asset',
    'Migration/Evidence/Expansion/ContinuousWorld/protection-before.json',
}}
critical.update(f02)
violations = [n for n,h in critical.items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
source = ROOT/'Unity/Vesper/Assets/Vesper/Expansion/LinearWorld'
snapshot = OUT/'L06/build-source'
source_changes = [p.relative_to(snapshot).as_posix() for p in snapshot.rglob('*') if p.is_file() and (not (source/p.relative_to(snapshot)).is_file() or sha(p)!=sha(source/p.relative_to(snapshot)))]
paths = [
    ROOT/'PLAY_VESPER_LINEAR.cmd',
    ROOT/'Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperLinearWorld_L06.unity',
    ROOT/'Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperLinearWorld_L06.unity.meta',
    ROOT/'Unity/Vesper/Builds/VesperLinearWorld_L06/VesperLinear.exe',
    ROOT/'Unity/Vesper/Builds/VesperLinearWorld_L06/VesperLinear_Data/Managed/Assembly-CSharp.dll',
]
paths.extend(p for p in snapshot.rglob('*') if p.is_file())
report = {
    'timeUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'priorBoundedInspection':'preservation-inspection.json:6497 files unchanged before final L06 build',
    'postBuildCriticalChecked':len(critical), 'violations':violations,
    'sourceMatchesL06BuildSnapshot':not source_changes, 'sourceChanges':source_changes,
    'deliveryHashes':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
    'notes':['No old baseline or preservation script regenerated or rerun.',
             'No full 24061-file final rehash. F01 built later than the earlier baseline; isolated output routing preserved it but this audit does not claim a historical full F01 hash comparison.',
             'F02 source hashes preserved; the Unity project has since compiled globally, but no F02 scene preparation, build or adoption was performed.'],
}
with (OUT/'delivery-audit.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
with (OUT/'git-status-delivery.txt').open('xb') as f:f.write(subprocess.check_output(['git','status','--short'],cwd=ROOT))
print(json.dumps({k:v for k,v in report.items() if k!='deliveryHashes'},indent=2))
if violations or source_changes:raise SystemExit(1)
