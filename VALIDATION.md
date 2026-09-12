> Latest decision,2026-09-09: the user accepted candidate58 visual quality as sufficient. This is user acceptance of the current baseline, not a new independent score,60FPS pass or original-reference parity. The adventurer/environment [expansion plan](EXPANSION_PLAN.md) was reviewed and documented; implementation and new tests have not started. Existing technical measurements and historical observations below remain unchanged.

> Previous playable handoff for candidate58: build0errors/0warnings; static 43.45, walk 44.09, orbit 43.44, zoom 43.84 FPS. Automated motion 33.424m, errors0/skips0/all-focused. Direct input unavailable; not monitor-present FPS. Original reference target8/10 and60FPS unmet. Latest independent score remains52:6.1/Tier2. See Migration/Evidence/AtmosphereV2/player-58/VALIDATION.md and PLAY.md. Older records follow.

> Latest Unity candidate52: independent6.1/10 Tier2 (verdict-unity-8.md), target8 unmet. Build0errors/0warnings. DefaultD3D12 natural cadence49.88-50.72FPS misses60; no concurrent render/heavyQA, all-focused/0errors. Separate motion389frames/33.425m/9.648-10.660Hz,0errors/skips; all three near-root destinations reached, seven original frames directly inspected. This is not display-present FPS, direct pointer input, or final adoption. Structural source prototypes V16 are underway but not imported. See candidate-52/SELF_REVIEW.md and CHECKPOINT.md; below is historical evidence.

> 최신 저장 진단 candidate47: 실제4구도와 player 프레임 직접 검토. 새로운 점수는 없고 마지막 독립 심사는 candidate41의6.0/Tier2. TreeV12/MasonryV13/PavingV13/국소 그림자 통합, 오류0/누락0. 같은 D3D12 player47의 국소 그림자42.20–43.20FPS, 전체 메시28.51–28.73, 그림자 없음50.42–51.16. D3D11 별도 실행44.68–45.47. 빌드 오류0/경고0, 모든 FPS 실행 focused/오류0/다른 렌더·무거운 검증 없음.60 미달이며 표시장치 present/가림 증거가 아닙니다. 별도 motion396프레임/20.606m/9.97–11.20Hz/누락0/오류0; 뿌리 접근은 첫 목적지에서 검사기의 도착 오차 때문에 멈춰 전체 경로 확인은 미완료입니다. 영상과 직접 검토 한계는 candidate-47/SELF_REVIEW.md. native pipe 재확인도 실패하여 최신 직접 입력 미완료. 목표8/사용자 채택 미달, 계속 작업 중.

> Previous Unity candidate41: independent6.0/10 Tier2, visual target unmet. Build0errors/0warnings. Noninstrumented cadence54.55-55.35FPS misses60; no concurrent render/all-focused/0errors. Separate motion324frames,13.436m,10.04-11.19Hz. Orbit exposes broad silver paving glare; low views expose simple masonry. This is not display-present FPS, direct input, or user acceptance. See CHECKPOINT.md and Migration/Evidence/AtmosphereV2/candidate-41. Older records below are historical.

> 2026-09-09 재개: 사용자가 이전 중단 상태를 해제했습니다. 현재 Unity candidate36은 독립5.8/10 Tier2이며 목표8/10과 사용자 최종 채택은 미달입니다. 실제 캡처 오류0, player빌드 오류0/경고0. 비계측 자연 루프 static58.753/walk59.829/orbit59.909/zoom59.931FPS이며 all-focused/오류0/다른렌더 없음. 실제 표시장치 present FPS와 가림을 확인한 것은 아닙니다. 연속 동작318프레임/13.478m/약10.02–10.94Hz 기록과 직접 이미지 검토는 별도 증거입니다. 최신 직접 마우스/키보드 검증은 Windows native pipe 연결 오류로 미완료입니다. 현재 세부 상태와 다음 자산 접근은 CHECKPOINT.md, `Migration/Evidence/AtmosphereV2/candidate-36` 및 `verdict-unity-6.md`를 보세요. 아래 브라우저 검증/점수는 보존된 과거 기록으로 Unity 점수가 아닙니다.

﻿# 검증 결과 — 2026-09-08 후속 2차

최신 상태는 [CHECKPOINT.md](CHECKPOINT.md). **시각 6.5/10, 목표 8/10 미달. 1 FPS 원인은 창 노출/자동화 상태에 연동된 Chrome 프레임 생성 제한으로 분리했습니다.** 이전 문서의 과거 60 FPS와 1시간 종료 기록은 `.dream-loop/continuation-2/validation-before.md`에 보존했습니다. 과거 수치를 현 후보의 성능으로 재사용하지 않습니다.

16:00 KST 추가 진단: 최소 HTML의 rAF p50은 사용자 창 전면 전환 전 1000.3ms, 후 16.7ms였습니다. 앱 코드 변경 없이 원래 데모도 1440×709에서 60 FPS / 프레임 p95 17.1ms로 회복됐습니다. 이후 자동화 캡처에서는 20.3 FPS가 기록돼 창 노출 상태에 의존합니다. 내부 Chromium 추적은 하지 않았으며 Windows 창 가림 감지가 가장 유력합니다. 원래 1536×1024 최종 성능 검증을 완료했다는 뜻은 아닙니다. 상세 증거는 `.dream-loop/cadence-diagnosis/REPORT.md`. 아래 1 FPS 기록은 진단 전 측정입니다.

## 시각

기존 구도/목표를 유지하며 석재 v5, 나무 v6, 기사 v2와 생성 석재/수피/불꽃 텍스처, 반사·계단 조명·안개·룬·SMAA를 적용했습니다. 각 라운드 자기 검토 후 새 독립 심사를 실시했습니다. 점수는 **6.0 → 6.3 → 6.5/10**, 모두 Tier 2 통과입니다.

남은 차이: 규칙적이고 둥근 판석, 독립된 웅덩이와 선명한 반사 부족, 균일한 건축물 파손, 각진 나무 접합/끝가지, 원경 하단 불투명 경계, 구형 어깨와 약한 망토 주름, 넓고 밝은 불꽃 코어. 원문은 `.dream-loop/continuation-2/verdict-round-3.md`. 자동 점수는 사용자 시각 채택이 아닙니다.

## 최종 확인

연결된 Chrome, 1536×1024, pixelRatio 1.0.

| 확인 | 현 후보 결과 |
|---|---|
| 프로덕션 빌드 | 성공, 번들 크기 권고 경고 |
| 내비게이션 테스트 | 3개 통과 |
| 정지 처리량 | 95.33 frames/s, 180프레임 / 1888.20ms |
| 회전 처리량 | 86.28 frames/s, 180프레임 / 2086.20ms |
| 실제 rAF 계측 | 약 1 FPS, p50 약 1016ms |
| 클릭 이동 | 목표 도착, 경로 7 → 0개, 거리 2.613 |
| 지연 추적/회전/줌 | 위치·각도·줌 및 조작 카운터 변경 |
| 외부 이동 차단 | blockedCount 1, 영역 내 위치 유지 |
| 최종 앱 오류 | 캡처 errors 배열 0개 |

벤치마크는 10프레임 묶음마다 gl.finish()로 GPU 완료를 기다리며 이벤트 루프 양보 시간을 제외합니다. 실제 표시 FPS가 아닙니다. 일반 표시 GPU 타이머는 평균 약 46ms도 기록되어 처리량과 직접 일치하지 않습니다. 이를 근거로 60 FPS를 보장하지 않습니다.

visibility=visible, focused=true 상태에서도 약 1초 갱신이 지속됩니다. 원인을 창 가림 등으로 단정하지 않았습니다. 연속 보행·망토·불꽃·AO의 자연스러운 동작과 목표 표시 FPS는 미검증입니다. 개발 중 수정 전 오류까지 없었다는 뜻은 아닙니다.

## AO 자세 비교

V 키로 작은 회전, 1.8% 줌 변화, 0.075 단위 이동에서 캐시 재투영과 같은 자세/시간의 새 AO를 비교했습니다. 모든 경우 재투영 카운터가 증가했습니다.

| 변화 | 평균 RGB 차이 (0–255) | 최대 채널 차이 >16 픽셀 |
|---|---:|---:|
| 회전 | 0.3204 | 0.0353% |
| 이동 | 0.0426 | 0.0139% |
| 줌 | 0.3223 | 0.0366% |

국소 비교에서 넓게 늘어진 잔상은 발견하지 못했습니다. 임계치는 일반 품질 표준이 아니며 연속 동작 검증을 대체하지 않습니다.

## 증거

- `preview.png`: 최신 심사에 제출한 실제 렌더. 목표 이미지 아님.
- `.dream-loop/continuation-2/round-{1,2,3}.png`, `.json`: 라운드 화면/계측.
- 같은 폴더 `review-round-*.md`, `verdict-round-*.md`: 자기 검토/독립 평가.
- `round-3-benchmark-{static,orbit}.json`: 현 후보 처리량 원문.
- `final-controls/`: 1788849967880 이동 시작, 1788849990856 도착/추적, 1788850003917 회전/줌, 1788850017734 영역 밖 클릭 차단.
- `ao-proof/motion-proof-1788849933743-*`: 최종 AO 원본 6장, 계측, 8배 차이 영상, 분석 JSON.
- `assets-v5/`, `tree-assets-v6/`, `knight-assets/`: 로컬 Blender 소스·미리보기·형상 검사.
- `material-image-prompts.md`, `flame-image-prompt.md`: 생성 프롬프트. 생성 normal map은 실측 스캔 아님.

임시 외부 계정/서비스 데이터는 만들지 않았습니다. 기존 증거/자산을 보존했고 loopback 서버와 데모 탭은 사용자 확인용으로 유지합니다.
