# -*- coding: utf-8 -*-
import requests, json
UA={'User-Agent':'Mozilla/5.0','Referer':'https://gu.qq.com/'}
EM={'User-Agent':'Mozilla/5.0','Referer':'https://data.eastmoney.com/'}
def t(name,url,headers=UA):
    try:
        r=requests.get(url,headers=headers,timeout=8)
        print(name,'->',r.status_code,'len',len(r.text),'::',r.text[:400].replace(chr(10),' '))
        print('---')
    except Exception as e:
        print(name,'ERR',e)
t('TX-pk','https://qt.gtimg.cn/q=s_pk')
t('EM-clist-zt','https://push2ex.eastmoney.com/getTopicZDFen?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=5&sort=fbt:asc&date=')
t('EM-overview','https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3')
