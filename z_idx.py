# -*- coding: utf-8 -*-
f=r"C:/Users/mine/Downloads/quant_research/webui/index.html"
t=open(f,encoding="utf-8").read()
# add a channel section after the pa-panel close
old='''        <div class="pa-body" id="pa-body"><span class="muted">选择品种后点击「运行双Agent研判」→ 稳健(6.16) 与 激进(6.24) 同时给出生决策。</span></div>
      </div>'''
new='''        <div class="pa-body" id="pa-body"><span class="muted">选择品种后点击「运行双Agent研判」→ 稳健(6.16) 与 激进(6.24) 同时给出生决策。</span></div>
      </div>
      <div class="pa-panel" style="margin-top:10px">
        <div class="pa-head">
          <span class="t">下跌宽通道 AI</span>
          <span class="pa-sub">线性回归通道 · 宽度/斜率/位置</span>
          <button id="btn-channel" class="btn-orange mini">下跌宽通道分析</button>
        </div>
        <div class="pa-body" id="ch-body"><span class="muted">选择品种后点击「下跌宽通道分析」→ 识别并解读下跌宽通道。</span></div>
      </div>'''
assert old in t, "pa anchor"
t=t.replace(old,new,1)
# include channel_panel.js with other scripts
old2='<script src="sentiment_panel.js"></script>'
new2='<script src="sentiment_panel.js"></script>\n  <script src="channel_panel.js"></script>'
if old2 in t:
    t=t.replace(old2,new2,1)
else:
    # fallback: append before </body>
    t=t.replace('</body>', '<script src="channel_panel.js"></script>\n</body>')
open(f,"w",encoding="utf-8").write(t)
print("index patched; ch includes=", t.count("channel_panel.js"))
