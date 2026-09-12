# L09 길 전환 — 실제 Unity 화면 비교

모든 이미지는1536×1024 Windows 실행본의 원본 캡처다. 왼쪽은L06 장면을 별도 재현한RoadBaseline, 오른쪽은L09. 같은 위치·기본 카메라를 사용했다. 생성한 목표 이미지는 이 표에 사용하지 않았다. 비와 캐릭터의 정지 애니메이션 위상은 촬영마다 다를 수 있다.

| 위치 | 이전 L06 장면 | 길 수정 L09 |
|---|---|---|
| 젖은 숲85m | ![이전 숲길](../RoadBaseline/capture/road-85.png) | ![L09 흙과 돌길](capture/road-85.png) |
| 비 구간 포장 변경126m | ![이전 갑작스러운 포장 변경](../RoadBaseline/capture/road-126.png) | ![L09 연속된 젖은 길](capture/road-126.png) |
| 서리 시작215m | ![이전 서리길](../RoadBaseline/capture/road-215.png) | ![L09 눈이 섞이는 길](capture/road-215.png) |
| 설산 전환234m | ![이전 좁아지는 포장](../RoadBaseline/capture/road-234.png) | ![L09 눈 사이에 남는 돌](capture/road-234.png) |
| 이전 길 끝238m | ![이전 잘린 길 끝](../RoadBaseline/capture/road-238.png) | ![L09 계속 이어지는 눈길](capture/road-238.png) |
| 눈길244m | ![이전 눈길](../RoadBaseline/capture/road-244.png) | ![L09 묻혀 가는 돌길](capture/road-244.png) |

원본16개와 정확한 캐릭터 좌표는 [촬영 기록](capture/report.json)에 있다. 이 정적 위치 배치 촬영은 실제 왕복 이동 검사와 별개다.
