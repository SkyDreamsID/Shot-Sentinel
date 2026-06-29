@echo off
setlocal enabledelayedexpansion

:: 1. Cek apakah Python sudah terinstall di sistem
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ======================================================
    echo [ERROR] Python tidak ditemukan!
    echo ======================================================
    echo Tools ini butuh Python 3 buat jalanin kodenya.
    echo Silakan download dan install dulu di: https://www.python.org/downloads/
    echo.
    echo *PENTING: Saat install, pastikan centang "Add Python.exe to PATH"!
    echo ======================================================
    pause
    exit /b
)

:: 2. Cek apakah library pendukung sudah lengkap
python -c "import exifread, colorama" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Library pendukung belum lengkap. Menginstall via pip...
    
    if exist "%~dp0requirements.txt" (
        python -m pip install -r "%~dp0requirements.txt"
    ) else (
        python -m pip install exifread==3.0.0 colorama==0.4.6
    )
    
    cls
)

:: 3. Jalankan script utama
python "%~dp0main.py" %*