from pathlib import Path
import configparser,hashlib,json,os,subprocess,zipfile

ROOT=Path(__file__).resolve().parents[4]
DEST=Path('D:/임시게임/VESPER_W10_Desktop')
E=ROOT/'Migration/Evidence/Packaging/W10Desktop'
SOURCE=ROOT/'Unity/Vesper/Builds/VesperWeatherWorld_W10'
ARCHIVE=DEST.with_suffix('.zip')
assert DEST.is_dir() and not ARCHIVE.exists() and not (E/'final-verification.json').exists()

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

actual_obs=Path(os.environ['APPDATA'])/'obs-studio/basic'
protected_obs=[actual_obs/'profiles/VESPER_FHD_30/basic.ini',actual_obs/'profiles/VESPER_FHD_60/basic.ini',actual_obs/'scenes/VESPER_FHD.json']
obs_before={str(p):sha(p) for p in protected_obs}
test_root=E/'isolated-setup-test-02';assert not test_root.exists()
test_root.mkdir()
mock_obs=test_root/'obs-config';mock_videos=test_root/'recordings'
setup=DEST/'OBS/Setup-OBS.ps1'
cmd=['powershell.exe','-NoLogo','-NoProfile','-ExecutionPolicy','Bypass','-File',str(setup),'-ObsConfigRoot',str(mock_obs),'-RecordingDirectory',str(mock_videos)]
first=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(test_root/'first-run.log').write_bytes(first.stdout);assert first.returncode==0, first.stdout
created={p.relative_to(mock_obs).as_posix():sha(p) for p in mock_obs.rglob('*') if p.is_file()}
second=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(test_root/'repeat-run.log').write_bytes(second.stdout);assert second.returncode==0
assert created=={p.relative_to(mock_obs).as_posix():sha(p) for p in mock_obs.rglob('*') if p.is_file()}
conflict=test_root/'conflict-obs';sentinel=conflict/'basic/profiles/VESPER_W10_5070_60/existing.txt'
sentinel.parent.mkdir(parents=True);sentinel.write_text('pre-existing user data')
bad_cmd=cmd.copy();bad_cmd[bad_cmd.index('-ObsConfigRoot')+1]=str(conflict)
third=subprocess.run(bad_cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(test_root/'conflict-run.log').write_bytes(third.stdout)
assert third.returncode!=0 and sentinel.read_text()=='pre-existing user data'
assert list(conflict.rglob('*'))==[conflict/'basic',conflict/'basic/profiles',sentinel.parent,sentinel]
profile=mock_obs/'basic/profiles/VESPER_W10_5070_60'
cfg=configparser.ConfigParser(interpolation=None);cfg.read(profile/'basic.ini',encoding='utf-8-sig')
assert cfg['General']['Name']=='VESPER W10 RTX5070 60'
assert cfg['Video']['FPSCommon']=='60' and cfg['Video']['OutputCX']=='1920' and cfg['Video']['OutputCY']=='1080'
assert cfg['AdvOut']['RecEncoder']=='obs_nvenc_h264_tex'
assert Path(cfg['AdvOut']['RecFilePath']).resolve()==mock_videos.resolve()
encoder=json.loads((profile/'recordEncoder.json').read_text(encoding='utf-8'))
assert encoder['rate_control']=='CQP' and encoder['cqp']==20 and encoder['lookahead'] is False
scene=json.loads((mock_obs/'basic/scenes/VESPER_W10_Desktop.json').read_text(encoding='utf-8'))
assert scene['name']=='VESPER W10 Desktop' and scene['modules']=={}
assert len(scene['sources'])==2 and not any(k.startswith(('DesktopAudioDevice','AuxAudioDevice')) for k in scene)
capture=next(x for x in scene['sources'] if x['id']=='game_capture')
assert capture['settings']['capture_audio'] is False and capture['mixers']==0
before=json.loads((E/'source-before.json').read_text(encoding='utf-8'))
assert all(sha(SOURCE/p)==h for p,h in before.items())
copy_report=json.loads((E/'copy-verification.json').read_text(encoding='utf-8'))
expected={p:h for p,h in before.items() if not any(p.startswith(x+'/') for x in copy_report['omittedDevelopmentSymbols'])}
assert expected=={p.relative_to(DEST/'Game').as_posix():sha(p) for p in (DEST/'Game').rglob('*') if p.is_file()}
assert all(sha(Path(p))==h for p,h in obs_before.items())
for p in DEST.rglob('*'):
    if p.is_file() and p.suffix in {'.cmd','.ps1','.json','.template','.txt','.url'}:
        raw=p.read_bytes()
        assert b'C:\\Users\\brian' not in raw and b'C:/Users/brian' not in raw, p
        assert b'\x08' not in raw, p
for name in ['VesperLinear.exe','UnityPlayer.dll','MonoBleedingEdge/EmbedRuntime/mono-2.0-bdwgc.dll','D3D12/D3D12Core.dll','VesperLinear_Data/globalgamemanagers']:
    assert (DEST/'Game'/name).is_file()
startup=json.loads((E/'startup-check.json').read_text(encoding='utf-8-sig'))
assert startup['started'] and startup['engineInitialized'] and not startup['errors']
public_report={'runtimeFiles':len(expected),'runtimeBytesMatchW10':True,'originalBuildUnchanged':True,'localObsSettingsUnchanged':True,
 'setupChecks':{'newIsolatedInstall':True,'repeatKeepsExistingSettings':True,'conflictRefusesOverwrite':True,'portableRecordingPath':True,'nvenc60Profile':True,'noAudioCaptureOrAutomationScripts':True},
 'copiedGameStartup':'Engine initialized and process responded in the Unicode transfer path; hidden startup check only.',
 'targetDesktopValidation':'RTX5070 device and recording have not been tested here; perform the short test in the included guide.'}
(DEST/'Info/PACKAGE_VERIFICATION.json').write_text(json.dumps(public_report,indent=2),encoding='utf-8')
manifest={p.relative_to(DEST).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(DEST.rglob('*')) if p.is_file()}
(DEST/'Info/FILE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(ARCHIVE,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(DEST.rglob('*')):
        if p.is_file():z.write(p,Path(DEST.name)/p.relative_to(DEST))
with zipfile.ZipFile(ARCHIVE) as z:
    assert z.testzip() is None
    for p,details in manifest.items():
        assert hashlib.sha256(z.read(DEST.name+'/'+p)).hexdigest()==details['sha256']
    assert set(z.namelist())=={DEST.name+'/'+p for p in manifest}|{DEST.name+'/Info/FILE_MANIFEST.json'}
result={**public_report,'folder':str(DEST),'folderBytes':sum(p.stat().st_size for p in DEST.rglob('*') if p.is_file()),'zip':str(ARCHIVE),'zipBytes':ARCHIVE.stat().st_size,'zipSha256':sha(ARCHIVE),'zipCrcAndContentHashesVerified':True}
(E/'final-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True,indent=2))
