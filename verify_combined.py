# -*- coding: utf-8 -*-
import json, os
base = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(base,"out","sr_combined.json")
d = json.load(open(p, encoding="utf-8"))
print("analyzed:", d["analyzed"], "failed:", d["failed"])
print("prob_ready:", d["prob_ready"], "calibrated:", d["calibrated"])
print("errors:", d["errors"][:4])
print("elapsed:", d["elapsed_s"], "s")
print("data_dir:", d["data_dir"])
