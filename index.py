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
    con.commit()
    return con


def iter_images(root):
    for p in sorted(Path(root).rglob("*")):
        if p.suffix.lower() in EXTS and DB_DIR not in p.parts:
            yield p


def scan(root, con=None):
    close = con is None
    con = con or open_db(root)
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
        t = im.copy()
        t.thumbnail((192, 192))
        t.save(thumbs_dir(root) / ("%d.jpg" % cur.lastrowid), quality=82)
        n += 1
    con.commit()
    if close:
        con.close()
    return n
