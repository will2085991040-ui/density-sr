# -*- coding: utf-8 -*-
import requests, time, json
HE={'User-Agent':'Mozilla/5.0','Referer':'https://quote.eastmoney.com/'}
def g(url):
    for i in range(3):
        try:
            r=requests.get(url,headers=HE,timeout=15)
            if r.status_code==200: return r.text
        except Exception:
            time.sleep(1.2)
    return None
txt=g('https://push2.eastmoney.com/api/qt/clist/get?fid=f3&po=1&pz=6000&pn=1&np=1&fltt=2&invt=2&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f12,f2,f3')
if not txt:
    print('none')
else:
    print('len',len(txt))
    j=json.loads(txt)
    diff=j.get('data',{}).get('diff',[])
    print('total',j.get('data',{}).get('total'),'got',len(diff))
    if diff:
        ups=sum(1 for x in diff if x.get('f3',0)>=0)
        downs=sum(1 for x in diff if x.get('f3',0)<0)
        print('up',ups,'down',downs,'flat',len(diff)-ups-downs)
        zt=sum(1 for x in diff if x.get('f3',0)>=9.8)
        dt=sum(1 for x in diff if x.get('f3',0)<=-9.8)
        print('approx_zt',zt,'approx_dt',dt)
    t2=g('https://push2.eastmoney.com/api/qt/ulist.get?fltt=2&secids=1.000001,0.399001,1.000300,0.399006&fields=f2,f3,f4,f6,f12,f14')
    if t2:
        j2=json.loads(t2)
        print('idx',json.dumps(j2.get('data',{}).get('diff',[])+j2.get('data',{}).get('data',[])))
