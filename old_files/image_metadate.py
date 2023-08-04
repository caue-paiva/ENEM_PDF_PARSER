import pyexifinfo as pxi

info = pxi.get_json("0Im0.png")


for i in info:
    for key, value in i.items():
        print(f"key: {key},  value:{value},")