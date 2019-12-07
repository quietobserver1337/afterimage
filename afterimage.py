#!/usr/bin/env python3
"""afterimage — scan a folder of images and report near-duplicates."""
import sys
from pathlib import Path

import hashing

EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    thresh = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    hashes = {}
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() not in EXTS:
            continue
        try:
            hashes[p] = hashing.dhash(hashing.load(p))
        except Exception as e:
            print("skip", p, e, file=sys.stderr)
    print("hashed %d images" % len(hashes))
    paths = sorted(hashes)
    for i, a in enumerate(paths):
        for b in paths[i + 1:]:
            d = hashing.hamming(hashes[a], hashes[b])
            if d <= thresh:
                print("%3d  %s  ~  %s" % (d, a, b))


if __name__ == "__main__":
    main()
