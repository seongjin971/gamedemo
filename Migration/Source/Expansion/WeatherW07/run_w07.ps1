param([ValidateSet('Inspect','Prepare','Build','Capture','Traverse','Performance')][string]$Action,[string]$Label='')
$ErrorActionPreference='Stop'
$w07Root=(Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$w07Project=Join-Path $w07Root 'Unity/Vesper'
$w07Evidence=Join-Path $w07Root 'Migration/Evidence/Expansion/WeatherWorld/W07'
if($Action -in @('Inspect','Prepare','Build')){
 if(Get-Process Unity -ErrorAction SilentlyContinue){throw 'Unity editor already running'}
 $w07Exe='C:/Program Files/Unity/Hub/Editor/6000.5.7f1/Editor/Unity.exe'
 $w07Log=Join-Path $w07Evidence ($Action.ToLower()+$Label+'.log')
 if(Test-Path -LiteralPath $w07Log){throw "Refuse existing evidence $w07Log"}
 $w07Args=@('-batchmode','-projectPath',('"'+$w07Project+'"'),'-executeMethod',("Vesper.Expansion.WeatherW07.Editor.WeatherW07Build.$Action"),'-logFile',('"'+$w07Log+'"'))
 $w07P=Start-Process -FilePath $w07Exe -ArgumentList $w07Args -WorkingDirectory $w07Project -WindowStyle Hidden -PassThru
}else{
 if(Get-Process Unity -ErrorAction SilentlyContinue){throw 'Finish editor before runtime verification'}
 $w07Exe=Join-Path $w07Project 'Builds/VesperWeatherWorld_W07/VesperLinear.exe'
 $w07Out=Join-Path $w07Evidence ($Action.ToLower()+$Label)
 if(Test-Path -LiteralPath $w07Out){throw "Refuse existing evidence $w07Out"}
 New-Item -ItemType Directory -Path $w07Out | Out-Null
 $w07Others=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^(Vesper.*|obs64)\.exe$'} | Select-Object ProcessId,Name,ExecutablePath)
 ConvertTo-Json -InputObject $w07Others | Set-Content -LiteralPath (Join-Path $w07Out 'concurrent-processes.json') -Encoding UTF8
 $w07Args=@('-screen-width','1920','-screen-height','1080','-screen-fullscreen','1','-window-mode','exclusive','-force-d3d12',('-w07'+$Action),('"'+$w07Out+'"'),'-logFile',('"'+(Join-Path $w07Out 'player.log')+'"'))
 $w07P=Start-Process -FilePath $w07Exe -ArgumentList $w07Args -WorkingDirectory (Split-Path $w07Exe) -WindowStyle Normal -PassThru
}
[pscustomobject]@{id=$w07P.Id;action=$Action;exe=$w07Exe}|ConvertTo-Json
