# -*- coding: utf-8 -*-
import os, glob
d = r"C:\Users\mine\Desktop\新建文件夹 (5)"
for p in sorted(glob.glob(os.path.join(d, "*.jpg"))):
    try:
        sz = os.path.getsize(p)
        print(os.path.basename(p), sz)
    except Exception as e:
        print("err", p, e)
# try to extract EXIF basic (dimensions) without PIL if needed
try:
    from PIL import Image
    for p in sorted(glob.glob(os.path.join(d, "*.jpg"))):
        im = Image.open(p)
        print(os.path.basename(p), "->", im.size, im.mode)
except Exception as e:
    print("PIL", e)
