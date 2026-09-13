# VESPER 개발 인계 — 2026-09-13

현재 개발 시작점은 **Weather World W10**입니다. 소스 정리 기준은 기존 장면·제작 원본 보존, 반복 캡처·캐시 제외입니다. 이번 전달에는 `sfx/`의 WAV 원본 76개도 포함합니다.

## 처음 실행하기

1. Git LFS를 설치하고 저장소를 받은 뒤 `git lfs pull`을 실행합니다.
2. Unity Hub에 **Unity 6000.5.7f1 (017862109af0)**과 Windows Build Support를 설치합니다.
3. Hub에서 **`Unity/Vesper`** 폴더를 프로젝트로 추가하고 가져오기가 끝날 때까지 기다립니다.
4. **`Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W10.unity`**를 열고 Play를 누릅니다.

패키지는 URP **17.5.0**, AI Navigation **2.0.14**이며 `Packages/manifest.json`과 `packages-lock.json`에 고정되어 있습니다. 기존 에셋을 열고 플레이하는 데 외부 생성 서비스 API 키는 필요하지 않습니다.

클릭 이동 / **Q·E** 좌우 회전 / 휠 확대·축소 / **Shift** 달리기 / **R** 시작점 복귀. R은 선택한 시점 각도를 유지합니다. 마우스 드래그는 회전하지 않고 버튼을 놓은 지점으로 이동하며, 상하 시점 각도는 고정입니다. 음향은 없습니다.

## Windows 빌드

1. W10 장면을 열고 **File → Build Profiles**에서 Windows / x86_64를 선택합니다.
2. Scene List에 **W10 장면만 활성화**합니다. 저장된 `EditorBuildSettings.asset`은 초기 `VesperMigrationSlice.unity`를 가리킵니다.
3. Unity 프로젝트 기준 **`Builds/VesperWeatherWorld_W10/VesperLinear.exe`**로 빌드합니다.
4. 저장소 루트의 [PLAY_VESPER_WEATHER.cmd](PLAY_VESPER_WEATHER.cmd)를 실행합니다. 1920×1080 전체화면, Direct3D 12 옵션을 사용합니다.

실행 빌드는 Git에 포함하지 않습니다. 기존 `PLAY_*.cmd`도 해당 버전을 빌드한 뒤 사용할 수 있습니다. `WeatherW10Build.PrepareAndBuild`는 최초 후보 작성 도구이며 기존 W10이 있으면 중단합니다. 일반 재빌드에는 위 절차를 사용하세요.

## 파일 안내

| 경로 | 역할 |
| --- | --- |
| `Unity/Vesper/Assets`, `Packages`, `ProjectSettings` | Unity 전체 소스·장면·자산·설정. `.meta`와 GUID를 함께 유지 |
| `Assets/Vesper/Expansion/WeatherW10/Runtime` (Unity 프로젝트 기준) | 현재 버전의 이동·카메라·날씨 코드 |
| `sfx` | 환경음·발소리 WAV 76개. 폴더·파일명 원본 유지, Unity 미연결 |
| `Migration/Source`, `ArtSource` | 제작 원본, 변환·검증 도구, 에셋 출처 |
| `Migration/Evidence/Expansion/WeatherWorld/W10` | 최신 보고서·실행 화면·검증 자료·당시 소스 사본 |
| `Migration/Evidence`의 문서·JSON 등 | 과거 검증 기록. 제외된 과거 이미지·영상 링크는 원본 PC에서 확인 |
| `src`, `public`, `tests` | 보존된 Three.js 브라우저 데모 |
| `Tools/export_github.py` | 현재 제외 규칙을 적용하여 별도 전달 폴더 생성 |
| `HANDOFF_CONTENTS.json` (전달 폴더에 생성) | 복사 파일 목록·SHA-256·용량·LFS 확인 결과 |

W10은 이전 버전의 자산도 참조합니다. 이전 폴더를 버전명만 보고 삭제하지 마세요. 과거 장면, 제작 원본, `.meta`, 출처·이용 조건 문서를 보존합니다. 새 작업은 새 버전의 장면·빌드·근거 경로에서 진행하는 기존 방식을 따릅니다.

읽는 순서: 이 문서 → [CHECKPOINT.md](CHECKPOINT.md) **최상단** → [PLAY_WEATHER.md](PLAY_WEATHER.md) → [W10 보고서](Migration/Evidence/Expansion/WeatherWorld/W10/REPORT.md). CHECKPOINT 하단은 누적된 과거 기록이므로 하단의 ‘최신’이나 ‘미착수’를 현재 상태로 해석하지 마세요.

과거 `prepare_*`, `seed_*`, `apply_f01.py`, `preserve.py`, `safe_stop.py`는 후보·보존 기준을 작성하는 도구입니다. 최초 설치에 필요하지 않습니다. 일부 도구와 OBS 안내에는 원본 PC의 절대 경로가 남아 있으므로 재사용할 때 확인하세요. OBS 프로필과 녹화 위치는 새 PC에 자동 설치되지 않습니다.

## 검증 상태

기존 W10 보고서에는 빌드 오류·경고 0, 합성 입력 검사 19개 통과, FHD 실행 화면 6장, 대표 보행 51.76~61.99 FPS가 기록되어 있습니다. **이전 환경에서 측정한 기록**이며 이번 소스 정리에서 Unity를 재빌드하거나 FPS를 다시 측정한 결과가 아닙니다.

새 개발자 PC의 Unity 가져오기·Play·직접 입력과 사용자 최종 시각·플레이 수락은 별도로 확인해야 합니다. 정리·복사·해시 검증 결과는 게임의 최종 시각 수락을 의미하지 않습니다.

## 사운드 원본

`sfx/`에는 WAV **76개, 118,365,466바이트(약 118MB)**가 있습니다. `ambience/`는 아침·밤·비·눈 환경음과 강물·새·벌레·늑대·천둥 등의 소리이며, `footstep/`은 바닥별 발소리입니다. 공백과 기존 철자를 포함한 폴더·파일명을 그대로 보존했습니다.

파일 전달만 완료한 상태이며, Unity `Assets` 가져오기·AudioSource 배치·재생 코드·믹싱은 적용하지 않았습니다. 기존 W10은 게임 내 음향이 연결되지 않은 상태로 유지됩니다. 새 개발자가 사운드 통합을 진행할 때 이 원본을 사용하세요.

## GitHub 재업로드용 폴더 만들기

원본 작업 폴더에서 Python **3.11 이상**과 Git을 사용합니다.

```powershell
# 포함할 파일·Unity 메타데이터·100 MiB 초과 파일의 LFS 설정 검사
python -B Tools/export_github.py

# 존재하지 않는 새 폴더에 복사하고 SHA-256 검증
python -B Tools/export_github.py --output .github-export/gamedemo-20260913
```

전달 폴더에는 소스와 안내 문서만 복사하며 `.git` 이력은 복사하지 않습니다. 출력 경로가 이미 있으면 중단하므로 새 버전을 만들 때는 새 폴더명을 사용하세요. 복사 오류가 나면 해당 출력은 미완성으로 취급하고 오류를 해결한 뒤 다른 새 경로로 생성합니다.

원본 Git에는 과거 캡처가 이미 추적되어 있습니다. `.gitignore`는 기존 추적 파일이나 과거 커밋을 제거하지 않습니다. 이 도구는 추적 중인 파일에도 현재 제외 규칙을 적용하므로 **재업로드에는 생성된 전달 폴더를 사용**하세요. 원본에서 `git add .`만 실행하면 과거 기록까지 정리되는 것은 아닙니다.

전달 폴더에서 새 저장소를 시작할 때는 다음 순서를 사용합니다. GitHub에 만든 **새 빈 저장소 URL**을 지정하세요.

```powershell
git init -b main
git lfs install --local
git add .
git commit -m "Prepare VESPER W10 developer handoff"
git remote add origin <새-빈-저장소-URL>
git push -u origin main
```

기존 저장소를 갱신하려면 해당 저장소를 별도 clone한 다음 전달 폴더와 변경·제외 파일을 대조하여 일반 커밋으로 반영합니다. 원본 프로젝트의 이력과 기존 GitHub 이력은 서로 다르므로 원본 폴더를 바로 연결하거나 force push로 교체하지 마세요. 이번 업로드는 기존 `main`의 파일 구성을 정리된 전달본과 `sfx/`로 교체하는 일반 커밋입니다. 이전 커밋 이력은 보존합니다.

`.gitattributes`는 100 MiB를 넘는 제작 원본 2개를 Git LFS로 지정합니다. Git LFS가 설치된 환경에서 **첫 `git add` 전에** `git lfs install --local`을 실행하세요. ZIP 다운로드에 LFS 포인터만 들어 있다면 Git으로 clone한 뒤 `git lfs pull`을 사용하세요.

제외 항목은 Unity 캐시·빌드, `node_modules`, `dist`, 개인 `.dream-loop`, 편집기 임시 파일, Blender 백업, Python 캐시, 환경 파일·인증서, 과거 반복 캡처·동영상·로그입니다. 해당 자료는 원본 PC에 보존합니다. 프로젝트 전체에 새로운 오픈소스 라이선스를 부여하지 않았으며, 외부 에셋의 출처·이용 조건은 해당 원본 문서를 따릅니다.

## 초기 브라우저 데모

현재 설치된 Vite 8.2.2가 지원하는 Node.js 버전을 사용하세요. 이 환경은 Node.js 24 계열입니다. 저장소 루트에서 실행합니다.

```powershell
npm ci
npm run dev
```

Chrome에서 `http://127.0.0.1:5173/`을 엽니다. `npm run build`, `node --test`로 브라우저 빌드·단위 검사를 실행할 수 있습니다. 초기 안뜰 데모이며 Unity W10과 별개입니다. [브라우저 원본 설명](docs/BROWSER_BASELINE.md)을 참고하세요.
