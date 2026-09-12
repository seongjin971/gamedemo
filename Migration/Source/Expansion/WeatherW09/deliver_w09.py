from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W09'
def read(name):return json.loads((E/name).read_text(encoding='utf-8-sig'))
build,capture,traverse,performance=map(read,['build.json','capture/report.json','traverse/report.json','performance/report.json'])
preserve,movement,flash=map(read,['protected-after.json','movement-preservation.json','flash-coverage.json'])
assert build['result']=='Succeeded' and build['errors']==0 and build['warnings']==0
assert all(r['failures']==0 and not r['errors'] and r['audioSources']==0 for r in [capture,traverse,performance])
assert all(r['passed'] for r in [preserve,movement,flash])
assert (E/'judge.md').is_file()
out=E/'REPORT.md'
if out.exists():raise SystemExit('W09 delivery already written')
fps=[p['fps'] for p in performance['performance']]
fmin,fmax=min(fps),max(fps)
table='\n'.join(f"| {p['scene']} | {p['fps']:.2f} | {p['p95Ms']:.2f} | {p['maxMs']:.2f} |" for p in performance['performance'])
ratios=[v for c in flash['comparisons'].values() for v in c['W09OverW06']]
report=f'''# W09 — 폐허 지붕 연결 보수 · 더 강한 전체 화면 섬광

W06을 보존한 별도 W09 장면·Windows 실행본이다. 사용자가 지정한 구조물 연결 보수와 천둥 강화 범위에서 눈에 띄는 개선을 확인했다. 실제 설치된 Dream Loop Pro와 새 독립 평가를 적용했다. 독립 판정 및 Pro 점수는 [judge.md](judge.md)에 있으며, 이번 전달은 전체 참고 이미지8점 달성이나 사용자 최종 수락을 뜻하지 않는다.

새 독립 평가: 구조물 보수·더 강한 전체 화면 섬광 모두 요청 범위 PASS. 별도 참고 이미지 일치도는 구조물7.15, 기본 섬광6.00, 강한 섬광5.75/10이다. 강한 화면 밝기 증가와 전체 참고 이미지의 재질/조명 일치도는 별개다.

실행: [PLAY_VESPER_WEATHER.cmd](../../../../../PLAY_VESPER_WEATHER.cmd),1920×1080 전체화면. 이전 W06은 [PLAY_VESPER_WEATHER_W06.cmd](../../../../../PLAY_VESPER_WEATHER_W06.cmd), W05 실행기도 유지한다. 녹화 버튼은 같은 최신 실행기를 참조하며 기존 OBS 설정은 그대로다. 새 OBS 녹화 품질 검증은 하지 않았다.

## 변경과 실제 화면

- **구조물:** 기존 지붕 시각 복제본의 폭·높이를 벽/기둥에 맞추고 목재 연결7개를 더했다. 평소에는 불투명 깊이 기록을 사용해 겹침과 주황색 틈을 줄인다. 쉼터에 들어가면 실제 투명 셰이더 변형으로 지붕이 투명해져 캐릭터를 드러낸다. 기존 아치 입구·석벽·기둥·바닥·이동 충돌은 그대로다.
- **천둥:** 원래 이중 점멸과 전체 화면 범위를 유지하고 최종 화면 밝기에 곱셈 방식의 증폭을 추가했다. W06 비교 최고점보다 화면4영역 평균 픽셀 밝기가 약{min(ratios):.2f}~{max(ratios):.2f}배다. 물리 광도 배수는 아니다. 원래 어둠으로 돌아오며 방향광 강도·방향, 섬광 간격/강한 이벤트 규칙은 바꾸지 않았다. 번개 줄기·음향 없음.
- **눈·맵:** W06 눈발과 강가→어두운 숲→비 숲→폐허→밤 설산 구성 유지. 기존 공유 코드와 자산은 변경하지 않았다.

| 비교 | 이전 W06 상태 | W09 실제 결과 |
| --- | --- | --- |
| 지붕 연결/기와 | [이전](capture/canopy-W06-0.59.png) | [수정](capture/canopy-W09-0.59.png) |
| 다른 시점 | [이전](capture/canopy-W06-1.1.png) | [수정](capture/canopy-W09-1.1.png) |
| 기본 섬광 | [이전](capture/abbey-W06-flash.png) | [더 강한 섬광](capture/abbey-W09-flash.png) |
| 드문 강한 섬광 | [이전](capture/abbey-W06-strong.png) | [더 강한 섬광](capture/abbey-W09-strong.png) |

[평상시](capture/abbey-W09-normal.png) · [점멸 후 어둠 복귀](capture/abbey-after-flash.png) · [쉼터 안 캐릭터 가독성](capture/canopy-sheltered.png) · [실제 아치 통과](traverse/shelter-entry.png).

원본 FHD 캡처{len(capture['captures'])}장과 이동 캡처1장. W06 이름 비교 화면은 새 실행본 안에 보존한 원래 지붕/원래 효과를 활성화한 비교용 캡처이며 W06 실행 파일을 새로 촬영한 것은 아니다. 구조물 확대 구도는 검사용 카메라이고 일반 플레이 카메라는 변경하지 않았다. 생성 목표 이미지는 `.dream-loop/weather-world/W07/target.png`로, 실제 화면과 구분한다. 생성 방식/정확한 프롬프트는 같은 폴더 `TARGET.md`에 있다.

## 검증

- 빌드 오류{build['errors']}/경고{build['warnings']}. 실제 캡처·이동·성능 실행 오류0/오디오0.
- 폐허192↔204m 화면 클릭{traverse['clicks']}회와 아치/쉼터 진입·복귀 이동 요청4회. 실제 모터 이동{traverse['distance']:.2f}m, {len(traverse['checks'])}확인 통과. 충돌·바닥 지지·도착·쉼터 출입을 확인했다. 합성 화면 입력/모터 요청이며 사용자 직접 조작 수락과 구분한다. 전체 이동 검사 묶음은 실행하지 않았다.
- 섬광 시간·어둠 복귀·방향광 강도 유지 검사{len(performance['checks'])}개 통과. `pulse-timing.csv`의 노출 값은 설정/시간 검사이며 화면 밝기는 별도 `flash-coverage.json`과 실제 이미지로 확인했다.
- 충돌382개, 기존 Transform6,623개, 프리팹 Transform·내비게이션·기존 런타임9파일 동일. 새 시각 Transform10개. 원래 지붕 충돌은 그대로 두고 새 시각 지붕만 정렬했다.
- 시작 시점 보호{preserve['protectedFiles']:,}파일 변경0, 공유 스킬 변경0. `.gitignore`·`package-lock.json`·W01~W06 및 기존 E02/F01/L09 보존. 기준을 새로 덮어쓰거나 과거 생성기·이전 빌드를 재실행하지 않았다.

## 대표 성능

Intel Arc130V, D3D12,1920×1080, 각6초. **사용자가 실행한 W06(PID7972)을 종료하지 않고 유지한 상태**, OBS 녹화 없음. 따라서 단독 실행 FPS/이전 W06 벤치마크와의 성능 증감/녹화 품질 인증으로 해석하지 않는다. 엔진 프레임 간격 표본이다.

| 위치-동작 | FPS | p95 ms | 최대 ms |
| --- | ---: | ---: | ---: |
{table}

대표 범위{fmin:.2f}~{fmax:.2f}FPS. 60FPS 고정이나 표시장치 프레임 보장은 주장하지 않는다.

## 소스와 보존한 중간 후보

최종 장면 `Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W09.unity`, 빌드 `Unity/Vesper/Builds/VesperWeatherWorld_W09/VesperLinear.exe`. 추가 코드는 `Expansion/WeatherW07`, `WeatherW08`, `WeatherW09`에 격리했다. `W09/source/`는 최종 추가 소스·새 재질·장면 스냅샷, `W07/before-source/`는 작업 전 공유 날씨 소스다.

W07은 구조물 개선/노출 값 진단, W08은 화면 섬광 개선/쉼터 투명화 진단으로 보존했다. W09가 최종 후속 전달본이다. 공유 노출 경로의 수치 변경만으로 이미지가 변하지 않는 원인을 광범위하게 수정하지 않았으며, 실제 출력 증폭으로 이번 요청을 해결했다. 목재/기와의 세부 재질과 강한 섬광 때의 평평한 밝기 인상은 독립 평가의 잔여 차이와 함께 남는다.
'''
out.write_text(report,encoding='utf-8')
launcher=ROOT/'PLAY_VESPER_WEATHER.cmd'
prior=ROOT/'PLAY_VESPER_WEATHER_W06.cmd'
assert 'VesperWeatherWorld_W06' in launcher.read_text()
if prior.exists():raise SystemExit('W06 launcher already exists; inspect before delivery')
prior.write_bytes(launcher.read_bytes())
launcher.write_bytes(launcher.read_bytes().replace(b'VesperWeatherWorld_W06',b'VesperWeatherWorld_W09'))
play=ROOT/'PLAY_WEATHER.md';s=play.read_text(encoding='utf-8').replace('# VESPER — 눈발·전체 화면 섬광 W06','# VESPER — 구조물 보수·더 강한 섬광 W09')
s=s.replace('- 천둥은 방향 없이', '- 폐허 지붕을 벽·기둥에 맞춰 연결하고 목재 지지를 보완했습니다. 쉼터 안에서는 지붕이 투명해져 캐릭터가 보입니다.\n- 천둥 최고점은 W06보다 더 밝습니다. 화면 영역별 평균 픽셀 밝기 약1.44~1.50배이며 물리 광도 배수는 아닙니다.\n- 천둥은 방향 없이')
s=s.replace('이전 날씨 버전은 `PLAY_VESPER_WEATHER_W05.cmd`','이전 날씨 버전은 `PLAY_VESPER_WEATHER_W06.cmd`와 `PLAY_VESPER_WEATHER_W05.cmd`').replace('새 W06은','새 W09는').replace('[W06 보고서](Migration/Evidence/Expansion/WeatherWorld/W06/REPORT.md)','[W09 보고서](Migration/Evidence/Expansion/WeatherWorld/W09/REPORT.md)')
play.write_text(s,encoding='utf-8')
top=f'''# 최신 전달 — 구조물 보수·더 강한 전체 화면 섬광 W09

**WEATHER_W09_READY_FOR_USER_REVIEW / VISIBLE_IMPROVEMENT_DELIVERED / NO_AUDIO.** W06 기준 사용자 후속 요청2개를 별도 W09에 적용했다. 지붕을 아치벽/기둥에 맞추고 목재 연결·기와 겹침·쉼터 투명화를 보완했다. 전체 화면 섬광 최고점 픽셀 밝기는 W06 비교보다 영역별 약1.44~1.50배. 평상시 어둠·전체 화면 이중 점멸·번개 줄기 없음·W06 눈·무음 유지.

실행: **[PLAY_VESPER_WEATHER.cmd](PLAY_VESPER_WEATHER.cmd)** → W09/FHD 전체화면. W06은 **[PLAY_VESPER_WEATHER_W06.cmd](PLAY_VESPER_WEATHER_W06.cmd)**, W05도 보존. [실제 전후 화면·보고](Migration/Evidence/Expansion/WeatherWorld/W09/REPORT.md), [새 독립 평가](Migration/Evidence/Expansion/WeatherWorld/W09/judge.md).

빌드 오류0/경고0, FHD17장+이동1장, 폐허/쉼터 이동{traverse['distance']:.2f}m/화면클릭4회+모터요청4회/20확인, 효과 검사8개 통과. 보호12,155파일 변경0, 기존 충돌382/Transform6,623/내비게이션/원본 런타임 동일. 대표 {fmin:.2f}~{fmax:.2f}FPS는 기존 W06 게임을 유지한 상태의 엔진 간격이며 OBS 녹화 성능·단독 실행 성능이 아니다. W07/W08은 진단 후보로 보존했다.

실제 설치 Pro·생성 목표·새 독립 시각 평가를 적용했다. 요청 범위의 눈에 띄는 결과로 종료하며 전체 Pro8점/사용자 최종 수락과 구분한다. 공유 스킬/기존 자산과 증거/사용자 파일 보존. 추가 요청은 W09 기준 새 버전에서 시작한다. 과거 생성기·기준·전체 이동 묶음 재실행 금지. 확인 당시 사용자 W06 PID7972는 계속 실행 중이었다.

독립 평가: 두 요청 범위 PASS. 참고 이미지 일치도 구조물7.15/기본 섬광6.00/강한 섬광5.75. 짙고 단순한 목재와 강한 점멸 때 평평한 밝기 인상은 남는다.

---

'''
checkpoint=ROOT/'CHECKPOINT.md';checkpoint.write_text(top+checkpoint.read_text(encoding='utf-8'),encoding='utf-8')
cp=ROOT/'.dream-loop/weather-world/CHECKPOINT.md'
cp.write_text(f'''# Weather World — latest W09 delivered

W09_READY_FOR_USER_REVIEW / VISIBLE_IMPROVEMENT_DELIVERED / NO_AUDIO. User asked to fix the attached canopy and strengthen thunder; specific repair was delegated. Actual installed Dream Loop Pro, generated repair target and fresh independent judge were used. See `Migration/Evidence/Expansion/WeatherWorld/W09/REPORT.md` and `judge.md` for score and evidence limits; no Pro8/final-user-acceptance claim.

- Main launcher now W09,1920x1080 fullscreen. Added W06 launcher, kept W05. OBS launcher/settings unchanged; no new recording test.
- Canopy spans arch and pier seats with7 timber joints, opaque exterior depth and real transparent shelter cutaway. Whole-frame multiplicative thunder amplification produces1.44–1.50x W06 peak grayscale averages by quadrant. W06 double pulses/normal darkness/no bolts/no audio/snow retained.
- Build0 errors/0 warnings,17 FHD captures+1 traversal capture; targeted4 screen clicks+4 motor requests/{traverse['distance']:.2f}m/20 checks PASS;8 pulse checks PASS. Old full movement suite not run.
- Independent judge scope PASS/PASS; separate target scores canopy7.15/default flash6.00/strong5.75. Dark simple timbers and pale flattening at flash peaks remain. No automatic further iteration.
- Representative6 samples {fmin:.2f}–{fmax:.2f}FPS while user's original W06 PID7972 remained alive. Engine cadence, no OBS; not isolated A/B or display/recording quality.
- Protected12,155 initial files and installed skill unchanged. Original382 colliders/6623 transforms/nav refs/all9 original weather runtime files unchanged. Added WeatherW07/08/09 namespaces; W09/source is final snapshot, W07/before-source original source.
- W07 is the structural/exposure-setting diagnostic (rendered flash not stronger); W08 is stronger screen flash with cutaway diagnostic; W09 is the delivered candidate. Preserve all evidence and do not rerun old builders/generators/baselines. Future work starts new version from W09 and new user instructions.
- Stop at visible result; further polish not pending. User W06 process was never stopped by this task; QA W09 processes exit on their own. Recheck actual processes on resume.

---

'''+cp.read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps({'delivered':'W09','fps':[fmin,fmax],'distance':traverse['distance'],'report':str(out)},ensure_ascii=False))
