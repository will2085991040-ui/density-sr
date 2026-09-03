# -*- coding: utf-8 -*-
p = r'C:/Users/mine/Downloads/quant_research/server.py'
t = open(p, encoding='utf-8').read()
anchor = "    if not out['live'] and 'kline' not in out:"
assert anchor in t, 'missing anchor'
blk = [
"    # ---- 策略信号(触发位/开平仓/情绪过滤) ----",
"    try:",
"        from aiquant.signal_engine import signals_for",
"        from aiquant.market_sentiment import sentiment_market",
"        cl = out.get('closes') or []",
"        def _ema(aa,n):",
"            if not aa: return None",
"            k=2.0/(n+1); e=aa[0]",
"            for x in aa: e=(x-e)*k+e",
"            return e",
"        ema5=ema10=ema20=None",
"        if len(cl)>=20: ema20=_ema(cl,20)",
"        if len(cl)>=10: ema10=_ema(cl,10)",
"        if len(cl)>=5: ema5=_ema(cl,5)",
"        sent = sentiment_market()",
"        qq = out.get('quote') or {}; px = qq.get('price')",
"        sig = signals_for(symbol, market, tf, price=px, sr_bands=out.get('bands'),",
"                          ema5=ema5, ema10=ema10, ema20=ema20, sentiment=sent)",
"        out['signal'] = sig",
"        out['sentiment'] = {'score': sent.get('score'), 'label': sent.get('label'),",
"                            'suggest': sent.get('suggest')}",
"    except Exception:",
"        pass",
""
]
t = t.replace(anchor, "\n".join(blk) + "\n" + anchor, 1)
open(p,'w',encoding='utf-8').write(t)
print('realtime signal block inserted')
