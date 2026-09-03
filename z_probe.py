# -*- coding: utf-8 -*-
import requests, json
UA={'User-Agent':'Mozilla/5.0','Referer':'https://gu.qq.com/'}
def t(name,url):
    try:
        r=requests.get(url,headers=UA,timeout=8)
        text=r.text
        print(name,'->',r.status_code,'len',len(text))
        print(text[:600].replace('\\n',' '))
        print('---')
    except Exception as e:
        print(name,'ERR',e)
# Tencent market A-state (breadth)
t('AQAS','https://proxy.finance.qq.com/ifzqgtimg/appstock/app/mktAState/getMktAState')
t('SINA','https://hq.sinajs.cn/list=sh000001')
t('GJ','https://qt.gtimg.cn/q=s_sh000001')
t('EM-breadth','https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids=1.000001,0.399001,1.000300,0.399006&fields=f2,f3,f12')
