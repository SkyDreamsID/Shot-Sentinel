#!/usr/bin/env bash

# Tentukan direktori script berada
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Mengambil file yang terpilih dari Nemo / Nautilus
SELECTED_FILES=()

if [ -n "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS" ]; then
    while IFS= read -r line; do
        [ -n "$line" ] && SELECTED_FILES+=("$line")
    done <<< "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS"
elif [ -n "$NEMO_SCRIPT_SELECTED_FILE_PATHS" ]; then
    while IFS= read -r line; do
        [ -n "$line" ] && SELECTED_FILES+=("$line")
    done <<< "$NEMO_SCRIPT_SELECTED_FILE_PATHS"
else
    for arg in "$@"; do
        SELECTED_FILES+=("$arg")
    done
fi

# Jika dijalankan dari file manager (tidak ada terminal TTY), buka terminal baru
if [ ! -t 0 ]; then
    for term in x-terminal-emulator gnome-terminal mate-terminal xfce4-terminal konsole alacritty kitty xterm; do
        if command -v "$term" >/dev/null 2>&1; then
            if [ "$term" = "gnome-terminal" ] || [ "$term" = "mate-terminal" ]; then
                exec "$term" -- bash "$0" "${SELECTED_FILES[@]}"
            else
                exec "$term" -e bash "$0" "${SELECTED_FILES[@]}"
            fi
            exit 0
        fi
    done
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "Shot Sentinel" "Terminal emulator tidak ditemukan! Jalankan lewat terminal manual."
    fi
    exit 1
fi

# Cek Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "======================================================"
    echo "[ERROR] Python 3 tidak ditemukan!"
    echo "======================================================"
    echo "Program ini membutuhkan Python 3 untuk dijalankan."
    echo "Silakan install python3 lewat package manager Anda:"
    echo "sudo apt install python3 python3-pip"
    echo "======================================================"
    read -p "Tekan Enter untuk keluar..."
    exit 1
fi

# Cek & install dependencies
python3 -c "import exifread, colorama" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[INFO] Library pendukung belum lengkap. Menginstall via pip..."
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        python3 -m pip install -r "$SCRIPT_DIR/requirements.txt"
    else
        python3 -m pip install exifread==3.0.0 colorama==0.4.6
    fi
    clear
fi

# Jalankan script utama
python3 "$SCRIPT_DIR/main.py" "${SELECTED_FILES[@]}"
