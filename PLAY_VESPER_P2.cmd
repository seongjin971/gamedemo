@echo off
setlocal
set "VESPER_P2_EXE=%~dp0Unity\Vesper\Builds\VesperP2ClickFix\VesperP2.exe"
if not exist "%VESPER_P2_EXE%" (
  echo VESPER P2 build is missing. See PLAY_P2.md.
  pause
  exit /b 1
)
start "" "%VESPER_P2_EXE%" -screen-width 1536 -screen-height 1024 -screen-fullscreen 0
