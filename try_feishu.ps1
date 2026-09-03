
$token = "BO4lw44noi89FBkwrEiczxy7nna"
$urls = @(
  "https://internal-api-drive-stream.feishu.cn/space/api/docx/get_document/BO4lw44noi89FBkwrEiczxy7nna?from=from_copylink",
  "https://my.feishu.cn/wikis/BO4lw44noi89FBkwrEiczxy7nna",
  "https://my.feishu.cn/wukong/api/hub/query/BO4lw44noi89FBkwrEiczxy7nna"
)
foreach($u in $urls){
  "--- $u"
  $r = curl.exe -s -L -o "C:\Users\mine\Downloads\quant_research\feishu_try.json" -w "code=%{http_code} size=%{size_download}" --max-time 20 -A "Mozilla/5.0" $u 2>&1
  $r
  if(Test-Path "C:\Users\mine\Downloads\quant_research\feishu_try.json"){ $sz = (Get-Item "C:\Users\mine\Downloads\quant_research\feishu_try.json").Length; if($sz -gt 200){ $c = Get-Content "C:\Users\mine\Downloads\quant_research\feishu_try.json" -Raw -Encoding UTF8; "  body-preview: " + $c.Substring(0,[Math]::Min(300,$c.Length)) } }
}
