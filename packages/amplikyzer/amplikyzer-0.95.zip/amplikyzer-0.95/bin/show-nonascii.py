# works on linux
# Sven Rahmann, August 2011

import sys

def non_ascii_lines(buf):
    nl = [i for (i,x) in enumerate(buf) if x==ord(b'\n')]
    na = [i for (i,x) in enumerate(buf) if x>=128]
    nalines = [1+sum(i<p for i in nl) for p in na]
    return nalines


fnames = sys.argv[1:]
for fname in fnames:
    with open(fname,"rb") as f:
        buf = f.read()
        lines = non_ascii_lines(buf)
        if len(lines)>0:
            print("{}: lines".format(fname), ", ".join(map(str,lines)))
# done.
