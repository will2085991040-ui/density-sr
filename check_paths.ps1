Get-PSDrive -PSProvider FileSystem | Select-Object Name, Root | Format-Table -AutoSize | Out-String
"--- fixed paths ---"
$paths = "D:\A股_K线数据","D:\K线数据","C:\Users\mine\Downloads\A股_K线数据","C:\Users\mine\Downloads\K线数据"
$apd = [Environment]::GetFolderPath('ApplicationData')
$paths | ForEach-Object { if(Test-Path $_){ "EXISTS: $_" } else { "missing: $_" } }
"--- MetaQuotes(MT5) ---"
$mq = Join-Path $apd "MetaQuotes"
if(Test-Path $mq){ Get-ChildItem $mq -Recurse -Depth 2 -ErrorAction SilentlyContinue | Select-Object -First 25 FullName } else { "no MetaQuotes dir at $mq" }