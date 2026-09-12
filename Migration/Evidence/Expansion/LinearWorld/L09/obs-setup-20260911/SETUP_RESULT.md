# OBS 설치 및 녹화 설정 완료 — 2026-09-11

OBS Studio 32.2.1을 공식 winget 패키지로 설치했다. 설치 프로그램 SHA-256 검증이 통과했다. 프로필 `VESPER FHD 30`, 장면 모음 `VESPER FHD`, 장면 `VESPER`가 활성화되어 있다.

## 최종 설정

- 캔버스/출력 모두 1920×1080, 30 FPS, NV12/Rec.709/제한 범위.
- Intel QuickSync H.264 하드웨어 인코더 `obs_qsv11_v2`, ICQ 21, TU4, High, 키프레임 2초, B-frame 3.
- Hybrid MP4, 저장 폴더 `C:\Users\brian\Videos\VESPER`.
- 게임 캡처는 OBS가 열거한 `VESPER Unity migration:UnityWndClass:VesperLinear.exe`를 선택했다. D3D12 공유 텍스처 캡처 성공을 로그에서 확인했다.
- 게임 캡처 `limit_framerate=false`. 초기 true 설정에서 보인 짧은 반복 프레임을 줄이기 위해 조정했다.
- 현재 2880×1800 화면의 게임 백버퍼에 포함된 검은 여백은 bounds outer + crop으로 제외한다. 출력에 게임 화면과 UI가 잘리지 않고 가득 차는 것을 실제 녹화 프레임에서 확인했다.
- 전역 데스크톱/마이크 소스 없음, 게임 오디오 캡처 false. 녹화의 AAC 트랙을 PCM으로 디코딩한 전 샘플이 0이었다.
- Ctrl+Shift+F9 시작, Ctrl+Shift+F10 종료. 바인딩이 현재 프로필에 저장되어 있다.
- 방송/자동 녹화/리플레이 버퍼를 시작하지 않았다. 설정 검증 Lua는 finished=true로 저장되고 타이머가 제거되었다. 향후 실행에서도 자동 동작하지 않는다.

## 검증 결과와 한계

실제 L09 실행본의 기존 opt-in 성능 프로브로 정지/걷기/카메라 회전을 녹화했다. 원래 전체 이동 검사 묶음이나 빌드/장면 생성은 실행하지 않았다.

초기 68.17초 녹화와 최종 67.73초 녹화는 모두 1920×1080, 30/1 FPS였다. 최종 영상의 디코딩 타임스탬프 간격은 약 33.333ms로 일정했다. OBS 로그에는 렌더링/인코딩 지연 항목이 없었다.

160×90 밝기 영상의 프레임 차이를 이용한 보조 검사에서, 움직이는 프레임 사이의 거의 같은 프레임 구간은 초기 183회에서 최종 27회로 감소했다. 최종 최대 길이는 2프레임이다. 이는 휴리스틱이며 정확한 드롭 프레임 수나 완전한 무끊김 판정이 아니다. 두 테스트의 시작 시점과 화면 맞춤도 달라 엄밀한 동일 프레임 A/B는 아니다. 최종 원본 끝부분에는 자동 테스트 게임 종료 후 검은 화면이 포함되어 있으며, 전달용 샘플에서는 그 구간을 제외했다.

현재 설치된 computer-use의 네이티브 연결 파이프가 없어 실제 키 입력이나 OBS 버튼 클릭은 검증하지 못했다. 설정 및 녹화 시작/중단은 OBS의 공식 Lua API로 실행했고, 실제 MP4 및 OBS 로그로 검증했다. 앱 제어를 위한 별도 네이티브 도우미나 인증 없는 네트워크 서버를 만들지 않았다.

## 파일

- `verification.json`: 초기 설정 두 녹화 분석.
- `verification-final.json`: 최종 이동 녹화 분석.
- `final-config/`: 최종 프로필 및 장면 설정 사본.
- `final-motion-frame.png`, `final-fit-frame.png`: 실제 녹화 프레임.
- `test-videos/`: 이번 설정에서 만든 원본 3개를 보존. 분석 JSON의 원래 Videos 경로에서 이 폴더로 이동했으며 파일명/내용은 동일하다.
- `C:\Users\brian\Videos\VESPER\VESPER_FHD_TEST.mp4`: 최종 원본에서 추출한 약 58초 무음 H.264 샘플. 재인코딩하지 않았다. 구간별 테스트 이동이므로 연속 산책을 담은 최종 홍보 영상은 아니다.
- `game-preservation.json`: L09 EXE와 Assembly-CSharp.dll이 기존 전달 해시와 일치함.
- 루트 `RECORD_VESPER.cmd`, `OBS_RECORDING.md`: 다음 녹화 실행 및 사용법.

기존 Unity 코드·장면·공유 자산·빌드와 PLAY_VESPER_ROAD.cmd는 이번 설정에서 변경하지 않았다. OBS 설정 갱신 시 녹화를 중단하고 장면을 저장한 뒤 설치 직후의 자체 OBS 프로세스를 재시작했다. 해당 재시작 표시 파일만 `setup-restart-markers/`에 보존했다.

공식 근거: https://obsproject.com/kb/quick-start-guide , https://obsproject.com/kb/hardware-encoding , https://docs.obsproject.com/scripting . 설정 키는 `reference/`의 OBS 32.2.1 소스로 확인했다.
