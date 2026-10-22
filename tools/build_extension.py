"""Build the Blender extension zip for extensions.blender.org.

Copies the icon into the extension package, then runs Blender's own
validator and builder.

Usage: python tools/build_extension.py <path-to-blender.exe>
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "extension" / "blend1_blue"
DIST = ROOT / "dist"


def main(blender):
    shutil.copyfile(ROOT / "icons" / "blend1-blue.ico", SOURCE / "blend1-blue.ico")
    DIST.mkdir(exist_ok=True)
    for command in (
        ["validate", str(SOURCE)],
        ["build", "--source-dir", str(SOURCE), "--output-dir", str(DIST)],
    ):
        subprocess.run([blender, "--factory-startup", "--command", "extension", *command], check=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
