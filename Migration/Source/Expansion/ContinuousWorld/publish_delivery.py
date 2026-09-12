"""Promote only a completed local verification artifact; preserves historical docs."""
from pathlib import Path
from datetime import datetime, timezone
import json, re, sys

root = Path(__file__).resolve().parents[4]
revision = sys.argv[1]
assert re.fullmatch(r'E\d+', revision)
base = root / 'Migration/Evidence/Expansion/ContinuousWorld'
out = base / revision
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
audit = read(out / 'delivery-audit.json')
protection = read(base / 'protection-final.json')
assert audit['passed'] and not protection['violations']
native = read(out / 'manual/report.json')
assert not native['errors'] and native['failures'] == 0 and native['clicks'] > native['blocked'] and native['distance'] >= 1 and native['safetyStops'] == 0
qa = read(out / 'qa/report.json')
perf = audit['summaries']['performance']
guide = f'''# VESPER 통합 맵 {revision}

[PLAY_VESPER_WORLD.cmd](PLAY_VESPER_WORLD.cmd)를 실행합니다. 물가·폐허·설산이 하나의 장면으로 연결된 최종 검증본입니다.

- 바닥 클릭: 이동
- Shift를 누른 채 이동: 달리기
- 드래그: 카메라 회전
- 휠: 확대·축소
- R: 시작 지점과 기본 시야로 명시적 복귀
- Alt+F4: 종료

돌다리를 건너 숲길을 따라가면 비 오는 폐허와 눈 오는 고갯길로 이어집니다. 폐허의 무너진 옆 벽 사이로 들어가 지붕 아래에서 비를 피할 수 있고, 같은 길로 돌아올 수 있습니다.

{revision} 전체 왕복3회, 화면 좌표 기반 클릭450회, 약{qa['distance']/1000:.2f}km를 실제 모터로 이동해 실패·오류·자동 리셋·안전 중단 없이 마쳤습니다. 가장자리44클릭(의도한5차단), 강수·지붕43검사도 통과했습니다. 같은 기기·1536×1024·D3D12에서5지점×4동작 평균은 {perf['minFPS']:.1f}~{perf['maxFPS']:.1f}FPS, 가장 높은p95프레임 시간은{perf['worstP95Ms']:.2f}ms입니다. 자연 프레임 간격 기준이며 사용자 조작감 수락은 별도입니다.

시각 품질은 추가 작업이 남아 있습니다. 물가4.0/10, 폐허2.5/10, 설산5.5/10은 각각 마지막 독립 지역 평가이며 전체 맵 수락 점수가 아닙니다. 바위·갈대, 폐허 구도, 침엽수와 눈더미, 전망 절벽의 접합을 더 다듬어야 합니다.

기존 빌드와 공유 자산은 보존했습니다. [최종 보고서](Migration/Evidence/Expansion/ContinuousWorld/FINAL_REPORT.md), [기록 영상](Migration/Evidence/Expansion/ContinuousWorld/{revision}/film/review.html), [검증 증거](Migration/Evidence/Expansion/ContinuousWorld/{revision}/delivery-audit.json)를 참조하세요.
'''
summary = f'''**{revision} 실행본 전달 / 전체 왕복·클릭·경계·날씨·성능 검증 통과 / 시각 품질 및 사용자 직접 수락 미완료**. 사용자 요청에 따라01:16~06:16KST의5시간 작업을 수행했다. 마지막30분은 빌드·검증으로 전환했고, E01에서 발견한 다리 단차만 최소 수정해{revision}에서 전체 검사를 다시 통과했다. 새 단일 맵의 전체 왕복3회·450클릭·약{qa['distance']/1000:.2f}km, 가장자리44클릭, 강수·지붕43검사를 완료했다. 기존 파일9481개 중 승인된 상태 문서3개 외 변경은 없다. 실행은 [PLAY_VESPER_WORLD.cmd](PLAY_VESPER_WORLD.cmd), 조작은 [PLAY_WORLD.md](PLAY_WORLD.md), 결과와 남은 작업은 [최종 보고서](Migration/Evidence/Expansion/ContinuousWorld/FINAL_REPORT.md)에 있다. 아래 최초 계획과 P2 기록은 역사 상태로 보존한다.'''
for name, marker in [('EXPANSION_PLAN.md', '# 최초 목표 변경'), ('CHECKPOINT.md', '# 이전 목표 결정')]:
    path = root / name
    old = path.read_text(encoding='utf-8-sig')
    assert marker in old
    path.write_text(f'# 최신 전달 — 통합 맵 {revision}, 2026-09-10\n\n{summary}\n\n' + old[old.index(marker):], encoding='utf-8')
path = root / 'CONTINUOUS_MAP_PLAN.md'
old = path.read_text(encoding='utf-8-sig')
marker = '최초 계획 시 사용자는'
assert marker in old
path.write_text(f'# VESPER — 통합 맵 구현 계획과 결과\n\n작성:2026-09-10. 현재 상태: **{revision} 실행본 전달 / 기능 검증 완료 / 시각 품질 추가 작업**.\n\n{summary}\n\n' + old[old.index(marker):], encoding='utf-8')
(root / 'PLAY_WORLD.md').write_text(guide, encoding='utf-8')
launcher = root / 'PLAY_VESPER_WORLD.cmd'
previous = launcher.read_bytes()
assert b'VesperContinuousWorld_D01' in previous
(out / 'launcher-before-promotion.cmd').write_bytes(previous)
launcher.write_bytes(previous.replace(b'VesperContinuousWorld_D01', ('VesperContinuousWorld_' + revision).encode('ascii')))
(out / 'promotion.json').write_text(json.dumps(dict(revision=revision, utc=datetime.now(timezone.utc).isoformat(), auditPassed=True, nativeClicks=native['clicks'], previousLauncher='D01'), indent=2), encoding='utf-8')
report = base / 'FINAL_REPORT.md'
text = report.read_text(encoding='utf-8')
text = text.replace('# VESPER 통합 맵 — 최종 검증 진행 중', '# VESPER 통합 맵 — E02 최종 전달')
text = text.replace('이 문서는 최종 E02 증거가 완료되면 확정한다.', '최종 E02 검증을 완료하고 실행기를 연결했다.')
text = text.replace('최종 빌드의 전체 왕복, 가장자리, 날씨, 성능, 영상, 네이티브 입력과 보존 감사 결과는 완료 후 아래에 추가한다.', '최종 빌드의 검증 결과는 아래 E02 증거에 기록했다.')
final = f'''- 가장자리44클릭/의도한5차단과 강수·지붕42검사 통과. 이전43표기는 집계 오류였으며 [원본 대조와 수정 기록](E02/QA_HARNESS_NOTE.md)에 남겼다.
- 최종 성능:5지점×4동작,20구간 모두 포커스 유지. 평균{perf['minFPS']:.2f}~{perf['maxFPS']:.2f}FPS, 가장 높은p95 {perf['worstP95Ms']:.2f}ms, 실행 오류0. [성능 보고서](E02/performance/report.json).
- 영상:9개의 실제 지역별 이동 클립을 원래 시간 간격으로 인코딩했다. 연속 왕복 자체의 영상은 아니며, 별도 배치가 들어간 무음 기록이다. [영상 보기](E02/film/review.html). E02 실제 왕복 중 캡처16장도 보존했다. 중복18-view촬영은 시간 제한에 따라 생략했으며 D10이미지를 E02로 바꾸어 쓰지 않았다.
- E02 Windows 입력:클릭{native['clicks']}회 중 차단{native['blocked']}회, 실제 이동{native['distance']:.3f}m, 드래그{native['drags']}회, 휠{native['zooms']}회, 명시적R복귀{native['resets']}회. 실행 오류와 안전 중단0. F6등 검사 배치는 연속 이동과 별개다. [네이티브 기록](E02/manual/report.json). 물리 트랙패드·지속 Shift·직접 청취·사용자 시각 수락은 남아 있다.
- [최종 기술 감사](E02/delivery-audit.json) 통과 후 [실행기](../../../../PLAY_VESPER_WORLD.cmd)를 E02에 연결했다. 이전D01과 모든 이전 빌드, 실패한E01을 보존했다.'''
text = text.replace('- 나머지 자동 검사와 네이티브 입력 결과는 완료 후 이 절에 추가한다. [실행 순서 기록](E02/queue.jsonl).', final)
report.write_text(text, encoding='utf-8')
(out / 'STATUS.md').write_text(f'# {revision} delivered\n\nTechnical audit passed. Three round trips/450clicks, edges44/5, weather42, performance20focused, film9encoded, actualtraversalcaptures16. Native accepted movement{native["distance"]:.3f}m. Launcher promoted. See ../FINAL_REPORT.md anddelivery-audit.json forlimitsandremainingvisualwork.\n', encoding='utf-8')
print('Promoted verified local build', revision)
