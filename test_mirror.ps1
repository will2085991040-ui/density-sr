$sites = @(
  "https://pypi.tuna.tsinghua.edu.cn/simple/numpy/",
  "https://mirrors.aliyun.com/pypi/simple/numpy/",
  "https://pypi.org/simple/numpy/",
  "https://mirrors.cloud.tencent.com/pypi/simple/numpy/"
)
foreach($s in $sites){
  $r = curl.exe -s -o NUL -w "http=%{http_code} time=%{time_total}" --max-time 20 $s 2>&1
  "$($s) => $r"
}