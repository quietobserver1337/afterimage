#!/usr/bin/env python3
"""afterimage — local image similarity index.

    afterimage.py scan [root]
    afterimage.py dupes [root] [thresh]
    afterimage.py similar <id> [root] [thresh]
"""
import sys

import hashing
import index


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    root = sys.argv[2] if len(sys.argv) > 2 else "."
    if cmd == "scan":
        print("indexed %d new images" % index.scan(root))
    elif cmd == "dupes":
        thresh = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        con = index.open_db(root)
        rows = con.execute("SELECT path, dhash FROM images").fetchall()
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                d = hashing.hamming(rows[i][1], rows[j][1])
                if d <= thresh:
                    print("%3d  %s  ~  %s" % (d, rows[i][0], rows[j][0]))
    elif cmd == "similar":
        want = int(sys.argv[2])
        root = sys.argv[3] if len(sys.argv) > 3 else "."
        thresh = int(sys.argv[4]) if len(sys.argv) > 4 else 6
        con = index.open_db(root)
        for x, y, d in index.find_similar(con, max_dist=thresh):
            if want in (x, y):
                other = y if x == want else x
                row = con.execute("SELECT name FROM images WHERE id=?",
                                  (other,)).fetchone()
                print("%3d  #%d  %s" % (d, other, row[0] if row else "?"))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
