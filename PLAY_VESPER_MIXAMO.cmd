@echo off
setlocal
set "VESPER_MIXAMO_EXE=%~dp0Unity\Vesper\Builds\VesperMixamo\VesperMixamo.exe"
if not exist "%VESPER_MIXAMO_EXE%" (
  echo VESPER Mixamo player build is missing. See PLAY_EXPANSION.md.
  pause
  exit /b 1
)
start "" "%VESPER_MIXAMO_EXE%" -screen-width 1536 -screen-height 1024 -screen-fullscreen 0
