@echo off
setlocal
set "VESPER_RUN_EXE=%~dp0Unity\Vesper\Builds\VesperRun\VesperRun.exe"
if not exist "%VESPER_RUN_EXE%" (
  echo VESPER running build is missing. See PLAY_EXPANSION.md.
  pause
  exit /b 1
)
start "" "%VESPER_RUN_EXE%" -screen-width 1536 -screen-height 1024 -screen-fullscreen 0
