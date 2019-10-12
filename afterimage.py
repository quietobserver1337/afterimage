#!/usr/bin/env python3
"""afterimage — scan a folder of images and report near-duplicates."""
import sys
from pathlib import Path
from PIL import Image

EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


def ahash(path, size=8):
    im = Image.open(path).convert("L").resize((size, size), Image.ANTIALIAS)
    px = list(im.getdata())
    avg = sum(px) / len(px)
    bits = 0
    for i, v in enumerate(px):
        if v >= avg:
            bits |= 1 << i
    return bits


def dist(a, b):
    return bin(a ^ b).count("1")


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    hashes = {}
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() not in EXTS:
            continue
        try:
            hashes[p] = ahash(p)
        except Exception as e:
            print("skip", p, e, file=sys.stderr)
    print("hashed %d images" % len(hashes))
    paths = sorted(hashes)
    for i, a in enumerate(paths):
        for b in paths[i + 1:]:
            d = dist(hashes[a], hashes[b])
            if d <= 5:
                print("%3d  %s  ~  %s" % (d, a, b))


if __name__ == "__main__":
    main()
