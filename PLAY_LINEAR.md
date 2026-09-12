# VESPER 직선형 기후 산책 — L06

[PLAY_VESPER_LINEAR.cmd](PLAY_VESPER_LINEAR.cmd)를 실행한다. Windows 창 모드1536×1024, Direct3D12. 기존 E02 실행기는 `PLAY_VESPER_WORLD.cmd`, F01 실행기는 `PLAY_VESPER_WORLD_F01.cmd`로 유지된다.

물가 다리 → 젖은 숲 → 비 오는 폐허 → 서리 오르막 → 설산 순서로 약300m의 한 길을 걷는다. 화면의 길 앞쪽을 클릭하면서 진행한다. 기본 시점에서는 대체로 오른쪽 위가 진행 방향이다. 이동 중 비·눈·빛·안개가 위치에 따라 이어서 바뀐다. 휴식 없이 걷는 이론 시간은 약2분14초이며, 클릭과 구경 시간은 별도다.

| 조작 | 동작 |
| --- | --- |
| 왼쪽 클릭 | 클릭한 바닥까지 이동 |
| 왼쪽 버튼 드래그 | 시점 회전 |
| 마우스 휠 | 확대·축소 |
| Shift 누르기 | 이동 중 달리기 |
| R | 시작 위치와 기본 시점으로 돌아가기 |
| 창 닫기 / Alt+F4 | 종료 |

음향은 넣지 않았다. 사용자가 별도로 제작할 예정이다.

주요 풍경 위치는 다리25m, 숲85m, 폐허150m, 서리215m, 설산275m다. 설산에서는 돌 포장이 눈 아래로 사라지고 다져진 눈길이 이어진다. 이번 버전은 직진하며 풍경의 변화를 보는 검토용 실행본이다.

장면: `Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperLinearWorld_L06.unity`. 새 코드와 자산은 `Unity/Vesper/Assets/Vesper/Expansion/LinearWorld`, 이전 후보와 증거는 각각의 버전 경로에 남아 있다.

검증 결과와 남은 시각 차이는 [작업 보고서](Migration/Evidence/Expansion/LinearWorld/FINAL_REPORT.md)에 기록한다. 생성한 목표 이미지와 동일한 완성도나 사용자 최종 수락을 뜻하지 않는다.
