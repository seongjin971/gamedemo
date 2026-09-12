from pathlib import Path
import hashlib, json, re, shutil

ROOT = Path(__file__).resolve().parents[4]
E = ROOT / 'Migration/Evidence/Expansion/WeatherWorld/W10'
A = ROOT / 'Unity/Vesper/Assets/Vesper/Expansion'
NEW = A / 'WeatherW10/Runtime'
assert not E.exists() and not NEW.exists(), 'Preserve existing W10'
E.mkdir(parents=True)

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

# A new task snapshot; no historical baseline or generator is rerun.
old = json.loads((ROOT/'Migration/Evidence/Expansion/WeatherWorld/W07/protected-before.json').read_text())
paths = {ROOT/p for p in old}
for folder in ['Unity/Vesper/Assets', 'Unity/Vesper/Packages', 'Unity/Vesper/ProjectSettings',
               'Unity/Vesper/Builds/VesperWeatherWorld_W09', 'Migration/Evidence/Expansion/WeatherWorld',
               'Migration/Source/Expansion/WeatherW07', 'Migration/Source/Expansion/WeatherW08',
               'Migration/Source/Expansion/WeatherW09']:
    paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and E not in p.parents)
paths.update(ROOT/p for p in ['PLAY_VESPER_WEATHER_W06.cmd', 'PLAY_VESPER_WEATHER_W05.cmd', 'RECORD_VESPER_WEATHER.cmd'])
(E/'protected-before.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}, indent=2))
skill=Path('C:/Users/brian/.codex/skills/dream-loop')
(E/'skill-before.json').write_text(json.dumps({str(skill/p):sha(skill/p) for p in ['SKILL.md','references/pro-mode/workflow.md']},indent=2))
for p in ['CHECKPOINT.md','.dream-loop/weather-world/CHECKPOINT.md','PLAY_WEATHER.md','PLAY_VESPER_WEATHER.cmd']:
    dest=E/'before-delivery'/p
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/p,dest)

sources = list((A/'WeatherWorld/Runtime').glob('World*.cs'))
sources += [A/'WeatherW07/Runtime'/n for n in ['WeatherW07Flash.cs','WeatherW07Roof.cs','WeatherW07Variant.cs']]
sources += [A/'WeatherW08/Runtime/WeatherW08Flash.cs']
NEW.mkdir(parents=True)
mapping=[]
for p in sources:
    code=p.read_text(encoding='utf-8-sig')
    before=E/'before-source'/p.name
    shutil.copy2(p,before) if before.parent.exists() else (before.parent.mkdir(parents=True),shutil.copy2(p,before))
    for ns in ['WeatherWorld','WeatherW07','WeatherW08']:
        code=code.replace('Vesper.Expansion.'+ns, 'Vesper.Expansion.WeatherW10')
    lines=code.splitlines(); seen=set(); clean=[]
    for line in lines:
        if line.startswith('using '):
            if line in seen: continue
            seen.add(line)
        clean.append(line)
    code='\n'.join(clean)+'\n'
    if p.name=='WorldEnvironment.cs':
        assert 'Drag to orbit' in code
        code=code.replace('Drag to orbit','Q / E to orbit')
    if p.name=='WorldCamera.cs':
        code=code.replace('Vector3 target, initialPlayer, press, lastMouse;', 'Vector3 target, initialPlayer;')
        code=code.replace('        bool dragging;\n','')
        first=code.index('            if (Mathf.Abs(Input.mouseScrollDelta.y)')
        last=code.index('\n        void OnGUI()',first)
        code=code[:first]+'''            HandleKeys(Input.GetKey(KeyCode.Q), Input.GetKey(KeyCode.E),
                Input.GetKeyDown(KeyCode.R), Input.mouseScrollDelta.y, Time.unscaledDeltaTime);
        }
        // Native polling and the opt-in player probe share this input path.
        public void HandleKeys(bool q, bool e, bool reset, float scroll, float dt) {
            float direction = (e ? 1 : 0) - (q ? 1 : 0);
            if (direction != 0) Orbit(direction * .65f * Mathf.Min(dt, .05f), 0);
            if (Mathf.Abs(scroll) > .001f) { zooms++; SetZoom(Zoom - scroll * .55f); }
            if (reset) { resets++; ResetView(); }
        }
''' + code[last:]
        first=code.index('            if (type == EventType.MouseDown)')
        last=code.index('                    clicks++;',first)
        code=code[:first]+'''            if (type == EventType.MouseDown) { pointerHeld = true; }
            else if (type == EventType.MouseDrag && pointerHeld) {
                // A left-button drag never changes yaw or elevation.
            } else if (type == EventType.MouseUp && pointerHeld) {
                pointerHeld = false;
                // Release chooses the destination even after pointer movement.
                if (player) {
''' + code[last:]
        code=code.replace('desiredAngle = .59f; desiredElevation = .88f; Zoom = homeSize; target = homeTarget;',
                          'Zoom = homeSize; target = homeTarget; // R returns home without changing the chosen angle.')
        assert 'Orbit(-delta' not in code and 'dragging' not in code
    (NEW/p.name).write_text(code,encoding='utf-8')
    mapping.append({'old':p.relative_to(ROOT/'Unity/Vesper').as_posix(),'new':(NEW/p.name).relative_to(ROOT/'Unity/Vesper').as_posix()})
(E/'script-map.json').write_text(json.dumps(mapping,indent=2))
(E/'SCOPE.md').write_text('W10: Q/E-only camera rotation. Left drag releases a movement click; elevation stays fixed. Wheel zoom and Shift run remain, R returns home without rotating. W09 visuals, weather, geometry, movement algorithm and shared source preserved. Version-local runtime copies are needed to update typed component references and the HUD without editing old shared scripts. Controls-only change; no new visual target or asset work. Verify native input path in player, targeted movement, actual FHD captures and representative engine cadence.\n',encoding='utf-8')
print(json.dumps({'protected':len(paths),'versionedRuntimeFiles':len(mapping)}))
