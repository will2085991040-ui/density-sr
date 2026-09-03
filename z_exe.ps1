$exe='C:/Users/mine/Downloads/quant_research/dist_v92/dsr_sr.exe'
$p=Start-Process -FilePath $exe -PassThru
"pid=" + $p.Id
Start-Sleep -Seconds 50
"alive=" + (-not $p.HasExited)
if($p.HasExited){ "exitcode=" + $p.ExitCode }
"--- _MEI temp dirs (newest) ---"
Get-ChildItem $env:TEMP -Directory -Filter '_MEI*' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3 | ForEach-Object{ $_.Name + ' age_s=' + [math]::Round(((Get-Date)-$_.LastWriteTime).TotalSeconds,0) + ' size=' + [math]::Round((Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum/1MB,0) + 'MB' }
"--- boot ---"
if(Test-Path "$env:USERPROFILE/_dsr_sr_boot.txt"){ "boot=" + (Get-Content "$env:USERPROFILE/_dsr_sr_boot.txt") } else { "no boot" }
