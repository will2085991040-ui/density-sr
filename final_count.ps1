
"combined files: $((Get-ChildItem 'C:\Users\mine\Downloads\quant_research\ashare_combined' -Filter *.parquet|Measure-Object).Count)"
"stocks dir files: $((Get-ChildItem 'C:\Users\mine\Downloads\quant_research\ashare_stocks' -Filter *.parquet|Measure-Object).Count)"