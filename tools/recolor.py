"""Recolor the Blender orange in an .ico to its exact complementary blue.

Every orange-hued pixel is rotated 180 degrees in hue while keeping its
lightness and saturation, which in RGB is simply (max + min) - channel.
Blender orange #E87D0D therefore becomes #0D78E8, and the anti-aliased
edges (orange blended with white or transparency) stay perfectly smooth.

Usage: python tools/recolor.py <in.ico> <out.ico>
"""
import colorsys
import sys

from PIL import Image

SIZES = [256, 128, 96, 64, 48, 32, 24, 16]


def is_orange(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return s > 0.15 and 0.02 < h < 0.14  # roughly 7-50 degrees


def complement(r, g, b):
    k = max(r, g, b) + min(r, g, b)
    return k - r, k - g, k - b


def recolor(img):
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and is_orange(r, g, b):
                px[x, y] = (*complement(r, g, b), a)
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
