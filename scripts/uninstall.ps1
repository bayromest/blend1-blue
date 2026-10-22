# blend1-blue uninstaller: puts everything back the way it was.
$ErrorActionPreference = 'Stop'

$AppName  = 'blend1-blue'
$ProgId   = 'Blender.BackupFile'
$Classes  = 'HKCU:\Software\Classes'
$State    = "HKCU:\Software\$AppName"
$IconDir  = Join-Path $env:LOCALAPPDATA $AppName

$Extensions = 1..32 | ForEach-Object { ".blend$_" }
$Previous = if (Test-Path "$State\Previous") { Get-Item "$State\Previous" }

foreach ($ext in $Extensions) {
    $key = "$Classes\$ext"
    if (-not (Test-Path -LiteralPath $key)) { continue }
    if ((Get-Item -LiteralPath $key).GetValue('') -ne $ProgId) { continue }

    $old = if ($Previous) { $Previous.GetValue($ext) }
    if ($old) {
        Set-Item -LiteralPath $key -Value $old
    } elseif ((Get-Item -LiteralPath $key).SubKeyCount -eq 0) {
        Remove-Item -LiteralPath $key -Recurse -Force
    } else {
        Remove-ItemProperty -LiteralPath $key -Name '(default)'
    }
}

foreach ($path in "$Classes\$ProgId", $State) {
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Recurse -Force }
}
if (Test-Path -LiteralPath $IconDir) { Remove-Item -LiteralPath $IconDir -Recurse -Force }

Add-Type -Namespace Win32 -Name Shell -MemberDefinition @'
[DllImport("shell32.dll")] public static extern void SHChangeNotify(int eventId, uint flags, IntPtr item1, IntPtr item2);
'@
[Win32.Shell]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)

Write-Host 'blend1-blue removed. Backup icons are back to normal.' -ForegroundColor Cyan
