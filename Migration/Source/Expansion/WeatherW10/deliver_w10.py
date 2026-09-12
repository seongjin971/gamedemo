from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'Migration/Evidence/Expansion/WeatherWorld/W10'
verify=json.loads((E/'verification.json').read_text())
qa=json.loads((E/'input-qa-visible/report.json').read_text())
assert verify['passed'] and len(qa['performance'])==3 and 'PASS No audio sources' in qa['checks']
assert (E/'judge.md').exists() and not (E/'REPORT.md').exists()
fps=[p['fps'] for p in qa['performance']]
table='\n'.join(f"| {p['scene']} | {p['fps']:.2f} | {p['p95Ms']:.2f} |" for p in qa['performance'])
report=f'''# W10 — Q/E 전용 시점 회전

W09를 보존한 별도 장면·실행본이다. 이동 클릭의 작은 마우스 움직임이 시점 회전으로 해석되던 문제를 수정했다.

- Q를 누르면 왼쪽, E를 누르면 오른쪽으로 회전한다. 두 키를 함께 누르면 회전하지 않는다. 기존 회전 범위와 부드러운 움직임은 유지한다.
- 왼쪽 마우스 드래그는 각도를 바꾸지 않는다. 버튼을 놓은 지점을 이동 목적지로 처리한다. 상하 시점 각도는 고정한다.
- 휠 확대·축소, Shift 달리기를 유지한다. R은 시작점으로 복귀하며 선택한 시점 각도를 유지한다.
- 실제 게임 하단 안내를 `Q / E to orbit`으로 갱신했다.

실행: [PLAY_VESPER_WEATHER.cmd](../../../../../PLAY_VESPER_WEATHER.cmd) → W10,1920×1080 전체화면. 이전 W09는 [PLAY_VESPER_WEATHER_W09.cmd](../../../../../PLAY_VESPER_WEATHER_W09.cmd). W06/W05 실행기와 기존 OBS 설정도 보존한다.

## 실제 검증

빌드 오류0/경고0. 표시 상태의 Unity 실행본에서 입력·이동 확인 {len(qa['checks'])}개 PASS, 실행 오류0, 오디오0. 폐허 구간 클릭2회와 실제 이동 {qa['distance']:.2f}m에서 마우스 드래그 후 이동 및 일반 클릭 이동 모두 각도 유지·도착·바닥 지지·충돌 여유를 확인했다. Q/E 회전, 동시 입력, 휠, R, 달리기 속도, 짝 없는 마우스 해제·비활성화 때 입력 취소·오른쪽 버튼 무시도 확인했다.

검사는 실제 네이티브 입력 폴링이 호출하는 동일 함수에 합성 입력을 넣어 수행했다. 물리 키보드·마우스 직접 조작이나 사용자 수락을 대신하지 않는다. 전체 이동 검사 묶음은 실행하지 않았다. [독립 검토](judge.md)도 별도로 남겼다. 조작 변경만 요청받았으므로 새로운 시각 목표 제작이나 Pro 이미지 일치도 반복은 진행하지 않았다.

[Q/E 안내·기본 화면](input-qa-visible/start-qe-help.png) · [Q 회전](input-qa-visible/q-left.png) · [E 회전](input-qa-visible/e-right.png) · [드래그 후 이동](input-qa-visible/drag-release-walk-fixed-angle.png) · [W09 강한 섬광 유지](input-qa-visible/w09-strong-flash-retained.png) · [설산 유지](input-qa-visible/snow-retained.png). 모두 실제 원본1920×1080 캡처다.

대표 성능은 비 숲·폐허·설산에서 각6초 보행 중 엔진 간격을 측정했다. 동시 게임/OBS 프로세스 없음, 새 녹화 품질 검증 없음. 이전 버전과 조건을 맞춘 성능 증감 비교는 아니다.

| 위치-동작 | FPS | p95 ms |
| --- | ---: | ---: |
{table}

처음 `input-qa/` 시도는 숨김 창 때문에 화면 캡처가 실패했다. 해당 실패 근거를 보존했고 숨김 상태 성능은 채택하지 않았다. 같은 빌드를 표시 상태로 실행한 `input-qa-visible/`이 최종 검증이다.

## 보존과 소스

보호 {verify['protectedFiles']:,}파일 변경0, 공유 스킬 변경0. W09 장면과 W10 장면은 버전별 스크립트 GUID 연결 외에 직렬화 내용이 동일하다. 기존 충돌·Transform·내비게이션·재질·입자·지붕·섬광 설정을 유지했다. `.gitignore`와 `package-lock.json`도 그대로다.

공유 소스를 수정하지 않기 위해 W10 전용 런타임 이름공간에12파일을 복제하고 새 장면의 형식 참조를 연결했다. 동작 변경은 `WorldCamera.cs`, 안내 문구 변경은 `WorldEnvironment.cs`에 한정되며 다른 파일은 이름공간 외에 동일하다. 이전 파일/GUID/장면/빌드/근거는 보존했다.

최종 장면: `Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W10.unity`

최종 빌드: `Unity/Vesper/Builds/VesperWeatherWorld_W10/VesperLinear.exe`

정확한 소스: `W10/source/`, 수정 전 소스: `W10/before-source/`, 도구: `Migration/Source/Expansion/WeatherW10/`.
'''
(E/'REPORT.md').write_text(report,encoding='utf-8')
old=ROOT/'PLAY_VESPER_WEATHER.cmd'; kept=ROOT/'PLAY_VESPER_WEATHER_W09.cmd'
assert not kept.exists() and b'VesperWeatherWorld_W09' in old.read_bytes()
shutil.copy2(old,kept)
old.write_bytes(old.read_bytes().replace(b'VesperWeatherWorld_W09',b'VesperWeatherWorld_W10'))
p=ROOT/'PLAY_WEATHER.md'; text=p.read_text(encoding='utf-8-sig')
text=text.replace('# VESPER — 구조물 보수·더 강한 섬광 W09','# VESPER — Q/E 전용 시점 회전 W10')
text=text.replace('클릭 이동 / 드래그 시점 회전 / 휠 확대 / Shift 달리기 / R 시작점 복귀 / Alt+F4 종료.',
 '클릭 이동 / Q·E를 눌러 좌우 시점 회전 / 휠 확대 / Shift 달리기 / R 시작점 복귀(각도 유지) / Alt+F4 종료.\n\n마우스를 누른 채 움직여도 시점은 회전하지 않습니다. 버튼을 놓은 지점으로 이동하며 상하 각도는 고정됩니다.')
text=text.replace('이전 날씨 버전은 `PLAY_VESPER_WEATHER_W06.cmd`와 `PLAY_VESPER_WEATHER_W05.cmd`','이전 날씨 버전은 `PLAY_VESPER_WEATHER_W09.cmd`, `PLAY_VESPER_WEATHER_W06.cmd`, `PLAY_VESPER_WEATHER_W05.cmd`')
text=text.replace('새 W09는','새 W10은')
text=text.replace('검증 및 실제 전후 이미지:','조작 변경 검증: [W10 보고서](Migration/Evidence/Expansion/WeatherWorld/W10/REPORT.md).\n\n이전 시각 변경 검증 및 실제 전후 이미지:')
p.write_text(text,encoding='utf-8')
entry=f'''# 최신 전달 — Q/E 전용 시점 회전 W10

**WEATHER_W10_READY_FOR_USER_REVIEW / QE_ONLY_ORBIT / NO_AUDIO.** W09 기준 후속 조작 수정. 마우스 드래그 회전을 제거하고 Q/E를 누를 때만 좌우 회전한다. 상하 각도 고정, 버튼 해제 지점으로 클릭 이동, 휠/Shift 유지, R 시작점 복귀 때 선택 각도 유지. 게임 안내 갱신.

[PLAY_VESPER_WEATHER.cmd](PLAY_VESPER_WEATHER.cmd) → W10/FHD 전체화면. 이전 W09/W06/W05 별도 실행기 보존. [검증·실제 화면](Migration/Evidence/Expansion/WeatherWorld/W10/REPORT.md), [독립 검토](Migration/Evidence/Expansion/WeatherWorld/W10/judge.md).

빌드 오류0/경고0, 실제 FHD6장, 합성 입력 경로 검사{len(qa['checks'])}개 PASS, 폐허 클릭2회/{qa['distance']:.2f}m/각도 고정·이동 확인. 대표 보행 엔진 간격 {min(fps):.2f}~{max(fps):.2f}FPS, OBS 없음. 직접 키보드·마우스 수락이나 녹화 품질 검증은 별도. 첫 숨김 캡처 실패는 보존했고 표시 상태 재검증만 채택했다.

보호{verify['protectedFiles']:,}파일/공유 스킬 변경0. W10 장면은 W09의 버전별 스크립트 GUID만 변경,12 런타임 복제 중 카메라 입력/조작 안내 외 동작 동일. W09의 지붕·강한 전체 화면 이중 섬광·평상시 어둠·눈·이동·재질 유지. 기존 전체 이동 검사·과거 생성기는 재실행하지 않았다. 요청한 조작 수정 완료이며 추가 시각 반복은 대기 작업이 아니다.

---

'''
for name in ['CHECKPOINT.md','.dream-loop/weather-world/CHECKPOINT.md']:
 p=ROOT/name
 local_entry=entry if name=='CHECKPOINT.md' else entry.replace('(PLAY_VESPER_WEATHER.cmd)','(../../PLAY_VESPER_WEATHER.cmd)').replace('(Migration/','(../../Migration/')
 p.write_text(local_entry+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print(json.dumps({'delivered':'W10','checks':len(qa['checks']),'fps':[min(fps),max(fps)]}))
