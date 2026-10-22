# SPDX-FileCopyrightText: 2026 Bayrem
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Give Blender's backup files (.blend1 ... .blend32) a blue icon on Windows.

Enabling the extension applies the icon, disabling or uninstalling it puts
everything back. Only the current Windows user's file-type settings change
(HKEY_CURRENT_USER); Blender itself is never modified.
"""

import ctypes
import hashlib
import os
import shutil
import sys

import bpy

if sys.platform == "win32":
    import winreg

PROG_ID = "Blender.BackupFile"
CLASSES = "Software\\Classes"
STATE = "Software\\blend1-blue"
FILE_EXTS = "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts"

# Two styles, matching how .blend files look on this machine: the bare logo
# (Steam, portable, "Open with" choices) or the paper sheet used by the installer.
ICONS = {
    "logo": "blend1-blue.ico",
    "file": "blend1-blue-file.ico",
}

# Blender's "Save Versions" preference can keep up to 32 backups.
EXTENSIONS = [".blend%d" % n for n in range(1, 33)]

SHCNE_ASSOCCHANGED = 0x08000000
ASSOCSTR_COMMAND = 1
ASSOCSTR_DEFAULTICON = 15


# -----------------------------------------------------------------------------
# Registry helpers (HKEY_CURRENT_USER only)

def read_default(path):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            return winreg.QueryValueEx(key, "")[0]
    except OSError:
        return None


def write_default(path, value):
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, path) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, value)


def delete_tree(path):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            while True:
                try:
                    child = winreg.EnumKey(key, 0)
                except OSError:
                    break
                delete_tree(path + "\\" + child)
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
    except FileNotFoundError:
        pass


def has_subkeys(path):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            return winreg.QueryInfoKey(key)[0] > 0
    except OSError:
        return False


def notify_explorer():
    ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, 0, None, None)


# -----------------------------------------------------------------------------
# Apply / remove

def assoc_query(what, assoc, verb=None):
    buffer = ctypes.create_unicode_buffer(2048)
    length = ctypes.c_uint(len(buffer))
    result = ctypes.windll.shlwapi.AssocQueryStringW(0, what, assoc, verb, buffer, ctypes.byref(length))
    return buffer.value if result == 0 else ""


def blend_icon_style(assoc=".blend"):
    # The installer registers "blender-launcher.exe",1 (the paper sheet); everything
    # else ends up with the executable's own icon, index 0 (the bare logo).
    location = assoc_query(ASSOCSTR_DEFAULTICON, assoc)
    index = location.rsplit(",", 1)[1].strip() if "," in location else "0"
    return "file" if index == "1" else "logo"


def icon_path():
    """Where the icon is installed. The name carries a hash of its contents,
    because Windows caches icons by path and would keep showing an old one."""
    source = os.path.join(os.path.dirname(__file__), ICONS[blend_icon_style()])
    with open(source, "rb") as fh:
        digest = hashlib.sha1(fh.read()).hexdigest()[:8]
    name = "%s-%s.ico" % (os.path.splitext(os.path.basename(source))[0], digest)
    # The registry needs a path that survives extension updates.
    directory = bpy.utils.extension_path_user(__package__, path="", create=True)
    return source, os.path.join(directory, name)


def remove_icon_files(keep=None):
    directory = bpy.utils.extension_path_user(__package__, path="", create=True)
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if name.endswith(".ico") and path != keep:
            os.remove(path)


def blend_open_command(assoc=".blend"):
    """The command Windows uses to open .blend files, so backups open the same way."""
    command = assoc_query(ASSOCSTR_COMMAND, assoc, "open")
    exe = command.split('"')[1] if command.startswith('"') else command.split(" ")[0]
    # Without a .blend association Windows answers with its "Open with" picker.
    if os.path.basename(exe).lower().startswith("blender") and os.path.isfile(exe):
        return command
    return '"%s" "%%1"' % bpy.app.binary_path


def is_applied():
    return read_default(CLASSES + "\\.blend1") == PROG_ID


def is_current():
    icon = icon_path()[1]
    return (
        is_applied()
        and os.path.isfile(icon)
        and read_default(CLASSES + "\\" + PROG_ID + "\\DefaultIcon") == '"%s",0' % icon
    )


def apply():
    source, icon = icon_path()
    if not os.path.isfile(icon):
        shutil.copyfile(source, icon)
    remove_icon_files(keep=icon)

    write_default(CLASSES + "\\" + PROG_ID, "Blender Backup File")
    write_default(CLASSES + "\\" + PROG_ID + "\\DefaultIcon", '"%s",0' % icon)
    write_default(CLASSES + "\\" + PROG_ID + "\\shell\\open\\command", blend_open_command())

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, STATE + "\\Previous") as previous_key:
        for ext in EXTENSIONS:
            previous = read_default(CLASSES + "\\" + ext)
            if previous and previous != PROG_ID:
                winreg.SetValueEx(previous_key, ext, 0, winreg.REG_SZ, previous)
            write_default(CLASSES + "\\" + ext, PROG_ID)

            # A saved "Always open with" choice overrides the icon, so clear it.
            for choice in ("UserChoice", "UserChoiceLatest"):
                try:
                    delete_tree(FILE_EXTS + "\\" + ext + "\\" + choice)
                except OSError:
                    pass

    notify_explorer()


def remove():
    try:
        previous_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STATE + "\\Previous")
    except OSError:
        previous_key = None

    for ext in EXTENSIONS:
        path = CLASSES + "\\" + ext
        if read_default(path) != PROG_ID:
            continue
        try:
            old = winreg.QueryValueEx(previous_key, ext)[0] if previous_key else None
        except OSError:
            old = None
        if old:
            write_default(path, old)
        elif not has_subkeys(path):
            delete_tree(path)
        else:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, "")

    if previous_key:
        previous_key.Close()
    delete_tree(CLASSES + "\\" + PROG_ID)
    delete_tree(STATE)
    remove_icon_files()

    notify_explorer()


# -----------------------------------------------------------------------------
# Interface

class BLEND1BLUE_OT_refresh(bpy.types.Operator):
    """Apply the blue icon again, e.g. after installing a new Blender version"""
    bl_idname = "blend1_blue.refresh"
    bl_label = "Refresh Icons"

    def execute(self, context):
        try:
            apply()
        except OSError as ex:
            self.report({'ERROR'}, "Could not update the file icons: %s" % ex)
            return {'CANCELLED'}
        self.report({'INFO'}, "Backup files now have the blue icon")
        return {'FINISHED'}


class BLEND1BLUE_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        if is_applied():
            col.label(text="Backup files (.blend1 to .blend32) have the blue icon.", icon='CHECKMARK')
        else:
            col.label(text="Backup files don't have the blue icon yet.", icon='ERROR')
        col.label(text="Disable or uninstall this extension to restore the original icons.")
        layout.operator(BLEND1BLUE_OT_refresh.bl_idname, icon='FILE_REFRESH')


classes = (
    BLEND1BLUE_OT_refresh,
    BLEND1BLUE_AddonPreferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Also catches an icon that changed in an extension update.
    if sys.platform == "win32" and not bpy.app.background and not is_current():
        try:
            apply()
        except OSError as ex:
            print("Blend1 Blue: could not update the file icons:", ex)


def remove_if_disabled():
    # Blender also calls unregister() when it quits, where the icons must stay.
    # Quitting never gets to run this timer; disabling or uninstalling does, and
    # by then the extension is gone from the preferences.
    if __package__ not in bpy.context.preferences.addons and is_applied():
        try:
            remove()
        except OSError as ex:
            print("Blend1 Blue: could not restore the file icons:", ex)
    return None


def unregister():
    if sys.platform == "win32" and not bpy.app.background:
        bpy.app.timers.register(remove_if_disabled, first_interval=0.5, persistent=True)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
