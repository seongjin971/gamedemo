# Paving V11 촬영 자산 조사 완료

2026-09-09 KST. 이 문서는 자산 조사 단계 기록이다. 이후 root가 별도로 heightfield 제작을 승인했으며 결과는 BUILD_REPORT.md에 기록한다.

선정은 **ambientCG Tiles130 한 종**이다. [공식 자산 페이지](https://ambientcg.com/view?id=Tiles130)는 Surface Photogrammetry와 약 **2.3 × 1.15m** 범위를 명시한다. API의 `PBRPhotogrammetry`는 촬영으로 displacement를 얻었다는 뜻이다. [제작 방식 설명](https://docs.ambientcg.com/creation-methods/)과 [공식 API 문서](https://docs.ambientcg.com/api/v2/full_json/)를 확인했다. 원본 4K PNG ZIP 한 종을 API가 반환한 주소로 내려받고 그대로 보존했다.

`maps/`에는 원본 Color, 16bit NormalGL/NormalDX, Roughness, 16bit Displacement와 배포 ZIP의 AO 및 재질 파일이 있다. 배포된 blend는 제공자 원본이며 실행하지 않았다. **원본 픽셀은 수정하지 않았다.** `manifest.json`은 파일별 SHA256, 크기, PNG 비트 수, 요청/최종 URL, UTC 다운로드 시각을 담는다. 121,594,785바이트 ZIP은 공식 API 크기와 일치하며 ZIP CRC를 검사했다. 제공자 해시는 API에 없어 독립적인 제공자 SHA 검증을 주장하지 않는다.

CC0 1.0이며 상업 사용과 원본 재배포가 허용되고 크레딧은 선택 사항이다. ambientCG는 자산 미리보기 렌더에도 동일한 CC0를 적용한다. [공식 라이선스](https://docs.ambientcg.com/license/). 원본과 라이선스/제작 방식 페이지 스냅샷은 `source/`에 있다. Poly Haven 조사용 렌더/현장 사진은 별도 사이트 콘텐츠이므로 이를 CC0 게임 자산으로 간주하지 않는다.

직접 본 자료: `Migration/Reference/concept.png`, candidate-36의 `full.png`와 `zoom.png`, `verdict-unity-6.md`; 공식 후보 21종의 렌더; 유력 후보 3종의 실제 상면 맵; 선정 자산의 내려받은 4K Color/NormalGL/Roughness/Displacement. 원본 네 맵은 `preview.html`에서 나란히 확인할 수 있다. 작은 구체 렌더만으로 선정하지 않았다.

| 후보 | 직접 관찰한 적합성 | 결정 |
|---|---|---|
| ambientCG Tiles130 | 큰 불균일 직사각 판석, 일부 큰 관통 파손, 표면 광물결, 폭이 달라지는 흙/파편 메움 | 선정 |
| Poly Haven Monastery Stone Floor | 마모와 퇴적물은 좋으나 상면에서 삼각/다각형 비중이 높음 | 제외 |
| Poly Haven Cobblestone Floor06 | 찌그러진 직사각과 자연 틈이 좋으나 작은 cobble의 밀도가 높음 | 제외 |
| SlateFloor02/03, StoneTiles02, SlateDriveway, SlabTiles | 불규칙 모자이크 또는 넓고 반질한 판석 | 제외 |
| PatternedSlateTiles, MixedRockTiles | 얇은 반복 띠 또는 장식 자갈 줄눈 | 제외 |
| CastleWallVariation, MedievalBlocks03 | 벽재의 돌출/규칙적 적층 | 제외 |
| ambientCG PavingStones142/149/148/141/144/034, Tiles138/027, PH CobblestoneFloor08 | 작은 cobble·둥근 자갈·혼합 장식 패턴·현대 타일의 반복 중 하나가 우세 | 제외 |

Tiles130의 장점은 흙으로 메워진 접합부와 파손이 Color/Height/Normal에 함께 존재한다는 점이다. candidate36의 길고 검은 반복 틈에 미세 잡음을 더하는 방식과 다른 소스다. 다만 **원본에도 긴 수평 코스와 중앙의 가는 띠가 있다. 그대로 작은 크기로 반복하면 줄 반복 문제가 다시 생길 수 있다.** 건조한 황록색 역시 concept의 차가운 젖은 회색과 다르다. 선정은 후속 native 검증용 소스 준비이며 최종 외관 채택 판정이 아니다.

후속 제작 계약은 원본 측정치와 아트 배율을 구분한다. 원본은 2.3 × 1.15m, 승인된 장면 배율은 2.0이므로 4.6 × 2.3m 주기로 적용한다. 큰 석재는 사진상 약 0.3–0.5m에서 장면상 약 0.6–1.0m로 읽힐 것으로 추정한다. 이 값은 사진을 통한 대략적 추정이며 개별 돌 실측은 아니다. 높이맵은 0–65535이고 API `dimensionZ=0`이다. 제공자 mtlx의 scale=1은 물리적 1m 측정 증거가 아니므로 세로 변위는 별도 **아트 선택 40mm**로 명시한다. 장면 전체의 샘플 최솟값/최댓값으로 다시 정규화하지 않는다.

기하와 모든 재질 맵에 같은 연속 world-XZ→UV를 적용한다. 행별 UV offset, 구간 cutoff, 무작위 패치 회전은 쓰지 않는다. 그래야 촬영한 경사/파손과 Color의 접합부가 일치한다. 반복 완화는 이 첫 검증에서 해결됐다고 주장하지 않으며, 먼저 실제 4K 소스와 지형의 일치를 확인한다.

기존 최고 석재 Y≈-0.02365보다 독립 수면 Y=-0.004가 약19.65mm 높다. root가 확인한 현 상태에 따르면 검은 틈은 수면의 Z 가림 때문이 아니다. V11 지형 최고 상한 -0.0236과 독립 수면 -.004를 유지한다. 촬영된 흙메움 높이를 그대로 포함하는 연속 stonebed가 필요하며 모든 줄눈을 인위적인 깊은 구멍으로 뚫지 않는다. 후속 수면 검증은 줄눈 2개 이상을 가로지르는 불규칙 웅덩이 3–5개, 수면 아래 은은한 틈, 얕고 연속된 불 반사, 젖은 돌과 독립 물의 차이를 따로 본다. 수면을 돌의 높이맵으로 변위시키지 않는다. 물 통합은 root 담당이다.

조사 완료 시 기존 V10 mesh SHA256 `e9dace2039a9fb50ce028aa3b7cbff1f06893421dfa2d896e19c38f48d34c240`가 전달본과 일치했다. `qa.json`에 원본/기존 증거 해시와 실제 맵 decode 검사가 있다. 이 문서 작성 시 Unity 수정/통합은 없었다.
