@echo off
setlocal
set "VESPER_WORLD_EXE=%~dp0Unity\Vesper\Builds\VesperContinuousWorld_D01\VesperWorld.exe"
if not exist "%VESPER_WORLD_EXE%" (
  echo VESPER integrated world build is missing. See PLAY_WORLD.md.
  pause
  exit /b 1
)
start "" "%VESPER_WORLD_EXE%" -screen-width 1536 -screen-height 1024 -screen-fullscreen 0 -force-d3d12
