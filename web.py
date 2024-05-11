#!/usr/bin/env python3
"""afterimage web ui — read-only view over the local index."""
import argparse
import json
import os
import time
from pathlib import Path

from flask import Flask, abort, render_template, send_file

import index as store

VERSION = "0.4.2"
OBSERVER = os.environ.get("AFTERIMAGE_OBSERVER", "quietobserver")

app = Flask(__name__)
ROOT = "samples"
CON = None
STARTED = time.time()
_SIMILAR = None


def similar_pairs():
    global _SIMILAR
    if _SIMILAR is None:
        _SIMILAR = store.find_similar(CON, max_dist=7)
    return _SIMILAR


def fmt_uptime():
    s = int(time.time() - STARTED)
    return "%02d:%02d:%02d" % (s // 3600, (s % 3600) // 60, s % 60)


@app.route("/")
def home():
    rows = CON.execute(
        "SELECT id, name, width, height, bytes, ahash, dhash, palette, "
        "indexed_at FROM images ORDER BY id DESC LIMIT 48").fetchall()
    cur = rows[0] if rows else None
    return render_template(
        "index.html", rows=rows, cur=cur,
        stats=store.stats(CON, ROOT),
        similar=similar_pairs()[:18], pairs=len(similar_pairs()),
        cur_pal=json.loads(cur[7]) if cur and cur[7] else [],
        cur_when=time.strftime("%Y-%m-%d %H:%M",
                               time.localtime(cur[8])) if cur else "",
        observer=OBSERVER, uptime=fmt_uptime(), version=VERSION,
        root=str(Path(ROOT).resolve()))


@app.route("/thumb/<int:i>")
def thumb(i):
    p = store.thumbs_dir(ROOT) / ("%d.jpg" % i)
    if not p.exists():
        abort(404)
    return send_file(str(p), mimetype="image/jpeg")


def main():
    global ROOT, CON
    ap = argparse.ArgumentParser(prog="web.py")
    ap.add_argument("--root", default="samples")
    ap.add_argument("--port", type=int, default=8777)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    ROOT = args.root
    CON = store.open_db(ROOT)
    if store.stats(CON, ROOT)["frames"] == 0:
        print("indexing %s ..." % ROOT)
        print("indexed %d new frames" % store.scan(ROOT, CON))
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
