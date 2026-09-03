# -*- coding: utf-8 -*-
p = r'C:/Users/mine/Downloads/quant_research/aiquant/market_sentiment.py'
t = open(p, encoding='utf-8').read()
anchor = "    if not txt:\n        return None"
assert anchor in t, 'a1'
insert = "    if not txt:\n        # 回退: 腾讯行情(s_sh000001 等) 上证/创业板指\n        try:\n            import requests\n            r = requests.get('https://qt.gtimg.cn/q=s_sh000001,s_sz399001,s_sz399006', timeout=8, headers={'User-Agent': 'Mozilla/5.0'})\n            r.encoding = 'gbk'\n            out = {}\n            for line in r.text.split(';'):\n                if '~' not in line: continue\n                f = line.split('~')\n                if len(f) < 6: continue\n                code = str(f[2])\n                out[code] = {'name': f[1], 'pct': float(f[5]) if f[5] else None, 'close': float(f[3]) if f[3] else None}\n            return out or None\n        except Exception:\n            return None\n"
t = t.replace(anchor, insert, 1)
open(p,'w',encoding='utf-8').write(t)
print('tencent idx fallback added')
