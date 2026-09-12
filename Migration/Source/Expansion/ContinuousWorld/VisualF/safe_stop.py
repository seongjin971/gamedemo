from pathlib import Path
import json,hashlib,subprocess,datetime
ROOT=Path(__file__).resolve().parents[5]
OUT=ROOT/'Migration/Evidence/Expansion/ContinuousWorld/VisualF'
baseline=json.loads((OUT/'preservation-baseline-20260910.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
critical=[n for n in baseline if n.startswith('Unity/Vesper/Builds/VesperContinuousWorld_E02/') or n.startswith('Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Runtime/') or n in {'.gitignore','package-lock.json','PLAY_VESPER_WORLD.cmd','Migration/Evidence/Expansion/ContinuousWorld/protection-before.json','Migration/Evidence/Expansion/ContinuousWorld/E02/delivery-audit.json','Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperContinuousWorld.unity','Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperContinuousWorld.unity.meta'}]
allowed={'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Runtime/WorldLayout.cs'}
changed=[n for n in critical if not (ROOT/n).is_file() or sha(ROOT/n)!=baseline[n]]
audit={'timeUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Limited safe-stop audit: entire E02 Windows build, old continuous scene, runtime source, launcher, user IDE files and original protection baseline. Full 24061-file rehash deferred at user request to stop promptly.','checked':len(critical),'authorizedSourceChanges':[n for n in changed if n in allowed],'violations':[n for n in changed if n not in allowed]}
(OUT/'safe-stop-preservation.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
current=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld'
snapshot={p.relative_to(ROOT).as_posix():sha(p) for p in current.rglob('*') if p.suffix in {'.cs','.shader'}}
(OUT/'F02-uncompiled-source-manifest.json').write_text(json.dumps(snapshot,indent=2))
(OUT/'git-status-safe-stop.txt').write_bytes(subprocess.check_output(['git','status','--short'],cwd=ROOT))
launcher=ROOT/'PLAY_VESPER_WORLD_F01.cmd'
with launcher.open('x',encoding='ascii',newline='') as f:
 f.write('@echo off\r\nsetlocal\r\nset "VESPER_F01_EXE=%~dp0Unity\\Vesper\\Builds\\VesperContinuousWorld_F01\\VesperWorld.exe"\r\nif not exist "%VESPER_F01_EXE%" exit /b 1\r\nstart "" "%VESPER_F01_EXE%" -screen-width 1536 -screen-height 1024 -screen-fullscreen 0 -force-d3d12\r\n')
intro='''# 최신 안전 정지 — Visual F01 보존 / F02 미빌드, 2026-09-10

사용자의 이동을 위한 안전 종료 요청으로 작업을 멈췄다. 이번 우선순위는 통합 맵의 시각 제작이며 과거 이동 우선·5시간 제한은 적용하지 않는다. 실제 설치된 Dream Loop Pro workflow를 읽고 적용했다.

새 F01 장면/Windows 빌드와 실제 Unity 18개 정적 비교 화면을 보존했다. 빌드 오류0/경고0, 준비 경로12개 연결/누락 스크립트0. 독립 평가: 물가5.45, 폐허6.15, 설산342시점7.90. 전망 공간은 형태 미달이며 매끈한 절벽 면 노출이 커진 국소 퇴행도 있다. 시각 품질 완료·최종 이동/성능 검증·사용자 수락을 주장하지 않는다.

기본 `PLAY_VESPER_WORLD.cmd`는 E02 그대로다. 별도 `PLAY_VESPER_WORLD_F01.cmd`는 검토용 중간 F01이다. 작성 중 F02는 소스/Blender 후보만 저장했고 컴파일·Unity 가져오기·새 장면·빌드·시각 채택을 하지 않았다. F02 소스는 F01 실행본과 구분해야 한다.

재개 기준: [Visual F 안전 정지 보고](Migration/Evidence/Expansion/ContinuousWorld/VisualF/SAFE_STOP.md), [.dream-loop 최신 체크포인트](.dream-loop/continuous-world/VisualF/CHECKPOINT.md). 아래 E02 및 이전 기록은 역사 상태다. E02 날씨 검사는 원본 기준42개이며 상단 역사 요약의43개는 집계 오류다.

---

'''
for name in ['CHECKPOINT.md','EXPANSION_PLAN.md','CONTINUOUS_MAP_PLAN.md']:
 p=ROOT/name
 (OUT/('before-safe-stop-'+name)).write_bytes(p.read_bytes())
 p.write_text(intro+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print(json.dumps(audit,ensure_ascii=False))
