@echo off
setlocal
set "VESPER_P1_EXE=%~dp0Unity\Vesper\Builds\VesperExpansion\VesperAdventurer.exe"
if not exist "%VESPER_P1_EXE%" (
  echo VESPER P1 player build is missing. See PLAY_EXPANSION.md.
  pause
  exit /b 1
)
start "" "%VESPER_P1_EXE%" -screen-width 1536 -screen-height 1024 -screen-fullscreen 0
