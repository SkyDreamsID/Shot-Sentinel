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

echo "====================================================="
echo "             Shot Sentinel Linux Uninstaller"
echo "====================================================="
echo

NEMO_DIR="$HOME/.local/share/nemo/scripts/Shot Sentinel"
NAUTILUS_DIR="$HOME/.local/share/nautilus/scripts/Shot Sentinel"
CAJA_DIR="$HOME/.local/share/caja/scripts/Shot Sentinel"
DESKTOP_DIR="$HOME/Desktop/Shot Sentinel"

REMOVED=0

# Hapus dari Nemo
if [ -L "$NEMO_DIR" ] || [ -f "$NEMO_DIR" ]; then
    rm -f "$NEMO_DIR"
    echo "[OK] Integrasi Nemo dihapus."
    REMOVED=1
fi

# Hapus dari Nautilus
if [ -L "$NAUTILUS_DIR" ] || [ -f "$NAUTILUS_DIR" ]; then
    rm -f "$NAUTILUS_DIR"
    echo "[OK] Integrasi Nautilus dihapus."
    REMOVED=1
fi

# Hapus dari Caja
if [ -L "$CAJA_DIR" ] || [ -f "$CAJA_DIR" ]; then
    rm -f "$CAJA_DIR"
    echo "[OK] Integrasi Caja dihapus."
    REMOVED=1
fi

# Hapus dari Desktop
if [ -L "$DESKTOP_DIR" ] || [ -f "$DESKTOP_DIR" ]; then
    rm -f "$DESKTOP_DIR"
    echo "[OK] Shortcut Desktop dihapus."
    REMOVED=1
fi

echo
if [ $REMOVED -eq 0 ]; then
    echo "[INFO] Shot Sentinel tidak terdeteksi terinstall di sistem."
else
    echo "[OK] Shot Sentinel berhasil dibersihkan dari sistem."
fi

echo
echo "====================================================="
echo "Uninstall selesai."
echo "====================================================="
echo
read -p "Tekan Enter untuk menutup..."
