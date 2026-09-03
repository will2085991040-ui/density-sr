# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r'C:/Users/mine/Downloads/quant_research')
import server
from aiquant.signal_engine import signals_for
r = server.realtime_json('600519','A股','daily')
bands = r.get('bands') or []
cl = r.get('closes') or []
qq = r.get('quote') or {}
px = qq.get('price') or (cl[-1] if cl else None)
print('px', px, 'bands', len(bands), 'cl', len(cl), 'bandtypes', set(b.get('zone_type') for b in bands))
s = signals_for('600519','A股','daily',price=px,sr_bands=bands)
print('direct sig', json.dumps(s,ensure_ascii=False))
