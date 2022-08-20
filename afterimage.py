#!/usr/bin/env python3
"""afterimage — local image similarity index.

    afterimage.py scan    [--root DIR]
    afterimage.py dupes   [--root DIR] [--thresh N]
    afterimage.py similar <id> [--root DIR] [--thresh N]
    afterimage.py stats   [--root DIR]
"""
import argparse

import index


def main():
    ap = argparse.ArgumentParser(prog="afterimage")
    ap.add_argument("cmd", choices=["scan", "dupes", "similar", "stats"])
    ap.add_argument("target", nargs="?", default=None)
    ap.add_argument("--root", default=".")
    ap.add_argument("--thresh", type=int, default=6)
    a = ap.parse_args()
    con = index.open_db(a.root)

    if a.cmd == "scan":
        print("indexed %d new images" % index.scan(a.root, con))
    elif a.cmd == "dupes":
        for x, y, d in index.find_similar(con, max_dist=a.thresh):
            print("%3d  #%d ~ #%d" % (d, x, y))
    elif a.cmd == "similar":
        want = int(a.target)
        for x, y, d in index.find_similar(con, max_dist=a.thresh):
            if want in (x, y):
                other = y if x == want else x
                row = con.execute("SELECT name FROM images WHERE id=?",
                                  (other,)).fetchone()
                print("%3d  #%d  %s" % (d, other, row[0] if row else "?"))
    elif a.cmd == "stats":
        s = index.stats(con, a.root)
        print("%(frames)s frames, %(seen)s seen, db %(db)s" % s)


if __name__ == "__main__":
    main()
