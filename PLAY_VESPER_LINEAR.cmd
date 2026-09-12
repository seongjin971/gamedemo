@echo off
setlocal
set "VESPER_LINEAR_EXE=%~dp0Unity\Vesper\Builds\VesperLinearWorld_L06\VesperLinear.exe"
if not exist "%VESPER_LINEAR_EXE%" exit /b 1
start "" "%VESPER_LINEAR_EXE%" -screen-width 1536 -screen-height 1024 -screen-fullscreen 0 -force-d3d12
