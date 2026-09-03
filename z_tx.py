# -*- coding: utf-8 -*-
import requests
UA={'User-Agent':'Mozilla/5.0','Referer':'https://gu.qq.com/'}
def t(name,q):
    try:
        r=requests.get('https://qt.gtimg.cn/q='+q,headers=UA,timeout=8)
        r.encoding='gbk'
        print(name,'->',r.text[:300].replace(chr(10),' '))
    except Exception as e:
        print(name,'ERR',e)
t('AMKT','marketA')
t('QUANCN','qt_usc')
t('RISE','s_rise')
t('PNK','pz_res')  
t('EDGE','b3_china')
t('SCORE','market_cn')
t('BREADTH','a000001')
