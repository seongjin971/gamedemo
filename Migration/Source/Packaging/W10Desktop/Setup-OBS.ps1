param(
    [string]$ObsConfigRoot = (Join-Path ([Environment]::GetFolderPath('ApplicationData')) 'obs-studio'),
    [string]$RecordingDirectory = (Join-Path ([Environment]::GetFolderPath('MyVideos')) 'VESPER')
)
$ErrorActionPreference = 'Stop'
if (Get-Process obs64 -ErrorAction SilentlyContinue) {
    throw 'Close OBS normally after stopping any recording, then run this setup again.'
}
$profileName = 'VESPER_W10_5070_60'
$sceneName = 'VESPER_W10_Desktop'
$profilePath = Join-Path $ObsConfigRoot ('basic\profiles\' + $profileName)
$scenePath = Join-Path $ObsConfigRoot ('basic\scenes\' + $sceneName + '.json')
if ((Test-Path -LiteralPath $profilePath) -or (Test-Path -LiteralPath $scenePath)) {
    if ((Test-Path -LiteralPath (Join-Path $profilePath 'basic.ini')) -and
        (Test-Path -LiteralPath (Join-Path $profilePath 'recordEncoder.json')) -and
        (Test-Path -LiteralPath $scenePath)) {
        Write-Host 'The VESPER desktop profile and scene already exist. Kept your settings unchanged.'
        exit 0
    }
    throw 'An incomplete or conflicting VESPER desktop setup exists. Nothing was overwritten.'
}
$templatePath = Join-Path $PSScriptRoot 'Profile\basic.ini.template'
$encoderPath = Join-Path $PSScriptRoot 'Profile\recordEncoder.json'
$sceneTemplatePath = Join-Path $PSScriptRoot 'Scene\VESPER_W10_Desktop.json'
foreach ($required in @($templatePath, $encoderPath, $sceneTemplatePath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw ('Missing package file: ' + $required) }
}
if ($RecordingDirectory.IndexOfAny([char[]]"`r`n") -ge 0) { throw 'Invalid recording directory.' }
$configText = [IO.File]::ReadAllText($templatePath).Replace('@@RECORDING_DIRECTORY@@', $RecordingDirectory.Replace('\', '/'))
New-Item -ItemType Directory -Path $RecordingDirectory -Force | Out-Null
New-Item -ItemType Directory -Path $profilePath | Out-Null
New-Item -ItemType Directory -Path (Split-Path $scenePath) -Force | Out-Null
[IO.File]::WriteAllText((Join-Path $profilePath 'basic.ini'), $configText, (New-Object Text.UTF8Encoding($false)))
Copy-Item -LiteralPath $encoderPath -Destination (Join-Path $profilePath 'recordEncoder.json')
Copy-Item -LiteralPath $sceneTemplatePath -Destination $scenePath
Write-Host 'Ready: VESPER W10 RTX5070 60 / VESPER W10 Desktop'
Write-Host ('Recordings: ' + $RecordingDirectory)
Write-Host 'Use 03_RECORD.cmd to open OBS and the game. Recording starts only when you press Ctrl+Shift+F9.'
