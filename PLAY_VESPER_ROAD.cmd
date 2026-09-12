@echo off
setlocal
set "VESPER_ROAD_EXE=%~dp0Unity\Vesper\Builds\VesperLinearWorld_L09\VesperLinear.exe"
if not exist "%VESPER_ROAD_EXE%" exit /b 1
start "" "%VESPER_ROAD_EXE%" -screen-width 1920 -screen-height 1080 -screen-fullscreen 1 -window-mode exclusive -force-d3d12
