# -*- coding: utf-8 -*-
import re, py_compile
f='C:/Users/mine/Downloads/quant_research/aiquant/pa_llm.py'
t=open(f,encoding='utf-8').read()
i=t.find('_prompt_files')
j=t.find('def _build_prompt')
block = chr(10).join([
  'def _prompt_files(stage):',
  '    import os, glob',
  '    here = os.path.dirname(os.path.abspath(__file__))',
  '    kdir = os.path.join(here, "..", "knowledge", "prompts")',
  '    order = (["1-提示词大纲","2-二元决策","3-市场诊断框架","4-文件16"] if stage=="诊断" else',
  '              ["1-提示词大纲","2-二元决策","5-震荡区间分析","6-震荡区间交易","7-二次入场","8-文件19","文件18-突破","10-铁丝网","11-磁力位","12-逐棒","4-文件16","13-文件17","文件23"])',
  '    pool = sorted(glob.glob(os.path.join(kdir, "*.txt")))',
  '    picked, out = [], []',
  '    for key in order:',
  '        for p in pool:',
  '            if key in os.path.basename(p) and p not in picked:',
  '                picked.append(p); out.append(open(p, encoding="utf-8").read().strip()); break',
  '    return out',
  '',
  'def _system_prompt(stage="决策"):',
  '    try:',
  '        return (chr(10)*2).join(_prompt_files(stage))',
  '    except Exception:',
  '        return ""',
  '',
])
if i>=0 and j>i:
    t = t[:i] + block + t[j:]
    open(f,'w',encoding='utf-8').write(t)
    py_compile.compile(f, doraise=True)
    print('loader ok, block len', len(block))
else:
    print('anchors not found', i, j)
