"""Recolor the Blender orange in an .ico to Blender's own logo blue.

Blender orange #E87D0D becomes #265787, the dark blue of the logo's eye.
Anti-aliased edges are orange blended with white, so each orange-hued pixel
is unmixed into (amount of orange, amount of white) and remixed with the
blue instead. Edges stay perfectly smooth; transparency is untouched.

Usage: python tools/recolor.py <in.ico> <out.ico>
"""
import colorsys
import sys

from PIL import Image

SIZES = [256, 128, 96, 64, 48, 32, 24, 16]
ORANGE = (0xE8, 0x7D, 0x0D)
BLUE = (0x26, 0x57, 0x87)


def is_orange(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return s > 0.03 and 0.02 < h < 0.14  # roughly 7-50 degrees


def to_blue(r, g, b):
    # The blue channel separates orange (13) from white (255) the most.
    t = min(max((255 - b) / (255 - ORANGE[2]), 0.0), 1.0)
    return tuple(round(t * c + (1 - t) * 255) for c in BLUE)


def recolor(img):
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and is_orange(r, g, b):
                px[x, y] = (*to_blue(r, g, b), a)
    return img


def main(src, dst):
    ico = Image.open(src)
    frames = []
    for size in SIZES:
        ico.size = (size, size)
        frames.append(recolor(ico.copy()))
    # Pillow writes each frame as-is when given pre-rendered sizes.
    frames[0].save(dst, format="ICO", sizes=[(s, s) for s in SIZES], append_images=frames[1:])
    print(f"wrote {dst}")


if __name__ == "__main__":
    main(*sys.argv[1:])
