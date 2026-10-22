# extensions.blender.org listing

Everything needed for the submission form at
<https://extensions.blender.org/submit/>.

| Field | Value |
| --- | --- |
| File | `dist/blend1_blue-1.0.0.zip` (built with `tools/build_extension.py`) |
| Icon | [`listing/icon-256.png`](listing/icon-256.png) |
| Featured image | [`listing/featured-1920x1080.png`](listing/featured-1920x1080.png) |
| Website | https://github.com/bayromest/blend1-blue |
| Report issues | https://github.com/bayromest/blend1-blue/issues |

Name, tagline, tags, license and permissions come from `blender_manifest.toml`.

## Description

Paste this into the description field:

```markdown
Every time you save, Blender keeps the previous version as `yourfile.blend1`. On Windows that
backup gets the exact same orange icon as your real file, right next to it, so it's easy to
open the wrong one and lose work.

**Blend1 Blue gives every backup (`.blend1` up to `.blend32`) the Blender logo in Blender's own
blue**, so the real file and the backup are instantly told apart.

- Enable the extension and the icons change. Nothing else to do.
- Double-clicking a backup still opens it in Blender, so recovering after a crash works as before.
- Disable or uninstall the extension and everything goes back exactly as it was, including any
  file association you had before.
- Closing Blender keeps the icons.
- Installed a new Blender version? Click *Refresh Icons* in the extension's preferences.

**How it works:** it only changes Windows' file-type settings for your own user account
(`HKEY_CURRENT_USER`), the same place Blender's own *Register* button writes to. No admin rights,
no background process, and Blender itself is never modified.

Windows only. Not compatible with the Microsoft Store version of Blender, whose sandbox keeps
registry changes private. A no-Blender installer is also available on the project page.
```

## Notes for the moderators

Paste this into the "notes" or first comment if asked:

> The add-on writes to `HKEY_CURRENT_USER\Software\Classes` (the same place Blender's own
> *Register File Association* button writes to), which is why it declares the `files`
> permission. Changes are applied in `register()` and reverted when the add-on is disabled or
> uninstalled. Because Blender also calls `unregister()` on exit, the revert is deferred with a
> timer and only runs if the add-on is no longer enabled. The icon file is copied to
> `bpy.utils.extension_path_user`. No network access.
