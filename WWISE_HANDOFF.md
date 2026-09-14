# Wwise W11 실행 및 작업 기록

**Wwise 2025.1.10.9233을 Unity 6000.5.7f1에 연결했습니다.** 실제 Unity Play Mode에서 Bank 로딩·게임 동기화·발소리 이벤트·재시작 검사 88개가 통과했고, Wwise 출력 WAV에 무음이 아닌 신호가 기록됐습니다. 사람이 듣고 진행하는 최종 음량·음색 조정은 별도입니다.

작업 브랜치는 `feat/wwise-w11`, 기준은 W10의 `8fc50948e7725cd54ff14159beb0137b52a6589f`입니다. Wwise 연결 커밋은 `15159e3`이며, 후속 전수 점검 수정도 같은 브랜치에 포함합니다. 자세한 내용은 [점검 결과](Audio/AUDIT.md)에 정리했습니다.

## 실행

1. Unity Hub의 **Vesper** 프로젝트를 엽니다. 로컬 경로: `/Users/ai/gamedemo/Unity/Vesper`.
2. `Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W11.unity`를 엽니다. 메뉴 `Vesper > W11 Audio > 1 Prepare or Open Scene`으로도 열 수 있습니다.
3. Play를 누릅니다. 화면의 오디오 상태가 `Wwise connected`가 되면 연결된 상태입니다. 기존 이동·달리기·카메라 조작과 R 복귀를 그대로 사용합니다.
4. 음향 편집은 `Audio/VesperAudio/VesperAudio.wproj`를 Wwise에서 엽니다. Unity와 별도로 Wwise를 실행해 두지 않아도 인게임 사운드는 재생됩니다.

이 Mac에는 다음 항목이 설치돼 있습니다.

- Wwise Authoring/SDK **2025.1.10.9233**, Mac·Windows 플랫폼.
- Unity Integration **2025.1.10.4304**, SDK 버전 일치.
- Unity **6000.5.7f1 arm64**, Windows Build Support (Mono), Apple Metal Toolchain 17C7003j.
- Unity Hub 프로젝트 등록, W11 장면의 초기화·리스너·음원 컴포넌트 연결, `VESPER_WWISE` 활성화.

## 연결된 사운드

| 게임 입력 | Wwise 설정 |
| --- | --- |
| 발 디딤 | `Play_Footstep`, `SurfaceType`의 Mud/Gravel/Snow/Rock별 Random Container. 한 번에 한 샘플, 반복 회피. Mud에는 wet 원본을 사용 |
| 진행 거리의 연출 시간 | `TimeOfDay` 0~24 RTPC로 낮/밤 배경음과 자연음 음량 변화. 실제 게임 시계는 아님 |
| 기존 날씨의 비 강도 | `RainIntensity` 0~1 RTPC로 비 배경·강한 비·비바람 혼합, 건조 지역 자연음 억제 |
| 숲↔설산 | `Area` State, 경계 270.5m 및 2m 여유 폭. Continuous Switch, 진입·이탈 1.5초 페이드 |
| 호수/강 접근 | 별도 `Play_Lake_Ambience` 음원 `(0,-0.55,-25)`. 3D 거리 감쇠: 0m 0dB, 8m -3dB, 20m -18dB, 40m -96dB |
| 카메라 줌 | 리스너 위치는 캐릭터를 따르고 방향은 카메라를 따름. 줌으로 호수와의 청취 거리가 바뀌지 않음 |
| 정지·공중·R 복귀 | 불필요한 발소리 억제, 상태 갱신, 환경음 중복 시작 방지 |

원본 WAV **76개**를 이름이 같은 파일끼리 충돌하지 않도록 원래 폴더를 보존해 가져왔습니다. 실제 활성 AudioFileSource 76개와 원본 SHA-256이 모두 일치합니다. 새·벌레·풀·바람·부엉이·늑대 소리는 시간/날씨에 맞춰 간격을 두고 랜덤 재생합니다. 현재 Bank에는 **67개** 음원이 포함됩니다. 천둥 3개는 화면 섬광 동기화 전까지, concrete 6개는 별도 표면 분류를 추가하기 전까지 `Source_Library`에 보관합니다.

발 접촉 위상은 실제 애니메이션 클립에서 샘플링했습니다: 걷기 좌/우 `0.325 / 0.841667`, 달리기 `0.391667 / 0.883333`. 프로필 `Assets/Vesper/Expansion/WeatherW11/W11AudioProfile.asset`에서 조정할 수 있습니다. 혼합 지면의 표면 분류는 콜라이더 태그와 편집 가능한 구역 기준이며 셰이더 픽셀 판정은 아닙니다.

## 확인한 결과

- SDK 활성 상태의 실제 Unity 프로젝트 컴파일·장면 참조 검사 통과.
- Metal Toolchain 설치 후 일반 Editor 화면에서 W11 장면 렌더링과 `Wwise connected`, 대기 중 이벤트 2개·오류 0을 확인했습니다. [실행 화면](Audio/wwise-editor-verified.png).
- Unity Play Mode **88개 검사 통과, 실패 0, 오류 0, 프로세스 종료 코드 0**. 엔진에서 RTPC/State/Switch 값을 다시 읽어 확인하고, 보행·달리기 이벤트와 비활성화/재활성화 후 중복 재생을 검사했습니다. 후속 검사는 그래픽 없이 수행했으며 일반 Editor 렌더링은 위의 이전 확인 기록입니다.
- Wwise에서 Mac/Windows SoundBank 생성: **경고 0, 오류 0**. 플랫폼별 `Init.bnk`, `Vesper_W11.bnk`와 메타데이터가 `Assets/StreamingAssets/Audio/GeneratedSoundBanks/`에 있습니다. 67개 음원은 Bank 내부에 포함되므로 별도 WEM 복사가 필요하지 않습니다.
- Wwise 엔진 출력 캡처: 48kHz 스테레오, 약 6.57초, peak -28.62dBFS, 무음 아님, 클리핑 0. Gravel/Mud/Rock/Snow 발소리도 환경음 없이 따로 녹음하여 모두 비무음·클리핑 0을 확인했습니다. 이 수치는 사람의 청음 평가를 대신하지 않습니다.
- 빌드 설정 검사 9개와 Windows x64 Mono 재빌드 성공, 종료 코드 0. 실행 파일·Wwise 네이티브 DLL과 Windows Bank 포함 및 Bank 해시 일치를 확인했습니다. Windows에서 직접 실행한 결과는 아닙니다.
- Python 회귀 검사 **16개 통과**: authoring 계획 8개, Unity 전달 파일 검사 4개, 출력 캡처 판정 4개. 초기 구현의 Random/Sequence 및 Step/Continuous 열거값 오류와 같은 이름의 WAV 충돌을 수정했습니다.
- 기존 엔진 독립 상태 검사 40개와 최초 Unity 상태 검사 42개도 이전 작업에서 통과했습니다.

보고서: [전체 상태](Audio/validation.json), [Unity/Wwise 실행 검사](Audio/unity-wwise-validation.json), [음원·Bank·출력 신호 검사](Audio/output-signal-validation.json), [Bank 생성 로그](Audio/soundbank-generation.json). 실제 캡처 파일은 로컬 `Audio/unity-wwise-validation.wav`에 있습니다.

배치 실행은 Wwise가 기본적으로 오디오 엔진을 끄므로 `-wwiseEnableWithNoGraphics`가 필요합니다. 명시적인 오디오 검사에서만 포커스 상실에 따른 정지를 해제하며 일반 게임 설정은 유지합니다. Play Mode 종료 후 Editor를 닫도록 해 native 오디오 플러그인이 정상 해제되도록 했습니다. 원격 Profiler 연결 없이 실행한 최종 검사가 기준입니다.

## 재생성 및 검증

이미 작성된 Wwise 프로젝트가 포함돼 있으므로 일반 실행에는 아래 authoring 명령이 필요하지 않습니다. 최초 scaffold 생성 도구는 이름 충돌을 만나면 중단하며 기존 작업을 덮어쓰지 않습니다. 가져오기는 WwiseConsole에서 하나의 undo 작업으로 묶이지 않으므로, 새 프로젝트에 적용하고 실패하면 저장 상태를 확인합니다.

```sh
# 음향 편집용 Python 환경은 각 PC에서 한 번 준비 (macOS 예시)
python3 -m venv .wwise-venv
source .wwise-venv/bin/activate
python -m pip install waapi-client==0.8

# WAAPI를 쓰려면 먼저 실행하고 다른 터미널에서 아래 명령을 사용
'/Applications/Audiokinetic/Wwise_2025.1.10.9233/Wwise.app/Contents/Tools/WwiseConsole.sh' \
  waapi-server "$PWD/Audio/VesperAudio/VesperAudio.wproj" --wamp-port 8085 --http-port 8095

# 새 프로젝트의 scaffold가 필요할 때만 사용
python3 Tools/prepare_wwise.py
python Tools/prepare_wwise.py \
  --apply --project Audio/VesperAudio/VesperAudio.wproj --url ws://127.0.0.1:8085/waapi

# 명시한 프로젝트가 WAAPI 서버에 열려 있을 때 W11 음향 설정 적용
python Tools/author_wwise_mix.py \
  --project Audio/VesperAudio/VesperAudio.wproj --url ws://127.0.0.1:8085/waapi

# Wwise 프로젝트를 저장한 뒤 Bank 생성
'/Applications/Audiokinetic/Wwise_2025.1.10.9233/Wwise.app/Contents/Tools/WwiseConsole.sh' \
  generate-soundbank "$PWD/Audio/VesperAudio/VesperAudio.wproj" --platform Mac Windows

python3 -m unittest discover -s Tools/tests -p 'test_*.py' -v

# Unity를 닫고 실행
'/Applications/Unity/Hub/Editor/6000.5.7f1/Unity.app/Contents/MacOS/Unity' \
  -batchmode -nographics -wwiseEnableWithNoGraphics \
  -projectPath "$PWD/Unity/Vesper" \
  -executeMethod Vesper.Expansion.WeatherW11.Editor.WeatherW11Setup.ValidateStateBatch \
  -w11StateQA "$PWD/Audio/unity-wwise-validation.json" -w11AudioQA \
  -logFile /tmp/vesper-w11-audio-validation.log

# 위 Unity 검사에서 새로 생성한 캡처 측정
python3 Tools/validate_wwise_assets.py --capture Audio/unity-wwise-validation.wav \
  --footstep-captures Audio/unity-wwise-validation-footsteps-*.wav
```

기본 Build Profiles의 활성 장면도 W11로 설정했습니다. Mac/Windows 이외 대상과 누락·빈 파일·잘린 Bank는 빌드 전에 오류로 처리합니다. Windows 빌드는 Unity 메뉴 `Vesper > W11 Audio > 4 Build Windows Player`를 사용합니다. 결과 경로는 `Unity/Vesper/Builds/VesperWeatherWorld_W11/VesperAudio.exe`입니다. Windows에서의 실행·청음은 이 Mac에서 검증하지 않았습니다.

Wwise 설치 시 생성된 빈 기본 프로젝트와 설치 ZIP은 `/Users/ai/.local/share/VesperWwiseBackups/20260914/integration`에 보관했습니다. 실제 연결은 저장소의 `Audio/VesperAudio`를 사용합니다. SDK 설명서·디버그 심볼·authoring 캐시는 로컬에 두고 Git에서는 제외합니다.

API 설정은 설치된 2025.1.10의 WAAPI schema와 SDK 문서를 기준으로 확인했습니다. [공식 WAAPI 안내](https://www.audiokinetic.com/library/edge/?id=waapi.html&source=SDK), [공식 WAQL 참고](https://www.audiokinetic.com/library/edge/?id=waql_reference.html&source=SDK).
