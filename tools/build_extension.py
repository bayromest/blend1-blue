"""Build the extension and the self-hosted extension repository.

Copies the icons into the extension package, validates and builds it with
Blender's own tooling, then regenerates the static repository in docs/,
which GitHub Pages serves at https://bayromest.github.io/blend1-blue/.

Usage: python tools/build_extension.py <path-to-blender.exe>
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "extension" / "blend1_blue"
REPO = ROOT / "docs"


def blender_command(blender, *args):
    subprocess.run([blender, "--factory-startup", "--command", "extension", *args], check=True)


def main(blender):
    for icon in ("blend1-blue.ico", "blend1-blue-file.ico"):
        shutil.copyfile(ROOT / "icons" / icon, SOURCE / icon)

    # The repository only offers the latest version.
    REPO.mkdir(exist_ok=True)
    for old in REPO.glob("*.zip"):
        old.unlink()

    blender_command(blender, "validate", str(SOURCE))
    blender_command(blender, "build", "--source-dir", str(SOURCE), "--output-dir", str(REPO))
    blender_command(
        blender, "server-generate", "--repo-dir", str(REPO),
        "--html", "--html-template", str(ROOT / "tools" / "repo_template.html"),
    )
    shutil.copyfile(ROOT / "assets" / "preview-dark.png", REPO / "preview.png")
    (REPO / ".nojekyll").touch()


if __name__ == "__main__":
    main(*sys.argv[1:])
