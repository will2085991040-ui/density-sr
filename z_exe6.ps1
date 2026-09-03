$exe='C:/Users/mine/Downloads/quant_research/dist_v92/dsr_sr.exe'
$boot="$env:USERPROFILE/_dsr_sr_boot.txt"
Remove-Item $boot -Force -ErrorAction SilentlyContinue
$p=Start-Process -FilePath $exe -PassThru
$url=$null
for($i=0;$i -lt 120;$i++){ if(Test-Path $boot){ $url=(Get-Content $boot).Trim(); break }; if($p.HasExited){break}; Start-Sleep 1 }
if(-not $url){ Write-Output "NO_BOOT"; if(-not $p.HasExited){Stop-Process -Id $p.Id -Force}; exit }
Write-Output ("url=" + $url)
$js=(Invoke-WebRequest -Uri ($url+'sentiment_panel.js') -TimeoutSec 20 -UseBasicParsing).Content
Write-Output ("hasSrcBadge=" + $js.Contains([string][char]0x6570))
$rt=(Invoke-WebRequest -Uri ($url+'api/rt/realtime?symbol=600519&tf=daily') -TimeoutSec 30 -UseBasicParsing).Content | ConvertFrom-Json
Write-Output ("realtime: src=" + $rt.source + " bars=" + $rt.kline.Count + " bands=" + $rt.bands.Count + " signal=" + $rt.signal.signal + " sentLabel=" + $rt.sentiment.label)
if(-not $p.HasExited){ Stop-Process -Id $p.Id -Force }
