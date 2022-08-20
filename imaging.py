"""image loading, perceptual hashes, thumbnails."""
from pathlib import Path

from PIL import Image

EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff"}


def iter_images(root):
    for p in sorted(Path(root).rglob("*")):
        if p.suffix.lower() in EXTS and ".afterimage" not in p.parts:
            yield p


def load(path):
    return Image.open(path).convert("RGB")


def ahash(im, size=8):
    g = im.convert("L").resize((size, size), Image.ANTIALIAS)
    px = list(g.getdata())
    avg = sum(px) / len(px)
    bits = 0
    for i, v in enumerate(px):
        if v >= avg:
            bits |= 1 << i
    return bits


def dhash(im, size=8):
    g = im.convert("L").resize((size + 1, size), Image.ANTIALIAS)
    px = list(g.getdata())
    bits, i = 0, 0
    for y in range(size):
        for x in range(size):
            if px[y * (size + 1) + x] > px[y * (size + 1) + x + 1]:
                bits |= 1 << i
            i += 1
    return bits


def hamming(a, b):
    return bin(a ^ b).count("1")


def thumb(im, size=192):
    t = im.copy()
    t.thumbnail((size, size), Image.ANTIALIAS)
    return t


def palette(im, n=5):
    q = im.resize((64, 64)).quantize(colors=n, method=Image.MEDIANCUT)
    pal = q.getpalette()[: n * 3]
    return ["#%02x%02x%02x" % tuple(pal[i:i + 3])
            for i in range(0, len(pal), 3)]
