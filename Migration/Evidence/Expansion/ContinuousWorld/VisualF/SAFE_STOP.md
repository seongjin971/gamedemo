# Visual F 안전 정지 — 2026-09-10 20:55 KST

사용자가 이동을 위해 안전 종료를 요청하여 구현을 중단했다. **F01은 실행 가능한 시각 중간 후보, F02는 미컴파일/미빌드 소스**다. 시각 품질 완료와 사용자 수락은 미달/미확인이다.

## 실행과 현재 상태

- 기존 실행: [PLAY_VESPER_WORLD.cmd](../../../../../PLAY_VESPER_WORLD.cmd) → 보존된 E02.
- 새 중간 후보: [PLAY_VESPER_WORLD_F01.cmd](../../../../../PLAY_VESPER_WORLD_F01.cmd) → `Unity/Vesper/Builds/VesperContinuousWorld_F01/VesperWorld.exe`.
- F01 장면: `Assets/Vesper/Scenes/Expansion/VesperContinuousWorld_F01.unity`.
- 종료 확인 시 Unity/Blender/Vesper 프로세스 없음. 자체 제출 Higgsfield 작업 완료/원본 다운로드 완료. 두 독립 평가자 종료.
- Git 리셋/스태시/정리/커밋 없음. .gitignore/package-lock.json 변경 없음.

## 적용한 스킬과 제작 범위

실제 설치된 `C:/Users/brian/.codex/skills/dream-loop/SKILL.md`가 연결하는 `references/pro-mode/workflow.md`를 읽고 적용했다. 별도 dream-loop-pro 폴더는 없지만 실제 Pro 문서가 설치되어 있다. 자산 조달 문서 assets-3d.md도 읽었다. 기존 세 시안을 그대로 유지하고 실제 Unity 캡처와 새 독립 평가를 사용했다.

이번 요청이 과거 이동 우선 지시와 종료된 5시간 제한을 대체한다. 착수 때 전체 왕복/450클릭/경계/날씨 묶음을 다시 실행하지 않았다. E02 원본 날씨 검사42개와 기존 최종 감사 통과를 확인했다.

## F01에서 구현한 것

- 폐허 도로 중앙을 166~198m에서 정렬하고 양끝을 기존 길과 완만하게 연결.
- 도로를 향하는 입구 아치, 위치가 맞는 지붕과 하부 프레임, 지면부터 이어지는 후면 벽으로 구조 재배치. 지붕의 강수 차단 범위도 새 지붕 위치에 맞춤.
- 전망 공간의 대칭적인 큰 바위와 얇은 받침을 제거하고 지형에 묻힌 비대칭 암반 배치.
- 전망 지형 세분화, 전역 높이 함수로 이웃 지형 조각의 법선 일치, 유기적인 절벽 가장자리 및 별도 삼면 투영 지면 셰이더.
- 생성기가 F 버전마다 별도 장면과 Generated/버전 자산을 만들도록 수정. Unity 장면/YAML 직접 편집 없음.

## 실제 Unity 전후와 독립 평가

모두1536×1024 런타임 원본 PNG다. 순간 배치 정적 촬영이며 연속 이동 증거가 아니다. 기존 캡처 모드의 fixturePlacements 카운터0은 실제 배치가 없다는 뜻이 아니므로 해당 카운터로 이동을 주장하지 않는다.

| 지역 | E02 이번 촬영 | F01 | 이번 E02 평가 → F01 평가 |
| --- | --- | --- | --- |
| 물가 | [전](before-E02/hero-water-45-zoom8_2.png) | [후](../F01/capture/hero-water-45-zoom8_2.png) | 5.45 → 5.45 |
| 폐허 기본 시점 | [전](before-E02/view-180.png) | [후](../F01/capture/view-180.png) | 5.80 → 6.15 |
| 설산342m | [전](before-E02/view-342.png) | [후](../F01/capture/view-342.png) | 7.90 → 7.90 |
| 전망375m | [전](before-E02/view-375.png) | [후](../F01/capture/view-375.png) | 별도 형태 미달 |
| 물가→폐허 연결 | [전](before-E02/view-120.png) | [후](../F01/capture/view-120.png) | 식생·공간 반복 남음 |
| 폐허→설산 연결 | [전](before-E02/view-265.png) | [후](../F01/capture/view-265.png) | 회색 길·큰 바위 반복 남음 |

각 폴더에 기본/인접 시점18장이 있다. [새 기준 평가](baseline-judge.md), [F01 독립 평가](F01-judge.md). D10/D09/D08 과거 점수는 재사용하지 않았다. 설산342 점수를 전망 공간이나 전체 맵 점수로 확장하지 않는다.

**남은 큰 문제:** 폐허의 작은 규칙적 석판, 얇고 회색인 잔해, 평평한 밝은 반사 얼룩. 물가의 반복 바위, 가느다란 갈대, 불투명한 얕은 물과 다리 접속부. 설산의 평면 가지와 덩어리진 눈. 전망 공간은 직선 이음이 덜 기계적으로 보이지만 매끈한 절벽 면이 더 드러난 국소 퇴행이 있다. 먼 전망도 미해결이다.

## 최소 확인과 보존

- [F01 준비](../F01/prepare.json): 12개 경로 연결, 누락 스크립트0. 연결 계산이며 실제 이동 통과가 아니다.
- [F01 빌드](../F01/build.json): 성공, 오류0/경고0,36.13초.
- [F01 정적 촬영](../F01/capture/report.json):18장, 런타임 오류0. E02도 이번 별도 경로에서18장 촬영.
- F01 변경 구간 실제 이동, 새 지붕의 차단 검증, 대표 성능, 사용자 직접 플레이/시각 수락은 **미실시**. 안전 정지 때문에 최종 검사 전 중단했다.
- 이번 별도 보존 기준 [24,061개 파일](preservation-baseline-20260910.json). 원래 protection-before.json을 재생성하지 않았다.
- [안전 종료 시 제한 감사](safe-stop-preservation.json): E02 Windows 빌드 전체, 기존 통합 장면, 런타임, 기존 실행기, .gitignore, package-lock.json, 원래 보존 기준 등207개 검사. 승인된 WorldLayout.cs 수정 외 위반0. 전체24,061개 종료 후 재해시는 재개 시 남는다.
- F01의 prepare-source/build-source가 당시 소스를 보존한다. **현재 작업 소스는 작성 중인 F02를 포함하므로 F01 실행본 소스와 동일하다고 주장하지 않는다.**

## 작성 중 F02 — 채택하지 않은 후보

현재 `Editor/WorldVisualF.cs`에 F01 외 버전용 분기와 `Editor/WorldVisualFDetail.cs`가 추가되어 있다. `VisualFRiver.shader`, `VisualFWetStone.shader`도 새 파일이다. 마지막 수정 후 Unity를 실행하지 않았으므로 컴파일/임포트 미확인이다. [정지 시 소스 해시](F02-uncompiled-source-manifest.json).

Blender 원본/FBX는 `Migration/Source/Expansion/ContinuousWorld/VisualF/` 아래:
- `FirVolume/`: 작은 가지 묶음 침엽수2종, 각 약27.8k삼각형. 기존 생성 가지 텍스처 재사용, Unity 미채택.
- `DetailAssets/`: 큰 불규칙 석판3종, 굵기/휘어짐을 늘린 갈대. Unity 미채택.
- 생성 코드 `generate_fir_volume.py`, `generate_detail_assets.py`, 파생 갈대 생성 코드와 manifest 보존.
- F02 코드에는 자산 가져오기, 새 석판 길/폐허 바닥, 물가 바위 비율/갈대/수중 돌, 침엽수 교체와 절벽 암반 추가가 작성됐다. 실행 효과는 아직 확인하지 않았다.

## Higgsfield 기록

- 시작잔액2421.5, 종료조회2378.0, 잔액 차이43.5.
- 이 작업에서 제출한 생성은 **1건**: `3e65cfe6-9a44-4e95-aa7e-2b9929ebc732`, GPT Image2 요청,2K/high 석회암 albedo. 비용 사전견적6.5크레딧. 잔액차43.5 전체를 이 생성 비용으로 귀속할 수 없으며 차액37의 원인은 확인하지 않았다.
- 원본 `VisualF/LimestoneFineF.png`, 정확한 프롬프트와 제출/완료 메타데이터 `limestone-submission.json`, `limestone-job-current.json`, URL/해시 `limestone-download.json`.
- 원본 이미지 픽셀 수정 없음. Unity 가져오기/화면 비교/채택 전이다. 생성 완료를 시각 개선으로 계산하지 않는다. 충전/구독 변경 없음.

## 바로 재개하는 순서

1. 루트 최신 상태 문서 → 이 보고 → `.dream-loop/continuous-world/VisualF/CHECKPOINT.md` 순으로 읽는다. 옛 `.dream-loop/continuous-world/LATEST.md`의 큐/시간 제한은 폐기된 역사 상태다.
2. Git/실행 프로세스와 새 Pro 설치 문서를 확인하고 기존 E02/F01·이전 결과를 보존한다. `apply_f01.py`, `safe_stop.py`, `preserve.py before`는 이미 실행했으므로 다시 실행하지 않는다.
3. 작성 중 F02 C#/셰이더와 Blender 자산/생성 텍스처를 먼저 검토한다. 필요 수정 후 고유한 F02 경로에서 prepare/build. 기본 실행기를 옮기지 않는다.
4. 실제 Unity 기본/인접/연결부 화면으로 비교하고 새 독립 Pro 평가를 받는다. 반복되는 석판/물가/절벽 문제는 수치 조정 대신 큰 구조로 해결한다.
5. 최종 맵 구성이 안정된 후 변경된 물가 접속부·폐허 길/입구/지붕·전망 지형의 최소 이동 확인과 대표 성능 측정. 전체 검사는 회귀 근거가 있을 때만.
6. 8점/FPS 등의 자동 종료 기준과 사용자 최종 수락을 구분하고, 미달이나 정체는 솔직하게 남긴다. 이 안전 정지는 사용자의 명시적 중단이며 Pro 기준 달성을 의미하지 않는다.
