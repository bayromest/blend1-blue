<div align="center">

<img src="icons/blend1-blue.png" width="128" alt="Blue Blender backup icon">

# blend1-blue

**Give Blender's `.blend1` backup files a blue icon, so you stop opening the backup by accident.**

Windows · no admin rights · one double-click to install, one to undo

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

1. **[Download the latest release](../../releases/latest)** (or *Code → Download ZIP*) and unzip it.
2. Double-click **`Install.cmd`**.

That's it. Icons refresh immediately; you can delete the unzipped folder afterwards.

> [!NOTE]
> Windows may ask *"Do you want to run this file?"* because it came from the internet.
> Click **Run**. The scripts are short and readable, take a look at
> [`scripts/install.ps1`](scripts/install.ps1) first if you like.

## Uninstall

Double-click **`Uninstall.cmd`**. Everything goes back the way it was, including any
association that existed before you installed.

## What it actually does

Nothing magic, and nothing outside your own user account:

| What | Where |
| --- | --- |
| Copies the blue icon | `%LOCALAPPDATA%\blend1-blue\blend1-blue.ico` |
| Registers a "Blender Backup File" type with that icon | `HKCU\Software\Classes\Blender.BackupFile` |
| Points `.blend1` … `.blend32` at it | `HKCU\Software\Classes\.blendN` |
| Reuses Blender's own *open* command for `.blend` | so double-click still opens Blender |
| Clears any saved *"Always open with"* choice for backups | it would otherwise override the icon |
| Remembers anything it replaced | `HKCU\Software\blend1-blue`, used by the uninstaller |

No admin rights, no background process, no Blender add-on, nothing touches Blender itself.
Upgrading or reinstalling Blender doesn't undo it.

> [!TIP]
> If you install a **new Blender version** and want backups to open in it, just run
> `Install.cmd` again. It picks up whatever Blender currently opens `.blend` files with.

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

## FAQ

**Does it change anything in Blender?**
No. File icons belong to Windows, so this only touches Windows' file-type settings for
your user account. Blender itself is never modified.

**macOS / Linux?**
Not yet. On Linux this is doable with a shared-mime-info entry; contributions are very
welcome.

**My backups are still orange.**
Run `Install.cmd` again and press <kbd>F5</kbd> in Explorer. If a cached icon still
sticks, sign out and back in.

**Can I turn off `.blend1` files completely?**
Yes, in Blender: *Edit → Preferences → Save & Load → Save Versions = 0*. But backups have
saved a lot of people's work. This project is for keeping them *and* not tripping over them.

## Contributing

Issues and pull requests are welcome, especially a macOS or Linux version, or a better
icon idea.

## License

The scripts are [MIT](LICENSE).

The icon is derived from Blender's logo icon. Blender and the Blender logo are trademarks of
the [Blender Foundation](https://www.blender.org/about/logo/). This is an independent
community project, not affiliated with or endorsed by the Blender Foundation.
