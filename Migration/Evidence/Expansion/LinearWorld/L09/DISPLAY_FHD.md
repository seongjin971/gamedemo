# 사용자 요청 — FHD 전체화면

2026-09-11 후속 요청에 따라 PLAY_VESPER_ROAD.cmd를1920×1080 전체화면으로 변경했다. 이전1536×1024 창 모드에서 실행 인자만 변경했으며L09 실행본·장면·자산은 그대로다.

새 인자: `-screen-width 1920 -screen-height 1080 -screen-fullscreen 1 -window-mode exclusive -force-d3d12`.

실행 중 Screen.width/height가1920/1080임을 기존 관측 모드로 확인하고 원본 화면도 직접 검토했다. 오류0, 음원0. 기록은 [표시 확인](display-fhd-20260911-115426/report.json), [실제 FHD 원본](display-fhd-20260911-115426/manual-start.png). 확인용 프로세스만 종료한 후 같은 설정의 일반 플레이 실행본을 관측 옵션 없이 열어 두었다: [일반 실행 기록](display-fhd-20260911-115426/normal-play.json). 이동 묶음이나 성능 검사를 다시 실행하지 않았다.

Unity 공식 [Player 실행 인자](https://docs.unity3d.com/ja/current/Manual/PlayerCommandLineArguments.html)의 해상도/전체화면 설정을 적용했다. RoadR01/delivery-artifacts.json의 기존 실행기 해시는 이 사용자 요청 전 기록으로 보존하며, 이후 실행기 차이는 승인된 표시 설정 변경이다. 기존1536×1024 성능 수치를 FHD 측정 결과로 재사용하지 않는다.
