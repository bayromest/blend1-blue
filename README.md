<div align="center">

<img src="icons/blend1-blue.png" width="128" alt="Blue Blender backup icon">

# blend1-blue

**Give Blender's `.blend1` backup files a blue icon, so you stop opening the backup by accident.**

Windows · Blender extension or one double-click · no admin rights · fully undoable

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/preview-dark.png">
  <img src="assets/preview-light.png" width="600" alt="scene.blend with the normal orange icon next to scene.blend1 and scene.blend2 with a blue icon">
</picture>

</div>

---

## The problem

Every time you save, Blender keeps the previous version as `yourfile.blend1`. On Windows
that backup gets **the exact same orange icon** as the real file, sitting right next to it.

So you double-click the wrong one, work for an hour, and realise you were in last save's
version. We've all done it.

## The fix

`blend1-blue` gives every backup (`.blend1` up to `.blend32`) its own icon: the official
Blender logo, the same one your `.blend` files show, with the orange swapped for **Blender's own logo blue**.

- Orange `.blend` → your file.
- Blue `.blend1` → the backup. Leave it alone unless something went wrong.

Double-clicking a backup still opens it in Blender, so recovering from a crash works
exactly like before. It just won't happen by accident anymore.

## Install

### Option A: Blender extension (recommended)

1. Download **`blend1_blue-1.0.0.zip`** from the [latest release](../../releases/latest).
2. Drag it into Blender, or go to *Edit → Preferences → Get Extensions → ⌄ → Install from Disk*.
3. That's it. The blue icons apply as soon as the extension is enabled.

Soon also on [extensions.blender.org](https://extensions.blender.org): search **Blend1 Blue**
right inside Blender's *Get Extensions*.

**To undo:** disable or uninstall the extension. Closing Blender does *not* remove the icons,
they stay until you turn the extension off.

### Option B: without Blender

1. Download **`blend1-blue-windows.zip`** from the [latest release](../../releases/latest) and unzip it.
2. Double-click **`Install.cmd`**.

**To undo:** double-click **`Uninstall.cmd`**.

> [!NOTE]
> Windows may ask *"Do you want to run this file?"* because it came from the internet.
> Click **Run**. The scripts are short and readable, take a look at
> [`scripts/install.ps1`](scripts/install.ps1) first if you like.

Both options do exactly the same thing and can be mixed: undoing with either one cleans up
after the other.

## What it actually does

Nothing magic, and nothing outside your own Windows user account:

| What | Where |
| --- | --- |
| Registers a "Blender Backup File" type with the blue icon | `HKCU\Software\Classes\Blender.BackupFile` |
| Points `.blend1` … `.blend32` at it | `HKCU\Software\Classes\.blendN` |
| Reuses the command Windows opens `.blend` files with | so double-click still opens the same Blender |
| Clears any saved *"Always open with"* choice for backups | it would otherwise override the icon |
| Remembers anything it replaced | `HKCU\Software\blend1-blue`, used when undoing |

The icon file itself lives in the extension's user folder (Option A) or in
`%LOCALAPPDATA%\blend1-blue` (Option B). No admin rights, no background process, and Blender
itself is never modified.

> [!TIP]
> Installed a **new Blender version** and want backups to open in it? Click
> *Refresh Icons* in the extension's preferences, or run `Install.cmd` again.

## The color

The Blender logo has two colors besides white: the orange `#E87D0D` and the blue of
its eye, `#265787`. Backups simply use the logo's own blue everywhere, so they still look
unmistakably like Blender, just "the quiet one".

| | Hex | |
| --- | --- | --- |
| Blender orange | `#E87D0D` | ![#E87D0D](https://placehold.co/16x16/E87D0D/E87D0D.png) |
| Blender blue | `#265787` | ![#265787](https://placehold.co/16x16/265787/265787.png) |

The icon is generated from Blender's own logo icon by [`tools/recolor.py`](tools/recolor.py),
which replaces only the orange pixels, including their anti-aliased edges, so outlines stay
perfectly smooth. The white ring and the eye are untouched. Every size from 16 to 256 px is included.

To rebuild it yourself from your Blender install (needs Python with `pillow` and `pefile`):

```bash
python tools/extract_icon.py "C:\path\to\Blender\blender.exe" 0 blender-logo.ico
python tools/recolor.py blender-logo.ico icons/blend1-blue.ico
```

To build the extension zip (validated by Blender's own extension tooling):

```bash
python tools/build_extension.py "C:\path\to\Blender\blender.exe"
```

## FAQ

**Does it change anything in Blender?**
No. File icons belong to Windows, so this only touches Windows' file-type settings for
your user account. Blender itself is never modified.

**Microsoft Store version of Blender?**
Store apps run in a sandbox that keeps their registry changes private, so the extension
can't change Explorer's icons from there. Use Option B instead.

**macOS / Linux?**
Not yet. On Linux this is doable with a shared-mime-info entry; contributions are very
welcome.

**My backups are still orange.**
Click *Refresh Icons* in the extension's preferences (or run `Install.cmd` again) and press <kbd>F5</kbd> in Explorer. If a cached icon still
sticks, sign out and back in.

**Can I turn off `.blend1` files completely?**
Yes, in Blender: *Edit → Preferences → Save & Load → Save Versions = 0*. But backups have
saved a lot of people's work. This project is for keeping them *and* not tripping over them.

## Contributing

Issues and pull requests are welcome, especially a macOS or Linux version, or a better
icon idea.

## License

[GPL-3.0-or-later](LICENSE), like Blender itself and as required for extensions on
extensions.blender.org.

The icon is derived from Blender's logo icon. Blender and the Blender logo are trademarks of
the [Blender Foundation](https://www.blender.org/about/logo/). This is an independent
community project, not affiliated with or endorsed by the Blender Foundation.
