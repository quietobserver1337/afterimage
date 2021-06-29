#!/usr/bin/env python3
"""afterimage web ui — read-only view over the local index."""
import os
import sys
import time

from flask import Flask, abort, render_template, send_file

import index as store

VERSION = "0.4.0"
OBSERVER = os.environ.get("AFTERIMAGE_OBSERVER", "quietobserver")

app = Flask(__name__)
ROOT = "."
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
        "SELECT id, name, width, height, bytes, ahash, dhash, indexed_at "
        "FROM images ORDER BY id DESC LIMIT 60").fetchall()
    cur = rows[0] if rows else None
    stats = {
        "frames": CON.execute("SELECT COUNT(*) FROM images").fetchone()[0],
        "seen": store.meta_get(CON, "frames_seen"),
    }
    return render_template(
        "index.html", rows=rows, cur=cur, stats=stats,
        similar=similar_pairs()[:18], pairs=len(similar_pairs()),
        observer=OBSERVER, uptime=fmt_uptime(), version=VERSION)


@app.route("/thumb/<int:i>")
def thumb(i):
    p = store.thumbs_dir(ROOT) / ("%d.jpg" % i)
    if not p.exists():
        abort(404)
    return send_file(str(p), mimetype="image/jpeg")


if __name__ == "__main__":
    ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
    CON = store.open_db(ROOT)
    app.run(port=8777)
