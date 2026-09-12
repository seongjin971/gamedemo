param(
    [ValidateSet('Prepare','Refine','Build','Capture','Motion','Traverse','Performance')][string]$Action = 'Capture',
    [string]$Revision = 'W01'
)
$ErrorActionPreference = 'Stop'
$weatherRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$weatherProject = Join-Path $weatherRoot 'Unity/Vesper'
$weatherEvidence = Join-Path $weatherRoot "Migration/Evidence/Expansion/WeatherWorld/$Revision"
New-Item -ItemType Directory -Path $weatherEvidence -Force | Out-Null
if ($Action -eq 'Prepare' -or $Action -eq 'Refine' -or $Action -eq 'Build') {
    if (Get-Process Unity -ErrorAction SilentlyContinue) { throw 'Unity is already running; do not overlap project writers.' }
    $weatherExe = 'C:/Program Files/Unity/Hub/Editor/6000.5.7f1/Editor/Unity.exe'
    $weatherLog = Join-Path $weatherEvidence ($Action.ToLower()+'.log')
    if (Test-Path -LiteralPath $weatherLog) { throw "Existing evidence log: $weatherLog" }
    $weatherArgs = @('-batchmode','-projectPath',('"'+$weatherProject+'"'),'-executeMethod',("Vesper.Expansion.WeatherWorld.Editor.WeatherBuild.$Action"),'-weatherRevision',$Revision,'-logFile',('"'+$weatherLog+'"'))
    $weatherProcess = Start-Process -FilePath $weatherExe -ArgumentList $weatherArgs -WorkingDirectory $weatherProject -WindowStyle Hidden -PassThru
} else {
    if (Get-Process VesperLinear,Unity -ErrorAction SilentlyContinue) { throw 'Close or finish the existing game/editor before isolated runtime verification.' }
    $weatherExe = Join-Path $weatherProject "Builds/VesperWeatherWorld_$Revision/VesperLinear.exe"
    if (!(Test-Path -LiteralPath $weatherExe)) { throw "Missing build: $weatherExe" }
    $weatherOutput = Join-Path $weatherEvidence $Action.ToLower()
    if (Test-Path -LiteralPath $weatherOutput) { throw "Existing runtime evidence: $weatherOutput" }
    New-Item -ItemType Directory -Path $weatherOutput | Out-Null
    $weatherArgs = @('-screen-width','1920','-screen-height','1080','-screen-fullscreen','1','-window-mode','exclusive','-force-d3d12',('-weather'+$Action),('"'+$weatherOutput+'"'),'-logFile',('"'+(Join-Path $weatherOutput 'player.log')+'"'))
    # Visible game is the subject of the requested actual-screen visual verification.
    $weatherProcess = Start-Process -FilePath $weatherExe -ArgumentList $weatherArgs -WorkingDirectory (Split-Path $weatherExe) -WindowStyle Normal -PassThru
}
[pscustomobject]@{ id=$weatherProcess.Id; action=$Action; revision=$Revision; executable=$weatherExe } | ConvertTo-Json
