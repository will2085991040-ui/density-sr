$exe='C:/Users/mine/Downloads/quant_research/dist_v92/dsr_sr.exe'
$boot="$env:USERPROFILE/_dsr_sr_boot.txt"
Remove-Item $boot -Force -ErrorAction SilentlyContinue
$p=Start-Process -FilePath $exe -PassThru
$url=$null
for($i=0;$i -lt 150;$i++){
  if(Test-Path $boot){ $url=(Get-Content $boot).Trim(); break }
  Start-Sleep -Seconds 1
}
"boot=" + $(if($url){"[$url]"}else{"NONE"})
if(-not $url){ "processAlive=" + (-not $p.HasExited) + " exit=" + $(if($p.HasExited){$p.ExitCode}else{'running'}) }
else {
  "GET index: " + [int](Invoke-WebRequest -Uri ($url+'') -TimeoutSec 20 -UseBasicParsing).StatusCode
  "GET panel js: " + [int](Invoke-WebRequest -Uri ($url+'sentiment_panel.js') -TimeoutSec 20 -UseBasicParsing).StatusCode
  try { $rt=(Invoke-WebRequest -Uri ($url+'api/rt/realtime?symbol=600519&tf=daily') -TimeoutSec 25 -UseBasicParsing).Content | ConvertFrom-Json; "RT src=" + $rt.source + " bars=" + $rt.kline.Count } catch { "rt ERR " + $_.Exception.Message }
  try { $se=(Invoke-WebRequest -Uri ($url+'api/rt/sentiment') -TimeoutSec 25 -UseBasicParsing).Content | ConvertFrom-Json; "SENT label=" + $se.label } catch { "sent ERR" }
}
if($p -and -not $p.HasExited){ Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
