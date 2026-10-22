"""Extract an icon group from a Windows executable and save it as a .ico file.

Usage: python tools/extract_icon.py <exe> <group-index> <out.ico>
"""
import struct
import sys

import pefile

RT_ICON = 3
RT_GROUP_ICON = 14


def resources(pe, type_id):
    for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        if entry.id == type_id:
            for res in entry.directory.entries:
                lang = res.directory.entries[0]
                yield res.id, pe.get_data(lang.data.struct.OffsetToData, lang.data.struct.Size)


def main(exe, index, out):
    pe = pefile.PE(exe)
    icons = dict(resources(pe, RT_ICON))
    groups = list(resources(pe, RT_GROUP_ICON))
    _, group = groups[int(index)]

    _, _, count = struct.unpack_from("<HHH", group, 0)
    entries = []
    for i in range(count):
        w, h, colors, _, planes, bpp, size, icon_id = struct.unpack_from("<BBBBHHIH", group, 6 + i * 14)
        entries.append((w, h, colors, planes, bpp, icons[icon_id]))

    offset = 6 + 16 * count
    header = struct.pack("<HHH", 0, 1, count)
    directory = b""
    for w, h, colors, planes, bpp, data in entries:
        directory += struct.pack("<BBBBHHII", w, h, colors, 0, planes, bpp, len(data), offset)
        offset += len(data)
    with open(out, "wb") as f:
        f.write(header + directory + b"".join(e[5] for e in entries))
    print(f"wrote {out}: {[(e[0] or 256, e[4]) for e in entries]}")


if __name__ == "__main__":
    main(*sys.argv[1:])
