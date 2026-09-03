# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
import gui
outf = r"C:\Users\mine\Downloads\quant_research\smoke2.txt"
app = gui.AiquantApp()
app.update_idletasks(); app.update()
app.v_sym.delete(0,"end"); app.v_sym.insert(0,"贵州茅台"); app.v_tf.set("daily")
app.cb_oos.set(True)
done = {}
def check():
    st = app.status.cget("text") or ""
    if "✅" in st:
        done["kline"] = app._img_ref is not None
        with open(outf,"w",encoding="utf-8") as f:
            f.write("viz_kline=%s\n" % (app._img_ref is not None))
            f.write("bt_tab=%s\n" % ("严谨" in (str(app.bt_tree.cget("columns")))))
        app.after(120, app.destroy)
    else:
        app.after(250, check)
app.after(300, app.do_viz)
# after viz, also run bt worker via same thread-safe path
def bt_after():
    app._bt_worker()
app.after(3500, bt_after)
app.after(9000, check)
app.mainloop()
print("done mainloop")
os._exit(0)
