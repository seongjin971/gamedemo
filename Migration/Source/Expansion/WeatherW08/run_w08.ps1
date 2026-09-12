param([ValidateSet('PrepareAndBuild','Capture','Traverse','Performance')][string]$Action,[string]$Label='')
$ErrorActionPreference='Stop'
$w08Root=(Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$w08Project=Join-Path $w08Root 'Unity/Vesper'
$w08Evidence=Join-Path $w08Root 'Migration/Evidence/Expansion/WeatherWorld/W08'
if($Action -in @('PrepareAndBuild')){
 if(Get-Process Unity -ErrorAction SilentlyContinue){throw 'Unity editor already running'}
 $w08Exe='C:/Program Files/Unity/Hub/Editor/6000.5.7f1/Editor/Unity.exe'
 $w08Log=Join-Path $w08Evidence ($Action.ToLower()+$Label+'.log')
 if(Test-Path -LiteralPath $w08Log){throw "Refuse existing evidence $w08Log"}
 $w08Args=@('-batchmode','-projectPath',('"'+$w08Project+'"'),'-executeMethod',("Vesper.Expansion.WeatherW08.Editor.WeatherW08Build.$Action"),'-logFile',('"'+$w08Log+'"'))
 $w08P=Start-Process -FilePath $w08Exe -ArgumentList $w08Args -WorkingDirectory $w08Project -WindowStyle Hidden -PassThru
}else{
 if(Get-Process Unity -ErrorAction SilentlyContinue){throw 'Finish editor before runtime verification'}
 $w08Exe=Join-Path $w08Project 'Builds/VesperWeatherWorld_W08/VesperLinear.exe'
 $w08Out=Join-Path $w08Evidence ($Action.ToLower()+$Label)
 if(Test-Path -LiteralPath $w08Out){throw "Refuse existing evidence $w08Out"}
 New-Item -ItemType Directory -Path $w08Out | Out-Null
 $w08Others=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^(Vesper.*|obs64)\.exe$'} | Select-Object ProcessId,Name,ExecutablePath)
 ConvertTo-Json -InputObject $w08Others | Set-Content -LiteralPath (Join-Path $w08Out 'concurrent-processes.json') -Encoding UTF8
 $w08Args=@('-screen-width','1920','-screen-height','1080','-screen-fullscreen','1','-window-mode','exclusive','-force-d3d12',('-w08'+$Action),('"'+$w08Out+'"'),'-logFile',('"'+(Join-Path $w08Out 'player.log')+'"'))
 $w08P=Start-Process -FilePath $w08Exe -ArgumentList $w08Args -WorkingDirectory (Split-Path $w08Exe) -WindowStyle Normal -PassThru
}
[pscustomobject]@{id=$w08P.Id;action=$Action;exe=$w08Exe}|ConvertTo-Json
