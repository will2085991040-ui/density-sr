# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r'C:/Users/mine/Downloads/quant_research')
import server
r = server.realtime_json('600519','A股','daily')
print('signal', json.dumps(r.get('signal'),ensure_ascii=False))
print('qprice', (r.get('quote') or {}).get('price'))
print('nbars', len(r.get('closes') or []))
print('bands_zones', [ (b.get('zone_type'), b.get('center')) for b in (r.get('bands') or []) ])
