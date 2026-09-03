
Get-Content "C:\Users\mine\Downloads\quant_research\watchdog.log" -Tail 8 -ErrorAction SilentlyContinue
$files = (Get-ChildItem "C:\Users\mine\Downloads\quant_research\ashare_stocks" -Filter *.parquet | Measure-Object).Count
"files: $files"