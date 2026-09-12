param(
 [ValidateSet('prepare','build','qa','edges','manual','capture','performance','baseline','weather','film','materials','ablation')][string]$Action,
 [string]$Revision='A03',
 [string]$Label='',
 [string]$Stage='A'
)
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$taskEvidence=Join-Path $taskRoot 'Migration/Evidence/Expansion/ContinuousWorld'
$taskProject=Join-Path $taskRoot 'Unity/Vesper'
if($Action -in @('prepare','build')){
 if(Get-Process Unity -ErrorAction SilentlyContinue){throw 'A Unity editor is still running; inspect its current task before another batch.'}
 $taskExe='C:\Program Files\Unity\Hub\Editor\6000.5.7f1\Editor\Unity.exe'
 $taskMethod=if($Action -eq 'prepare'){'Prepare'}else{'Build'}
 $taskLog=Join-Path $taskEvidence ($Revision+'-'+$Action+'.log')
 $taskSnapshot=Join-Path $taskEvidence ($Revision+'/'+$Action+'-source')
 New-Item -ItemType Directory -Path $taskSnapshot -Force | Out-Null
 $taskCodeRoot=Join-Path $taskProject 'Assets/Vesper/Expansion/ContinuousWorld'
 $taskSourceHashes=@(Get-ChildItem -LiteralPath $taskCodeRoot -Recurse -File | Where-Object {$_.Extension -in @('.cs','.shader')} | ForEach-Object {
  $taskRelative=$_.FullName.Substring($taskCodeRoot.Length+1)
  $taskCopy=Join-Path $taskSnapshot $taskRelative
  New-Item -ItemType Directory -Path (Split-Path -Parent $taskCopy) -Force | Out-Null
  Copy-Item -LiteralPath $_.FullName -Destination $taskCopy
  [pscustomobject]@{Path=$taskRelative;SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}
 })
 $taskSourceHashes | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $taskSnapshot 'manifest.json')
 $taskArgs=@('-batchmode','-projectPath',('"'+$taskProject+'"'),'-executeMethod',('Vesper.Expansion.ContinuousWorld.Editor.WorldBuild.'+$taskMethod),'-worldRevision',$Revision,'-worldStage',$Stage,'-logFile',('"'+$taskLog+'"'))
 $taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
}else{
 if(Get-Process VesperWorld,VesperP2 -ErrorAction SilentlyContinue){throw 'A player is still running; finish its current evidence before another player.'}
 if(-not $Label){$Label=$Action}
 $taskOut=Join-Path $taskEvidence ($Revision+'/'+$Label)
 New-Item -ItemType Directory -Path $taskOut -Force | Out-Null
 $taskExe=Join-Path $taskProject ('Builds/VesperContinuousWorld_'+$Revision+'/VesperWorld.exe')
 $taskOption=switch($Action){'qa'{'-worldQA'}'edges'{'-worldEdges'}'manual'{'-worldManual'}'capture'{'-worldCapture'}'performance'{'-worldPerformance'}'baseline'{'-p2Performance'}'weather'{'-worldWeatherQA'}'film'{'-worldFilm'}'materials'{'-worldMaterials'}'ablation'{'-worldAblation'}}
 if($Action -eq 'baseline'){$taskExe=Join-Path $taskProject 'Builds/VesperP2ClickFix/VesperP2.exe'}
 $taskArgs=@('-screen-width','1536','-screen-height','1024','-screen-fullscreen','0','-force-d3d12',$taskOption,('"'+$taskOut+'"'),'-worldInputTrace','-logFile',('"'+$taskOut+'/player.log"'))
 # This is the interactive render/input verification surface, not a hidden background service.
 $taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Normal -PassThru
}
[pscustomobject]@{Action=$Action;Revision=$Revision;PID=$taskProcess.Id;StartedUtc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json -Compress
