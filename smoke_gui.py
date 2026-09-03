# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
import gui
try:
    app = gui.AiquantApp()
    app.update_idletasks()
    # exercise one action that is cheap: scan list_symbols
    print("GUI constructed OK, tabs created")
    print("symbols A股:", len(app.cat()._stock) if app._cat else "?")
    app.destroy()
    print("DESTROYED")
except Exception as e:
    import traceback
    traceback.print_exc()
    print("GUI ERROR:", e)
