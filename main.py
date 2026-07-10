#!/usr/bin/env python3
import sys
import os
import datetime
from pathlib import Path
from colorama import init, Fore, Style

# Mengimpor modul logika bisnis dari subfolder logic/
from logic.metadata import load_config_file, ensure_alias_file
from logic.log_history import (
    get_master_history_path,
    create_session_log,
    find_latest_history_file,
    get_rename_count,
    log_session_entry
)
from logic.worker import (
    already_formatted,
    generate_rename_preview,
    execute_rename,
    execute_restore
)
from logic.exporter import export_session_history
from logic.settings import settings_menu
from logic.additional_features import show_additional_features
from logic.version import HEADER_TEXT

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Memuat konfigurasi utama
CONFIG = load_config_file()
ensure_alias_file()

IMAGE_EXTS = {x.lower() for x in CONFIG.get("supported_image_extensions", [])}
VIDEO_EXTS = {x.lower() for x in CONFIG.get("supported_video_extensions", [])}
SUPPORTED_EXTS = IMAGE_EXTS.union(VIDEO_EXTS)

LOG_FILE = Path(__file__).resolve().parent / "history" / "process_log.txt"

# Reconfigure stdout/stderr to UTF-8 to support block characters on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

init(autoreset=True)

# Warna Log/Status
Hijau   = Fore.GREEN
Kuning  = Fore.YELLOW
Merah   = Fore.RED
Cyan    = Fore.CYAN
BiruTua = Fore.BLUE
Abu     = Style.DIM

S_Sukses    = "[Berhasil]"
S_Gagal     = "[Gagal]"
S_Skip      = "[SKIP]"
S_Error     = "[ERROR]"
S_Done      = "[SELESAI]"
S_Skipped   = "[SKIPPED]"
S_Renamed   = "[RENAMED]"
S_Restored  = "[RESTORED]"
S_Failed    = "[FAILED]"

LOG_COLORS = {
    S_Sukses    : Hijau,
    S_Restored  : Hijau,
    S_Renamed   : Hijau,
    S_Skip      : Kuning,
    S_Skipped   : Kuning,
    S_Gagal     : Merah,
    S_Error     : Merah,
    S_Failed    : Merah,
    S_Done      : Cyan,
}

# String UI bilingual (main menu + pesan umum)
STRINGS = {
    "id": {
        "no_files"      : "Tidak ada file yang terdeteksi, Program dihentikan",
        "press_enter"   : "Tekan Enter untuk keluar...",
        "found"         : "Terdeteksi {n} file",
        "what_to_do"    : "Pengen Ngapain?",
        "opt_rename"    : "[1] Auto Rename (y)",
        "opt_restore"   : "[2] Restore ke nama asli (r)",
        "opt_settings"  : "[3] Pengaturan (s)",
        "opt_extra"     : "[4] Fitur Tambahan",
        "opt_cancel"    : "[E] Batal (Enter)",
        "prompt"        : "Pilih",
        "preview_label" : "[PREVIEW]",
        "no_change"     : "[Tidak berubah - sudah terformat]",
        "proceed"       : "Lanjutkan? (y/n)",
        "cancelled"     : "[Batal] Proses dibatalkan oleh pengguna.",
    },
    "en": {
        "no_files"      : "No files detected. Program stopped.",
        "press_enter"   : "Press Enter to exit...",
        "found"         : "Found: {n} files",
        "what_to_do"    : "What would you like to do?",
        "opt_rename"    : "[1] Auto Rename (y)",
        "opt_restore"   : "[2] Restore Original Name (r)",
        "opt_settings"  : "[3] Settings (s)",
        "opt_extra"     : "[4] Additional Features",
        "opt_cancel"    : "[E] Cancel (Enter)",
        "prompt"        : "Select",
        "preview_label" : "[PREVIEW]",
        "no_change"     : "[No change - already formatted]",
        "proceed"       : "Proceed? (y/n)",
        "cancelled"     : "[Cancel] Process cancelled by user.",
    },
}

def T(config: dict, key: str) -> str:
    """Ambil string UI sesuai bahasa di config. Fallback ke 'id'."""
    lang = config.get("language", "id")
    return STRINGS.get(lang, STRINGS["id"]).get(key, STRINGS["id"].get(key, key))

def log(prefix: str, message: str):
    color = LOG_COLORS.get(prefix, "")
    print(f"{color}{prefix}{Style.RESET_ALL} {message}")

    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"{timestamp} {prefix} {message}\n")
    except Exception:
        pass

def is_supported(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in SUPPORTED_EXTS

def get_target_paths(parsed_files: list[str] = None) -> list[Path]:
    if parsed_files:
        files = []
        for a in parsed_files:
            p = Path(a).expanduser().resolve()
            if p.is_dir():
                files.extend([item for item in p.iterdir() if is_supported(item)])
            elif p.is_file() and is_supported(p):
                files.append(p)
        return files
    else:
        return []

def draw_progress(current, total):
    bar_length = 20
    percent = int(100 * current // total) if total > 0 else 100
    filled_length = int(bar_length * current // total) if total > 0 else bar_length
    bar = '█' * filled_length + ' ' * (bar_length - filled_length)
    sys.stdout.write(f"\r[{Fore.GREEN}{bar}{Style.RESET_ALL}] {percent}% ({current}/{total})")
    sys.stdout.flush()
    if current == total:
        sys.stdout.write('\n')
        sys.stdout.flush()

# ---------------------------------------------------------------------------
# Summary helpers — Task 1 & 2
# ---------------------------------------------------------------------------

_SEP_WIDE = "=" * 60
_SEP_THIN = "-" * 60
_COL_W    = 22   # lebar kolom label

def _print_summary_header(title: str):
    print(f"\n{_SEP_WIDE}")
    print(f"[{title}]")
    print(_SEP_WIDE)

def _print_summary_row(label: str, value: int, color: str = ""):
    count_str = f"{value:,} file"
    if color:
        print(f"{label:<{_COL_W}}: {color}{count_str}{Style.RESET_ALL}")
    else:
        print(f"{label:<{_COL_W}}: {count_str}")

def _print_summary_footer(fail_count: int, lang: str, already_count: int = 0, op_type: str = "rename"):
    """Cetak footer summary sesuai kasus keberhasilan/kegagalan/sudah sesuai format."""
    print(_SEP_THIN)
    if fail_count > 0:
        if lang == "id":
            msg = f"Selesai dengan {fail_count:,} file gagal."
        else:
            msg = f"Completed with {fail_count:,} failed file(s)."
        print(f"{Merah}{msg}{Style.RESET_ALL}")
    elif already_count > 0:
        if lang == "id":
            print(f"{Hijau}Selesai.{Style.RESET_ALL}")
            if op_type == "rename":
                print(f"{already_count:,} file sudah sesuai format.")
            else:
                print(f"{already_count:,} file sudah menggunakan nama asli.")
        else:
            print(f"{Hijau}Completed.{Style.RESET_ALL}")
            if op_type == "rename":
                print(f"{already_count:,} file(s) were already renamed.")
            else:
                print(f"{already_count:,} file(s) were already using their original filenames.")
    else:
        if lang == "id":
            msg = "Selesai tanpa kegagalan."
        else:
            msg = "Completed successfully."
        print(f"{Hijau}{msg}{Style.RESET_ALL}")

def _print_failed_files(failed_list: list[tuple], lang: str):
    """Tampilkan section 'Failed Files' hanya jika ada kegagalan."""
    if not failed_list:
        return
    print()
    header = "File Gagal" if lang == "id" else "Failed Files"
    print(f"{Merah}{header}{Style.RESET_ALL}")
    print(_SEP_THIN)
    for name, reason in failed_list:
        print(f"  - {name}")
        label = "Alasan" if lang == "id" else "Reason"
        print(f"    {label} : {reason}")

def _print_log_paths(session_log: Path, exported_csv, config: dict):
    """Tampilkan path log sesi dan CSV export."""
    root = config.get("root_dir", Path(__file__).resolve().parent)
    try:
        rel_log = session_log.relative_to(root)
        log_display = rel_log.as_posix()
    except Exception:
        log_display = f"history/sessions/{session_log.name}"

    lang = config.get("language", "id")
    label = "Log" if lang == "en" else "Log"
    print(f"\n{Cyan}{label:<{_COL_W}}{Style.RESET_ALL}: {log_display}")

    if exported_csv and config.get("export_csv", False):
        try:
            rel_csv = exported_csv.relative_to(root)
            csv_display = rel_csv.as_posix()
        except Exception:
            csv_display = f"history/sessions/{exported_csv.name}"
        print(f"{'CSV Export':<{_COL_W}}: {csv_display}")

# ---------------------------------------------------------------------------
# Easter Egg milestones
# ---------------------------------------------------------------------------

_MILESTONES = {
    100:    (Fore.YELLOW,  "[MILESTONE]",  "You renamed your first 100 files! Keep going!"),
    500:    (Fore.CYAN,    "[BRONZE]",     "Great! You have renamed 500 files!"),
    1000:   (Fore.GREEN,   "[SILVER]",     "One thousand files protected from overwrite!"),
    5000:   (Fore.MAGENTA, "[GOLD]",       "Awesome! 5,000 files renamed!"),
    10000:  (Fore.BLUE,    "[PLATINUM]",   "Incredible! 10,000 memories secured!"),
    50000:  (Fore.YELLOW,  "[MASTER]",     "You have protected an enormous collection!"),
    100000: (Fore.RED,     "[LEGENDARY]",  "You probably own multiple hard drives by now."),
}

def _show_easter_eggs(initial_count: int, master_history: Path, config: dict):
    if not config.get("enable_easter_eggs", True):
        return
    final_count = get_rename_count(master_history)
    for milestone, (color, title, message) in _MILESTONES.items():
        if initial_count < milestone <= final_count:
            print(f"\n{color}{title}{Style.RESET_ALL}")
            print(message)

# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog="Shot Sentinel",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
v0.8 Beta - Anti-Overwrite media (Cross-platform)
-----------------------------------------------------------------------------------
Utility pencegah file foto/hasil hunting ketimpa atau hilang akibat penamaan bawaan
kamera yang berulang, seperti (DSC_1234). Otomatis merubah nama foto menjadi dengan
format penamaan: [CamModel]YYYY-MM-DD_HH-MM-SS_Index
sehingga aman untuk jangka panjang dan terhindar dari overwrite sistem
-----------------------------------------------------------------------------------
"""
    )

    parser.add_argument(
        "--mode",
        choices=["rename", "restore"],
        help="Langsung jalan tanpa terminal"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Path dari Explorer atau Cmd"
    )
    args = parser.parse_args()

    files = get_target_paths(args.files)

    if not files:
        log(S_Skip, "Tidak ada file yang terdeteksi, Program dihentikan")
        try:
            input("\nTekan Enter untuk keluar...")
        except EOFError:
            pass
        return

    # Pembersihan layar lintas platform
    clear_screen()

    if args.mode:
        choice = "1" if args.mode == "rename" else "2"
    else:
        # --- Main Menu Loop ---
        while True:
            # Reload config setiap iterasi supaya perubahan dari settings langsung berlaku
            from logic.metadata import load_config_file as _lcf
            CONFIG.update(_lcf())

            header = f"{HEADER_TEXT}"
            border = "=" * len(header)
            print(f"\n{border}")
            print(f"{header}")
            print(f"{border}\n")
            print(f"{T(CONFIG, 'found').format(n=len(files))}")
            print()
            print(f"{T(CONFIG, 'what_to_do')}")
            print(f"{T(CONFIG, 'opt_rename')}")
            print(f"{T(CONFIG, 'opt_restore')}")
            print(f"{T(CONFIG, 'opt_settings')}")
            print(f"{T(CONFIG, 'opt_extra')}")
            print(f"{Kuning}{T(CONFIG, 'opt_cancel')}{Style.RESET_ALL}")
            try:
                choice = input(f"\n{T(CONFIG, 'prompt')}: ").strip().lower()
            except EOFError:
                choice = "e"
                break

            if choice in ("3", "s"):
                clear_screen()
                CONFIG.update(settings_menu(CONFIG, preview_file=files[0] if files else None))
                clear_screen()
                continue
            elif choice == "4":
                clear_screen()
                show_additional_features(CONFIG)
                clear_screen()
                continue
            else:
                break

    # -----------------------------------------------------------------------
    # Mode Rename
    # -----------------------------------------------------------------------
    if choice in ('1', 'y'):
        preview_list = generate_rename_preview(files, CONFIG)
        if not args.mode:
            print(f"\n{Cyan}{T(CONFIG, 'preview_label')}{Style.RESET_ALL}")
            for old_p, new_p in preview_list:
                if old_p == new_p:
                    print(f"{old_p.name} -> {Abu}{T(CONFIG, 'no_change')}{Style.RESET_ALL}")
                else:
                    print(f"{old_p.name} -> {Hijau}{new_p.name}{Style.RESET_ALL}")

            total_files = len(files)
            if total_files > 5:
                print(f"... dan {total_files - 5:,} file lainnya")
            print()

            try:
                proceed = input(f"{T(CONFIG, 'proceed')}: ").strip().lower()
            except EOFError:
                proceed = "n"
            if proceed not in ('y', 'yes'):
                print(f"\n{Kuning}{T(CONFIG, 'cancelled')}{Style.RESET_ALL}")
                try:
                    input(f"\n{T(CONFIG, 'press_enter')}")
                except EOFError:
                    pass
                return

        import time
        start_time = time.perf_counter()

        master_history = get_master_history_path()
        session_log = create_session_log()
        session_ts = datetime.datetime.now().strftime("%d-%m-%Y_%H%M%S")

        initial_count = get_rename_count(master_history)

        print("\nRenaming files...")

        renamed_count = 0
        skipped_count = 0
        error_count   = 0
        error_details = []   # [(filename, reason), ...]
        total_files   = len(files)

        draw_progress(0, total_files)

        try:
            for status, file_path, detail in execute_rename(files, CONFIG, session_log, master_history, session_ts):
                if status == "renamed":
                    renamed_count += 1
                elif status == "skipped":
                    skipped_count += 1
                elif status == "error":
                    error_count += 1
                    error_details.append((file_path.name, str(detail)))

                current = renamed_count + skipped_count + error_count
                if current % 5 == 0 or current == total_files:
                    draw_progress(current, total_files)
        except KeyboardInterrupt:
            print(f"\n\n{Merah}[INTERRUPT] Proses dibatalkan oleh pengguna (Ctrl+C).{Style.RESET_ALL}")
            print(f"{Kuning}Menyimpan riwayat untuk file yang sudah berhasil diproses...{Style.RESET_ALL}")

        elapsed_time = time.perf_counter() - start_time

        # CSV export
        exported_csv = None
        if CONFIG.get("export_csv", False):
            try:
                exported_csv = export_session_history(session_log, "csv")
            except Exception:
                pass

        # --- Rename Summary (Task 1) ---
        lang = CONFIG.get("language", "id")
        _print_summary_header("RENAME SUMMARY")

        processed = renamed_count + skipped_count + error_count
        _print_summary_row("Processed",            processed,    "")
        _print_summary_row("Successfully Renamed",  renamed_count, Hijau)
        _print_summary_row("Already Renamed",       skipped_count, Abu)
        _print_summary_row("Failed",                error_count,   Merah if error_count > 0 else "")

        _print_log_paths(session_log, exported_csv, CONFIG)

        print(f"\n{'Time Elapsed':<{_COL_W}}: {elapsed_time:.1f}s")

        _print_failed_files(error_details, lang)
        _print_summary_footer(error_count, lang, already_count=skipped_count, op_type="rename")

        # Easter Egg
        _show_easter_eggs(initial_count, master_history, CONFIG)

        # Tunggu user sebelum keluar supaya window tidak langsung tutup
        try:
            input(f"\n{T(CONFIG, 'press_enter')}")
        except EOFError:
            pass
        sys.exit(0)

    # -----------------------------------------------------------------------
    # Mode Restore
    # -----------------------------------------------------------------------
    elif choice in ('2', 'r'):
        import time
        start_time = time.perf_counter()

        master_history = get_master_history_path()
        session_log = create_session_log("restore")
        print("\nRestoring files...")

        restored_count = 0
        skipped_count  = 0
        failed_count   = 0
        failed_details = []   # [(filename, reason), ...]
        total_files    = len(files)

        draw_progress(0, total_files)

        try:
            for status, file_path, detail in execute_restore(files, CONFIG, master_history):
                if status == "restored":
                    restored_count += 1
                    log_session_entry(session_log, file_path, detail)
                elif status in ("skipped_original", "skipped"):
                    skipped_count += 1
                else:
                    failed_count += 1
                    failed_details.append((file_path.name, str(detail)))

                current = restored_count + skipped_count + failed_count
                if current % 5 == 0 or current == total_files:
                    draw_progress(current, total_files)
        except KeyboardInterrupt:
            print(f"\n\n{Merah}[INTERRUPT] Proses dibatalkan oleh pengguna (Ctrl+C).{Style.RESET_ALL}")
            print(f"{Kuning}Menyimpan status untuk file yang sudah berhasil dikembalikan...{Style.RESET_ALL}")

        elapsed_time = time.perf_counter() - start_time

        # --- Restore Summary (Task 2) ---
        lang = CONFIG.get("language", "id")
        _print_summary_header("RESTORE SUMMARY")

        processed = restored_count + skipped_count + failed_count
        _print_summary_row("Processed",              processed,      "")
        _print_summary_row("Successfully Restored",   restored_count,  Hijau)
        _print_summary_row("Already Original",        skipped_count,   Abu)
        _print_summary_row("Failed",                  failed_count,    Merah if failed_count > 0 else "")

        _print_log_paths(session_log, None, CONFIG)

        print(f"\n{'Time Elapsed':<{_COL_W}}: {elapsed_time:.1f}s")

        _print_failed_files(failed_details, lang)
        _print_summary_footer(failed_count, lang, already_count=skipped_count, op_type="restore")

        # Tunggu user sebelum keluar supaya window tidak langsung tutup
        try:
            input(f"\n{T(CONFIG, 'press_enter')}")
        except EOFError:
            pass
        sys.exit(0)

    elif choice.lower() == 'e' or choice == '':
        # Batal / Exit
        return
    else:
        return

if __name__ == "__main__":
    main()