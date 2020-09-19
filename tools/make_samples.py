#!/usr/bin/env python3
"""generate a synthetic test corpus for afterimage.

    python3 tools/make_samples.py [n] [dir]
"""
import colorsys
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

FAMILIES = 12
SIZE = 128


def shade(hue, v):
    r, g, b = colorsys.hsv_to_rgb(hue % 1, 0.45 + 0.3 * v, 0.35 + 0.55 * v)
    return (int(r * 255), int(g * 255), int(b * 255))


def base(rng, size=SIZE):
    hue = rng.random()
    im = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(im)
    for y in range(size):
        d.line([(0, y), (size, y)], fill=shade(hue, y / size))
    for _ in range(rng.randint(1, 3)):
        x, y = rng.randint(8, size - 50), rng.randint(8, size - 50)
        r = rng.randint(12, 34)
        d.ellipse([x, y, x + r * 2, y + r * 2],
                  fill=shade(hue + 0.35, rng.random()))
    return im.filter(ImageFilter.GaussianBlur(1.2))


def variant(im, rng):
    im = im.copy()
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(rng.randint(2, 6)):
        x, y = rng.randint(0, SIZE - 4), rng.randint(0, SIZE - 4)
        r = rng.randint(1, 4)
        d.ellipse([x, y, x + r, y + r],
                  fill=(255, 255, 255, rng.randint(40, 120)))
    if rng.random() < 0.35:
        k = rng.uniform(0.92, 1.08)
        im = im.point(lambda v: min(255, int(v * k)))
    return im


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1400
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "samples")
    out.mkdir(exist_ok=True)
    rng = random.Random(20200919)
    bases = [base(random.Random(1000 + i)) for i in range(FAMILIES)]
    for i in range(n):
        variant(rng.choice(bases), rng).save(
            out / ("img_%04d.jpg" % i), quality=82)
        if (i + 1) % 200 == 0:
            print(i + 1)
    print("%d images -> %s" % (n, out))


if __name__ == "__main__":
    main()
