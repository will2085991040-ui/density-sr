
$dst = "C:\Users\mine\Downloads\quant_research\ashare_all4"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
# copy from ashare_stocks (沪主板+), ashare_multi(深主板), ashare_tdx(创业板/科创板)
foreach($src in @("ashare_stocks","ashare_multi","ashare_tdx")){
  $d = "C:\Users\mine\Downloads\quant_research\$src"
  if(Test-Path $d){ Get-ChildItem $d -Filter *.parquet | Copy-Item -Destination $dst -Force }
}
$c = (Get-ChildItem $dst -Filter *.parquet | Measure-Object).Count
"all4 files: $c"