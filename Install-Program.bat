@echo off
title Shot Sentinel Installer
color 0A
setlocal

set "TARGET=%~dp0program.bat"
set "SHORTCUT=%APPDATA%\Microsoft\Windows\SendTo\Shot Sentinel.lnk"

echo =====================================================
echo              Shot Sentinel Installer
echo =====================================================
echo.
echo [1/3] Mengecek file program...

if not exist "%TARGET%" (
    echo [ERROR] program.bat tidak ditemukan!
    echo Pastikan file installer berada di folder yang sama.
    echo.
    pause
    exit /b 1
)

echo [OK] program.bat ditemukan.
echo.

echo [2/3] Membuat shortcut ke menu Send To...

set "VBS_FILE=%TEMP%\CreateShortcut.vbs"
echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_FILE%"
echo Set Shortcut = WshShell.CreateShortcut("%SHORTCUT%") >> "%VBS_FILE%"
echo Shortcut.TargetPath = "%TARGET%" >> "%VBS_FILE%"
echo Shortcut.WorkingDirectory = "%~dp0" >> "%VBS_FILE%"
echo Shortcut.Description = "Shot Sentinel" >> "%VBS_FILE%"
echo Shortcut.IconLocation = "%SystemRoot%\System32\imageres.dll,15" >> "%VBS_FILE%"
echo Shortcut.Save >> "%VBS_FILE%"
cscript //nologo "%VBS_FILE%"
del "%VBS_FILE%" >nul 2>nul

echo.

echo [3/3] Verifikasi instalasi...

if exist "%SHORTCUT%" (
    echo [OK] Instalasi berhasil!
    echo.
    echo Shot Sentinel telah ditambahkan ke:
    echo Send To ^> Shot Sentinel
) else (
    echo [ERROR] Gagal membuat shortcut.
    pause
    exit /b 1
)

echo.
echo =====================================================
echo Instalasi selesai.
echo Klik kanan file ^> Send To ^> Shot Sentinel
echo =====================================================
echo.
pause