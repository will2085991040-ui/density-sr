$b="$env:USERPROFILE/_dsr_sr_boot.txt"
"boot=" + $(if(Test-Path $b){Get-Content $b}else{'none'})
$pr=Get-Process dsr_sr -ErrorAction SilentlyContinue
if($pr){ "cpu_s=" + [math]::Round($pr.TotalProcessorTime.TotalSeconds,0) + " wrtMB=" + [math]::Round($pr.WorkingSet64/1MB) + " threads=" + $pr.Threads.Count }
"MEI dirs:"
Get-ChildItem $env:TEMP -Directory -Filter '_MEI*' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | ForEach-Object{ "  " + $_.Name + " size=" + [math]::Round((Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue|Measure-Object Length -Sum).Sum/1MB,0) + "MB" }
"listening ports:"
if($pr){ Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object{$_.OwningProcess -eq $pr.Id} | Select-Object -ExpandProperty LocalPort }
