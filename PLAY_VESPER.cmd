@echo off
setlocal
set "VESPER_EXE=%~dp0Unity\Vesper\Builds\VesperPreview\Vesper.exe"
if not exist "%VESPER_EXE%" (
  echo VESPER player build is missing. See PLAY.md.
  pause
  exit /b 1
)
start "" "%VESPER_EXE%" -screen-width 1536 -screen-height 1024 -screen-fullscreen 0
