# -*- coding: utf-8 -*-
f="C:/Users/mine/Downloads/quant_research/build_onefile_v92.py"
t=open(f,encoding="utf-8").read()
if "channel_panel.js" not in t:
    t=t.replace("sentiment_panel.js')", "sentiment_panel.js','channel_panel.js')",1)
if "channel_analysis" not in t:
    t=t.replace("'--hidden-import','openai',", "'--hidden-import','openai',\n    '--hidden-import','aiquant.channel_analysis',",1)
if "j('knowledge')" not in t:
    sep = chr(10) + chr(10)
    t=t.replace("'--add-data', j('build','data_pack.zip') + os.pathsep + '.',", "'--add-data', j('build','data_pack.zip') + os.pathsep + '.',\n    '--add-data', j('knowledge') + os.pathsep + 'knowledge',",1)
open(f,"w",encoding="utf-8").write(t)
import py_compile
py_compile.compile(f,doraise=True)
print("patched:", "channel_panel.js" in open(f,encoding="utf-8").read(), "channel_analysis", "channel_analysis" in open(f,encoding="utf-8").read())