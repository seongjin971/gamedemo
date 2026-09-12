from pathlib import Path
import hashlib,json,sys,shutil
ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W07'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
if sys.argv[1]=='before':
    E.mkdir(parents=True,exist_ok=True)
    out=E/'protected-before.json'
    if out.exists():raise SystemExit('W07 baseline exists; never overwrite')
    paths=set()
    for folder in ['Unity/Vesper/Assets','Unity/Vesper/Packages','Unity/Vesper/ProjectSettings','Unity/Vesper/Builds/VesperWeatherWorld_W06','Migration/Evidence/Expansion/WeatherWorld','Migration/Source/Expansion/WeatherW06']:
        paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and E not in p.parents)
    old=json.loads((ROOT/'Migration/Evidence/Expansion/WeatherWorld/W06/protected-before.json').read_text())
    paths.update(ROOT/p for p in old)
    paths.update(ROOT/p for p in ['.gitignore','package-lock.json','RECORD_VESPER_WEATHER.cmd','PLAY_VESPER_WEATHER_W05.cmd'])
    out.write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)},indent=2))
    for name in ['Runtime','Editor','Shaders']:shutil.copytree(ROOT/'Unity/Vesper/Assets/Vesper/Expansion/WeatherWorld'/name,E/'before-source'/name)
    shutil.copy2(ROOT/'PLAY_VESPER_WEATHER.cmd',E/'PLAY_VESPER_WEATHER_W06.cmd')
    skill=Path('C:/Users/brian/.codex/skills/dream-loop')
    (E/'skill-before.json').write_text(json.dumps({str(skill/p):sha(skill/p) for p in ['SKILL.md','references/pro-mode/workflow.md','references/pro-mode/assets-3d.md']},indent=2))
    print('W07 protected files',len(paths))
elif sys.argv[1]=='after':
    before=json.loads((E/'protected-before.json').read_text())
    # The diagnostic editor was newly authored during this task before this snapshot.
    # It is a candidate file, not pre-existing user work; identify it separately.
    candidate=[p for p in before if p.startswith('Unity/Vesper/Assets/Vesper/Expansion/WeatherW07/')]
    changed=[p for p,h in before.items() if p not in candidate and (not (ROOT/p).is_file() or sha(ROOT/p)!=h)]
    skills=json.loads((E/'skill-before.json').read_text())
    skill_changes=[p for p,h in skills.items() if sha(Path(p))!=h]
    report={'protectedFiles':len(before)-len(candidate),'newTaskFilesPresentInInitialSnapshot':candidate,'changed':changed,'sharedSkillChanges':skill_changes,'passed':not(changed or skill_changes)}
    out=E/'protected-after.json'
    if out.exists():raise SystemExit('W07 audit result exists')
    out.write_text(json.dumps(report,indent=2));print(json.dumps(report));sys.exit(not report['passed'])
