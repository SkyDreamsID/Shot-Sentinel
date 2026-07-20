#!/usr/bin/env bash

# Jika dijalankan tanpa terminal (misal double-click dari file manager), buka terminal baru
if [ ! -t 1 ]; then
    SCRIPT_PATH=$(readlink -f "${BASH_SOURCE[0]}")
    for term in x-terminal-emulator gnome-terminal mate-terminal xfce4-terminal konsole alacritty kitty xterm; do
        if command -v "$term" >/dev/null 2>&1; then
            if [ "$term" = "gnome-terminal" ] || [ "$term" = "mate-terminal" ]; then
                exec "$term" -- bash "$SCRIPT_PATH" "$@"
            else
                exec "$term" -e bash "$SCRIPT_PATH" "$@"
            fi
            exit 0
        fi
    done
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TARGET="$SCRIPT_DIR/program.sh"

echo "====================================================="
echo "             Shot Sentinel Linux Installer"
echo "====================================================="
echo

# 1. Cek file program.sh
if [ ! -f "$TARGET" ]; then
    echo "[ERROR] program.sh tidak ditemukan!"
    echo "Pastikan file installer berada di folder yang sama."
    exit 1
fi

echo "[OK] program.sh ditemukan."
chmod +x "$TARGET"
chmod +x "$SCRIPT_DIR/main.py"

# 2. Cari directory script file manager
INSTALLED_FM=()

NEMO_DIR="$HOME/.local/share/nemo/scripts"
NAUTILUS_DIR="$HOME/.local/share/nautilus/scripts"
CAJA_DIR="$HOME/.local/share/caja/scripts"

# Setup Nemo (Linux Mint)
if [ -d "$(dirname "$NEMO_DIR")" ]; then
    mkdir -p "$NEMO_DIR"
    ln -sf "$TARGET" "$NEMO_DIR/Shot Sentinel"
    INSTALLED_FM+=("Linux Mint (Nemo)")
fi

# Setup Nautilus (Ubuntu/Debian)
if [ -d "$(dirname "$NAUTILUS_DIR")" ]; then
    mkdir -p "$NAUTILUS_DIR"
    ln -sf "$TARGET" "$NAUTILUS_DIR/Shot Sentinel"
    INSTALLED_FM+=("Ubuntu/Debian (Nautilus)")
fi

# Setup Caja (MATE)
if [ -d "$(dirname "$CAJA_DIR")" ]; then
    mkdir -p "$CAJA_DIR"
    ln -sf "$TARGET" "$CAJA_DIR/Shot Sentinel"
    INSTALLED_FM+=("MATE (Caja)")
fi

echo
if [ ${#INSTALLED_FM[@]} -eq 0 ]; then
    echo "[WARNING] Tidak ada file manager (Nemo/Nautilus/Caja) yang terdeteksi."
    echo "Membuat shortcut manual di Desktop..."
    DESKTOP_DIR="$HOME/Desktop"
    if [ -d "$DESKTOP_DIR" ]; then
        ln -sf "$TARGET" "$DESKTOP_DIR/Shot Sentinel"
        echo "[OK] Shortcut dibuat di Desktop."
    fi
else
    echo "[OK] Integrasi menu Klik Kanan berhasil dipasang untuk:"
    for fm in "${INSTALLED_FM[@]}"; do
        echo "  - $fm"
    done
fi

echo
echo "====================================================="
echo "Instalasi selesai."
echo "Klik kanan file -> Scripts (Skrip) -> Shot Sentinel"
echo "====================================================="
echo
read -p "Tekan Enter untuk menutup..."
