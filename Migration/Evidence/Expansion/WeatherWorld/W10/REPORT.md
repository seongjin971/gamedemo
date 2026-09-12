# W10 — Q/E 전용 시점 회전

W09를 보존한 별도 장면·실행본이다. 이동 클릭의 작은 마우스 움직임이 시점 회전으로 해석되던 문제를 수정했다.

- Q를 누르면 왼쪽, E를 누르면 오른쪽으로 회전한다. 두 키를 함께 누르면 회전하지 않는다. 기존 회전 범위와 부드러운 움직임은 유지한다.
- 왼쪽 마우스 드래그는 각도를 바꾸지 않는다. 버튼을 놓은 지점을 이동 목적지로 처리한다. 상하 시점 각도는 고정한다.
- 휠 확대·축소, Shift 달리기를 유지한다. R은 시작점으로 복귀하며 선택한 시점 각도를 유지한다.
- 실제 게임 하단 안내를 `Q / E to orbit`으로 갱신했다.

실행: [PLAY_VESPER_WEATHER.cmd](../../../../../PLAY_VESPER_WEATHER.cmd) → W10,1920×1080 전체화면. 이전 W09는 [PLAY_VESPER_WEATHER_W09.cmd](../../../../../PLAY_VESPER_WEATHER_W09.cmd). W06/W05 실행기와 기존 OBS 설정도 보존한다.

## 실제 검증

빌드 오류0/경고0. 표시 상태의 Unity 실행본에서 입력·이동 확인 19개 PASS, 실행 오류0, 오디오0. 폐허 구간 클릭2회와 실제 이동 11.94m에서 마우스 드래그 후 이동 및 일반 클릭 이동 모두 각도 유지·도착·바닥 지지·충돌 여유를 확인했다. Q/E 회전, 동시 입력, 휠, R, 달리기 속도, 짝 없는 마우스 해제·비활성화 때 입력 취소·오른쪽 버튼 무시도 확인했다.

검사는 실제 네이티브 입력 폴링이 호출하는 동일 함수에 합성 입력을 넣어 수행했다. 물리 키보드·마우스 직접 조작이나 사용자 수락을 대신하지 않는다. 전체 이동 검사 묶음은 실행하지 않았다. [독립 검토](judge.md)도 별도로 남겼다. 조작 변경만 요청받았으므로 새로운 시각 목표 제작이나 Pro 이미지 일치도 반복은 진행하지 않았다.

[Q/E 안내·기본 화면](input-qa-visible/start-qe-help.png) · [Q 회전](input-qa-visible/q-left.png) · [E 회전](input-qa-visible/e-right.png) · [드래그 후 이동](input-qa-visible/drag-release-walk-fixed-angle.png) · [W09 강한 섬광 유지](input-qa-visible/w09-strong-flash-retained.png) · [설산 유지](input-qa-visible/snow-retained.png). 모두 실제 원본1920×1080 캡처다.

대표 성능은 비 숲·폐허·설산에서 각6초 보행 중 엔진 간격을 측정했다. 동시 게임/OBS 프로세스 없음, 새 녹화 품질 검증 없음. 이전 버전과 조건을 맞춘 성능 증감 비교는 아니다.

| 위치-동작 | FPS | p95 ms |
| --- | ---: | ---: |
| 150-walk | 61.99 | 20.02 |
| 198-walk | 51.76 | 20.06 |
| 323-walk | 61.29 | 17.02 |

처음 `input-qa/` 시도는 숨김 창 때문에 화면 캡처가 실패했다. 해당 실패 근거를 보존했고 숨김 상태 성능은 채택하지 않았다. 같은 빌드를 표시 상태로 실행한 `input-qa-visible/`이 최종 검증이다.

## 보존과 소스

보호 12,714파일 변경0, 공유 스킬 변경0. W09 장면과 W10 장면은 버전별 스크립트 GUID 연결 외에 직렬화 내용이 동일하다. 기존 충돌·Transform·내비게이션·재질·입자·지붕·섬광 설정을 유지했다. `.gitignore`와 `package-lock.json`도 그대로다.

공유 소스를 수정하지 않기 위해 W10 전용 런타임 이름공간에12파일을 복제하고 새 장면의 형식 참조를 연결했다. 동작 변경은 `WorldCamera.cs`, 안내 문구 변경은 `WorldEnvironment.cs`에 한정되며 다른 파일은 이름공간 외에 동일하다. 이전 파일/GUID/장면/빌드/근거는 보존했다.

최종 장면: `Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W10.unity`

최종 빌드: `Unity/Vesper/Builds/VesperWeatherWorld_W10/VesperLinear.exe`

정확한 소스: `W10/source/`, 수정 전 소스: `W10/before-source/`, 도구: `Migration/Source/Expansion/WeatherW10/`.
