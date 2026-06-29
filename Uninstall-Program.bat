@echo off
title Shot Sentinel Uninstaller
color 0C
setlocal

set "SHORTCUT=%APPDATA%\Microsoft\Windows\SendTo\Shot Sentinel.lnk"

echo =====================================================
echo             Shot Sentinel Uninstaller
echo =====================================================
echo.

echo [1/2] Mengecek instalasi...

if not exist "%SHORTCUT%" (
    echo [INFO] Shot Sentinel belum terinstall.
    echo.
    pause
    exit /b
)

echo [OK] Instalasi ditemukan.
echo.

echo [2/2] Menghapus shortcut...

del "%SHORTCUT%" >nul 2>nul

if exist "%SHORTCUT%" (
    echo [ERROR] Gagal menghapus shortcut.
) else (
    echo [OK] Shot Sentinel berhasil dihapus.
)

echo.
echo =====================================================
echo Uninstall selesai.
echo =====================================================
echo.
pause