# Vesper Sound Director

Unity 장면의 대상과 보유 사운드 목록을 읽고, 자연어 연출 요청을 검증 가능한 사운드 계획으로 바꾸는 에디터 도구입니다. 계획을 적용하면 실제 Wwise 이벤트와 오브젝트별 볼륨을 사용해 재생합니다.

## 실행

1. 기존 안내대로 Unity Hub에서 `Unity/Vesper`를 Unity **6000.5.7f1**로 엽니다. [새 PC 안내](ONBOARDING.md)
2. **Vesper → Sound Director → Open**을 엽니다.
3. **W11 탐험 장면 열기 → 장면 다시 읽기**를 누릅니다. 현재 장면에는 6개 구간과 강의 실제 위치가 사운드 대상으로 등록돼 있습니다.
4. **연결 설정**에 OpenAI API 키를 입력합니다. 키는 Unity의 세션 저장소에만 보관되며 Git·장면·빌드에는 저장하지 않습니다. Play/정지 중에는 유지되고 Unity를 종료하면 지워집니다. Unity를 실행한 환경의 `OPENAI_API_KEY`도 지원합니다. ChatGPT/Launcher 로그인과 API 키는 별도입니다.
5. 연출 의도를 입력하고 **AI 연출 설계**를 누릅니다. 사용할 수 있는 Responses / Structured Outputs 지원 모델을 설정할 수 있으며 초기값은 `gpt-4o-mini`입니다. 실제 모델 접근 권한은 API 계정에 달려 있습니다.
6. 대상별 사운드, 볼륨, 반경, 전환 시간, 재생 간격과 선택 이유를 확인하고 **이 연출 적용**을 누릅니다.
7. **Play · 들어보기**로 실행하고 **A · 원본 / B · 연출** 또는 게임의 **Tab** 키로 비교합니다. **이전 연출 복원**은 Play를 멈춘 뒤 사용합니다.

API 키가 없으면 **예제 불러오기 · AI 아님**으로 적용·재생·복원 기능을 확인할 수 있습니다. 저장소에 포함된 초기 연출도 수동 작성 예제이며, 실제 AI 결과로 표시하거나 제출하지 않습니다.

AI 설계 시 요청문, 장면 대상의 이름·설명·위치·재질, 장면 오브젝트 이름 일부, 사운드 목록과 현재 계획이 OpenAI로 전송됩니다. 음원 파일, 게임 코드, 키는 계획 본문에 포함되지 않습니다. API 요청에는 `store: false`를 사용합니다.

## 지원 범위

- 사운드 76개 전체 목록, 환경음 17개 풀 선택. 발소리는 기존 게임의 접지·애니메이션 처리를 유지하며 AI의 수정 대상에서 제외합니다. 천둥은 화면의 번개와 동기화되지 않아 제외합니다.
- 장면당 최대 24개 대상, 계획당 최대 24개 레이어, 대상당 최대 3개 레이어.
- 레이어별 볼륨, 공간 반경, 전환 시간, 간헐적 자연음의 재생 간격. 실제 좌우 공간화는 Wwise가 처리하고 거리 감쇠와 시간 전환은 런타임이 계산합니다.
- 구조화된 AI 응답, 존재하는 대상/사운드 ID와 수치 범위 검사, 오류가 있을 때 최대 1회 수정 요청. 실패·취소·미완료 응답은 적용되지 않습니다.
- 현재 계획을 AI 입력에 포함하므로 “물소리만 더 가까이, 다른 소리는 유지” 같은 후속 요청을 할 수 있습니다.
- 설계 중 장면 또는 적용된 계획이 바뀌면 적용을 차단합니다. 검토 후 적용하며 이전 연출과 출처 정보를 복원할 수 있습니다.
- `VesperSoundDirector_Lab`은 연못·숲·폐허의 다른 배치에서 같은 계약과 실행기를 확인하는 두 번째 장면입니다. WASD 이동, Q/E 회전, Tab A/B를 지원합니다. 원본 A에는 별도의 환경음이 없습니다.

현재 장면 분석은 **Unity 오브젝트 정보와 편집 가능한 `SoundTarget` 설명**을 사용합니다. 이미지 인식, 실제 음원의 자동 청취·태깅, 새 효과음 생성, 플레이어 감정 추정은 구현 범위에 포함하지 않습니다. 사운드 설명은 원본 폴더 용도에 따라 사람이 작성했습니다.

다른 장면은 저장 후 **현재 장면 준비**를 누르세요. river/lake/pond/forest/grove/ruin/abbey/snow/water 이름의 렌더 오브젝트를 초기 후보로 찾습니다. 원하는 오브젝트를 선택해 **선택 오브젝트를 대상으로 추가**하고 Inspector에서 설명과 반경을 편집할 수 있습니다. 복제한 대상의 ID가 겹치면 **대상 ID 정리**로 고칩니다. 복잡한 임의 장면의 완전 자동 음향 설계를 보장하지 않습니다.

## 구현 구조

`장면 + 현재 계획 + 보유 자산 → AI 계획 → 로컬 검사 → Profile 저장 → Wwise 재생 → 정적 검사 / 실제 출력 검사`

- `Assets/Vesper/SoundDirector/Editor`: 장면 추출, Responses API, 검토·적용·복원, 편집기 화면.
- `Assets/Vesper/SoundDirector/Runtime`: 계획 데이터·검사 규칙, 사운드 대상, Wwise 재생, A/B 표시. API와 키는 런타임 빌드에 포함하지 않습니다.
- `Resources/VesperSoundCatalog.json`: 원본 경로·해시·길이, 풀별 설명과 허용 이벤트. AI는 이 목록의 ID만 선택할 수 있습니다.
- `Profiles`: 실제 적용 결과와 출처. `OpenAI`와 `Example · AI 아님`을 구분합니다.
- `Vesper_Director.bnk`: 17개 이벤트와 독립적인 설정을 포함한 약 6KB Bank. `Vesper_W11.bnk`의 기존 67개 내장 미디어를 공유하므로 별도 음원 복제가 없습니다. 두 Bank와 최신 Init를 함께 사용해야 합니다.
- Wwise가 공유 미디어를 정리하면서 기존 환경음의 MediaID 5개가 갱신됐습니다. 원본 WAV, 기존 믹스·발소리 설정은 유지합니다. Bank를 일부만 과거 버전으로 바꾸면 안 됩니다.

새 음원을 카탈로그에 등록하는 것은 첫 버전의 UI 밖 작업입니다. 원본·설명·허용 이벤트를 추가하고 Wwise Bank를 다시 생성해야 합니다. 기존 17개 풀의 조합·배치는 Wwise Authoring을 열지 않고 변경할 수 있습니다.

공식 API 계약: [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs). 서버 응답을 직접 실행하지 않고 검토 가능한 계획으로 해석합니다.

## 해커톤 시연

1. W11의 원본 A를 짧게 재생합니다.
2. “숲 초입은 편안하게, 폐허에 가까워질수록 불안하게. 물소리는 가까이에서만, 발소리는 유지”를 실제 AI에 요청합니다.
3. 선택한 대상과 사운드, 설정값, 근거를 보여주고 적용합니다.
4. 동일한 경로에서 A/B를 비교합니다.
5. 즉석 후속 요청으로 물소리 반경만 바꿉니다. 기존 계획 대비 변경·제거 목록을 확인합니다.
6. Sound Lab에서 새로운 요청을 실행해 장면 ID와 배치가 달라도 작동하는지 보여줍니다.

발표 전에는 실제 API 키로 두 장면의 자유로운 요청을 검증하고 사람의 청취 평가를 해야 합니다. 자동 출력 검사만으로 연출의 적절성이나 입상 가능성을 주장하지 않습니다. 측정할 항목은 작업 시간, 성공적으로 적용된 요청의 비율, 사람이 결과를 채택하는지 여부입니다.

## 검증과 재현

`Audio/Director/editor-validation.json`은 Unity의 실제 장면·Profile 적용·복원 검사와 주입된 모의 HTTP 응답을 사용한 API 계약 검사입니다. **실제 AI 호출 검증과 구별해야 합니다.** `w11-playback.json`, `lab-playback.json`은 네이티브 Wwise를 실행한 검사입니다. `audio-validation.json`은 사운드 원본·Bank 의존성과 실제 PCM 출력의 측정 결과입니다. WAV 캡처는 로컬에만 보관합니다.

Unity를 닫은 뒤 macOS에서 실행합니다.

```sh
UNITY='/Applications/Unity/Hub/Editor/6000.5.7f1/Unity.app/Contents/MacOS/Unity'
"$UNITY" -batchmode -nographics -projectPath "$PWD/Unity/Vesper" \
  -executeMethod Vesper.SoundDirector.Editor.DirectorValidation.PrepareAndValidateBatch \
  -logFile /tmp/vesper-director-editor.log

"$UNITY" -batchmode -nographics -wwiseEnableWithNoGraphics \
  -projectPath "$PWD/Unity/Vesper" \
  -executeMethod Vesper.SoundDirector.Editor.DirectorValidation.RunPlaybackBatch \
  -directorQA "$PWD/Audio/Director/w11-playback.json" \
  -logFile /tmp/vesper-director-w11.log

"$UNITY" -batchmode -nographics -wwiseEnableWithNoGraphics \
  -projectPath "$PWD/Unity/Vesper" \
  -executeMethod Vesper.SoundDirector.Editor.DirectorValidation.RunPlaybackBatch \
  -directorLab -directorQA "$PWD/Audio/Director/lab-playback.json" \
  -logFile /tmp/vesper-director-lab.log

python3 Tools/validate_sound_director.py --captures
```

`PrepareAndValidateBatch`는 두 데모 장면을 준비하고 수동 예제 연출을 저장합니다. 자신의 연출을 유지하려면 별도 체크아웃에서 실행하세요. 일반 메뉴의 “적용 결과 검사”는 연출을 바꾸지 않습니다.
