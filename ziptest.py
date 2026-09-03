import zipfile
for z in ["detect_support_resistance.zip","alphamaster.zip","abu.zip","vnpy.zip"]:
    try:
        zf = zipfile.ZipFile(z)
        names = zf.namelist()
        print("OK", z, "entries=", len(names), "first=", names[:2])
    except Exception as e:
        print("INVALID", z, ":", e)
