# -*- coding: utf-8 -*-
import requests, time, json
HE={'User-Agent':'Mozilla/5.0','Referer':'https://quote.eastmoney.com/','Accept':'*/*','Connection':'close'}
def g(url,headers,maxtry=5):
    for i in range(maxtry):
        try:
            r=requests.get(url,headers=headers,timeout=25)
            if r.status_code==200 and len(r.text)>20: return r.text
        except Exception:
            pass
        time.sleep(1.6)
    return None
txt=g('https://push2.eastmoney.com/api/qt/clist/get?fid=f3&po=1&pz=8000&pn=1&np=1&fltt=2&invt=2&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f12,f2,f3',HE)
print('none' if not txt else ('len '+str(len(txt))))
if txt:
    j=json.loads(txt)
    diff=j.get('data',{}).get('diff',[])
    print('total',j.get('data',{}).get('total'),'records',len(diff))
    if diff:
        ups=sum(1 for x in diff if x.get('f3',0)>=0); downs=len(diff)-ups
        zt=sum(1 for x in diff if x.get('f3',0)>=9.8); dt=sum(1 for x in diff if x.get('f3',0)<=-9.8)
        print('up',ups,'down',downs,'zt_geo',zt,'dt_geo',dt)
