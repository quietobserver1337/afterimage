"""sqlite index for a local image library."""
import sqlite3
import time
from pathlib import Path

import hashing

EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
DB_DIR = ".afterimage"


def db_path(root):
    return Path(root) / DB_DIR / "index.db"


def thumbs_dir(root):
    return Path(root) / DB_DIR / "thumbs"


def open_db(root):
    d = Path(root) / DB_DIR
    d.mkdir(exist_ok=True)
    thumbs_dir(root).mkdir(exist_ok=True)
    con = sqlite3.connect(db_path(root))
    con.execute("""CREATE TABLE IF NOT EXISTS images(
        id INTEGER PRIMARY KEY,
        path TEXT UNIQUE,
        name TEXT,
        mtime REAL,
        bytes INTEGER,
        width INTEGER,
        height INTEGER,
        ahash INTEGER,
        dhash INTEGER,
        indexed_at REAL)""")
    con.execute(
        "CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")
    con.commit()
    return con


def meta_get(con, key, default="0"):
    row = con.execute("SELECT value FROM meta WHERE key=?",
                      (key,)).fetchone()
    return row[0] if row else default


def meta_set(con, key, value):
    con.execute("INSERT OR REPLACE INTO meta VALUES(?,?)",
                (key, str(value)))


def iter_images(root):
    for p in sorted(Path(root).rglob("*")):
        if p.suffix.lower() in EXTS and DB_DIR not in p.parts:
            yield p


def scan(root, con=None):
    close = con is None
    con = con or open_db(root)
    seen = int(meta_get(con, "frames_seen"))
    n = 0
    for p in iter_images(root):
        st = p.stat()
        row = con.execute("SELECT id, mtime FROM images WHERE path=?",
                          (str(p),)).fetchone()
        if row and row[1] == st.st_mtime:
            continue
        try:
            im = hashing.load(p)
        except Exception:
            continue
        cur = con.execute(
            """INSERT OR REPLACE INTO images
            (path,name,mtime,bytes,width,height,ahash,dhash,indexed_at)
            VALUES(?,?,?,?,?,?,?,?,?)""",
            (str(p), p.name, st.st_mtime, st.st_size, im.width, im.height,
             hashing.ahash(im), hashing.dhash(im), time.time()))
        seen += 1
        t = im.copy()
        t.thumbnail((192, 192))
        t.save(thumbs_dir(root) / ("%d.jpg" % cur.lastrowid), quality=82)
        n += 1
    meta_set(con, "frames_seen", seen)
    con.commit()
    if close:
        con.close()
    return n


def find_similar(con, max_dist=6, limit=None):
    rows = con.execute(
        "SELECT id, dhash FROM images ORDER BY id").fetchall()
    pairs = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            d = hashing.hamming(rows[i][1], rows[j][1])
            if d <= max_dist:
                pairs.append((rows[i][0], rows[j][0], d))
                if limit and len(pairs) >= limit:
                    return pairs
    return pairs
