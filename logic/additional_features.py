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
from .settings import _header, _t, _safe_input, clear_screen

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
    print("-" * 50)
    
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
        
    print("-" * 50)
    _press_enter(lang)

def show_about(lang: str = "id"):
    """Menampilkan halaman About Shot Sentinel."""
    from .version import PROGRAM_NAME, PROGRAM_VERSION, PROGRAM_SLOGAN

    _header("ABOUT")

    SEP = "-" * 50
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
        print("-" * 50)
        print("Project ini dibuat karena developer frustrasi")
        print("kehilangan banyak foto akibat filename kamera")
        print("yang tertimpa di Windows Explorer.")
        print(SEP)
        print(f"\n{Fore.YELLOW}Keputusan Desain (SendTo vs Registry){Style.RESET_ALL}")
        print("-" * 50)
        print("Menggunakan SendTo karena integrasi Registry Windows memiliki")
        print("bug yang membuka banyak terminal saat memilih file lebih dari 1.")
        print("Akhirnya saya memilih merubahnya pakai Sendto")
        print(f"karena terinspirasi dari 'KDE Connect' yang sama-sama memakai Sendto,")
        print(f"dan hasilnya program berjalan normal sesuai ekspetasi dan lebih aman tanpa meninggalkan jejak ke sistem.")
    else:
        print(f"{Fore.YELLOW}Fun Fact{Style.RESET_ALL}")
        print("-" * 50)
        print("This project was created because the developer was frustrated")
        print("from losing many photos due to camera filenames being overwritten")
        print("in Windows Explorer.")
        print(SEP)
        print(f"\n{Fore.YELLOW}Design Decision (SendTo vs Registry){Style.RESET_ALL}")
        print("-" * 50)
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

    SEP = "-" * 50
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
    print("-" * 48)
    try:
        quotes = load_quotes(lang)
        quote = random.choice(quotes)
        print(f"\n{Fore.YELLOW}\"{quote}\"{Style.RESET_ALL}\n")
    except Exception:
        err_msg = "Asset tidak ditemukan." if lang == "id" else "Asset not found."
        print(f"\n{Fore.RED}{err_msg}{Style.RESET_ALL}\n")
    print("-" * 48)
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

def show_additional_features(config: dict) -> None:
    """
    Menu Fitur Tambahan.
    Berisi: Statistics, About, Developer Corner.
    """
    lang = config.get("language", "id")

    while True:
        _header("ADDITIONAL FEATURES" if lang == "en" else "FITUR TAMBAHAN")

        print("[1] Statistics")
        print("[2] About")
        print("[3] Developer Corner")
        print(f"\n{Fore.YELLOW}[E] {'Keluar' if lang == 'id' else 'Exit'}{Style.RESET_ALL}")

        choice = _safe_input(f"\n{'Pilih' if lang == 'id' else 'Select'}: ").strip()
        choice_lower = choice.lower()

        if choice == "1":
            _header("STATISTICS")
            print(f"{Style.DIM}(Coming soon){Style.RESET_ALL}")
            _press_enter(lang)
        elif choice == "2":
            show_about(lang)
        elif choice == "3":
            developer_corner_menu(config)
        elif choice_lower == "e" or choice == "":
            break
        else:
            invalid_msg = "Pilihan tidak valid." if lang == "id" else "Invalid choice."
            print(f"{Fore.YELLOW}[!] {invalid_msg}{Style.RESET_ALL}")
            time.sleep(1)

# Alias for backward-compatibility
additional_features_menu = show_additional_features
