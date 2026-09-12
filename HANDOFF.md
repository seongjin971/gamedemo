# VESPER 개발 인수인계 — 2026-09-12

## 시작 기준

- 현재 전달본: **Weather World W10**, `WEATHER_W10_READY_FOR_USER_REVIEW`.
- Unity: **6000.5.7f1 (017862109af0)**. 프로젝트 폴더는 `Unity/Vesper`입니다.
- 패키지: URP `17.5.0`, AI Navigation `2.0.14`. `Packages/manifest.json`과 `packages-lock.json`을 함께 보존합니다.
- 시작 장면: `Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W10.unity`.
- 주 실행 코드: `Assets/Vesper/Expansion/WeatherW10/Runtime/`. 이전 버전 자산·런타임도 참조하므로 과거 버전 폴더를 일괄 삭제하지 마세요.
- 우선 읽기: 이 문서 → [CHECKPOINT.md](CHECKPOINT.md) **최상단** → [PLAY_WEATHER.md](PLAY_WEATHER.md) → [W10 REPORT.md](Migration/Evidence/Expansion/WeatherWorld/W10/REPORT.md).

## 현재 동작과 남은 확인

강가, 비가 오기 전 어두운 숲, 비 오는 숲과 폐허, 밤 눈보라 설산을 연결한 시각 데모입니다. 클릭으로 이동하고 Shift로 달리며 Q/E로 좌우 시점을 회전합니다. 휠은 확대/축소, R은 시작점 복귀입니다. R을 눌러도 선택한 시점 각도는 유지됩니다. 마우스 드래그는 회전하지 않고 버튼을 놓은 위치로 이동합니다. 상하 시점 각도는 고정이며 음향은 없습니다.

W10 기존 기록에는 빌드 오류/경고 0, 합성 입력 검사 19개 통과, FHD 실제 실행 화면 6장, 대표 보행 51.76~61.99 FPS가 남아 있습니다. 이 수치는 이전 환경의 기록입니다. 이번 GitHub 전달에서 Unity를 새로 빌드하거나 성능을 재측정한 결과가 아닙니다. 새 개발자 PC에서 가져오기·Play·직접 입력을 확인하세요. 사용자 최종 시각·직접 플레이 수락과 전체 참고 이미지 8점 일치는 별도로 남아 있습니다. 추가 시각 반복이 자동으로 요구되는 상태는 아닙니다.

## Windows 실행 파일 만들기

1. README 안내대로 Git LFS 파일을 받은 뒤 Unity Hub에서 `Unity/Vesper`를 엽니다.
2. W10 장면을 직접 열어 Play 동작을 확인합니다.
3. **File → Build Profiles**에서 Windows / x86_64 프로필을 선택합니다.
4. Scene List에는 **W10 장면만 활성화**합니다. 기존 `EditorBuildSettings.asset`은 초기 `VesperMigrationSlice.unity`를 가리키므로 그대로 사용하지 마세요.
5. 출력 파일을 `Unity/Vesper/Builds/VesperWeatherWorld_W10/VesperLinear.exe`로 빌드합니다. Unity의 프로젝트 기준으로는 `Builds/VesperWeatherWorld_W10/VesperLinear.exe`입니다.
6. 저장소 루트의 `PLAY_VESPER_WEATHER.cmd`를 실행하면 1920×1080 전체화면으로 열립니다. Direct3D 12 실행 옵션이 포함되어 있으므로 해당 Windows 환경을 사용하세요.

`WeatherW10Build.PrepareAndBuild`는 최초 후보 작성용이며 이미 존재하는 W10 장면을 보호하기 위해 중단합니다. 일반 재빌드 명령으로 실행하지 마세요. 과거 `prepare_*`, `seed_*`, `apply_f01.py`, `preserve.py`, `safe_stop.py` 등은 이전 기준·후보를 생성하는 도구입니다. 초기 설치에 필요하지 않으며 인수인계 직후 일괄 실행하면 안 됩니다.

## 파일 구성과 보존

| 경로 | 용도 |
| --- | --- |
| `Unity/Vesper/Assets`, `Packages`, `ProjectSettings` | 실제 Unity 개발 프로젝트. 모든 `.meta`와 GUID를 함께 유지 |
| `Migration/Source`, `ArtSource` | Blender/모델/재질 제작 원본, 변환 및 검증 도구, 출처 문서 |
| `Migration/Evidence/Expansion/WeatherWorld/W10` | 최신 W10 보고서·검증 JSON·실제 캡처·당시 소스 사본 |
| `Migration/Evidence`의 문서/JSON | 과거 상태·검증 기록. 일부 과거 화면 링크는 로컬 보관 자료를 가리킴 |
| `src`, `public`, `tests`, `package*.json` | 보존된 Three.js 브라우저 데모 |
| `HANDOFF_CONTENTS.json` | 전달 목록과 원본 SHA-256, 의도적으로 제외한 파일 목록 |

candidate58 안뜰은 사용자가 받아들인 과거 작업 기준이고, E02/F01/L06/L09/W05/W06/W09는 보존된 이전 후보입니다. 현재 개발은 W10부터 시작합니다. F02는 과거 작성 중 후보로 별도 장면·빌드·시각 채택이 이루어지지 않았습니다. 문서 하단의 과거 '최신', '미착수', '미컴파일' 표기를 현재 상태로 해석하지 마세요.

새 변경은 새 버전의 장면·빌드·근거 경로로 작업하고, 이전 장면/자산/GUID/검증 기록을 덮어쓰지 않는 기존 프로젝트 방식을 따릅니다. GitHub `main`은 원본 작업 폴더의 미커밋 최신 파일을 포함한 **새 전달용 이력**입니다. 원본 HEAD는 `d8199c6`이며 원래 `unity-migration` 이력과 로컬 파일은 원본 PC에 그대로 남아 있습니다. 원본의 과거 커밋 ID/태그 링크는 이 새 저장소에 존재하지 않습니다.

## 전달 범위와 환경 의존성

Unity 캐시(`Library`, `Temp`, `Logs`, `UserSettings`), `node_modules`, `dist`, 실행 빌드, 개인 `.dream-loop` 작업 폴더, Blender 백업과 Python 캐시, 반복 생성된 과거 캡처·동영상·로그는 업로드하지 않았습니다. 원본 PC에서 삭제하지 않았습니다. 실행 파일이 없으므로 기존 `PLAY_*.cmd`는 각 버전을 빌드하기 전에는 실행되지 않습니다.

100 MiB를 넘는 제작 원본 2개는 Git LFS로 전달합니다. 포인터 텍스트만 받은 경우 `git lfs pull`을 실행하세요. 환경 설정 파일·API 키·계정 자격 증명은 저장소에 넣지 마세요. Unity 프로젝트 열기·Play·기존 에셋 빌드에는 이미지/모델 생성 서비스의 API 키가 필요하지 않습니다. 생성 도구를 다시 사용할 때는 도구별 환경 변수와 출처/이용 조건 문서를 먼저 확인하세요. 프로젝트 전체에 새 오픈소스 라이선스를 부여하지 않았습니다.

일부 과거 Python/PowerShell 도구와 OBS 녹화 안내에는 원본 PC의 절대 경로가 있습니다. 일반 Unity 실행에는 필요하지 않으며 재사용할 때 해당 PC 경로로 조정해야 합니다. OBS 프로필과 `C:\Users\brian\Videos\VESPER` 녹화 위치는 새 PC에 자동 설치되지 않습니다.

## 보존된 브라우저 데모

Node.js **22.12 이상** 또는 호환되는 최신 LTS에서 저장소 루트에서 실행합니다.

```sh
npm ci
npm run dev
```

Chrome에서 `http://127.0.0.1:5173/`을 엽니다. `npm run build`, `node --test`로 브라우저 소스 빌드/단위 검사를 실행할 수 있습니다. 이것은 초기 안뜰 브라우저 데모이며 최신 Unity W10과 별개입니다.
