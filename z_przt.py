# -*- coding: utf-8 -*-
import requests
EM={'User-Agent':'Mozilla/5.0','Referer':'https://data.eastmoney.com/'}
def t(name,url):
    try:
        r=requests.get(url,headers=EM,timeout=8)
        print(name,'->',r.status_code,'len',len(r.text),'::',r.text[:280].replace(chr(10),' '))
        print('---')
    except Exception as e:
        print(name,'ERR',e)
# 涨停池
t('ZTPOOL','https://push2ex.eastmoney.com/getTopicZTPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=3&sort=fbt%3Aasc&date=20260830')
# 涨跌家数分布 (sina-style)
t('DIST','https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=1&secids=1.000001,0.399001&fields=f2,f3')
# 市场涨跌家数 quick - 变大
t('BREADTH','https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=0&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3')
