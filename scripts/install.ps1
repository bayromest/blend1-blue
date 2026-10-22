# blend1-blue installer: gives Blender backup files (.blend1 ... .blend32) a blue icon.
# Per-user only (HKCU), no admin rights needed. Undo with Uninstall.cmd.
$ErrorActionPreference = 'Stop'

$AppName  = 'blend1-blue'
$ProgId   = 'Blender.BackupFile'
$Classes  = 'HKCU:\Software\Classes'
$State    = "HKCU:\Software\$AppName"
$FileExts = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts'
$IconDir  = Join-Path $env:LOCALAPPDATA $AppName
$IconSrc  = Join-Path $PSScriptRoot '..\icons\blend1-blue.ico'
$IconDst  = Join-Path $IconDir 'blend1-blue.ico'

# Blender's "Save Versions" preference can keep up to 32 backups.
$Extensions = 1..32 | ForEach-Object { ".blend$_" }

function Get-DefaultValue($Path) {
    if (Test-Path -LiteralPath $Path) { (Get-Item -LiteralPath $Path).GetValue('') }
}

# 1. Put the icon somewhere permanent, so the repo folder can be deleted afterwards.
New-Item -ItemType Directory -Force -Path $IconDir | Out-Null
Copy-Item -LiteralPath $IconSrc -Destination $IconDst -Force

# 2. Register a "Blender Backup File" type with the blue icon.
New-Item -Force -Path "$Classes\$ProgId" -Value 'Blender Backup File' | Out-Null
New-Item -Force -Path "$Classes\$ProgId\DefaultIcon" -Value "`"$IconDst`",0" | Out-Null

# Double-clicking a backup still opens it in Blender, using the same command as .blend files.
# Ask Windows itself, so "Open with" choices (Steam, portable, launcher...) are respected.
Add-Type -Namespace Win32 -Name Assoc -MemberDefinition @'
[DllImport("shlwapi.dll", CharSet = CharSet.Unicode)]
public static extern int AssocQueryString(int flags, int str, string assoc, string extra, System.Text.StringBuilder outBuf, ref uint outLen);
'@
$buffer = New-Object System.Text.StringBuilder 2048
$length = [uint32]2048
$ASSOCSTR_COMMAND = 1
$OpenCommand = if ([Win32.Assoc]::AssocQueryString(0, $ASSOCSTR_COMMAND, '.blend', 'open', $buffer, [ref]$length) -eq 0) { $buffer.ToString() }
if ($OpenCommand) {
    New-Item -Force -Path "$Classes\$ProgId\shell\open\command" -Value $OpenCommand | Out-Null
    Write-Host "Backups will still open with: $OpenCommand"
} else {
    Write-Host 'Blender is not registered for .blend files, so backups get the icon only.'
}

# 3. Point every backup extension at it, remembering anything we replace.
New-Item -Force -Path "$State\Previous" | Out-Null
foreach ($ext in $Extensions) {
    $key = "$Classes\$ext"
    $previous = Get-DefaultValue $key
    if ($previous -and $previous -ne $ProgId) {
        Set-ItemProperty -Path "$State\Previous" -Name $ext -Value $previous
    }
    if (-not (Test-Path -LiteralPath $key)) { New-Item -Path $key | Out-Null }
    Set-Item -LiteralPath $key -Value $ProgId

    # A saved "Always open with" choice overrides the icon, so clear it.
    foreach ($name in 'UserChoice', 'UserChoiceLatest') {
        $choice = "$FileExts\$ext\$name"
        if (Test-Path -LiteralPath $choice) {
            Remove-Item -LiteralPath $choice -Recurse -Force
            Write-Host "Cleared saved 'Open with' choice for $ext"
        }
    }
}

# 4. Tell Explorer to refresh icons right away (no restart needed).
Add-Type -Namespace Win32 -Name Shell -MemberDefinition @'
[DllImport("shell32.dll")] public static extern void SHChangeNotify(int eventId, uint flags, IntPtr item1, IntPtr item2);
'@
[Win32.Shell]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)

Write-Host ''
Write-Host 'Done! .blend1 backups now have a blue Blender icon.' -ForegroundColor Cyan
