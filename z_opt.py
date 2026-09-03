# -*- coding: utf-8 -*-
import py_compile
f=r"C:/Users/mine/Downloads/quant_research/aiquant/factor_mine.py"
t=open(f,encoding="utf-8").read()
old='''    X = np.vstack(Xs); y = np.concatenate(ys)
    clf = RandomForestClassifier(n_estimators=120, min_samples_leaf=8, random_state=7)
    clf.fit(X, np.where(y > 0, 1, 0))'''
new='''    X = np.vstack(Xs); y = np.concatenate(ys)
    # 提速: 采样上限控制训练体量, 保证 UI 秒出
    if len(X) > 26000:
        idx = np.random.RandomState(3).choice(len(X), 26000, replace=False)
        X, y = X[idx], y[idx]
    clf = RandomForestClassifier(n_estimators=70, min_samples_leaf=16, random_state=7)
    clf.fit(X, np.where(y > 0, 1, 0))'''
assert old in t, "mine"
t=t.replace(old,new,1)
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f,doraise=True)
print("mine optimized")
