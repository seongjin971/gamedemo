param([ValidateSet('prepare','build','capture','diagnostic','traverse','performance','manual')][string]$Action,[string]$Revision='L01',[string]$Label='')
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../..')).Path
$taskProject=Join-Path $taskRoot 'Unity/Vesper'
$taskEvidence=Join-Path $taskRoot ('Migration/Evidence/Expansion/LinearWorld/'+$Revision)
if($Action -in @('prepare','build')){
 if(Get-Process Unity -ErrorAction SilentlyContinue){throw 'Unity already running'}
 $taskSnapshot=Join-Path $taskEvidence ($Action+'-source')
 if(Test-Path -LiteralPath $taskSnapshot){throw 'Refuse snapshot overwrite; select a new revision'}
 New-Item -ItemType Directory -Path $taskSnapshot -Force | Out-Null
 $taskSource=Join-Path $taskProject 'Assets/Vesper/Expansion/LinearWorld'
 Get-ChildItem -LiteralPath $taskSource -Recurse -File | Where-Object {$_.Extension -in @('.cs','.shader')} | ForEach-Object {
  $taskRelative=$_.FullName.Substring($taskSource.Length+1);$taskCopy=Join-Path $taskSnapshot $taskRelative
  New-Item -ItemType Directory -Path (Split-Path -Parent $taskCopy) -Force | Out-Null
  Copy-Item -LiteralPath $_.FullName -Destination $taskCopy
 }
 $taskExe='C:/Program Files/Unity/Hub/Editor/6000.5.7f1/Editor/Unity.exe'
 $taskMethod=if($Action -eq 'prepare'){'Prepare'}else{'Build'}
 $taskArgs=@('-batchmode','-projectPath',('"'+$taskProject+'"'),'-executeMethod',('Vesper.Expansion.LinearWorld.Editor.LinearBuild.'+$taskMethod),'-linearRevision',$Revision,'-logFile',('"'+$taskEvidence+'/'+$Action+'.log"'))
 $taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
}else{
 if(Get-Process VesperLinear -ErrorAction SilentlyContinue){throw 'Linear player already running'}
 if(Get-Process Unity -ErrorAction SilentlyContinue){throw 'Wait for Unity build process to finish before runtime evidence'}
 $taskBuildReport=Join-Path $taskEvidence 'build.json'
 if(-not (Test-Path -LiteralPath $taskBuildReport)){throw 'Successful build report required before runtime evidence'}
 if((Get-Content -LiteralPath $taskBuildReport -Raw | ConvertFrom-Json).result -ne 'Succeeded'){throw 'Build did not succeed'}
 if(-not $Label){$Label=$Action};$taskOut=Join-Path $taskEvidence $Label
 if(Test-Path -LiteralPath $taskOut){throw 'Refuse evidence overwrite; use a new label'}
 New-Item -ItemType Directory -Path $taskOut -Force | Out-Null
 $taskExe=Join-Path $taskProject ('Builds/VesperLinearWorld_'+$Revision+'/VesperLinear.exe')
 $taskOption=switch($Action){'capture'{'-linearCapture'}'diagnostic'{'-linearCapture'}'traverse'{'-linearTraverse'}'performance'{'-linearPerformance'}'manual'{'-linearManual'}}
 $taskArgs=@('-screen-width','1536','-screen-height','1024','-screen-fullscreen','0','-force-d3d12',$taskOption,('"'+$taskOut+'"'),'-linearInputTrace','-logFile',('"'+$taskOut+'/player.log"'))
 if($Action -eq 'diagnostic'){$taskArgs+='-linearDiagnostics'}
 $taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Normal -PassThru
}
[pscustomobject]@{Action=$Action;Revision=$Revision;PID=$taskProcess.Id;Evidence=$taskEvidence;StartedUtc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json -Compress
