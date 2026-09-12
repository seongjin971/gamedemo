param([ValidateSet('Build','InputQA')][string]$Action,[ValidatePattern('^[-a-z0-9]*$')][string]$Label='')
$ErrorActionPreference='Stop'
$w10Root=(Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$w10Project=Join-Path $w10Root 'Unity/Vesper'
$w10Evidence=Join-Path $w10Root 'Migration/Evidence/Expansion/WeatherWorld/W10'
if(Get-Process Unity -ErrorAction SilentlyContinue){throw 'Unity editor is already running'}
if($Action -eq 'Build'){
 $w10Exe='C:/Program Files/Unity/Hub/Editor/6000.5.7f1/Editor/Unity.exe'
 $w10Log=Join-Path $w10Evidence 'build.log'
 if(Test-Path -LiteralPath $w10Log){throw 'Preserve existing build log'}
 $w10Args=@('-batchmode','-projectPath',('"'+$w10Project+'"'),'-executeMethod','Vesper.Expansion.WeatherW10.Editor.WeatherW10Build.PrepareAndBuild','-logFile',('"'+$w10Log+'"'))
}else{
 $w10Exe=Join-Path $w10Project 'Builds/VesperWeatherWorld_W10/VesperLinear.exe'
 $w10Out=Join-Path $w10Evidence ('input-qa'+$Label)
 if(Test-Path -LiteralPath $w10Out){throw 'Preserve existing runtime evidence'}
 New-Item -ItemType Directory -Path $w10Out | Out-Null
 $w10Others=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^(Vesper.*|obs64)\.exe$'} | Select-Object ProcessId,Name,ExecutablePath)
 ConvertTo-Json -InputObject $w10Others | Set-Content -LiteralPath (Join-Path $w10Out 'concurrent-processes.json') -Encoding UTF8
 $w10Args=@('-screen-width','1920','-screen-height','1080','-screen-fullscreen','1','-window-mode','exclusive','-force-d3d12','-w10InputQA',('"'+$w10Out+'"'),'-logFile',('"'+(Join-Path $w10Out 'player.log')+'"'))
}
$w10Style=if($Action -eq 'Build'){'Hidden'}else{'Normal'}
$w10Process=Start-Process -FilePath $w10Exe -ArgumentList $w10Args -WorkingDirectory $w10Project -WindowStyle $w10Style -PassThru
[pscustomobject]@{id=$w10Process.Id;action=$Action;exe=$w10Exe}|ConvertTo-Json
