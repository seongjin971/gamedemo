# Paving V11 heightfield 진단 소스

root의 별도 제작 승인 후 생성했다. Unity 통합 전 진단용이며 전체 장면 시각 통과를 뜻하지 않는다. Blender 렌더 6개를 직접 열어 V10과 같은 카메라로 비교했다. 현재 Blender 작업은 종료되었다.

**안정 JSON:** `paving-v11-mesh.json`  
SHA256: `6eca1cb9d1ce32764074f350de1ced3d43e197cb1db2308235deccf83640cb77`

| 검증 | 실제 결과 |
|---|---:|
| 삼각형 / 정점 | 155,742 / 78,686 |
| 면 cross·제공 normal 양수 | 155,742 |
| 음수 / 퇴화 면 / 과다 공유 edge | 0 / 0 / 0 |
| 면의 Y 방향 | 전부 위쪽 |
| unit normal 길이 | 0.999999892–1.000000111 |
| 독립 Pillow 높이 검증 | 6,053점, 최대 오차 8.25e-9m |
| UV 수식 최대 오차 | 6.53e-10 |
| V10 실제 XZ 외곽 bounds | 1nm 내 일치 |
| 원본 ZIP/맵·기존 V10 해시 | 모두 보존 |

`export-qa.json`과 `validate_heightfield.py`가 위 검증을 담는다. 독립 검사기는 Blender 이미지 읽기와 별개로 원본 16bit PNG를 Pillow로 읽어 V 반전/texel 중심/bilinear 반복을 검사했다. 실제 작동한 StoneV7 원본도 같은 검사기로 624 positive / 0 negative를 확인했다. 과거 V10의 잘못된 clockwise 판정은 재사용하지 않았다.

## 적용 계약

JSON은 `alreadyUnity=true`인 world-space identity mesh다. positions/normals는 xyz stride3, uv stride2, colors는 RGBA stride4이며 전부1이다. UInt32 index를 쓰고 추가 좌표 반사/삼각 순서 반전을 하지 않는다. 기존 V10 ground 메시 1개만 대체한다. 기존 계단·계단 lip·상부 landing 배치와 원본 선택 로직은 유지한다.

모든 채널은 `u=worldX/4.6`, `v=worldZ/2.3`를 공유한다. UV를 clamp하지 말고 repeat한다. 아트 배율은 원본2.3×1.15m의2.0배다. 행 offset, cutoff, 패치별 회전이 없다. Color는 sRGB, Roughness/Normal/Displacement는 비색상 데이터다. 재질 추가 UV배율은1, offset0으로 두어야 한다. 임의의 shader world좌표 배율을 덧씌우면 파손과 Color가 어긋난다.

높이는 `Y=-.0236+.040*(H-1)`로 계산했다. H는 원본16bit displacement의 반복 bilinear 샘플이다. **40mm는 아트 선택이며 실측 세로 범위가 아니다.** 장면별 최소/최대 정규화는 없다. 실제 격자 샘플은 원본의 최대값1을 정확히 밟지 않으므로 실제 Y범위는 **[-.059504466,-.024705101]**이다. -.0236은 상한이다. 독립 물 Y=-.004와 최소20.705mm 분리된다. 기존 V10 두께의 바닥값-.15676까지 채운 입체 석재가 아니라 얕은 열린 heightfield 표면이다. 측면·바닥은 생성하지 않았으며 경계 edge1628은 외곽/보존된 void의 정상 열린 경계다.

내보낸 normal은 변위 기하로부터 계산한 unit vertex normal이다. 4K NormalGL은 JSON normal에 구워 넣지 않았다. Blender textured preview에서는 별도의 tangent-space NormalGL strength0.45를 사용했다. Unity도 geometry normal을 기반으로 고해상도 normal detail을 별도 적용해야 한다. U는+X, V는+Z이므로 평평한 면에서 tangent+X, bitangent+Z, normal+Y이며 tangent handedness는-1이다. `RecalculateTangents`로 이를 만들거나 동일한 기준을 shader에서 구현한다. GL/DX 혼동으로 녹색 채널을 두 번 뒤집지 않는다. 최종 강도는 native 입사광 아래에서 확인하며 높이의 큰 경사를 중복 과장하지 않는다.

## 실제 범위와 계단

V10 실제 외곽 X **[-8.936228752,9.040660858]**, Z **[-11.101970673,21.067903519]**를 보존했다. 기존 front envelope X[-8.944121361,9.047286987], Z[-1.567998648,21.072914124]와 rear19개 row rectangle의 합집합을 실제 V10 외곽 AABB로만 clip했다. 따라서 원래 bevel 때문에 생긴 5–8mm 외곽 차이를 넓히지 않았다. 총 coverage492.30116m²이며 `heightfield-metadata.json`에 사각형20개의 정확한 좌표가 있다. 내부 줄눈은 흙을 포함한 연속 stonebed로 대체된다. 단순한 전체32×18m 사각형이 아니며 뒤쪽 중앙의 계단 void와 큰 누락 patch를 채우지 않았다.

원본 `unity-scene.json`에서 같은 floor material의 상승한 인스턴스를 별도로 확인했다. 가장 아래 계단은 native X[-6.35,.73], Z=-1.71, Y=.297 부근이며 다음 표면들은 Z=-1.496, Y=.306–.315다. Front ground가 Z=-1.568부터 시작하므로 **최하단 계단 nose 아래 일부 XZ 투영 영역은 원래처럼 ground와 겹친다.** 이는 낮은 ground를 기존처럼 유지한 결과이며 계단 표면 대체가 아니다. 뒤쪽 상부 landing의 인스턴스 중심은 native X[-6.835,1.22], Z[-9.48,-6.20], Y=2.83이다. 이들 50개와 상승 계단은 원래 y<.2 선택 밖이며 V11에 포함하지 않았다. 뒷 row 마스크의 양옆 stonebed가 구조물의 외곽 아래에 일부 겹치는 기존 상태도 유지한다.

기본 균일 격자 간격은88mm이며 coverage 경계의 정확한 X/Z 좌표를 추가했다. 이 경계 보강으로 몇몇 좁은 삼각형은 존재하지만 면적>7.13e-8m², 정방향/정상 법선이며 퇴화면은 없다. height 변화가 동일한 연속 함수이므로 경계에서 UV/변위 phase가 뛰지 않는다.

## 직접 시각 검사

`previews/before-v10-neutral-{full,close}.png`, `after-v11-neutral-{full,close}.png`, `after-v11-textured-{full,close}.png`는 동일 조명/카메라다. Textured preview는 실제 내려받은4K Color/Roughness/NormalGL을 사용했다. V10은 깨끗하고 긴 검은 줄눈이 형태를 지배했다. V11 textured close에서는 돌 내부 큰 파손, 작은 부스러기, 폭이 다른 모래/흙 채움, 광물결이 함께 읽힌다. Source상 마모 패턴과 지형/UV가 일치한다.

한계도 분명하다. 중성 기하만 보면40mm 높이차가 아주 부드럽고 얕게 읽힌다. 88mm 격자는 작은 칩의 실제 기하를 모두 담지 못하므로 미세 경계는 normal/color에 의존한다. 원본의 얇은 수평 띠가 전체 바닥에 반복되고, 소스 고유의 건조 황색이 그대로 보인다. 이 첫 연속UV 검증에서는 반복이나 최종 장면 색을 해결했다고 주장하지 않는다. 물·반사·야간 노출을 넣은 native 진단이 다음 판단 근거다. 새 meshes/maps를 준비한 사실만으로 verdict6의 바닥/물 blocker가 해결된 것은 아니다.

## 재현

`build_heightfield_v11.py`를 Blender5.2.1 background, threads6으로 실행하면 현재 JSON, metadata, authored blend 및 같은 카메라6개 렌더가 나온다. `validate_heightfield.py`는 일반 Python+Pillow로 실행한다. 배포 원본 `maps/Tiles130_4K-PNG.blend`는 실행하지 않았다. 우리의 저작 scene은 `paving-v11.blend`다. `build.log`에는 Blender의 재질 API deprecation warning과 함께6개 렌더 저장, blend 저장, BUILD_DONE 및 Blender quit이 기록돼 있다. Unity 소스/장면/기존 V10에는 쓰지 않았다.
