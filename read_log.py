import codecs
import sys

try:
    with codecs.open("run.log", "r", "utf-16le") as f:
        lines = f.readlines()
        print("".join(lines[-30:]))
except Exception as e:
    print(e)
