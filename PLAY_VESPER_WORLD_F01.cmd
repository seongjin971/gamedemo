@echo off
setlocal
set "VESPER_F01_EXE=%~dp0Unity\Vesper\Builds\VesperContinuousWorld_F01\VesperWorld.exe"
if not exist "%VESPER_F01_EXE%" exit /b 1
start "" "%VESPER_F01_EXE%" -screen-width 1536 -screen-height 1024 -screen-fullscreen 0 -force-d3d12
