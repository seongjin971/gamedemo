from pathlib import Path
import configparser,copy,hashlib,json,os,shutil,subprocess,uuid

ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'Unity/Vesper/Builds/VesperWeatherWorld_W10'
DEST=Path('D:/임시게임/VESPER_W10_Desktop')
E=ROOT/'Migration/Evidence/Packaging/W10Desktop'
assert SOURCE.is_dir() and not DEST.exists() and not E.exists(), 'Preserve existing package/evidence'
assert DEST.parent.resolve()==Path('D:/임시게임').resolve()
E.mkdir(parents=True); DEST.mkdir()

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

before={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file()}
(E/'source-before.json').write_text(json.dumps(before,indent=2))
excluded=[]
for p in SOURCE.iterdir():
    if p.name.endswith('_BurstDebugInformation_DoNotShip'):
        excluded.append(p.name);continue
    target=DEST/'Game'/p.name
    target.parent.mkdir(exist_ok=True)
    if p.is_dir():shutil.copytree(p,target)
    else:shutil.copy2(p,target)

def write(name,text,bom=False):
    p=DEST/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text,encoding='utf-8-sig' if bom else 'utf-8',newline='\r\n' if name.endswith(('.cmd','.txt','.ps1')) else None)

game_start=r'''@echo off
setlocal
set "VESPER_EXE=%~dp0Game\VesperLinear.exe"
if not exist "%VESPER_EXE%" (
 echo Game files are missing. Extract the entire VESPER_W10_Desktop folder first.
 pause
 exit /b 1
)
start "" /D "%~dp0Game" "%VESPER_EXE%" -screen-width 1920 -screen-height 1080 -screen-fullscreen 1 -window-mode exclusive -force-d3d12
'''
write('01_PLAY.cmd',game_start)
write('04_PLAY_WINDOWED.cmd',game_start.replace('-screen-fullscreen 1 -window-mode exclusive','-screen-fullscreen 0'))
write('02_SETUP_OBS_ONCE.cmd',r'''@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0OBS\Setup-OBS.ps1"
set "VESPER_SETUP_RESULT=%ERRORLEVEL%"
if not "%VESPER_SETUP_RESULT%"=="0" echo Setup did not complete. Read the message above.
pause
exit /b %VESPER_SETUP_RESULT%
''')
write('03_RECORD.cmd',r'''@echo off
setlocal
set "VESPER_OBS=%ProgramFiles%\obs-studio\bin\64bit\obs64.exe"
if not exist "%VESPER_OBS%" set "VESPER_OBS=%LocalAppData%\Programs\obs-studio\bin\64bit\obs64.exe"
if not exist "%VESPER_OBS%" (
 echo Install OBS Studio for Windows from https://obsproject.com/download first.
 pause
 exit /b 1
)
if not exist "%APPDATA%\obs-studio\basic\profiles\VESPER_W10_5070_60\basic.ini" (
 echo Run 02_SETUP_OBS_ONCE.cmd first.
 pause
 exit /b 1
)
if not exist "%APPDATA%\obs-studio\basic\scenes\VESPER_W10_Desktop.json" (
 echo Run 02_SETUP_OBS_ONCE.cmd first.
 pause
 exit /b 1
)
tasklist /FI "IMAGENAME eq obs64.exe" /NH | find /I "obs64.exe" >nul
if not errorlevel 1 (
 echo OBS is already running. Stop recording and close OBS normally, then run this launcher again.
 echo This launcher does not close OBS or change an active recording.
 pause
 exit /b 1
)
for %%I in ("%VESPER_OBS%") do set "VESPER_OBS_DIR=%%~dpI"
start "" /D "%VESPER_OBS_DIR%" "%VESPER_OBS%" --profile "VESPER W10 RTX5070 60" --collection "VESPER W10 Desktop" --scene "VESPER"
tasklist /FI "IMAGENAME eq VesperLinear.exe" /NH | find /I "VesperLinear.exe" >nul
if errorlevel 1 call "%~dp001_PLAY.cmd"
echo OBS is open. Ctrl+Shift+F9 starts recording; Ctrl+Shift+F10 stops it.
''')
write('OBS/OBS_DOWNLOAD.url','[InternetShortcut]\nURL=https://obsproject.com/download\n')
shutil.copy2(Path(__file__).with_name('Setup-OBS.ps1'),DEST/'OBS/Setup-OBS.ps1')
cfg=configparser.ConfigParser(interpolation=None);cfg.optionxform=str
cfg.read(Path(os.environ['APPDATA'])/'obs-studio/basic/profiles/VESPER_FHD_60/basic.ini',encoding='utf-8-sig')
cfg['General']['Name']='VESPER W10 RTX5070 60'
cfg['AdvOut']['RecFilePath']='@@RECORDING_DIRECTORY@@'
cfg['AdvOut']['RecEncoder']='obs_nvenc_h264_tex'
cfg['Video']['FPSCommon']='60';cfg['Video']['FPSInt']='60'
cfg['Output']['FilenameFormatting']='VESPER W10 %CCYY-%MM-%DD %hh-%mm-%ss'
p=DEST/'OBS/Profile/basic.ini.template';p.parent.mkdir(parents=True)
with p.open('w',encoding='utf-8') as f:cfg.write(f,space_around_delimiters=False)
encoder={'rate_control':'CQP','cqp':20,'keyint_sec':2,'preset':'p5','tune':'hq','multipass':'qres','profile':'high','lookahead':False,'adaptive_quantization':True,'bf':2,'device':-1}
write('OBS/Profile/recordEncoder.json',json.dumps(encoder,indent=2)+'\n')
scene=json.loads((Path(os.environ['APPDATA'])/'obs-studio/basic/scenes/VESPER_FHD.json').read_text(encoding='utf-8-sig'))
scene['name']='VESPER W10 Desktop';scene['modules']={};scene['saved_projectors']=[]
scene['quick_transitions']=[];scene['preview_locked']=True
sources={s['id']:s for s in scene['sources']};assert set(sources)=={'scene','game_capture'}
capture=sources['game_capture'];capture['uuid']=str(uuid.uuid4());capture['mixers']=0;capture['muted']=True
capture['settings'].update(capture_audio=False,capture_cursor=False,capture_overlays=False,limit_framerate=False)
sources['scene']['uuid']=str(uuid.uuid4());sources['scene']['settings']['items'][0]['source_uuid']=capture['uuid']
assert not any(k.startswith(('DesktopAudioDevice','AuxAudioDevice')) for k in scene)
write('OBS/Scene/VESPER_W10_Desktop.json',json.dumps(scene,ensure_ascii=False,indent=2)+'\n')

write('00_먼저읽기.txt',r'''VESPER W10 — 데스크톱 전달본

이 폴더 전체를 Windows 데스크톱으로 복사하세요.
ZIP으로 옮겼다면 먼저 전체 압축을 푸세요. Unity 설치는 필요 없습니다.

게임만 실행
  01_PLAY.cmd — 1920×1080 전체화면
  04_PLAY_WINDOWED.cmd — 1920×1080 창모드 (필요할 때)

RTX 5070으로 녹화 — 처음 한 번만 준비
  1. OBS Studio 32.2.1 이상 Windows 버전을 설치합니다.
     OBS 폴더의 OBS_DOWNLOAD.url이 공식 다운로드 페이지를 엽니다.
  2. OBS가 열려 있으면 녹화를 중단한 뒤 OBS를 완전히 닫습니다.
  3. 02_SETUP_OBS_ONCE.cmd를 실행합니다.
     VESPER 전용 프로필·장면을 추가하며 다른 OBS 설정은 덮어쓰지 않습니다.
  4. 03_RECORD.cmd를 실행합니다. OBS와 게임이 열립니다.

녹화 조작
  Ctrl + Shift + F9  : 녹화 시작
  Ctrl + Shift + F10 : 녹화 중단
  OBS 버튼이 '녹화 중단'으로 바뀌고 녹화 시간이 증가하면 녹화 중입니다.
  먼저 녹화를 중단한 뒤 게임을 종료하세요.
  저장 위치: 데스크톱 사용자 계정의 동영상(Videos)\VESPER 폴더

게임 조작
  왼쪽 클릭/버튼 해제 지점으로 이동
  Q / E: 좌우 시점 회전 — 마우스 드래그는 시점을 회전시키지 않습니다.
  휠: 확대·축소 / Shift: 달리기 / R: 시작점 복귀(각도 유지)
  Alt + F4: 게임 종료

전달 내용
  최신 W10: 지붕 보수, 강화한 전체 화면 이중 섬광, 눈보라, Q/E 회전.
  게임과 녹화 설정은 무음입니다.
  Game 폴더의 exe·Data·DLL·하위 폴더를 함께 보관하세요.

녹화 설정과 확인 방법은 OBS_60FPS_안내.txt를 참고하세요.
이 패키지의 파일 검증과 원래 W10 검증은 Info 폴더에 있습니다.
''',True)
write('OBS_60FPS_안내.txt',r'''RTX 5070 — VESPER W10 녹화

권장 첫 실행 순서
  02_SETUP_OBS_ONCE.cmd → 03_RECORD.cmd
  OBS를 이미 사용 중이면 기존 녹화를 마치고 완전히 닫은 후 진행하세요.
  이 도구는 OBS를 설치하거나 드라이버를 바꾸지 않습니다.
  같은 VESPER 전용 설정이 이미 있으면 기존 값을 유지합니다.

적용되는 프로필
  프로필: VESPER W10 RTX5070 60
  장면 모음: VESPER W10 Desktop / 장면: VESPER
  캔버스·출력: 1920×1080, 60FPS
  인코더: NVIDIA NVENC H.264
  CQP 20 / P5 / 고화질 / 2패스(1/4 해상도) / High
  키프레임 2초 / Look-ahead 끔 / 적응형 양자화 켬 / B-frame 2
  파일: Hybrid MP4 / 무음 AAC 트랙
  저장: 해당 데스크톱 사용자의 동영상(Videos)\VESPER

이 프로필은 노트북용 Intel QuickSync 프로필과 별도입니다.
방송 계정·스트림 키·노트북 사용자 경로·자동화 Lua 스크립트는 포함하지 않습니다.
OBS 자체는 공식 사이트에서 따로 설치하세요.

처음 30초 정도 직접 이동하며 시험 녹화하세요.
  - OBS 미리보기에 게임 화면이 잡히는지 확인합니다.
  - '보기 → 통계'에서 렌더링/인코딩 지연이 누적되는지 확인합니다.
  - 저장된 영상을 재생해 움직임을 확인합니다.
  - 이번 PC의 실제 60FPS 녹화 성공은 데스크톱에서 확인해야 합니다.

문제가 생기면
  - NVIDIA NVENC가 없으면 NVIDIA 드라이버와 OBS 버전을 확인합니다.
  - 검은 화면이면 게임을 먼저 실행하고 게임 캡처 속성의 특정 창을
    'VESPER Unity migration / VesperLinear.exe'로 선택합니다.
  - 한 모니터의 전체화면 게임에서 Alt+Tab하면 미리보기가 멈출 수 있습니다.
    게임을 다시 앞으로 가져오거나 04_PLAY_WINDOWED.cmd로 확인하세요.
  - 화면 크기·비율이 맞지 않으면 04_PLAY_WINDOWED.cmd를 사용해 봅니다.
  - OBS를 사용자 지정 위치에 설치했다면 OBS를 직접 열고 위 프로필·장면 모음을
    선택한 뒤 01_PLAY.cmd로 게임을 실행하면 됩니다.

공식 참고
  https://obsproject.com/download
  https://obsproject.com/kb/advanced-recording-settings-guide
  https://obsproject.com/kb/game-capture-source
  설정 키 확인: OBS Studio 32.2.1 plugins/obs-nvenc/nvenc.c 및 nvenc-properties.c
''',True)
for source,name in [
 (ROOT/'Migration/Evidence/Expansion/WeatherWorld/W10/build.json','Info/W10-build.json'),
 (ROOT/'Migration/Evidence/Expansion/WeatherWorld/W10/input-qa-visible/report.json','Info/W10-original-input-checks.json'),
 (ROOT/'Migration/Evidence/Expansion/WeatherWorld/W10/input-qa-visible/start-qe-help.png','Info/W10-game-screen.png')]:
    (DEST/name).parent.mkdir(exist_ok=True);shutil.copy2(source,DEST/name)
write('Info/VALIDATION.txt','''The Game directory is a byte-identical copy of the delivered W10 runtime.
Only the Unity BurstDebugInformation_DoNotShip directory is omitted.
The original W10 build had 0 errors / 0 warnings and 19 passing targeted input checks.
The original FPS samples are from the laptop without OBS, not from the RTX 5070 desktop.
Desktop NVENC settings follow OBS official baseline settings and 32.2.1 source keys.
The target desktop is not connected here; actual NVENC/recording/driver performance is not certified.
''')
copied={p.relative_to(DEST/'Game').as_posix():sha(p) for p in (DEST/'Game').rglob('*') if p.is_file()}
assert all(before[p]==h for p,h in copied.items())
assert set(copied)=={p for p in before if not any(p.startswith(x+'/') for x in excluded)}
assert all(sha(SOURCE/p)==h for p,h in before.items())
report={'destination':str(DEST),'runtimeFiles':len(copied),'runtimeBytes':sum((DEST/'Game'/p).stat().st_size for p in copied),'copiedRuntimeMatchesW10':True,'sourceBuildUnchanged':True,'omittedDevelopmentSymbols':excluded,'obsProfile':'VESPER W10 RTX5070 60','obsEncoder':'obs_nvenc_h264_tex','desktopRecordingTest':'pending on target RTX5070 desktop'}
(E/'copy-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
