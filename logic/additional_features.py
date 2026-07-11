"""
logic/additional_features.py
-----------------
Additional Features menu and Developer Corner.
"""
import time
import importlib
import random
from pathlib import Path
from colorama import Fore, Style
from .settings import _header, _t, _safe_input, clear_screen, SEP_LEN

# Import kaomoji frames dynamically from dev-present.py
dev_present = importlib.import_module("logic.dev_present")
KAOMOJI_FRAMES = dev_present.KAOMOJI_FRAMES

# Helper functions for assets management
def get_assets_dir() -> Path:
    """Mengembalikan path direktori assets."""
    return Path(__file__).resolve().parent.parent / "assets"

def load_text_file(path: Path) -> str:
    """Membaca isi berkas teks dengan encoding UTF-8 secara utuh."""
    if not path.exists():
        raise FileNotFoundError(f"Asset file not found: {path}")
    return path.read_text(encoding="utf-8")

def load_ascii(name: str) -> str:
    """Membaca berkas ASCII art berdasarkan nama berkas."""
    path = get_assets_dir() / "ascii" / f"{name}.txt"
    return load_text_file(path)

def load_quotes(lang: str = "id") -> list[str]:
    """Membaca semua kutipan dari quotes_id.txt atau quotes.txt/quotes_en.txt."""
    assets_dir = get_assets_dir()
    if lang == "id":
        path = assets_dir / "quotes" / "quotes_id.txt"
        if not path.exists():
            path = assets_dir / "quotes" / "quotes.txt"
    else:
        path = assets_dir / "quotes" / "quotes_en.txt"
        if not path.exists():
            path = assets_dir / "quotes" / "quotes.txt"
            
    content = load_text_file(path)
    # Pisahkan per baris, abaikan baris kosong
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        raise ValueError("No quotes found in asset file")
    return lines

def display_text(path: Path) -> str:
    """Membaca isi berkas teks untuk ditampilkan langsung."""
    return load_text_file(path)

def check_skip():
    import sys
    if sys.platform == "win32":
        try:
            import msvcrt
            if msvcrt.kbhit():
                while msvcrt.kbhit():
                    msvcrt.getch()
                return True
        except (ImportError, Exception):
            pass
    else:
        try:
            import select
            if select.select([sys.stdin], [], [], 0.0)[0]:
                sys.stdin.read(1)
                return True
        except Exception:
            pass
    return False

def sleep_and_check(duration_ms):
    steps = int(duration_ms / 20)
    for _ in range(steps):
        if check_skip():
            return True
        time.sleep(0.02)
    return False

def play_kaomoji_animation():
    """Jalankan animasi Kaomoji. Tombol apa saja untuk skip."""
    frames = KAOMOJI_FRAMES

    for idx, (f, delay_sec) in enumerate(frames):
        clear_screen()
        for line in f:
            print(line)

        delay_ms = int(delay_sec * 1000)

        if idx == len(frames) - 1:
            while True:
                if check_skip():
                    return
                time.sleep(0.05)

        if sleep_and_check(delay_ms):
            return

    sleep_and_check(200)

def _press_enter(lang: str):
    """Tampilkan 'press enter to return' sesuai bahasa."""
    prompt = "\nTekan Enter untuk kembali..." if lang == "id" else "\nPress Enter to return..."
    _safe_input(prompt)

def dev_waifu_art(lang: str = "id"):
    clear_screen()
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}[SUNAO NAKO]{Style.RESET_ALL}")
    filename = "nako.txt" if lang == "id" else "nako_en.txt"
    path = get_assets_dir() / "ascii" / filename
    if not path.exists():
        path = get_assets_dir() / "ascii" / "nako.txt"
    try:
        content = load_text_file(path)
        print(content)
    except Exception:
        err_msg = "Asset tidak ditemukan." if lang == "id" else "Asset not found."
        print(f"{Fore.RED}{err_msg}{Style.RESET_ALL}")
    
    prompt = "\nKalau belum yakin, jangan pencet Enter..." if lang == "id" else "\nIf you're not sure, don't press Enter..."
    _safe_input(prompt)

def developer_notes(lang: str = "id"):
    _header("DEVELOPER NOTES")
    print("-" * SEP_LEN)
    
    notes_file = "developer_notes_id.txt" if lang == "id" else "developer_notes.txt"
    path = get_assets_dir() / "notes" / notes_file
    if not path.exists():
        path = get_assets_dir() / "notes" / "developer_notes.txt"
        
    try:
        content = display_text(path)
        print(content)
    except Exception:
        err_msg = "Asset tidak ditemukan." if lang == "id" else "Asset not found."
        print(f"{Fore.RED}{err_msg}{Style.RESET_ALL}")
        
    print("-" * SEP_LEN)
    _press_enter(lang)

def show_about(lang: str = "id"):
    """Menampilkan halaman About Shot Sentinel."""
    from .version import PROGRAM_NAME, PROGRAM_VERSION, PROGRAM_SLOGAN

    _header("ABOUT")

    SEP = "-" * SEP_LEN
    W = 18   # lebar kolom label

    print(f"{SEP}")
    print(f"{'Application':{W}} : {Fore.CYAN}{PROGRAM_NAME}{Style.RESET_ALL}")
    print(f"{'Version':{W}} : {Fore.YELLOW}{PROGRAM_VERSION}{Style.RESET_ALL}")
    print(f"{'Tagline':{W}} : {PROGRAM_SLOGAN}")
    print(SEP)
    print(f"{'Developer':{W}} : Rifki Eka Putra (SkyDreamsID)")
    print(f"{'Language':{W}} : Python 3")
    print(f"{'Libraries Used':{W}} : colorama, exifread")
    print(f"{'Repository':{W}} : github.com/SkyDreamsID/Shot-Sentinel")
    print(f"{'License':{W}} : Non-Commercial")
    print(SEP)
    print()
    if lang == "id":
        print(f"{Fore.YELLOW}Fun Fact{Style.RESET_ALL}")
        print("-" * SEP_LEN)
        print("Project ini dibuat karena developer frustrasi")
        print("kehilangan banyak foto akibat filename kamera")
        print("yang tertimpa di Windows Explorer.")
        print(SEP)
        print(f"\n{Fore.YELLOW}Keputusan Desain (SendTo vs Registry){Style.RESET_ALL}")
        print("-" * SEP_LEN)
        print("Menggunakan SendTo karena integrasi Registry Windows memiliki")
        print("bug yang membuka banyak terminal saat memilih file lebih dari 1.")
        print("Akhirnya saya memilih merubahnya pakai Sendto")
        print(f"karena terinspirasi dari 'KDE Connect' yang sama-sama memakai Sendto,")
        print(f"dan hasilnya program berjalan normal sesuai ekspetasi dan lebih aman tanpa meninggalkan jejak ke sistem.")
    else:
        print(f"{Fore.YELLOW}Fun Fact{Style.RESET_ALL}")
        print("-" * SEP_LEN)
        print("This project was created because the developer was frustrated")
        print("from losing many photos due to camera filenames being overwritten")
        print("in Windows Explorer.")
        print(SEP)
        print(f"\n{Fore.YELLOW}Design Decision (SendTo vs Registry){Style.RESET_ALL}")
        print("-" * SEP_LEN)
        print("Using SendTo because the Windows Registry integration has a")
        print("bug that opens multiple terminals when selecting more than 1 file.")
        print("Ultimately, I chose to switch to SendTo after being inspired by")
        print("'KDE Connect' which also uses SendTo. As a result, the program")
        print("runs normally as expected and is safer without leaving traces in the system.")
    print(SEP)

    _press_enter(lang)

def developer_credits(lang: str = "id"):
    from .version import PROGRAM_NAME, PROGRAM_VERSION, PROGRAM_SLOGAN

    _header("CREDITS")

    SEP = "-" * SEP_LEN
    W = 18   # lebar kolom label

    print(f"{SEP}")
    print(f"{'Application':{W}} : {Fore.CYAN}{PROGRAM_NAME}{Style.RESET_ALL}")
    print(f"{'Version':{W}} : {Fore.YELLOW}{PROGRAM_VERSION}{Style.RESET_ALL}")
    print(f"{'Developer':{W}} : Rifki Eka Putra (SkyDreamsID)")
    print(f"{'Language':{W}} : Python 3")
    print(f"{'Libraries Used':{W}} : colorama, exifread")
    print(f"{'Repository':{W}} : github.com/SkyDreamsID/Shot-Sentinel")
    print(f"{'License':{W}} : Non-Commercial")
    print(SEP)
    _press_enter(lang)

def random_quote(lang: str = "id"):
    _header("RANDOM QUOTE")
    print("-" * SEP_LEN)
    try:
        quotes = load_quotes(lang)
        quote = random.choice(quotes)
        print(f"\n{Fore.YELLOW}\"{quote}\"{Style.RESET_ALL}\n")
    except Exception:
        err_msg = "Asset tidak ditemukan." if lang == "id" else "Asset not found."
        print(f"\n{Fore.RED}{err_msg}{Style.RESET_ALL}\n")
    print("-" * SEP_LEN)
    _press_enter(lang)

def developer_corner_menu(config: dict) -> None:
    lang = config.get("language", "id")

    while True:
        _header("DEVELOPER CORNER")

        print("[1] DEV Waifu's")
        print("[2] Animation")
        print("[3] Developer Notes")
        print("[4] Credits")
        print("[5] Random Quote")
        print(f"\n{Fore.YELLOW}[E] {'Kembali' if lang == 'id' else 'Back'}{Style.RESET_ALL}")

        choice = _safe_input(f"\n{'Pilih' if lang == 'id' else 'Select'}: ").strip()
        choice_lower = choice.lower()

        if choice == "1":
            dev_waifu_art(lang)
        elif choice == "2":
            play_kaomoji_animation()
        elif choice == "3":
            developer_notes(lang)
        elif choice == "4":
            developer_credits(lang)
        elif choice == "5":
            random_quote(lang)
        elif choice_lower == "e" or choice == "":
            break
        else:
            invalid_msg = "Pilihan tidak valid." if lang == "id" else "Invalid choice."
            print(f"{Fore.YELLOW}[!] {invalid_msg}{Style.RESET_ALL}")
            time.sleep(1)

def show_additional_features(config: dict, files: list = None) -> None:
    """
    Menu Fitur Tambahan v1.0.
    Berisi: Statistics, HTML Report, Integrity Check, About, Developer Corner.
    """
    if files is None:
        files = []
        
    lang = config.get("language", "id")

    while True:
        _header("ADDITIONAL FEATURES" if lang == "en" else "FITUR TAMBAHAN")

        print("[1] Statistics Dashboard")
        print("[2] Generate HTML Report")
        print("[3] Integrity Check")
        print("[4] About")
        print("[5] Developer Corner")
        print(f"\n{Fore.YELLOW}[E] {'Keluar' if lang == 'id' else 'Exit'}{Style.RESET_ALL}")

        choice = _safe_input(f"\n{'Pilih' if lang == 'id' else 'Select'}: ").strip()
        choice_lower = choice.lower()

        if choice == "1":
            _header("STATISTICS DASHBOARD")
            try:
                from logic.statistics import get_statistics
                stats = get_statistics()
                
                # Protection Rank
                pr = stats.get('protection_rank', {})
                rank_name = pr.get('current_rank', 'UNRANKED')
                next_rank = pr.get('next_rank', 'NONE')
                progress_pct = pr.get('progress_percent', 0.0)
                remaining = pr.get('remaining', 0)
                
                print(f"\n{Style.BRIGHT}Protection Rank{Style.RESET_ALL}")
                if rank_name == "MAX RANK":
                    print(f"{Fore.MAGENTA}{rank_name}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}{rank_name}{Style.RESET_ALL}")
                    
                print(f"Protected Files : {stats['total_rename']:,}")
                print(f"Next Rank       : {next_rank} ({pr.get('next_threshold', 0):,})")
                print(f"Remaining       : {remaining:,} files")
                
                # ASCII Progress Bar
                bar_len = 20
                filled = int((progress_pct / 100.0) * bar_len)
                bar_str = "█" * filled + "░" * (bar_len - filled)
                print(f"Progress        : {Fore.GREEN}{bar_str}{Style.RESET_ALL} {progress_pct}%\n")
                
                print("-" * SEP_LEN)
                print(f"Total Renamed   : {Fore.GREEN}{stats['total_rename']:,}{Style.RESET_ALL}")
                print(f"Total Restored  : {Fore.GREEN}{stats['total_restore']:,}{Style.RESET_ALL}")
                muc, muc_count = stats.get('most_used_camera', ('None', 0))
                print(f"Most Used Camera: {Fore.CYAN}{muc}{Style.RESET_ALL} ({muc_count:,} files)")
                ls, ls_count = stats.get('largest_session', ('None', 0))
                print(f"Largest Session : {Fore.YELLOW}{ls}{Style.RESET_ALL} ({ls_count:,} ops)")
                
                print("\nCamera Distribution:")
                for c, count in stats.get('camera_usage', {}).items():
                    print(f"  - {c}: {count:,}")
                print("\nFile Type Distribution:")
                for ext, count in stats.get('file_type_stats', {}).items():
                    print(f"  - {ext}: {count:,}")
            except Exception as e:
                print(f"{Fore.RED}Gagal memuat statistik: {e}{Style.RESET_ALL}")
            _press_enter(lang)
            
        elif choice == "2":
            _header("HTML REPORT GENERATOR")
            try:
                from logic.html_report import generate_html_report
                import os
                print("Menganalisa data master history dan membuat statistik...")
                out_path = generate_html_report()
                print(f"\n{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Report berhasil dibuat!")
                print(f"Tersimpan di: {Fore.CYAN}{out_path}{Style.RESET_ALL}")
                
                print("Membuka report di browser...")
                if os.name == 'nt':
                    os.startfile(out_path)
                
            except Exception as e:
                print(f"{Fore.RED}Gagal membuat report: {e}{Style.RESET_ALL}")
            _press_enter(lang)
            
        elif choice == "3":
            _header("INTEGRITY CHECK")
            if not files:
                print(f"{Fore.YELLOW}Peringatan: Anda tidak memasukkan file/folder target untuk di-scan.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Hanya akan mengecek kondisi History dan Config sistem.{Style.RESET_ALL}\n")
            try:
                from logic.integrity import run_integrity_check
                res = run_integrity_check(files)
                print(f"Total File Scanned : {res['total_scanned']}")
                print(f"System Config      : {'INVALID/CORRUPT' if res['invalid_config'] else 'OK'}")
                print(f"History Entries    : {res['broken_history']} broken entries found")
                
                print(f"\nDuplicate Filenames : {len(res['duplicate_filenames'])}")
                if res['duplicate_filenames']:
                    for f in res['duplicate_filenames'][:5]: print(f"  - {f}")
                    if len(res['duplicate_filenames']) > 5: print("  ... dll")
                    
                print(f"\nMissing EXIF        : {len(res['missing_exif'])}")
                print(f"Invalid Dates       : {len(res['invalid_date'])}")
                
                print(f"\nRename Conflicts    : {len(res.get('rename_conflict', []))}")
                if res.get('rename_conflict'):
                    for f in res['rename_conflict'][:5]: print(f"  - {f}")
                    if len(res['rename_conflict']) > 5: print("  ... dll")
            except Exception as e:
                print(f"{Fore.RED}Gagal melakukan Integrity Check: {e}{Style.RESET_ALL}")
            _press_enter(lang)
            
        elif choice == "4":
            show_about(lang)
        elif choice == "5":
            developer_corner_menu(config)
        elif choice_lower == "e" or choice == "":
            break
        else:
            invalid_msg = "Pilihan tidak valid." if lang == "id" else "Invalid choice."
            print(f"{Fore.YELLOW}[!] {invalid_msg}{Style.RESET_ALL}")
            time.sleep(1)

# Alias for backward-compatibility
additional_features_menu = show_additional_features
