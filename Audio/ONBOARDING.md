# 다른 PC에서 W11 실행하기

**플레이만 할 때는 Unity만 실행하면 됩니다.** 저장소에 Wwise Unity Integration과 Mac/Windows SoundBank가 포함돼 있어, 별도로 Integration을 다시 설치하거나 Wwise Authoring을 켜거나 Bank를 생성할 필요가 없습니다. Wwise Authoring은 소리·이벤트·믹스를 편집할 때 사용합니다.

## 처음 한 번 준비

1. Git와 Git LFS를 설치합니다.
2. Unity Hub에서 **Unity 6000.5.7f1**을 설치하고 Unity 라이선스를 활성화합니다. Windows 실행 파일도 만들려면 해당 Editor의 **Windows Build Support (Mono)**를 설치합니다.
3. 최신 작업 브랜치를 받습니다. 저장소 첫 화면의 `main`은 이전 W10이므로 브랜치를 지정하세요.

```sh
git clone --branch feat/wwise-w11 https://github.com/seongjin971/gamedemo.git
cd gamedemo
git lfs pull
```

이미 받아 둔 저장소는 다음 명령으로 갱신합니다.

```sh
git fetch origin
git switch feat/wwise-w11
git pull --ff-only origin feat/wwise-w11
git lfs pull
```

4. Unity Hub에서 **Add project from disk → `gamedemo/Unity/Vesper`**를 선택하고 엽니다. `Assets` 폴더나 저장소 최상위를 선택하지 않습니다.
5. 첫 패키지 설치·자산 가져오기·컴파일이 끝날 때까지 기다립니다. **Vesper 실행 준비** 창이 완료 상태가 되면 W11 장면을 열고 **Play**를 누릅니다. 게임 화면에 `Wwise connected`가 표시되면 연결된 상태입니다.

Unity 설치·라이선스 활성화와 운영체제의 그래픽 개발 도구 설치는 프로젝트 코드가 자동 처리하지 않습니다. macOS에서 `metal` 컴파일러 오류가 발생하면 Xcode의 Metal Toolchain 설치를 확인하세요.

## 자동 설정 브릿지가 처리하는 것

- 첫 가져오기 후 `VESPER_WWISE` 활성화를 확인하고, 빠져 있으면 추가한 뒤 컴파일을 이어갑니다.
- Unity와 같은 저장소의 `Audio/VesperAudio/VesperAudio.wproj`를 상대 경로로 연결합니다. 저장소 위치와 사용자 계정 이름이 달라도 적용됩니다.
- Mac/Windows SoundBank 경로와 초기화 설정을 맞추고, Bank 파일 구조·SDK 버전·현재 OS의 플러그인을 확인합니다.
- 포함된 Bank를 사용하도록 자동 생성·복사를 끕니다. 장면에 이미 배치된 플레이어 리스너를 사용하므로 추가 기본 리스너를 만들지 않습니다.
- 처음 열린 빈 장면은 W11로 전환합니다. 편집 중인 장면과 이미 저장된 장면은 자동으로 교체하지 않습니다. 이때는 준비 창의 **W11 장면 열기**를 누르면 됩니다.
- 비어 있거나 초기 데모만 있는 빌드 목록을 W11로 설정합니다. 개발자가 따로 구성한 빌드 목록은 유지합니다.
- 준비 결과를 로컬 `Unity/Vesper/UserSettings/VesperSetup.json`에 기록합니다. **Vesper > W11 Audio > Setup Status**에서 재확인할 수 있습니다.

장면의 초기화·리스너·음원 컴포넌트는 저장소에 포함돼 있으며, W11을 열 때 참조를 검사합니다. 누락된 저장소 파일은 새 빈 프로젝트나 임시 Bank로 대체하지 않고 누락 내용을 표시합니다.

## Wwise에서 음향도 편집할 때

1. Audiokinetic Launcher에서 **Wwise Authoring 2025.1.10.9233**을 설치합니다. 생성 대상에 맞는 Mac·Windows 플랫폼도 설치합니다.
2. Unity를 다시 열거나 **Setup Status → 설정 다시 확인**을 누릅니다. 표준 설치 폴더, `WWISESDK`·`WWISEROOT`, 이전에 지정한 로컬 경로에서 정확한 버전을 찾습니다.
3. 다른 위치에 설치했다면 **Wwise 설치 경로 선택**으로 설치 루트(Windows) 또는 `Wwise.app`/상위 설치 폴더(macOS)를 지정합니다.
4. **Wwise 프로젝트 열기**를 누릅니다. 같은 버전의 Wwise로 저장소의 프로젝트를 엽니다.
5. 편집 후 Wwise 프로젝트를 저장하고 **Mac·Windows SoundBank를 생성**합니다. 프로젝트에 설정된 상대 경로를 통해 Unity의 `StreamingAssets/Audio/GeneratedSoundBanks`로 출력됩니다. 다른 팀원에게 전달할 때 Wwise 프로젝트 변경과 생성된 Bank를 함께 커밋합니다.

설치 경로는 PC별 Unity EditorPrefs에 보관하며 실행 중인 Integration에 적용합니다. 공유 `WwiseSettings.xml`에 특정 개발자의 설치 경로를 넣을 필요가 없습니다. 다른 버전의 Authoring을 자동으로 선택하거나 프로젝트를 자동 업그레이드하지 않습니다.

WAAPI는 음향 편집 연동용입니다. 프로젝트의 기본 접속 주소는 `127.0.0.1:8080`이며, 포트나 사용 여부를 변경한 개발자의 설정은 자동 브릿지가 덮어쓰지 않습니다. 게임 내 오디오 재생은 WAAPI 연결 없이 동작합니다. [공식 Editor 설정 안내](https://www.audiokinetic.com/library/edge/?id=pg_editor_settings.html&source=unity).

Windows 재빌드는 **Vesper > W11 Audio > 4 Build Windows Player**입니다. 상세 음향 구조와 검증 명령은 [WWISE_HANDOFF.md](../WWISE_HANDOFF.md)를 참고하세요.

## 새 체크아웃 검증

원래 작업 폴더와 별도로 공백이 포함된 경로에 체크아웃을 만들었습니다. 시작 시 `Library`·`UserSettings`가 없었고, SDK 활성화 기호도 일부러 제거했습니다. Authoring 자동 탐색을 끈 상태로 Unity를 실행해 자동 복구와 첫 장면 준비 검사 **25개**, 실제 Wwise 실행 검사 **88개**가 통과했습니다. 환경음과 네 종류 발소리의 개별 캡처도 비무음·클리핑 0을 확인했습니다.

이는 macOS에서의 새 체크아웃 검증이며, Wwise 앱 자체를 제거한 테스트나 다른 Windows PC에서 직접 실행한 결과는 아닙니다. 시험용 Authoring 경로를 비워 게임 실행이 Authoring 경로에 의존하지 않는지 확인했습니다. Windows의 실제 플레이·청음은 해당 PC에서 확인해야 합니다.

근거: [초기 조건](bootstrap-fixture.json), [자동 설정 검사](bootstrap-validation.json), [실제 Wwise 실행 검사](fresh-clone-wwise-validation.json), [출력 측정](fresh-clone-output-validation.json).

현재 Mac에 설치된 Authoring의 실제 바이너리 plist 버전 확인, 로컬 설치 경로 적용, 반복 실행 시 공유 설정 보존 검사 **5개**도 통과했습니다. [설치 탐색 검사](authoring-discovery-validation.json).

같은 새 체크아웃에서 Authoring 설치 경로를 비운 채 Windows x64 Mono 빌드와 설정 검사 **9개**가 통과했습니다. 실행 파일·Wwise DLL·Windows Bank 포함과 Bank 해시 일치도 확인했습니다. [새 체크아웃 빌드 검사](fresh-clone-build-validation.json).

같은 검사를 반복하려면 작업 중인 프로젝트와 분리된 새 체크아웃에서 다음 명령을 사용합니다. 초기 조건을 비교하려면 실행 전에 해당 체크아웃에 `Library`·`UserSettings`가 없는지 확인하고, `ProjectSettings.asset`의 Standalone 설정에서 `VESPER_WWISE`만 제거합니다. 검사 코드는 테스트용 장면·빌드 설정 변경 후 원상 복구하지만 실제 작업 폴더에서 실행하지 않는 것을 권장합니다.

```sh
# macOS, 새 체크아웃 최상위에서 실행
'/Applications/Unity/Hub/Editor/6000.5.7f1/Unity.app/Contents/MacOS/Unity' \
  -batchmode -nographics -wwiseEnableWithNoGraphics \
  -projectPath "$PWD/Unity/Vesper" \
  -vesperAutoSetup -vesperVerifyFreshClone -vesperNoAuthoring \
  -w11StateQA "$PWD/Audio/fresh-clone-wwise-validation.json" -w11AudioQA \
  -logFile /tmp/vesper-fresh-clone.log
```
