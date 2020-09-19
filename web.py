#!/usr/bin/env python3
"""afterimage web ui — read-only view over the local index."""
import sys

from flask import Flask, abort, render_template, send_file

import index as store

app = Flask(__name__)
ROOT = "."
CON = None


@app.route("/")
def home():
    rows = CON.execute(
        "SELECT id, name, width, height, bytes FROM images "
        "ORDER BY id DESC LIMIT 60").fetchall()
    total = CON.execute("SELECT COUNT(*) FROM images").fetchone()[0]
    return render_template("index.html", rows=rows, total=total)


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
