# 최신 목표 결정 — P3·P4·P5를 하나의 연속 맵으로, 2026-09-10

**목표 확정 / 문서 갱신 완료 / 연속 맵 구현 미착수**. 사용자 요청에 따라 낮 물가(P3)·비 오는 폐허(P4)·눈 오는 고갯길(P5)을 하나의 맵 안에서 걸어 다니는 세 기후 구역으로 변경했다. 연결 길을 지나며 날씨·빛·안개·바람·환경음과 지면·식생이 위치에 따라 점진적으로 변한다. P3↔P4↔P5 통과 시 암전·순간이동·카메라 초기화·입력 중단 없이 왕복하는 것이 목표다.

P3에서 연속 이동·환경 혼합 기반과 물가를 만들고, P4·P5를 같은 맵에 확장한다. 인접 구역을 경계에서 함께 표시하고 먼 구역의 고비용 효과를 제한하며 경계 성능도 검증한다. 기존 밤 안뜰은 보존하고 새 맵 입구 연결 방식은 후속 설계에서 정한다. 세부 목표·단계·완료 조건은 **[EXPANSION_PLAN.md](EXPANSION_PLAN.md)** 5~8절이 최신 기준이다.

이번에는 문서만 변경했다. 현재 P2는 아래 기록의 페이드 전환 빌드이며, 새 목표가 구현된 상태가 아니다. 코드·장면·자산·실행기·빌드는 그대로다. 최신 P2 직접 사용자 수락 대기 상태도 변경하지 않았다. 이후 실제 구현 요청이 오면 새 목표를 기준으로 진행한다.

---

# 최신 전달 — P2 안뜰 바닥 이동 확장, 2026-09-10

**P2_GROUND_FIX_READY / INDEPENDENT_REVIEW_PASS / LATEST_USER_REVIEW_PENDING**. 사용자가 중단 후 재개를 요청했고, 안뜰 앞쪽과 나무 옆의 낮은 바닥으로 이동 영역을 넓혔다. 실제 바닥 형상으로 이동 영역을 만들고, 바닥의 좁은 장식 균열 때문에 경로망이 끊기던 문제를 발 지지 범위 판정으로 수정했다. 벽·나무 몸통·낭떠러지는 막고, 기존 연결 구역의 경사로·다리는 유지한다. 높은 장식 계단은 이번 낮은 바닥 영역에 포함하지 않는다.

실행: **[PLAY_VESPER_P2.cmd](PLAY_VESPER_P2.cmd)** → `Unity/Vesper/Builds/VesperP2ClickFix/VesperP2.exe`. 조작법: [PLAY_P2.md](PLAY_P2.md). 새 장면 `Assets/Vesper/Scenes/Expansion/VesperP2ClickFix.unity`. 원래 P2와 이전 네 빌드·장면·공유 시각 자산은 보존했다. P3 이후나 Windows AIXHost 오류는 작업하지 않았다.

최종 `ground-build-03` 오류0/경고0. `ground-player-03`은 화면 입력 처리→클릭 광선→경로→실제 도착 검사 29개 통과, 990개 이동 프레임에서 바닥 지지·몸체 여유 공간 확인. 이전 실패 위치·앞쪽 확장 바닥·나무 옆·다리 도착과 구역 왕복을 포함한다. 자기 화면 검토 및 새 독립 리뷰 통과. 정지/이동/회전/확대 성능은 수정본32.02~32.47FPS, 인접 이전 빌드32.61~33.69FPS로 1.8~3.8% 감소했다. 60FPS 달성은 주장하지 않는다.

최신 실행 창을 열어 사용자 확인을 요청했다. 실제 입력 도구는 여전히 native pipe 연결 불가이며, 29개 검사는 합성 포인터 입력이다. 과거 트랙패드 확인을 최신 빌드 수락으로 대신하지 않는다. 검증은 현재 정적 장면의 측정 경로에 한정하며 연속 충돌 보장을 주장하지 않는다.

증거와 제한: **[최종 검증](Migration/Evidence/Expansion/P2-ClickFix/VALIDATION.md)**. [중단 기록](Migration/Evidence/Expansion/P2-ClickFix/PAUSED.md)은 이전 시점의 기록이다. 이번 클릭·바닥 수정 이후 추가 맵 작업은 자동 진행하지 않는다.

---

# 최신 전달 — Mixamo 걷기·달리기 플레이 빌드, 2026-09-09

**P1_RUN_PLAYABLE_BUILD_READY / DIRECT_INPUT_REVIEW_PENDING**. 사용자가 걷기 전달 후 “좋아. 뛰는거도 해보자”라고 달리기 추가를 지시했다. 별도 P1Run 경로에서 공식 Mixamo Running을 기존 스킨과 Idle/Walk에 추가했다. **[PLAY_VESPER_RUN.cmd](PLAY_VESPER_RUN.cmd)** 실행. 이동 중 Shift를 누르면 달리고 놓으면 걷는다. 속도2.25→5.4(2.4배), 거리 기반 보폭·걷기/달리기 보행 주기 정렬과 가감속 전환을 구현했다. 굽힌 팔·긴 보폭·공중 구간이 걷기와 구분된다. 정지·급회전 발 재배치는 남는다.

candidate02/player02: 빌드 오류0/경고0, 자동 달리기23항목+기본 기능21항목 통과. 실제 동작469프레임/41.02643단위/최고5.4/오류0/누락0/all-focused, 캡처·플레이어 정상 종료0. 자기 검토 후 독립 검토에서 확인한 실제 화면의 큰 시각적 납품 장애는 발견되지 않았다. 직접 Shift·마우스 입력은 native 도구 연결 제한으로 미완료이며 자동 요청과 구분한다.

1536×1024/D3D12 인접 자연 루프: 이전 걷기36.86–37.75FPS, 새 빌드34.73–35.26FPS(5.4–6.6% 낮음,10% 큰 회귀 기준 이내). 새 빌드의 별도 연속 경로는 걷기33.96/달리기33.99FPS.60FPS·표시FPS 달성은 주장하지 않는다. [검증·영상](Migration/Evidence/Expansion/P1-Run/VALIDATION.md).

기존 candidate58·P1·Mixamo 걷기 장면/공유 자산/런타임/빌드/실행을 보존했다.176+174+173파일 해시 불변, Meshy 추가0회, P2 미착수. 새 장면 `Assets/Vesper/Scenes/Expansion/VesperAdventurerRun.unity`, 빌드 `Unity/Vesper/Builds/VesperRun/VesperRun.exe`. 시작 HEAD c2b23cd/작업 트리 깨끗함. 당시 실행 중인 VesperMixamo 플레이어1개는 검증 시작 전 안내 후 종료했다. 처음의 짧은 검증 경로는 가속/감속으로 전환 검사를 충족하지 못해 기존 안뜰의 긴 경로로 검증만 수정했고 최종 통과했다. 이번 달리기 후속 작업을 마무리한다.

# 이전 전달 — Mixamo 모션 적용 플레이 빌드, 2026-09-09

**MIXAMO_PLAYABLE_BUILD_READY / DIRECT_INPUT_REVIEW_PENDING**. 사용자가 같은 단계 반복 중단 조건을 철회하고 믹사모 실제 적용을 지시했다. 공식 Mixamo Walking / Breathing Idle을 기존 P1 골격으로 리타게팅하여 별도 장면·Windows 빌드에 적용했다. **[PLAY_VESPER_MIXAMO.cmd](PLAY_VESPER_MIXAMO.cmd)** 실행. 아래 중단은 이전 상태다. 기존 P1과 candidate58은 보존했고 P2는 미착수다.

더 곧은 보행 자세·앞으로 뻗는 부츠·절제된 팔 흔들림. 독립 검토에서는 유사 위상 대비 소폭 개선으로 판단했고 확인한 표본에 큰 시각적 장애는 없었다. 정지는 기존 짧은 블렌드이며 발 재배치와 작은 접지 드리프트 가능성이 남는다. 다운로드한 Stop은 원본 비교용으로 보존하며 런타임에서 재생하지 않는다. Meshy 추가 사용0회.

빌드 오류0/경고0, 실제 플레이어 자동 기능21통과/오류0. 동작643프레임·25.41694단위·6도착·누락0·오류0·all-focused. 별도1536×1024/D3D12 자연 루프는 기존 P1 32.25–32.75FPS, Mixamo33.56–34.05FPS. 큰 회귀 없으며60FPS·표시장치 FPS·직접 입력 검증은 달성 주장하지 않는다. 정적 캡처의 종료 오류는 확장 전용 리소스 정리로 정상 종료0을 확인했다. 기존176파일과 P1빌드174파일 해시 불변. 원래 장면·공유 런타임·재질·셰이더 변경 없음.

새 장면 `Assets/Vesper/Scenes/Expansion/VesperAdventurerMixamo.unity`, 빌드 `Unity/Vesper/Builds/VesperMixamo/VesperMixamo.exe`. [비교·검증 결과](Migration/Evidence/Expansion/P1-Mixamo/VALIDATION.md), [나란히 영상](Migration/Evidence/Expansion/P1-Mixamo/COMPARE.html). Native Windows Computer Use 연결 불가로 직접 클릭·드래그·휠·R 검증은 사용자 플레이에 남는다. 이번 Mixamo P1 작업을 마무리하고 추가 맵으로 자동 진행하지 않는다.

# 이전 시도 — Mixamo 걷기 개선, 반복 정체로 중단, 2026-09-09

**MIXAMO_ATTEMPT_STOPPED / P1_BUILD_PRESERVED**. 사용자는 P1 걷기가 어색하다고 보고했고 Dream Loop로 믹사모 개선을 지시하면서 제자리걸음처럼 되면 멈추고 보고하라고 했다. 사용자가 Adobe 로그인을 완료한 뒤 기존 모험가 메시를 Mixamo에 업로드하고 기준점을 지정했다. 자동 리깅은25본 요청과 기본65본으로 한 번 재시도 모두 완료 결과 없이 기준점 화면으로 돌아왔다. 명시적 오류 원인은 표시되지 않았다.

같은 단계가 반복되어 사용자 중단 조건에 따라 세 번째 재시도 없이 멈췄다. 새 모션 다운로드·Unity 가져오기·런타임 변경·새 빌드는 없으며, 개선된 걷기가 제자리걸음하는 것을 관찰했다는 뜻은 아니다. 기존 P1 빌드174개 파일 해시 불변을 확인했다. 현재 플레이는 아래의 P1 빌드 그대로다. Chrome의 Mixamo 기준점 화면을 인계용으로 유지했다.

증거: [Mixamo 시도 보고](Migration/Evidence/Expansion/P1-Mixamo/attempt-01/REPORT.md). 새 파일은 `Migration/Source/Expansion/P1-Mixamo`의 업로드 FBX·내보내기 스크립트·브리프와 별도 증거뿐이다. 기존 골격에 믹사모 모션을 직접 리타게팅하는 대안은 미착수다. 자동으로 계속 진행하지 않는다.

# 이전 전달 — P1 초보 모험가 플레이 빌드, 2026-09-09

**P1_PLAYABLE_BUILD_READY / DIRECT_INPUT_REVIEW_PENDING**. 사용자의 실제 구현 지시에 따라 기존 안뜰의 별도 장면에서 새 모험가로 걷는 Windows 빌드를 완성했습니다. 루트 **[PLAY_VESPER_P1.cmd](PLAY_VESPER_P1.cmd)** 실행, 조작은 [PLAY_EXPANSION.md](PLAY_EXPANSION.md). 최종 사용자 시각 채택과 직접 조작감 확인은 아직이며, 아래의 구현 미착수 기록은 과거 상태입니다. P1에서 종료하고 P2 이후로 자동 확장하지 않습니다.

추가 사용자 조건: Meshy 생성·리깅·애니메이션 작업은 합계 3회 정도로 제한. 현재 모델 35 + 리깅 5 + 대기 3크레딧, 총 3회 사용. 추가 요청은 눈에 띄는 품질상 필요를 설명하고 별도 승인 후에만 합니다. Higgsfield는 필요시 폭넓게 허용. 작업 예산은 03:43:13–06:03:13 UTC, 한국시간 12:43:13–15:03:13의 2시간 20분입니다.

최종 candidate03/player03: 얼굴·머리카락이 보이는 튜닉·가죽 조끼·바지·부츠·짧은 청록 어깨 천·작은 가방/주머니. 31,113삼각형/24본 스킨, 거리 기반 걷기, 별도 이동·애니메이션·카메라를 구현했습니다. 원본의 전투형 대기와 과도한 팔 벌림을 Blender에서 보정했고 근접 줌에서는 캐릭터 쪽으로 화면 중심을 옮깁니다. 정지·방향 전환은 안정적인 단순 블렌드이며 완전한 발 고정 정지 동작은 아닙니다.

Windows 빌드 오류0/경고0. 실제 플레이어 자동 기능21항목 통과/오류0, 동작659프레임·25.4169단위·누락0·오류0·all-focused. 자기 검토 후 독립 검토는 확인한 기본/회전/근접·정지/회전 표본에서 큰 시각적 납품 장애를 찾지 않았습니다. 연속 영상 전체를 실시간으로 보았다는 판정은 아닙니다. 최종1536×1024/D3D12 비계측 자연 루프는 기존 기사32.64–33.31FPS, P1 33.31–33.78FPS로10% 회귀 없음. 과거43.44–44.09FPS나 모니터 표시FPS와 구분하며60FPS는 미달입니다.

시작 Git은 `unity-migration` / `ce3e7bd`, 작업 트리 깨끗함, Unity·Blender·Vesper 프로세스 없음. [보존 감사](Migration/Evidence/Expansion/P1/protection-audit.json): 기존 빌드/실행/장면176개 파일 해시 불변. 원래 자산·셰이더·런타임·설정·과거 증거 변경 없음. 새 장면은 `Assets/Vesper/Scenes/Expansion/VesperAdventurerP1.unity`, 실행 파일은 `Unity/Vesper/Builds/VesperExpansion/VesperAdventurer.exe`입니다. 빌드 폴더는 Git 제외이며 파일 해시를 증거에 보관했습니다.

Windows Computer Use 재연결은 native pipe unavailable / os error2로 실패했습니다. 자동 검증은 실제 마우스·키보드 조작이 아니며 입력 카운터는0입니다. 반복 권한 요청은 하지 않았습니다. 진단용 근접 촬영 도구의 종료 오류는 임시 리소스 정리 후 정상 종료0으로 해결했습니다. 실제 비교 화면·영상·성능·남은 한계: **[P1 VALIDATION](Migration/Evidence/Expansion/P1/VALIDATION.md)**. 자산 출처: `Migration/Source/Expansion/P1/BRIEF.md`. 이후 작업은 사용자 직접 플레이 피드백 또는 별도 P2 지시부터입니다.

# 이전 결정 — candidate58 퀄리티 채택 및 확장 계획 검토, 2026-09-09

**USER_ACCEPTED_BASELINE / EXPANSION_PLAN_REVIEWED / IMPLEMENTATION_NOT_STARTED**.

사용자는 전달된 candidate58에 대해 “퀄리티 이정도면 충분해”라고 현재 시각 퀄리티를 채택했습니다. 새 목표는 가벼운 복장의 초보 모험가와 비·눈·물가·낮 환경입니다. 이후 “계획검토하고 수정할부분있으면 수정하고 문서 업데이트하자”라는 지시에 따라 계획과 상태 문서만 갱신했습니다.

검토된 제안은 [EXPANSION_PLAN.md](EXPANSION_PLAN.md)입니다. 권장 순서는 **P1 기존 안뜰의 새 모험가 → P2 경사·다리·구역 전환 검증 → P3 낮의 물가 → P4 비 오는 폐허 → P5 눈 오는 길**입니다. 첫 납품을 캐릭터로 좁히고, 낮과 물가를 한 신규 구역으로 묶었습니다. 각 환경은 고정된 조합으로 시작합니다. 이 순서와 세부 범위는 검토된 계획이며 P1–P5 전체 구현을 시작한 상태가 아닙니다.

채택 기준은 `7f7fd09`의 candidate58 장면과 플레이 빌드입니다. 사용자 시각 채택은 원래 concept의8/10 달성이나60FPS 통과를 뜻하지 않습니다. 기존8점 목표를 확장 착수의 선행 조건으로 삼지 않으며, 이미 채택된 안뜰의 추가 시각 반복은 종료합니다. 최신 독립 점수는 여전히 candidate52의6.1/10 Tier2입니다.

이 갱신 때 Git 작업 트리는 깨끗했고 브랜치는 `unity-migration`, HEAD는 `7f7fd09`였습니다. Unity·Blender·Vesper 플레이어 프로세스는 없었습니다. 기존 빌드·캡처·성능 보고를 읽었고, 새 실행이나 성능 측정은 하지 않았습니다. 기존 자동 검증43.44–44.09FPS, 직접 입력 검증 미완료 기록은 그대로 보존합니다.

현재 실행은 [PLAY.md](PLAY.md), 기술 증거는 [player58 검증](Migration/Evidence/AtmosphereV2/player-58/VALIDATION.md)을 보세요. 아래의 미채택·진행 중·중단 기록은 각 시점의 과거 상태이며 현재 사용자 결정보다 우선하지 않습니다.

# 이전 전달 — candidate58 플레이 빌드, 2026-09-09

**PLAYABLE_HANDOFF_BY_USER / VISUAL_TARGET_NOT_MET**. 사용자의 “적당히 검증하고 마무리해서 내가 플레이할수있게해” 지시에 따라 추가 시각 반복을 종료하고 플레이용 빌드를 전달합니다. 루트 `PLAY_VESPER.cmd`를 더블클릭하면 실행됩니다. 조작은 `PLAY.md`를 보세요. 이 전달은 최종 시각 채택이나8/10 달성이 아닙니다.

저장 장면은 `Assets/Vesper/Scenes/VesperAtmosphereV2.unity`의 candidate58입니다. TreeV16, MasonryV16, PavingV17, FlameV17, KnightV7, ContactV14 통합.57의 배경 회귀는 CityBackdrop queue1000 복원으로 수정했고 실제5구도를 직접 검토했습니다. 셰이더/런타임/누락 스크립트 오류0, 반사134. Depth priming은 기본 비활성·미채택입니다.

Windows 빌드 오류0/경고0. 같은1536×1024 비계측 자연 루프: static 43.45, walk 44.09, orbit 43.44, zoom 43.84FPS. 별도 연속 동작 427프레임/33.424m, 오류0/누락0/all-focused.60FPS는 미달이며 모니터 표시 FPS나 직접 입력 검증은 아닙니다. Windows native pipe 연결 불가로 최신 직접 마우스·키보드 검증은 미완료입니다.

큰 평평한 석재 면, 희뿌연 재질 얼룩, 규칙적인 계단 띠, 굵은 옆뿌리와 약한 화로 수면 반사가 남습니다. 최신 독립 심사는 candidate52의6.1/10 Tier2이며58의 점수가 아닙니다. 사용자의 현재 전달 지시에 따라 새 심사와 추가 개선은 보류합니다.

증거: `Migration/Evidence/AtmosphereV2/candidate-58/SELF_REVIEW.md`, `Migration/Evidence/AtmosphereV2/player-58/VALIDATION.md`. 실행 파일은 `Unity/Vesper/Builds/VesperPreview/Vesper.exe`이며 빌드 폴더는 Git 제외입니다. 원본 브라우저/첫 Unity 장면 및 과거 증거는 보존합니다. 아래 기록은 과거 상태입니다.

# 최신 저장 장면 — candidate52 검증 및 구조 수정 재개, 2026-09-09

**RESUMED_BY_USER / UNITY_ATMOSPHERE_V2_IN_PROGRESS / VISUAL_TARGET_NOT_MET**. 현재 저장 장면은52, 실제 full/orbit/zoom/slice와 이전 과광택 카메라 glare-orbit 총5구도를 직접 열었습니다. 오류0/누락0/반사146. PavingV15는 확인된 석판 한 개만11mm 낮추고 나머지 메시를 보존합니다. ContactV14와 KnightV7 실제 통합 완료. 미세 광물 주파수/거칠기와 수면의 공통 반사 환경을 수정했고 화로 범위3.6m로 중앙 계단의 갈색 띠를 줄였습니다. 둥근 판석·약한 물웅덩이/젖은 잔광·석조 반복은 여전히 목표 미달입니다.

`candidate-52/SELF_REVIEW.md`와 새 독립 `verdict-unity-8.md`: **6.1/10, Tier2**. 이전41의6.0에서 소폭 개선이며 목표 미달입니다. player52 빌드 오류0/경고0, D3D12 비계측 자연 루프 static49.8825/walk50.7176/orbit50.1631/zoom50.4290FPS. 오류0/all-focused/다른렌더·무거운검증 없음; 표시장치 present/가림 증거 아님. 별도 motion389프레임/33.424965m/9.648–10.660Hz/누락0/오류0/all-focused이며 뿌리3목적지 도착과 원본7프레임을 직접 확인했습니다. 넓은 반광·단순한 전면 갑옷·외벽 반복은 이동 중에도 남았습니다. 모든 권한을 재허용한 뒤에도 Windows Computer Use는 native pipe unavailable, 최신 직접 마우스/키보드 검증 미완료입니다. 반복 권한 요청 없이 나머지 검증을 계속합니다.

같은 문제가 반복되어 스킬의 정체 접근 규칙에 따라 구조 수정에 들어갔습니다. 새 PavingV16은 전경10장만 실제 절리선/각진 면/국소 줄눈으로 다시 만드는 시제품입니다. MasonryV16은5계단 코스·화면에 큰 하부8석재·보이는 외벽 구간을 새 파단면 구성으로 재작성 중입니다. TreeV16은 기존의 단일 바닥점 대신 뿌리 끝 전체 단면이 실제 틈/덮개 아래로 내려가도록 수정 중입니다. 모두 새 소스 폴더 작업이며 아직 Unity 미통합/미채택입니다. 원본52 및 과거 증거를 유지합니다. HEAD589910f 이후48–52 변경은 로컬 검증 이정표 커밋 준비 중.8/10·60FPS·사용자 채택 미완료이며 작업 중/안전정지 아님.

# 이전 저장 장면 — candidate50 재질 진단, 2026-09-09

작업 중/완료 아님.49에서는 수면 반사 하늘을 석재 IBL과 같은 환경으로 맞춰 푸른 얼룩을 줄였습니다.50에서는 돌 F0와 별도 빗물 막을 복원해 석조의 젖은 세부가 늘었으나 바닥의 넓은 은색 반광이 다시 강해졌습니다. 둘 모두 네 구도를 직접 검토했고 오류0/누락0, 각 자기 검토에 미달을 기록했습니다.50 저장 장면은 PavingV14/ContactV14/KnightV7이며51용 미세 광물 normal/roughness 주파수 수정은 코드만 적용, 아직 재생성 전입니다. PavingV15는 진단에서 불꽃 core를 가리는 것으로 확인된 석판 한 개만11mm 낮추는 별도 소스 검증/Blender 비교 중입니다.

48의 후속 검증은 완료했습니다. 같은 D3D12 player에서 공간 그림자47.81–48.90FPS, 통합 그림자47.19–47.80FPS로 차이는0.49–1.10FPS입니다. 전체47→48 이득을 공간 분할 덕분이라고 설명하지 않습니다. 빌드 오류0/경고0, 두 실행 오류0/all-focused/다른렌더 없음. 별도 motion390프레임/33.471m/9.66–10.77Hz/누락0/오류0/all-focused이며 뿌리 주변 세 목적지에 모두 도착한 기록과 원본0090/0103/0113을 직접 확인했습니다. 직접 입력/표시장치FPS 아님.49/50의 player 결과로 재사용하지 않습니다.

최신 독립 점수는 candidate41의6.0/Tier2 유지. 다음51의 실제 자기 검토 후 준비된 후보만 새 독립 심사 예정입니다.8/10·60FPS·사용자 최종 채택은 미완료. 마지막 커밋589910f 이후 변경은 미커밋 상태입니다.

# 이전 저장 장면 — candidate48 진단, 2026-09-09

현재 작업 중이며 완료/안전정지 아님. PavingV14(493개/104,872tri), ContactV14(정확히50개 잔해 제거/49개 보존/새1,084tri), KnightV7을 실제 Unity 장면에 통합했습니다. 네 구도와 reflection.png 직접 검토, 오류0/누락0/반사109. 큰 판석과 면 음영·망토 주름은 개선됐지만 흐린 수면·약한 화염 반사·계단 밴딩이 남아 새 독립 심사 준비 미달입니다. 최신 독립 점수는 candidate41의6.0 유지. `candidate-48/SELF_REVIEW.md` 참조.

정확한 화로 그림자492,370tri를167개 공간 청크로 나눴고 기존 통합 메시를 비활성 보존했습니다. 동일player의 `-vesperUnpartitionedFireCasters`로 비교할 예정이며 현재 성능 개선 확정 전입니다. player48 빌드 중. 보행 검사기는 실제 route 완료를 기준으로 다음 목적지로 전환하고 도착 기록을 추가했으며, 근접 뿌리 구간을9초로 늘렸습니다. 이 새 검사기의 player 실행은 아직 전입니다. Windows 권한 재허용 후에도 list_apps는 native pipe unavailable, 최신 직접 입력 완료 아님.

# 이전 저장 장면 — candidate47 진단, 2026-09-09

로컬 검증 이정표는 `589910f`(candidate47 구조/그림자 진단 보존)입니다. 이후 작업으로 probe의 목적지 전환을 실제 경로 완료 기준으로 고쳤고 KnightV7 입력을 빌더에 연결했습니다. 이 두 변경은 아직 새 Unity 실행 전이며 저장 장면은47입니다.

후속47검증: 동일 실행 파일 D3D11 강제 실행은44.68–45.47FPS/오류0/all-focused로 소폭 빠르나60미달이며 기본API는 D3D12 유지. 별도D3D12 motion396프레임/20.606m/9.97–11.20Hz/오류0/누락0/all-focused. 직접0034/0100/0132/0200/0335/0395를 열었고 뿌리 첫 접근은 유효하나 검사기가 snapped grid 도착과 요청 좌표의.15m 차이를 처리하지 못해 첫 목적지에서 멈췄습니다. 전체뿌리 경로 검증 완료 아님, 다음 probe를 실제 경로 완료 기준으로 고쳐 다시 검사할 예정입니다. Windows list_apps 재확인도native pipe unavailable. 반복 권한 요청 없이 나머지 작업을 계속합니다.

candidate47은 PavingV13의866개 이웃 판석을 통합한 진단입니다. 실제4구도와 player static을 열어 확인했고 돌 구분은 개선됐지만 둥근 패드 인상/작은 돌 과다/일부 cap 부채꼴 음영/약한 젖은 질감이 남아 심사 준비 미달입니다. 최신 독립 점수는 여전히 candidate41의6.0입니다. `candidate-47/SELF_REVIEW.md` 참조. 같은 player47-fixed(D3D12,빌드 오류0/경고0)3조건 cleanFPS: 국소 그림자42.20–43.20, 전체 메시28.51–28.73, 그림자 없음50.42–51.16. 모두 focused/오류0/다른렌더·무거운검증 없음, 실제표시FPS/직접입력 아님. 국소 그림자는 약327만 중49.8만삼각형을 보존하며 화면의 큰 그림자 관계를 유지했습니다. 첫full-caster진단은 보조메시 표시버그로 무효, fixed별도증거가 유효합니다. 새 뿌리 주변 motion과 API비교 예정. KnightV7 소스가 준비됐고 ContactV14 실제렌더/PavingV14큰판석 수정은 진행 중, 아직 Unity 미통합입니다. 현재 작업 중이며 완료/안전정지 상태가 아닙니다.

# 이전 저장 장면 — candidate46 진단, 2026-09-09

candidate46 저장/실제4구도 검토 완료, `candidate-46/SELF_REVIEW.md`. TreeV12+StairsV13+정확히8개portalV13+국소 그림자 메시를 통합했습니다. 오류0/누락0/반사107. 뿌리의25점 world hull과.28m 여유를 생성했고167개 경로/구간20점 검사를 통과했습니다. 보행 실측은 아직 없습니다. 두 화로의 전체 입력3,144,963삼각형 중 실제 광원 범위와 겹치는491,006삼각형을 보존한 그림자 메시를 따로 생성했습니다. 화면 동일성/FPS 개선은 아직 비교 전입니다. PavingV12 징검돌 문제와 계단 밴딩 등이 남아 심사 준비 미달/새 점수 없음. PavingV13은 소스 엄격 검사 통과 후 실제 미리보기 검토 중입니다. 현재 작업 중이며 완료/안전정지 상태가 아닙니다.

# 이전 저장 장면 — candidate45 진단, 2026-09-09

현재 저장 장면은 candidate45(PavingV12)입니다.4구도를 직접 열어 보니24개의 돌만 올라와 징검돌처럼 보여 자기 검토에서 심사 준비 미달로 보류했습니다. 새 독립 점수는 없으며 candidate41의6.0이 최신입니다. `candidate-45/SELF_REVIEW.md`에 같은 player45-diagnostics 실행 파일의4조건 자연 프레임 실험을 기록했습니다. 기본 soft32FPS, 그림자 없음56FPS, hard32FPS, 바닥 그림자 없음32FPS. 모든 구간 focused/오류0/다른Unity·Blender·무거운 검증 없음이며 표시장치 present나 직접 입력 검증은 아닙니다. 점광원 그림자 비용을 확인했고, 가시 메시/달빛 그림자를 보존한 정확한 국소 그림자 메시 코드를 작성 중입니다. 아직 컴파일·렌더·성능 검증 전입니다. 계단V13은 소스/미리보기/해시 검토를 거쳐 빌더에 연결했으나 Unity 실행 전입니다. TreeV12와 PavingV13 및 portalV13은 소스 렌더 검토 중입니다. 현재 작업 중이며 완료/안전정지 상태가 아닙니다.

# 이전 저장 장면 — candidate44 진단, 2026-09-09

현재 장면은 candidate44 조명/수면/효과 진단입니다. `candidate-44/SELF_REVIEW.md`와 `lighting-diagnosis-41.md` 참조. 새 독립 점수는 없으며 최신 심사는 아래 candidate41의6.0입니다. 로컬 검증 이정표 커밋은 `c857436`이고 이후 수정은 진행 중입니다.

실제 광원 분리와 player41의 정확한 회전 카메라 재현으로 바닥 은색 광택의 원인을 달빛+중복 코팅으로 확인하고 제거했습니다. 별도 물 위의 화로 반사, 석재 SH 간접광, 국소 그림자/반사광, 룬 빛 번짐과 불씨를 수정했습니다.44의4구도 직접 검토/오류0/반사113. player44 빌드 오류0/경고0이나 비계측 자연 루프31.50–31.83FPS로 크게 하락했습니다. all-focused/오류0/다른렌더·무거운 자산검증 없음. 추가 점광원 그림자를 의심하며 분리 측정할 예정입니다. PavingV12는 자체 검사를 통과하여45에 통합 중이고 MasonryV13/TreeV12는 면·체적·이미지 결함 수정 중/아직 미통합입니다. 새 구조 후보를 준비한 뒤 심사와 성능/동작 검증을 이어갑니다. 작업 중이며 안전정지/완료 상태가 아닙니다.

# 이전 진행 기록 — candidate41, 2026-09-09

**RESUMED_BY_USER / UNITY_ATMOSPHERE_V2_IN_PROGRESS / VISUAL_TARGET_NOT_MET**.
현재 저장 장면은 candidate41이며, 아래 candidate36 기록은 이전 이정표입니다.
로컬 이정표 커밋은 `48b9d84`; 이후 변경은 현재 검증 중입니다.

- `Migration/Evidence/AtmosphereV2/candidate-41`의 실제 Unity full/orbit/zoom/slice를 직접 비교했습니다. 셰이더/런타임/누락 스크립트 오류0, 반사108회. 최종 채택된 화면이 아닙니다.
- 새 독립 심사는 **6.0/10, Tier2**, `verdict-unity-7.md`. 이전 candidate36은5.8. 나무의 조형은 크게 개선됐지만 바닥이 얕은 갈라진 판처럼 보이고, 판석/물웅덩이 분리와 석조 밴딩이 여전히 큰 미달입니다. 깨끗해진 일부 문 기둥의 파손 디테일은 국소 후퇴로 판정됐습니다.
- TreeV11: imagegen 입력 → Meshy7 Ultra 1건(35크레딧) → Blender157,999삼각형 파생. 원본3,073,248삼각형/맵과 해시 보존. 실제 Unity 통합 완료. 넓은 가지의 부푼 접합부, 짧은 뿌리, 측면에서 납작한 수관은 남았습니다. 수피 과광택은41에서 낮췄습니다.
- PavingV11: ambientCG Tiles130 CC0 촬영 자료의 연속 색/높이/GL노멀/거칠기/AO를 적용했습니다. 최종 UV주기9.2×4.6m는 원본의4배인 아트 선택이며40mm 변위는 실측 보정값이 아닙니다.155,742삼각형. 작은 격자는 줄었지만 개별 판석의 입체감이 부족하여 다음 구조 수정 대상입니다.
- MasonryV11의90개 일체형 계단이 정확히278개 기존 riser/tread/lip을 대체했습니다. MasonryV12의 좁은 어깨 단면과 불균등 코스도 통합했습니다. 계단/외벽의 갈색 띠와 단순한 블록 면은 해결되지 않았습니다.
- KnightV6: 기존 망토를 보존하면서 어깨 두 메시의120개 법선 이상 면을 수정하고, 기존80삼각형 투구 껍질을1920삼각형으로 보완했습니다. 실제 Unity 통합 완료. 원시 천 시뮬레이션3회가 실패했다는 이전 제한은 그대로입니다.
- player41 빌드 오류0/경고0. 비계측 자연 루프 static54.706/walk55.350/orbit54.550/zoom55.101FPS로60미달, 오류0/all-focused/다른렌더 없음. 표시장치 present/가림 검증은 아닙니다. 별도 연속 기록324프레임/13.436m/10.04–11.19Hz/누락0/오류0. 직접 원본 프레임을 열어 보행 회전과 카메라 변화, 회전 시 바닥의 넓은 은색 광택 결함, 최저 시점 외벽의 단순함을 확인했습니다. 영상은 실제 시간 간격의 VFR이며60FPS 영상이나 직접 입력 결과가 아닙니다. Windows native pipe 연결 실패로 최신 직접 입력 검증은 미완료입니다.
- 다음 작업은 판석의 실제 경계/두께와 수면 분리, 계단·외벽 밴딩의 구조 원인을 함께 해결하는 것입니다.8/10,60FPS 검증 및 사용자 최종 채택은 미완료입니다. 과거1시간 제한은 적용하지 않습니다.

# 이전 작업 재개 진행 기록 — 2026-09-09

**RESUMED_BY_USER / UNITY_ATMOSPHERE_V2_IN_PROGRESS / VISUAL_TARGET_NOT_MET**. 사용자의 명시적 재개 지시로 아래 PAUSED_BY_USER 상태를 해제했습니다. 실제 시작 상태는 candidate28의 미커밋 변경이며 HEAD는0ade1b8입니다. 시작 시 Unity/Blender/player 프로세스0개. 기존 변경의 binary patch와 저장 장면을 `.dream-loop/unity-atmosphere-v2/resume-29-baseline`에 보존했습니다. 새 증거는 candidate29 이후 별도 경로로 기록합니다. 과거 점수/FPS를 새 후보 결과로 사용하지 않습니다.

- 현재 저장 장면은 **candidate36**입니다. 증거 `Migration/Evidence/AtmosphereV2/candidate-36`: 오류0/누락0/반사114. TreeV10 최종과 PavingV10 마모/정방향 메시, 분리 수면의 유전체 Fresnel을 적용했습니다. 최종 채택 아님.
- 최신 독립 점수는 **candidate36의5.8/10, Tier2**, `Migration/Evidence/AtmosphereV2/verdict-unity-6.md`. candidate30은5.6, 31–35는 진단/자기 검토이며 새 점수 없음. 이전5.4는candidate23, 브라우저6.5는 별도 과거 심사입니다.8/10/사용자 최종 채택 미달. 반복 격자·석조 밴딩·나무의 매끈한 굵은 가지가 핵심 미달이며 구조적 자산 전략을 재검토 중입니다.
- Rock05 색/GL노멀/선형거칠기/AO를 적용했습니다. 출처/MD5/SHA256은 `Migration/Source/AtmosphereV2/PhotographicStone/provenance-rock05.json`. Rock01/기존 생성 광물 자료 보존. 수면과 석재 IBL의 구름 반사를 각각 낮추고, 별도 수면과1024 반사 텍스처를 유지했습니다.
- 반복 지적에 따라 TreeV10 수관/뿌리와 PavingV10 지상 포장을 Blender에서 재구성했습니다. 나무 접합 턱과 포장 역방향 컬링은34에서 수정됐습니다. 잘못된 winding 검사와 거절된 나무 접합 후보는 Source 패키지/33증거에 보존했습니다. 최종 포장114,550삼각형/426개 석재, 나무90,768삼각형.36에서 최종 재생성 입력을 반영했지만 심사는 여전히 Tier3 미달입니다.
- KnightV5의7메시는 이미candidate28에 통합되어 있었습니다. 이를 보존하고 망토 가독성을 조정했습니다. 원시 천 시뮬레이션3회는 실패 자료이며 현재 망토는 주름을 이용한 아트 디렉션 결과입니다.
- player30 비계측 자연 루프: static44.49/walk44.69/orbit44.24/zoom45.21FPS, 오류0/all-focused. 당시 다른 Unity/Blender 렌더 없음. 실제 표시장치 present FPS/가림 확인 아님. 계측player27과 직접 비교하지 않습니다.
- player36 빌드 성공/오류0/경고0. 초기화 셰이더 경고와 URP clone 이름 경고를 수정했습니다. 비계측 자연 루프 static58.753/walk59.829/orbit59.909/zoom59.931FPS, p95 각각17.556/16.688/16.680/16.688ms, 오류0/all-focused, 다른Unity/Blender 렌더 없음. 표시장치 present/가림 확인 아님. walk에는 도착 후 정지가 포함됩니다.
- player36 자동 연속 기록318프레임/약10.02–10.94Hz/13.478m/오류0/누락0/all-focused. 직접 원본 프레임에서 상하 반전 수정, 보행 자세·회전·줌·카메라 한계범위를 확인했습니다. 최저 시점은 외벽 반복과 배경의 단순함을 더 드러냅니다. 기록은 비계측FPS나 직접 입력 결과와 별개이며 영상은 실제 타임스탬프 간격으로 인코딩했습니다. 완전한 움직임 품질/사용자 플레이 채택 아님.
- 사용자가 직접 조작에 모든 권한을 허용했지만 Windows Computer Use는 재확인해도 `native pipe is unavailable`로 연결되지 않습니다. 최신 직접 마우스/키보드 검증 미완료. player16 기록을 최신 검증으로 쓰지 않습니다.
- Higgsfield CLI 로그인 연결 확인. Meshy API balance HTTP200/2584크레딧 확인 후, TreeV11용 imagegen 단독 나무 입력으로 Meshy7 Ultra/4k PBR 작업1건을 생성했습니다. task `01a081af-3cd5-7223-a3cf-715978cae838`,35크레딧. 아직 생성/Blender/Unity 검토 중이며 채택 아님. 인증정보는 저장/출력하지 않았고 다른 프로젝트는 읽기만 했습니다.
- 다음: TreeV11 이미지 기반3D 자산, PavingV11 촬영 기반 높이맵, 석조 밴딩의 구조 원인 해결 → 실제 Unity4구도 자기 검토 → 준비된 후보 새 독립 심사 → 새player 성능/연속 동작/가능한 직접 조작 → 검증된 변경 로컬커밋. KnightV6는 별도 자산 검토 중/Unity 미통합. 현재 작업 중이며 완료/안전정지 상태가 아닙니다. 과거1시간 제한 없음.

# 이전 안전 정지 체크포인트 — 2026-09-08

**PAUSED_BY_USER / UNITY_ATMOSPHERE_V2_IN_PROGRESS / CANDIDATE28_SAVED / VISUAL_TARGET_NOT_MET**. 사용자의 “안전지점에서 종료해줘” 지시에 따라 새 반복을 중단하고 candidate28을 저장했습니다. 기술 검증·시각 품질·성능·사용자 최종 채택은 별개이며, 재개 지시 전 추가 작업을 시작하지 않습니다.

- 브랜치 `unity-migration`. 재개 기준은 이 체크포인트를 포함하는 최신 로컬 커밋이며 원격/push는 없습니다. 시작 기준 커밋은 `0ade1b8`이었습니다.
- 현재 저장 장면은 `Unity/Vesper/Assets/Vesper/Scenes/VesperAtmosphereV2.unity`, **candidate28 반사 선명화 + 석재 PBR 재조정 + KnightV5 통합 진단 후보**입니다. 실행 가능한 중간 상태이며 시각 채택된 결과가 아닙니다.
- 실제 캡처 증거는 `Migration/Evidence/AtmosphereV2/candidate-28`. full/orbit/zoom은1536×1024, slice는1037×739이며 `capture.json`은 Intel Arc130V에서 셰이더 오류0, 런타임 오류0, 누락 스크립트0, 반사 갱신120회를 기록합니다.
- 직접 비교 결과: candidate27의 흰 구름 같은 넓은 수면 블러는 크게 줄었고 따뜻한 반사 형상과 KnightV5의 완만한 세로 주름/불균일한 밑단이 Unity 화면에 나타났습니다. 그러나 젖은 구역은 아직 어두운 얼룩처럼 뭉치고 Rock01 요철은 전체 화면 거리에서 평탄하며, 포털/계단 반복과 나무 조형도 남았습니다. **자기 검토에서 독립 심사 준비 미달**로 판정했으며 새 점수를 부여하지 않았습니다.
- KnightV5는 `Migration/Source/AtmosphereV2/KnightV5/knight-v5-unity-meshes.json`에서 기존7개 GameObject/Transform/재질을 유지한 채 통합했습니다. 망토7,736삼각형이며 원시 천 시뮬레이션 성공으로 주장하지 않습니다. Unity 장면 통합과 정적 캡처만 확인했고 애니메이션/연속 이동 검증은 하지 않았습니다.
- 이번 라운드는 Windows player 빌드, 비계측 FPS, 직접 입력, 연속 이동·회전·줌, 새 독립 심사를 실행하지 않았습니다. 마지막 독립 Unity 점수는 여전히 candidate23의5.4/10 Tier2이고, 마지막 성능 자료도 이전 체크포인트의 별도 조건 자료입니다. Dream Loop8/10,60FPS,사용자 최종 채택은 미달입니다.
- 석재 셰이더의 DepthNormals `normalTS`를 명시적으로 초기화해 기존 잠재적 미초기화 경로를 수정했습니다. 새 player 빌드를 하지 않았으므로 기존5개 빌드 경고가 모두 해소됐다고 주장하지 않습니다. `ProjectSettings.enableFrameTimingStats`는0입니다.
- 첫 Unity 실행 래퍼의 진행 출력이 없어 상태 확인 중 두 번째 호출이 잠시 겹쳤지만, 단일 candidate28 출력 경로의 완전한 캡처를 확보했고 이후 모든 Unity/Blender/player 프로세스가 정상 종료한 것을 확인했습니다. 종료 시 생성·에이전트 작업은 없습니다.
- 보존: `main`, `browser-baseline-2026-09-08`, 브라우저2413d5d, `public`, 루트 `ArtSource`, `preview.png`, `VesperMigrationSlice.unity`, 원래 `Generated`, 과거 `.dream-loop`/Migration 증거는 수정하지 않았습니다.

재개 순서: 이 최신 블록과 Git/프로세스 확인 → concept/browser/candidate23/26/27/28 직접 비교 → candidate28을 보존한 새 경로에서 Rock05의 더 거친 **노멀·거칠기만** 비교하고 Rock01의 차가운 색 유지 → 수면 반사 밝기/투명도로 어두운 얼룩 축소 → 자기 검토 통과 후보만 새 독립 심사 → 동일 조건 비계측 player 성능과 연속 이동·회전·줌 검증. 전체 화면 색보정만으로 완료 처리하지 않습니다.

## 이전 candidate27 안전 정지 기록

**PAUSED_BY_USER / UNITY_ATMOSPHERE_V2_IN_PROGRESS / VISUAL_TARGET_NOT_MET**. 사용자의 “안전지점에서 멈춰줘” 지시에 따라 중단했습니다. 재개 지시 전 새 반복 작업을 시작하지 않습니다. 기술 검증·시각 품질·사용자 최종 채택은 별개입니다.

- 브랜치 `unity-migration`. 최신 안전 저장 커밋은 `git log -1 --oneline`으로 확인합니다. 직전 커밋 `45bbc35`, 그 이전 `93bc56c`. 원격/push 없음.
- 현재 저장 장면은 `Unity/Vesper/Assets/Vesper/Scenes/VesperAtmosphereV2.unity`, **candidate27 실측 석재 진단 후보**입니다. 실행 가능한 중간 상태이며 시각 채택된 결과가 아닙니다. candidate26보다 돌이 지나치게 매끈해져 자기 검토에서 미달 판정했습니다. 전체 변경을 되돌리지 말고 다음 재질 비교에 활용합니다.
- 최종 재개 가능성 검증: 새 Editor에서 `VesperPlayerBuild.CaptureCheckpoint` 실행 → 프레임 시간 프로파일링 설정을 Editor API로 끄고 저장 장면을 재캡처. 증거 `Migration/Evidence/AtmosphereV2/checkpoint-27`. slice1037×739, full/orbit/zoom1536×1024. 구체적 오류 수는 `capture.json` 참조.
- 현재 코드/장면에 적용: 타일 이음새를 가로지르는 별도 얕은 수면, TreeV9 수피/뿌리/곡선 가지(74,671삼각형), StoneV7 및 MasonryV8 여섯 변형/두 외벽 코스, 긴 외벽을 나눈1,739코스, 일부 바닥 정렬/크기와 인레이 단절. 기존 달빛·화로·반사·원경·룬·불씨·풀 바람·이동/카메라 구현 유지.
- candidate26은 `.dream-loop/unity-atmosphere-v2/round-26-varied-masonry`, candidate27은 `round-27-photographic-stone`. 추적 증거 `Migration/Evidence/AtmosphereV2/candidate-26`, `candidate-27`. 둘 다 셰이더/런타임/누락 스크립트 오류0. 27에서 색 이미지 기반 요철을 분리된 색/GL 노멀/선형 거칠기 맵으로 바꾸고 Forward/DepthNormals의 노멀 계산을 통일했습니다.
- 현재 석재 외부 맵: Poly Haven Rock01, Rob Tuytel, CC0. URL/해시 `Migration/Source/AtmosphereV2/PhotographicStone/provenance.json`. Rock05 맵은 `.dream-loop/unity-atmosphere-v2/pbr-rock`에 다운로드/해시 확인만 했으며 **미적용**입니다. 기존 생성 광물 텍스처도 보존했습니다.
- 새 망토 `Migration/Source/AtmosphereV2/KnightV5`는 **Blender 미리보기/데이터 검증까지만 완료, Unity 미통합**. 시뮬레이션 주름에 기존 폭0.714m를 복원한 아트 디렉션 결과, 망토7,736삼각형. 다른6개 메시/Transform/재질 보존. 현재 Unity 기사는 여전히 KnightV3입니다. 원시 천 시뮬레이션3회는 폭/정착 조건 실패로 보존했고, 최종 후보를 순수 물리 평형 결과라고 부르지 않습니다.
- 최신 독립 Unity 점수는 **candidate23의5.4/10, Tier2**입니다. 이전4.5→4.8→4.9→5.4. 24–27은 새 독립 심사에 제출하지 않았습니다. 브라우저6.5를 Unity 점수로 쓰지 않았습니다. Tier3 재질/반복/나무 및8/10 목표는 미달입니다.
- Windows player-v27-timing 빌드 성공/오류0/경고5, 런타임 오류0. 1536×1024 자연 루프에서 static29.75,walk29.02,orbit30.62,zoom32.14FPS; GPU 중앙값 약31–35ms. **FrameTiming 계측 빌드의 진단값**으로, 비계측 candidate23의50.7–51.8FPS와 동일 조건 비교가 아닙니다. 성능 저하 원인은 아직 확정하지 않았습니다. 60FPS 미달입니다.
- player27 보고서는 모든 프레임focused로 기록됐지만 UI 캡처 시도에서 게임 화면을 확보하지 못했습니다. 앞선 “다른 창에 가려진 구간” 설명은 보고서로 입증되지 않았으므로 실제 가림/표시 FPS를 확정하지 않습니다. 표시장치 present 추적도 아닙니다. 직접 입력 검증은 앞선 player16(드래그/클릭/휠/R,5.01m이동,오류0)과 구분합니다.
- 남은 경고: D3D11 빌드의 StoneSurfaceNormal/normalTS 잠재적 미초기화 경고2건, 기존 Flame pow 경고 등 총5. 컴파일 오류/실행 오류는0이지만 경고를 숨기지 않습니다. 다음 코드 변경 전에 out 변수 초기화 경로를 점검합니다.
- 전용 자산 `Assets/Vesper/AtmosphereV2`, 재생성 입력 `Migration/Source/AtmosphereV2`. **기존 VESPER/Build migration slice 메뉴는 원본 Generated/장면을 재작성하므로 후보에 사용하지 않습니다.** 재생성은 `VesperAtmosphereBuild.BuildAndCapture`, 저장 장면 검사만 할 때는 `VesperAtmosphereCapture.Run`. 명령은 `Migration/Evidence/AtmosphereV2/README.md`.
- 보존: `main`, `browser-baseline-2026-09-08`, 브라우저2413d5d, 원래 Unity 장면/Generated, `public`, 루트 `ArtSource`, `preview.png`, 과거 `.dream-loop`. 다른 Unity 프로젝트 수정 없음. 씬/재질/설정/메타는 Editor API로만 변경합니다.
- 정지 시 진행 중 생성/에이전트 작업 없음. 마지막 Unity 캡처 프로세스도 정상 종료했습니다. 무거운 재생성/빌드/렌더는 중복 실행하지 않습니다. 종료/보존 최종 보고 `Migration/Evidence/AtmosphereV2/safe-stop.json`.

재개 순서: 이 문서와 실제 Git/프로세스 확인 → concept/candidate23/26/27 직접 비교 → 실측 석재의 과도한 평활화와 물 반사 흐림 원인 해결 → 준비된 KnightV5 Unity 통합/비교 →1536×1024 자기 검토 후 새 독립 심사 → 동일 조건 비계측 성능 및 연속 입력 검증. 새 작업은 사용자 재개 지시 후 진행합니다.

## 이전 첫 이식 기록

현재 **UNITY_FIRST_SLICE_IMPLEMENTED / VISUAL_PARITY_PENDING**. 사용자가 지금 Unity로 옮겨 이어서 제작하기로 결정하고 Git 커밋 후 진행을 요청했습니다. 브라우저 기준을 보존하고 별도 Unity 프로젝트에 첫 비교 구역을 구현했습니다. 전체 이식, 시각 품질 유지, Dream Loop 8/10 및 실제 60 FPS는 완료 판정하지 않았습니다.

## Git과 프로젝트

- 경로: `C:/Users/brian/Dev/active/Dream Loop Astra`.
- 새 로컬 Git 저장소. 브라우저 보존 커밋 **`2413d5d`**, 태그 **`browser-baseline-2026-09-08`**, `main`에 보존.
- 현재 브랜치: **`unity-migration`**. Unity 첫 이식 커밋은 `git log -1 --oneline`으로 확인. 원격 저장소와 push 없음.
- Unity 프로젝트: **`Unity/Vesper`**, Editor **6000.5.7f1**, URP **17.5.0**.
- 장면: **`Assets/Vesper/Scenes/VesperMigrationSlice.unity`**. 이 장면을 열고 Play.
- 브라우저: `npm.cmd run dev`, `http://127.0.0.1:5173/`. 서버 생존은 재개 때 확인.
- `ArtSource`에 현재 기사/나무/석재 Blender 원본. 기존 `public`, `preview.png`, 과거 `.dream-loop` 증거 보존.

## 구현한 범위

기사·나무·광장·화로를 같은 구도로 비교하는 첫 Unity 구역입니다. 주변 원경 구조도 가져왔습니다. 실제 메시 95종, 소스 재질 22종, 인스턴스 4,711개를 가져왔고 깊은 기초 146개는 이번 비교에서 제외했습니다.

좌표/노멀/삼각형 방향 및 기사 계층을 변환했습니다. 석재/수피/불꽃/원경 이미지를 재사용하고 URP 재질, 바닥 평면 반사, 화로 조명, SSAO, 색보정을 구현했습니다. 클릭 이동 A*, 지연 카메라 추적, 드래그 회전, 휠 줌, R 초기화도 포팅했습니다. 일반 사용 중 임시 QA 코드는 활성화되지 않습니다.

브라우저에는 개발 전용 **U 내보내기**를 추가했습니다. 공유 Sprite 버퍼의 정점/UV 읽기 오류를 수정하고 회귀 테스트를 추가했습니다. Vite가 Unity 잠금 파일을 감시하지 않도록 제외했습니다. Unity 메시의 GPU 갱신과 재실행 후 색보정 유지 문제도 수정했습니다.

## 증거와 검증

- 비교 기준: `Migration/Reference/unity-browser-slice.png`.
- 실제 Unity 렌더: `Migration/Evidence/unity-slice.png`, 두 이미지 모두 **1037×739**. 전체 타깃 기준 해상도 1536×1024와 구분.
- 기술 보고: `Migration/Evidence/{import-report,validation,render-report,play-smoke}.json`.
- `node --test`: **5개 통과**, `npm.cmd run build`: 성공, 기존 번들 크기 권고 경고.
- Unity 검증은 경로 47개, 누락 스크립트, 재질, 저장된 색보정, 네이티브 캡처와 scripted Play 이동/반사를 검사합니다. 마지막 실행 값은 위 JSON 확인.
- 배치 Play의 명시적 렌더 요청 수는 실제 표시 FPS가 아닙니다. 직접 조작, 연속 체감 검증, Windows 빌드, 60 FPS 확인은 남아 있습니다.
- 전체 로그/중간 라운드/반사 원본 버퍼: `.dream-loop/unity-migration/`. 실패한 중간 결과도 보존했습니다.

## 다음 작업

1. 이 파일 → `Migration/README.md` → `Migration/Evidence/SELF_REVIEW.md` → 브라우저/Unity 실제 비교 이미지 확인.
2. 저장된 Unity 장면을 열어 Play 조작과 구도를 직접 확인. 재생성 메뉴는 `Generated`와 지정된 비교 장면을 다시 작성하므로 일반 리뷰에는 실행 불필요.
3. 우선 **젖은 바닥의 밝기·거칠기·불빛 반사, 화로의 번짐, 나무 그림자, 원경 안개**를 브라우저와 맞추기. 모델 교체나 기존 브라우저 라운드 되돌리기로 섞지 않기.
4. 이후 룬 선, 불씨, 안개/바람, 전체 카메라와 UI 등 남은 이식을 진행하고 Unity에서 Dream Loop 개선을 이어가기. 첫 비교 구역 확인과 전체 AAA 타깃 채택은 별개입니다.
5. 자기 검토에서 준비됐을 때 같은 해상도의 전체 타깃 캡처와 새 독립 심사. 브라우저 **6.5/10**을 Unity 점수로 사용하지 않기.

원래 Dream Loop 목표와 이전 지시: `Migration/Reference/concept.png`, `Migration/Reference/verdict-round-3.md`, 기존 `VALIDATION.md`. 이전 CHECKPOINT 원문은 보존 태그에서 확인할 수 있습니다. 별도 Unity 게임 프로젝트는 수정하지 않았습니다.

## 이전 Chrome 성능 진단

3D 없는 HTML에서도 rAF 약 1초 지연을 재현했고 사용자가 Chrome을 앞으로 가져온 뒤 코드 변경 없이 약 59.2회/초로 회복됐습니다. 창 노출/자동화 상태에 연동된 제한이 원인이며 Chromium 내부의 정확한 촉발 동작까지 확정하지 않았습니다. 브라우저 검증에는 연결된 Chrome을 보이게 유지하세요. 자세한 전후 증거는 `.dream-loop/cadence-diagnosis/REPORT.md`에 보존했습니다.
