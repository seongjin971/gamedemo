# VESPER — The Last Sanctuary

강가에서 어두운 숲과 비 오는 폐허를 지나 밤 눈보라 설산으로 이어지는 Unity 탐험 데모입니다. 현재 개발 시작점은 **Weather World W10**이며 게임 내 음향은 아직 연결하지 않았습니다. 환경음·발소리 WAV 76개를 `sfx/`에 개발용 원본으로 함께 제공합니다.

**처음 받았다면 [개발 인계 문서](HANDOFF.md)를 먼저 읽으세요.** 최신 상태는 [CHECKPOINT.md](CHECKPOINT.md) 최상단에 있습니다.

Wwise W11 연동 코드·음원 매핑 준비본과 남은 환경 설정은 [Wwise 작업 인계](WWISE_HANDOFF.md)에 있습니다. 실제 음향 재생 검증은 아직 완료되지 않았으며 현재 플레이 기준은 W10입니다.

![W10 실제 실행 화면](Migration/Evidence/Expansion/WeatherWorld/W10/input-qa-visible/start-qe-help.png)

## Unity 실행

1. Git LFS를 설치하고 `git clone https://github.com/seongjin971/gamedemo.git`로 받은 뒤 저장소에서 `git lfs pull`을 실행합니다.
2. Unity Hub에서 **Unity 6000.5.7f1**로 **`Unity/Vesper`** 폴더를 엽니다.
3. **`Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W10.unity`**를 열고 Play를 누릅니다.

클릭 이동 · **Q/E** 좌우 회전 · 휠 확대/축소 · **Shift** 달리기 · **R** 시작점 복귀. 자세한 조작은 [PLAY_WEATHER.md](PLAY_WEATHER.md)에 있습니다.

실행 파일은 Git에 포함되지 않습니다. Windows 빌드 절차는 [HANDOFF.md](HANDOFF.md#windows-빌드)를 따르세요. 기존 빌드 목록은 초기 장면을 가리키므로 **W10 장면을 직접 지정**해야 합니다.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `Unity/Vesper` | 현재 프로젝트와 보존된 이전 장면·공유 자산 |
| `sfx` | 환경음·발소리 WAV 76개, 약 118MB. Unity 미연결 원본 |
| `Migration/Source`, `ArtSource` | 제작 원본, 변환·검증 도구, 출처 기록 |
| `Migration/Evidence` | 과거 보고서·검증 데이터와 최신 W10 실행 화면 |
| `src`, `public`, `tests` | 초기 Three.js 브라우저 데모 |
| `Tools/export_github.py` | 원본 이력을 보존하면서 재업로드용 폴더 생성 |

이전 버전 자산을 현재 장면도 참조하므로 Unity 폴더를 버전명만 보고 삭제하지 마세요. 캐시·실행 빌드·반복 캡처·개인 환경 파일은 업로드 대상에서 제외합니다. 100 MiB를 넘는 제작 원본 2개는 Git LFS를 사용합니다.

## 재업로드 준비

원본 작업 폴더에서 다음 명령으로 별도 전달 폴더를 만듭니다. Python 3.11 이상과 Git이 필요하며, 출력 경로는 새 경로여야 합니다.

```powershell
python -B Tools/export_github.py --output .github-export/gamedemo-20260913
```

기존 추적 파일에도 제외 규칙을 적용하고 복사본의 SHA-256을 확인합니다. 원본 `.git` 이력과 로컬 보관 파일은 보존됩니다. 실제 업로드 방법과 기존 저장소 갱신 시 주의점은 [HANDOFF.md](HANDOFF.md#github-재업로드용-폴더-만들기)에 있습니다.

## 검증 기록

[W10 보고서](Migration/Evidence/Expansion/WeatherWorld/W10/REPORT.md)에 기존 빌드·입력 검사와 실제 실행 화면이 있습니다. 과거 환경의 검증이며, 새 PC의 Unity 가져오기·Play·직접 조작 및 사용자 최종 수락은 별도로 확인합니다.

## 초기 브라우저 데모

저장소 루트에서 `npm ci`, `npm run dev` 후 Chrome으로 `http://127.0.0.1:5173/`을 엽니다. `npm run build`, `node --test`로 빌드·단위 검사를 실행할 수 있습니다. Node.js 22.12 이상을 사용할 수 있으며 현재 작업 환경은 24 계열입니다.

브라우저는 초기 안뜰 데모이며 Unity W10과 별개입니다. 원본 요청·조작·렌더링 설명은 [브라우저 기준 문서](docs/BROWSER_BASELINE.md)에 보존했습니다. `preview.png`도 초기 브라우저 화면입니다.
