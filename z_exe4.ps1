$exe='C:/Users/mine/Downloads/quant_research/dist_v92/dsr_sr.exe'
"exe_mtime=" + (Get-Item $exe).LastWriteTime
$boot="$env:USERPROFILE/_dsr_sr_boot.txt"
Remove-Item $boot -Force -ErrorAction SilentlyContinue
$p=Start-Process -FilePath $exe -PassThru
$url=$null
for($i=0;$i -lt 240;$i++){
  if(Test-Path $boot){ $url=(Get-Content $boot).Trim(); break }
  if($p.HasExited){ "DIED_AT=" + $i + " exit=" + $p.ExitCode; break }
  Start-Sleep -Seconds 1
}
"boot=" + $(if($url){"[$url]"}else{"NONE(waited=$i)"})
if($url){
  "index=" + [int](Invoke-WebRequest -Uri ($url+'') -TimeoutSec 20 -UseBasicParsing).StatusCode
  "panel=" + [int](Invoke-WebRequest -Uri ($url+'sentiment_panel.js') -TimeoutSec 20 -UseBasicParsing).StatusCode
  "realtime=" + [int](Invoke-WebRequest -Uri ($url+'api/rt/realtime?symbol=600519&tf=daily') -TimeoutSec 25 -UseBasicParsing).StatusCode
  "sent=" + [int](Invoke-WebRequest -Uri ($url+'api/rt/sentiment') -TimeoutSec 25 -UseBasicParsing).StatusCode
}
if(-not $p.HasExited){ Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
