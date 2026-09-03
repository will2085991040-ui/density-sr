
# merge ashare_multi into combined dir along with ashare_stocks (skip dupes)
$combined = "C:\Users\mine\Downloads\quant_research\ashare_combined"
New-Item -ItemType Directory -Force -Path $combined | Out-Null
# copy from ashare_stocks
Get-ChildItem "C:\Users\mine\Downloads\quant_research\ashare_stocks" -Filter *.parquet | Copy-Item -Destination $combined -Force
# copy from ashare_multi (overwrite, keep superset)
Get-ChildItem "C:\Users\mine\Downloads\quant_research\ashare_multi" -Filter *.parquet | Copy-Item -Destination $combined -Force
$c = (Get-ChildItem $combined -Filter *.parquet | Measure-Object).Count
"combined files: $c"