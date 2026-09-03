
$root = "C:\Users\mine\Desktop\大A量化监控系统"
$subs = @("A股数据","MT5_K线数据(1)","OKX_K线数据(1)","PA_Agent-6.16（稳但机会少）","PA_Agent6.24（激进但机会多）")
foreach($sub in $subs){
  $d = Join-Path $root $sub
  Write-Output ("===== " + $sub + " =====")
  if(Test-Path $d){
    $items = Get-ChildItem $d -ErrorAction SilentlyContinue | Select-Object -First 15
    $total = (Get-ChildItem $d -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    foreach($it in $items){
      $t = if($it.PSIsContainer){"<DIR>"}else{"file"}
      Write-Output ("  " + $t.PadRight(6) + " " + $it.Name.PadRight(45) + " " + $it.Length)
    }
    Write-Output ("  (recurse file total: " + $total + ")")
  } else { Write-Output "  MISSING" }
  Write-Output ""
}