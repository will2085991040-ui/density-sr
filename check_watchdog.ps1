
Start-Sleep -Seconds 30
if(Test-Path "C:\Users\mine\Downloads\quant_research\watchdog.log"){ Get-Content "C:\Users\mine\Downloads\quant_research\watchdog.log" -Tail 4 } else { "no watchdog log yet" }
$files = (Get-ChildItem "C:\Users\mine\Downloads\quant_research\ashare_stocks" -Filter *.parquet | Measure-Object).Count
"files: $files"