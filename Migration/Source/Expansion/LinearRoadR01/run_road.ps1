param([ValidateSet('baseline','prepare','build','capture','traverse','performance')][string]$Action,[string]$Revision='L07',[string]$Label='')
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$taskProject=Join-Path $taskRoot 'Unity/Vesper'
if($Action -eq 'baseline'){$Revision='RoadBaseline'}
$taskEvidence=Join-Path $taskRoot ('Migration/Evidence/Expansion/LinearWorld/'+$Revision)
if(Get-Process Unity -ErrorAction SilentlyContinue){throw 'Unity is already running'}
if($Action -in @('baseline','prepare','build')){
 $taskSnapshot=Join-Path $taskEvidence ($Action+'-source')
 if(Test-Path -LiteralPath $taskSnapshot){throw 'Refuse snapshot overwrite'}
 New-Item -ItemType Directory -Path $taskSnapshot -Force | Out-Null
 $taskSource=Join-Path $taskProject 'Assets/Vesper/Expansion/LinearWorld'
 Get-ChildItem -LiteralPath $taskSource -Recurse -File | Where-Object {$_.Extension -in @('.cs','.shader') -and $_.FullName -notmatch '[\\/]Generated[\\/]'} | ForEach-Object {
  $taskRelative=$_.FullName.Substring($taskSource.Length+1);$taskCopy=Join-Path $taskSnapshot $taskRelative
  New-Item -ItemType Directory -Path (Split-Path -Parent $taskCopy) -Force | Out-Null
  Copy-Item -LiteralPath $_.FullName -Destination $taskCopy
 }
 $taskMethod=switch($Action){'baseline'{'BuildBaseline'}'prepare'{'Prepare'}'build'{'Build'}}
 $taskArgs=@('-batchmode','-projectPath',('"'+$taskProject+'"'),'-executeMethod',('Vesper.Expansion.LinearWorld.Editor.LinearRoadBuild.'+$taskMethod),'-roadRevision',$Revision,'-logFile',('"'+$taskEvidence+'/'+$Action+'.log"'))
 $taskProcess=Start-Process -FilePath 'C:/Program Files/Unity/Hub/Editor/6000.5.7f1/Editor/Unity.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
}else{
 if(Get-Process VesperLinear -ErrorAction SilentlyContinue){throw 'Linear player already running'}
 $taskBuild=Join-Path $taskEvidence 'build.json'
 if(-not(Test-Path -LiteralPath $taskBuild)){throw 'Build report missing'}
 if((Get-Content -LiteralPath $taskBuild -Raw | ConvertFrom-Json).result -ne 'Succeeded'){throw 'Successful build required'}
 if(-not $Label){$Label=$Action};$taskOut=Join-Path $taskEvidence $Label
 if(Test-Path -LiteralPath $taskOut){throw 'Refuse runtime evidence overwrite'}
 New-Item -ItemType Directory -Path $taskOut -Force | Out-Null
 $taskOption=switch($Action){'capture'{'-roadCapture'}'traverse'{'-roadTraverse'}'performance'{'-roadPerformance'}}
 $taskArgs=@('-screen-width','1536','-screen-height','1024','-screen-fullscreen','0','-force-d3d12',$taskOption,('"'+$taskOut+'"'),'-linearInputTrace','-logFile',('"'+$taskOut+'/player.log"'))
 $taskExe=Join-Path $taskProject ('Builds/VesperLinearWorld_'+$Revision+'/VesperLinear.exe')
 $taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Normal -PassThru
}
[pscustomobject]@{Action=$Action;Revision=$Revision;PID=$taskProcess.Id;Evidence=$taskEvidence;StartedUtc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json -Compress
