"""perceptual hashes."""
from PIL import Image


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
