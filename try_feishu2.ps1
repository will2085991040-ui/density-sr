
"--- follow redirects for wiki link ---"
curl.exe -s -L -o "C:\Users\mine\Downloads\quant_research\feishu_wiki.html" -w "code=%{http_code} final=%{url_effective} size=%{size_download}" --max-time 25 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" "https://my.feishu.cn/wiki/BO4lw44noi89FBkwrIiczxy7nna?from=from_copylink" 2>&1
""
"--- extract any docx token / document titles from html ---"
$c = Get-Content "C:\Users\mine\Downloads\quant_research\feishu_wiki.html" -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
if($c){
  if($c -match "[\\w]+BO4lw44noi89FB[A-Za-z0-9]*"){ "matched wiki token" }
  [regex]::Matches($c,'dashboard|wiki|docx|BO4lw|document_id') | Select-Object -First 10 | ForEach-Object { $_.Value }
  "len=" + $c.Length
}
