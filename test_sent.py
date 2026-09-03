# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.features.sentiment import sentiment, crawl_news
# offline test with synthetic headlines
head = ["公司发布超预期净利润增长", "股价强势突破新高", "遭监管问询，评级下调", "中标签约重大订单，回购计划启动"]
r = sentiment(headlines=head)
print("offline score:", r["score"], "label:", r["label"], "src:", r["source"], "top:", r["top"][:5])
# live crawl (may fail on network)
try:
    live = crawl_news("600519")
    print("live crawled news:", len(live), (live[:3] if live else "network unavailable"))
except Exception as ex:
    print("crawl err:", ex)
