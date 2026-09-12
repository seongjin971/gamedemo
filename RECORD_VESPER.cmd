@echo off
setlocal
set "VESPER_OBS_EXE=C:\Program Files\obs-studio\bin\64bit\obs64.exe"
if not exist "%VESPER_OBS_EXE%" exit /b 1
tasklist /FI "IMAGENAME eq obs64.exe" /NH | find /I "obs64.exe" >nul
if errorlevel 1 start "" /D "C:\Program Files\obs-studio\bin\64bit" "%VESPER_OBS_EXE%" --profile "VESPER FHD 30" --collection "VESPER FHD"
tasklist /FI "IMAGENAME eq VesperLinear.exe" /NH | find /I "VesperLinear.exe" >nul
if errorlevel 1 call "%~dp0PLAY_VESPER_ROAD.cmd"
endlocal
