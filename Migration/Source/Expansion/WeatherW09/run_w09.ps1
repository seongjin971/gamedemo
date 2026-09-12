param([ValidateSet('PrepareAndBuild','Capture','Traverse','Performance')][string]$Action,[string]$Label='')
$ErrorActionPreference='Stop'
$w09Root=(Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$w09Project=Join-Path $w09Root 'Unity/Vesper'
$w09Evidence=Join-Path $w09Root 'Migration/Evidence/Expansion/WeatherWorld/W09'
if($Action -in @('PrepareAndBuild')){
 if(Get-Process Unity -ErrorAction SilentlyContinue){throw 'Unity editor already running'}
 $w09Exe='C:/Program Files/Unity/Hub/Editor/6000.5.7f1/Editor/Unity.exe'
 $w09Log=Join-Path $w09Evidence ($Action.ToLower()+$Label+'.log')
 if(Test-Path -LiteralPath $w09Log){throw "Refuse existing evidence $w09Log"}
 $w09Args=@('-batchmode','-projectPath',('"'+$w09Project+'"'),'-executeMethod',("Vesper.Expansion.WeatherW09.Editor.WeatherW09Build.$Action"),'-logFile',('"'+$w09Log+'"'))
 $w09P=Start-Process -FilePath $w09Exe -ArgumentList $w09Args -WorkingDirectory $w09Project -WindowStyle Hidden -PassThru
}else{
 if(Get-Process Unity -ErrorAction SilentlyContinue){throw 'Finish editor before runtime verification'}
 $w09Exe=Join-Path $w09Project 'Builds/VesperWeatherWorld_W09/VesperLinear.exe'
 $w09Out=Join-Path $w09Evidence ($Action.ToLower()+$Label)
 if(Test-Path -LiteralPath $w09Out){throw "Refuse existing evidence $w09Out"}
 New-Item -ItemType Directory -Path $w09Out | Out-Null
 $w09Others=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^(Vesper.*|obs64)\.exe$'} | Select-Object ProcessId,Name,ExecutablePath)
 ConvertTo-Json -InputObject $w09Others | Set-Content -LiteralPath (Join-Path $w09Out 'concurrent-processes.json') -Encoding UTF8
 $w09Args=@('-screen-width','1920','-screen-height','1080','-screen-fullscreen','1','-window-mode','exclusive','-force-d3d12',('-w09'+$Action),('"'+$w09Out+'"'),'-logFile',('"'+(Join-Path $w09Out 'player.log')+'"'))
 $w09P=Start-Process -FilePath $w09Exe -ArgumentList $w09Args -WorkingDirectory (Split-Path $w09Exe) -WindowStyle Normal -PassThru
}
[pscustomobject]@{id=$w09P.Id;action=$Action;exe=$w09Exe}|ConvertTo-Json
