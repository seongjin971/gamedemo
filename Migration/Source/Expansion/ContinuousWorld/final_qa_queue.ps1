param([string]$Revision='E02',[int]$QaPid,[switch]$AfterPerformance)
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$taskEvidence=Join-Path $taskRoot ('Migration/Evidence/Expansion/ContinuousWorld/'+$Revision)
$taskEvents=Join-Path $taskEvidence 'queue.jsonl'
function Record-TaskEvent($Action,$State,$PidValue){
 [pscustomobject]@{Action=$Action;State=$State;PID=$PidValue;Utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Compress | Add-Content -LiteralPath $taskEvents -Encoding UTF8
}
function Wait-TaskPlayer($PidValue){
 $taskProcess=Get-Process -Id $PidValue -ErrorAction SilentlyContinue
 if($taskProcess){Wait-Process -Id $PidValue}
}
function Assert-TaskReport($Action){
 $taskReport=Get-Content -LiteralPath (Join-Path $taskEvidence ($Action+'/report.json')) -Raw -Encoding UTF8 | ConvertFrom-Json
 if($taskReport.failures -ne 0 -or @($taskReport.errors).Count -ne 0 -or $taskReport.resets -ne 0 -or $taskReport.safetyStops -ne 0){throw ($Action+' failed; evidence preserved, queue stopped')}
 if($Action -eq 'qa' -and ($taskReport.clicks -ne 450 -or $taskReport.blocked -ne 0 -or $taskReport.checks -notcontains 'PASS Full continuous round trip 3 without reset')){throw 'Full route is incomplete'}
 if($Action -eq 'edges' -and ($taskReport.clicks -ne 44 -or $taskReport.blocked -ne 5)){throw 'Edge suite is incomplete'}
 if($Action -eq 'weather' -and @($taskReport.checks).Count -ne 42){throw 'Weather suite is incomplete'}
 if($Action -eq 'performance' -and (@($taskReport.performance).Count -ne 20 -or @($taskReport.performance | Where-Object {$_.unfocused -gt 0}).Count -gt 0)){throw 'Performance suite is incomplete or unfocused'}
 if($Action -eq 'film' -and ($taskReport.clicks -ne 9 -or @($taskReport.checks).Count -ne 9)){throw 'Film suite is incomplete'}
 Record-TaskEvent $Action 'verified complete' 0
}
if($AfterPerformance){
 Assert-TaskReport 'weather'
 Record-TaskEvent 'performance' 'waiting for existing player' $QaPid
 Wait-TaskPlayer $QaPid
 Assert-TaskReport 'performance'
 $taskActions=@('film')
}else{
 Record-TaskEvent 'qa' 'waiting for existing player' $QaPid
 Wait-TaskPlayer $QaPid
 Assert-TaskReport 'qa'
 $taskActions=@('edges','weather','performance','film','capture')
}
foreach($taskAction in $taskActions){
 $taskRun=& (Join-Path $PSScriptRoot 'run.ps1') -Action $taskAction -Revision $Revision -Stage E | ConvertFrom-Json
 Record-TaskEvent $taskAction 'started' $taskRun.PID
 Wait-TaskPlayer $taskRun.PID
 Assert-TaskReport $taskAction
}
$taskManual=& (Join-Path $PSScriptRoot 'run.ps1') -Action manual -Revision $Revision -Stage E | ConvertFrom-Json
Record-TaskEvent 'manual' 'ready for native input; not automatically accepted' $taskManual.PID
$taskManual | ConvertTo-Json -Compress
