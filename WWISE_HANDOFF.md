# Wwise W11 작업 인계

기준: `main`의 `8fc50948e7725cd54ff14159beb0137b52a6589f`, Weather World W10.
작업 브랜치: `feat/wwise-w11`.

**W11 장면·프로필 생성과 Unity Play Mode 상태 검사 42개를 완료했습니다. 실제 음향이 연결된 플레이 빌드는 아직 아닙니다.**
W10 소스·장면·공유 자산·WAV 원본은 수정하지 않았습니다.

## 작성한 코드

Unity 프로젝트의 `Assets/Vesper/Expansion/WeatherW11/`에 있습니다.

- `WorldAudioState`: 바닥, 지역, 연출 시간, 비 강도 계산. R 복귀 시 지역 상태 즉시 초기화.
- `SurfaceAudioTag`: 다리 등 지정 콜라이더의 바닥 재질. 태그 우선 → 눈 덮임 → 설정된 석재 구간 → 비 구간 진흙 → 기본 자갈 순으로 판정.
- `WorldAudioProfile`: 시간 키, 지역 경계·여유 폭, 바닥 구역, 발 디딤 시점, Bank/Event 이름을 Inspector에서 편집.
- `WorldFootsteps`: 기존 W10 보행·달리기 진행도를 이용하는 발 디딤 신호. 정지·접지 해제·R 복귀 때 가짜 발소리 억제.
- `WwiseAudioBridge`: 초기화와 Bank 로딩 이후 상태를 보내고 환경음/호수 이벤트를 한 번 시작. 발소리 Switch와 Event는 같은 캐릭터 음원 오브젝트에 적용. 비활성화 시 해당 음원만 정지하고 직접 로딩한 Bank만 해제.
- `WorldAudioListener`: 캐릭터 위치와 카메라 방향을 따름. 줌으로 캐릭터-호수 거리가 바뀌지 않음.
- `WorldAudioDebug`: Editor/Development Build에서 상태와 이벤트·오류 수 표시.
- `WeatherW11Setup`: W10을 복사해 W11 참조를 연결하는 메뉴, 발 접촉 시점 샘플링, SDK 활성화, Windows 빌드. SDK/Bank가 없는 W11 사운드 빌드는 중단.
- `WeatherW11StateProbe`: 명시적인 배치 옵션으로만 실행하는 Editor 검사. 실제 장면·NavMesh·애니메이션을 사용해 지면/RTPC/지역/청취 위치와 보행·달리기 접촉 신호를 검사하고 JSON을 기록.

SDK를 설치하기 전에는 `VESPER_WWISE` 심볼을 설정하지 않습니다. 이 상태는 상태값 미리보기이며 Unity AudioSource로 대체 재생하지 않습니다. SDK 코드에는 `AkUnitySoundEngine` API를 사용하며, 실제 설치한 Integration에서의 컴파일 검증은 남아 있습니다.

## 기본 매핑과 조정할 값

| 프로토콜 | 기본 구현 |
| --- | --- |
| `SurfaceType` Switch | `Mud / Gravel / Snow / Rock`. `Mud`에 `footstep wet`을 연결하는 제안이며 청음 확인 필요. concrete 원본은 별도 라이브러리로 가져옴 |
| `TimeOfDay` RTPC | 0~24. 진행 거리 0/55/112/168/238/303m에 8/17/20/21/22/23시를 지정한 **음향용 연출 시간**. 게임 시계가 아님. 키 사이 부드러운 보간, 자정 이후는 25처럼 입력 가능 |
| `RainIntensity` RTPC | 기존 `WorldLayout.Weights(progress).y`, 0~1. 지붕 아래에서도 날씨 강도 자체를 유지 |
| `Area` State | 270.5m 기준 Forest/SnowMountain, 왕복 시 2m 여유 폭으로 경계 반복 전환 억제 |
| Lake | W10 다리의 위치를 확인해 `(0, -0.55, -25)`에 별도 음원 배치. Wwise 3D/Attenuation 설정 필요 |

혼합된 길의 바닥 분류는 편집 가능한 구역 기반 근사입니다. 셰이더의 개별 돌·진흙 픽셀을 읽는 구현은 아닙니다. 플레이하며 구역을 보정하거나 콜라이더 태그를 추가합니다.

## 검증한 것과 환경 제약

- 엔진 독립 C# 검사 **40개 통과**: 시간 보간·자정, 지역 왕복, 15/30/60/144 FPS의 발 디딤, 정지·접지 해제·복귀.
- Python authoring 계획 검사 **6개 통과**: WAV 76개 중복·누락 없음, SHA-256 일치, Switch 이름, RTPC 범위, Bank 이벤트 포함, 시간 곡선의 자정 연속성.
- Unity 6000.5.7f1의 실제 참조 DLL과 배포 템플릿의 URP DLL을 사용해 새 코드와 W10 의존 소스 **18개를 SDK 비활성 상태로 컴파일**, 경고를 오류로 처리하여 통과.
- Unity Personal 활성화 이후 실제 프로젝트 가져오기와 컴파일, W11 장면·프로필 생성, 참조 검사 완료. `PrepareBatch` 종료 코드 0. W10 장면에 268줄을 추가한 W11을 별도 저장했고 기존 장면 내용은 유지했습니다.
- 실제 클립 최저 발 높이를 샘플링한 좌/우 접촉 위상: 걷기 `0.325 / 0.841667`, 달리기 `0.391667 / 0.883333`. 프로필에 저장했으며 최종 청음·시각 조정은 남아 있습니다.
- **Unity Editor Play Mode 검사 42개 통과, 오류 0, 종료 코드 0.** 자갈/다리 석재/진흙/수도원 석재/눈 지면, RTPC 범위·비 전환, 지역 왕복 여유 폭, R 초기화, 줌·회전 시 청취 위치, 실제 걷기/달리기와 정지 접촉 신호를 확인했습니다. 보고서: [Audio/unity-state-validation.json](Audio/unity-state-validation.json).
- 이 검사는 `-nographics`와 고정 60Hz 시뮬레이션 간격을 사용합니다. 화면·성능·청음 검증은 아닙니다. 초기 배치에서는 프레임 간격이 너무 짧아 기존 모터의 첫 이동량이 부동소수점 정밀도 아래로 내려갔고, 검사 시간 간격을 고정해 해소했습니다. Editor 검색 인덱스 초기화와 Play Mode 진입의 충돌도 시작 지연으로 해소했습니다.
- Wwise Authoring/Unity Integration이 설치돼 있지 않으며 공식 다운로드 페이지 요청은 HTTP 403. SDK 호환성 확정, `.wproj` 작성, authoring 적용, SoundBank 생성, 실제 음향·Windows 빌드 검증은 미완료입니다.
- `/tmp/vesper-waapi-env`에 공식 `waapi-client 0.8`을 설치했습니다. 실행 중인 Wwise에 연결하거나 authoring 계획을 적용한 상태는 아닙니다.
- 현재 GitHub 계정은 원본 저장소에 READ 권한입니다. 로컬 변경이며 원격 업로드하지 않았습니다.

## 활성화 이후 재개 순서

1. Unity 라이선스 활성화는 완료됐습니다. 프로젝트 버전은 **6000.5.7f1**을 유지합니다.
2. **현재 필요한 단계:** Mac용 Audiokinetic Launcher를 다운로드·설치하고 로그인합니다. 이 Unity 버전과 호환되는 Wwise Authoring/Unity Integration을 설치합니다. 호환성을 확인하기 전 엔진이나 기존 자산을 내리지 않습니다. Mac 편집기용 및 Windows 대상 플랫폼 라이브러리가 필요합니다.
3. Unity에서 `Unity/Vesper`를 열고 `Vesper > W11 Audio > 1 Prepare or Open Scene`을 실행합니다. 이미 생성된 `VesperWeatherWorld_W11.unity`와 `W11AudioProfile.asset`을 열어 확인합니다.
4. 사용할 새 Wwise 프로젝트를 만들고 엽니다. 아래 계획을 확인한 후 해당 프로젝트에 authoring 가져오기를 적용합니다. 기존 프로젝트라면 중복된 프로토콜 이름을 먼저 조정해야 하며 도구는 기존 항목을 덮어쓰지 않습니다.
5. authoring 계획의 `authoring_required`를 완료합니다. 현재 도구는 구조·음원·게임 싱크·이벤트·Bank 포함 관계를 만들며, **RTPC 음량 곡선, 지역 Continuous 전환/크로스페이드, 호수 3D 감쇠, 자연음 랜덤 재생·청음 조정은 별도 작업**입니다. 천둥 원본은 라이브러리에만 포함하며 시각 섬광 동기화를 구현하기 전 자동 재생하지 않습니다.
6. Mac/Windows SoundBank를 생성합니다. 기본 프로젝트 설정에 맞춰 모든 `.bnk`·`.wem`·메타데이터를 `Assets/StreamingAssets/Audio/GeneratedSoundBanks/<platform>/`에 포함하고 Integration의 Bank base path를 일치시킵니다. 본 도구는 Bank를 생성하지 않습니다.
7. Unity의 `2 Enable Wwise SDK` 실행 → 컴파일 종료 → `3 Connect Wwise Components`. `Init.bnk`와 `Vesper_W11.bnk`가 로딩되고 테스트 음원이 재생되는지 확인합니다.
8. Wwise Profiler와 실제 청음으로 값/이벤트/위치 검증. 발 디딤은 자동 최저 높이 샘플링의 결과이므로 걷기·달리기 전환을 보며 조정합니다. 필요하면 `Recalibrate Foot Contacts` 메뉴를 사용합니다.
9. Windows Build Support를 설치한 환경에서 `4 Build Windows Player`. 결과는 `Builds/VesperWeatherWorld_W11/VesperAudio.exe`. 기존 기본 Build Scene List는 변경하지 않습니다.

## 도구 실행

저장소 루트에서 실행합니다.

```sh
# 로컬 파일만 읽어 가져오기 계획과 76개 음원 매핑 작성
python3 Tools/prepare_wwise.py

# Wwise가 준비된 이후에만: 가상환경에 공식 waapi-client 설치,
# Wwise Preferences에서 WAAPI 활성화, 명시한 프로젝트를 열어 둠
python3 -m venv /tmp/vesper-waapi-env
/tmp/vesper-waapi-env/bin/pip install waapi-client
/tmp/vesper-waapi-env/bin/python Tools/prepare_wwise.py --apply --project /absolute/path/VesperAudio.wproj

# 현재 통과한 검사 재실행 (macOS)
python3 Tools/test_audio_model.py --unity-contents '/Applications/Unity/Hub/Editor/6000.5.7f1/Unity.app/Contents'
python3 Tools/check_audio_compile.py --unity-contents '/Applications/Unity/Hub/Editor/6000.5.7f1/Unity.app/Contents'
python3 -m unittest discover -s Tools/tests -p 'test_*.py' -v

# Unity를 닫고 저장소 루트에서 실행: 실제 W11 Play Mode 상태 검증
'/Applications/Unity/Hub/Editor/6000.5.7f1/Unity.app/Contents/MacOS/Unity' \
  -batchmode -nographics -projectPath "$PWD/Unity/Vesper" \
  -executeMethod Vesper.Expansion.WeatherW11.Editor.WeatherW11Setup.ValidateStateBatch \
  -w11StateQA "$PWD/Audio/unity-state-validation.json" \
  -logFile /tmp/vesper-w11-state-validation.log
```

가져오기 계획은 [Audio/wwise-authoring-plan.json](Audio/wwise-authoring-plan.json)에 있습니다. 적용 스크립트 자체는 실제 WAAPI 연결 환경에서 실행하지 않았으므로, 성공한 authoring 결과로 해석하면 안 됩니다. 일부 가져오기가 실패하면 오류를 해결하고 프로젝트와 `Vesper_W11` Work Unit 상태를 확인한 뒤 재개합니다.

최종 완료 기준은 바닥별 발소리/걷기·달리기·정지, 숲↔설산 왕복, 비 강도/시간 변화, 호수 접근·이탈·줌, R 복귀·재실행의 중복 재생 없음, Windows 빌드의 Bank/음원 누락 및 런타임 오류 없음입니다. 이 기준은 아직 통과하지 않았습니다.

## 참고

- [Wwise Unity Integration 설치](https://www.audiokinetic.com/library/2024.1.5_8803/?id=pg_installunitypackage.html&source=Unity)
- [Wwise 최초 설치와 계정 로그인](https://www.audiokinetic.com/en/library/Launcher_2023.2.4.3909/?id=getting_started&source=InstallGuide)
- [Switch Container의 Step/Continuous 동작](https://www.audiokinetic.com/en/public-library/2024.1.8_8893/?id=defining_contents_and_behavior_of_switch_containers&source=Help)
- [WAAPI Switch 할당](https://www.audiokinetic.com/library/2024.1.8_8898/?id=ak_wwise_core_switchcontainer_addassignment_example_assigning_a_switch_container_s_child_to_a_state.html&source=SDK)

문서 버전은 API 참고용이며 현재 Unity 6000.5.7f1과의 호환성 인증을 의미하지 않습니다.
