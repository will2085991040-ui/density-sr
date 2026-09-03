# -*- coding: utf-8 -*-
import json, os
base=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(base,"out","sr_all4.json"),encoding="utf-8"))
print("analyzed:",d["analyzed"],"failed:",d["failed"],"prob_ready:",d["prob_ready"],"calibrated:",d["calibrated"],"elapsed:",d["elapsed_s"])
