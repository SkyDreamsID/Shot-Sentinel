"""
logic/duplicate_checker.py
-----------------
Modul untuk mendeteksi dan mengkarantina file duplikat.
Menggunakan Two-Pass Algorithm (Size Check -> MD5 Chunked Hashing)
demi kecepatan dan efisiensi RAM.
"""
import hashlib
import shutil
import time
import os
import random
import string
import platform
import subprocess
from pathlib import Path
from colorama import Fore, Style
from .settings import _header, _safe_input, clear_screen
from .version import SEP_LEN

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes
    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [
            ("hwnd", wintypes.HWND),
            ("wFunc", wintypes.UINT),
            ("pFrom", wintypes.LPCWSTR),
            ("pTo", wintypes.LPCWSTR),
            ("fFlags", wintypes.UINT),
            ("fAnyOperationsAborted", wintypes.BOOL),
            ("hNameMappings", wintypes.LPVOID),
            ("lpszProgressTitle", wintypes.LPCWSTR)
        ]

def send_to_recycle_bin(path: Path) -> bool:
    if IS_WINDOWS:
        try:
            FO_DELETE = 3
            FOF_ALLOWUNDO = 0x40
            FOF_NOCONFIRMATION = 0x10
            FOF_SILENT = 0x04

            shfos = SHFILEOPSTRUCTW()
            shfos.hwnd = None
            shfos.wFunc = FO_DELETE
            shfos.pFrom = str(path.resolve()) + '\0\0'
            shfos.pTo = None
            shfos.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
            
            result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(shfos))
            return result == 0
        except Exception:
            return False
    else:
        try:
            # Native Linux trash using GIO (standard on Ubuntu, Mint, Debian, GNOME, Cinnamon)
            res = subprocess.run(["gio", "trash", str(path.resolve())], capture_output=True)
            if res.returncode == 0:
                return True
        except Exception:
            pass

        try:
            # Optional python library fallback if installed
            from send2trash import send2trash
            send2trash(str(path.resolve()))
            return True
        except Exception:
            pass

        return False

def calculate_md5(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    """
    Menghitung MD5 Hash dari sebuah file menggunakan read chunks (default 1MB per chunk).
    Sangat ramah RAM untuk file video/foto raksasa.
    """
    hasher = hashlib.md5()
    try:
        with file_path.open('rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
    except Exception:
        return ""
    return hasher.hexdigest()

def run_duplicate_checker(files: list[Path], config: dict):
    lang = config.get("language", "id")
    clear_screen()
    
    title = "DUPLICATE CHECKER"
    _header(title)
    
    if not files:
        if lang == "id":
            print(f"{Fore.YELLOW}Tidak ada file untuk diproses.{Style.RESET_ALL}")
            _safe_input("\nTekan Enter untuk kembali...")
        else:
            print(f"{Fore.YELLOW}No files to process.{Style.RESET_ALL}")
            _safe_input("\nPress Enter to return...")
        return

    msg_start = "Menganalisis file..." if lang == "id" else "Analyzing files..."
    print(msg_start)
    
    # ---------------------------------------------------------
    # PASS 1: Size Check
    # ---------------------------------------------------------
    size_map = {}
    for p in files:
        if p.exists() and p.is_file():
            try:
                sz = p.stat().st_size
                if sz not in size_map:
                    size_map[sz] = []
                size_map[sz].append(p)
            except Exception:
                pass
                
    # Filter only sizes that have multiple files
    potential_duplicates = {sz: paths for sz, paths in size_map.items() if len(paths) > 1}
    
    # Calculate how many files actually need hashing
    files_to_hash = sum(len(paths) for paths in potential_duplicates.values())
    
    if files_to_hash == 0:
        if lang == "id":
            print(f"\n{Fore.GREEN}Luar Biasa! Tidak ada indikasi file duplikat (semua unik).{Style.RESET_ALL}")
            _safe_input("\nTekan Enter untuk kembali...")
        else:
            print(f"\n{Fore.GREEN}Excellent! No duplicate files detected (all unique).{Style.RESET_ALL}")
            _safe_input("\nPress Enter to return...")
        return
        
    msg_hash = (f"Ditemukan {files_to_hash} file berukuran identik. Melakukan verifikasi isi (Deep Hash)..." 
                if lang == "id" else 
                f"Found {files_to_hash} identical-sized files. Running content verification (Deep Hash)...")
    print(f"\n{msg_hash}")
    
    # ---------------------------------------------------------
    # PASS 2: Hash Check
    # ---------------------------------------------------------
    start_time = time.perf_counter()
    exact_duplicates = [] # List of tuples: (original, list of duplicates)
    
    for sz, paths in potential_duplicates.items():
        hash_map = {}
        for p in paths:
            h = calculate_md5(p)
            if h:
                if h not in hash_map:
                    hash_map[h] = []
                hash_map[h].append(p)
        
        # Add to our final list if there are actual hash collisions
        for h, identical_files in hash_map.items():
            if len(identical_files) > 1:
                # Sort files intelligently to find the "Original"
                # Priority 1: Shortest filename (e.g. IMG_001.jpg vs IMG_001 - Copy.jpg)
                # Priority 2: Oldest creation time
                identical_files.sort(key=lambda p: (len(p.name), p.stat().st_ctime))
                
                # Keep the first file as the "original", the rest are duplicates
                exact_duplicates.append((identical_files[0], identical_files[1:]))
                
    # ---------------------------------------------------------
    # PASS 3: Move (Karantina)
    # ---------------------------------------------------------
    if not exact_duplicates:
        if lang == "id":
            print(f"\n{Fore.GREEN}Semua file aman! Walaupun ada yang seukuran, isinya berbeda.{Style.RESET_ALL}")
            _safe_input("\nTekan Enter untuk kembali...")
        else:
            print(f"\n{Fore.GREEN}All files safe! Some had identical sizes, but contents differed.{Style.RESET_ALL}")
            _safe_input("\nPress Enter to return...")
        return
    total_duplicates = sum(len(dups) for orig, dups in exact_duplicates)

    print("\n" + ("#"*SEP_LEN) + "\n")
    if lang == "id":
        print(f"Ditemukan {Fore.YELLOW}{total_duplicates}{Style.RESET_ALL} file duplikat!")
        print("Pilih aksi untuk file-file duplikat ini:")
        print(f"{Fore.GREEN}[1] Isolate{Style.RESET_ALL} (Move ke folder kusus) {Fore.GREEN}[Recomended]{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[2] Recycle Bin{Style.RESET_ALL} (Move ke tempat sampah)")
        print(f"{Fore.RED}[3] Delete Permanen (High Risk){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[E] Batal / Abaikan{Style.RESET_ALL}\n")
    else:
        print(f"Found {Fore.YELLOW}{total_duplicates}{Style.RESET_ALL} duplicate files!")
        print("Choose an action for these duplicates:")
        print(f"{Fore.GREEN}[1] Isolate{Style.RESET_ALL} (Move to a special folder) {Fore.GREEN}[Recomended]{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[2] Recycle Bin{Style.RESET_ALL} (Move to trash)")
        print(f"{Fore.RED}[3] Permanent Delete (High Risk){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[E] Cancel / Ignore{Style.RESET_ALL}\n")
        
    while True:
        action_choice = _safe_input("Pilih (1/2/3/E): " if lang == "id" else "Select (1/2/3/E): ").strip().lower()
        if action_choice in ['e', '1', '2', '3']:
            break
            
    if action_choice == 'e':
        print(f"\n{Fore.YELLOW}Operasi dibatalkan.{Style.RESET_ALL}")
        return
        
    if action_choice == '3':
        # Captcha confirmation
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if lang == "id":
            print(f"\n{Fore.RED}PERINGATAN: File akan dihapus permanen dan tidak bisa dikembalikan!{Style.RESET_ALL}")
            print(f"Ketik kode ini untuk konfirmasi: {Fore.YELLOW}{code}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}WARNING: Files will be permanently deleted and cannot be recovered!{Style.RESET_ALL}")
            print(f"Type this code to confirm: {Fore.YELLOW}{code}{Style.RESET_ALL}")
            
        ans = _safe_input(">>> ").strip()
        if ans != code:
            if lang == "id":
                print(f"{Fore.RED}Kode salah! Operasi dibatalkan.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Incorrect code! Operation cancelled.{Style.RESET_ALL}")
            _safe_input("\nTekan Enter untuk kembali..." if lang == "id" else "\nPress Enter to return...")
            return
            
    total_processed = 0
    total_bytes_saved = 0
    quarantine_folder_name = "[Shot Sentinel] - Duplicates"
    
    if action_choice == '1':
        print("\n" + ("Mengisolasi duplikat..." if lang == "id" else "Isolating duplicates..."))
    elif action_choice == '2':
        print("\n" + ("Memindahkan ke Recycle Bin..." if lang == "id" else "Moving to Recycle Bin..."))
    elif action_choice == '3':
        print("\n" + ("Menghapus file secara permanen..." if lang == "id" else "Deleting files permanently..."))
    
    for original, duplicates in exact_duplicates:
        for dup in duplicates:
            try:
                file_size = dup.stat().st_size
                
                if action_choice == '1':
                    # ISOLATE
                    q_dir = dup.parent / quarantine_folder_name
                    q_dir.mkdir(parents=True, exist_ok=True)
                    target_path = q_dir / dup.name
                    if target_path.exists():
                        target_path = q_dir / f"{dup.stem}_{int(time.time())}{dup.suffix}"
                    shutil.move(str(dup), str(target_path))
                    print(f"  {Fore.YELLOW}[Karantina]{Style.RESET_ALL} {dup.name} -> {q_dir.name}")
                    
                elif action_choice == '2':
                    # RECYCLE BIN
                    if send_to_recycle_bin(dup):
                        print(f"  {Fore.YELLOW}[Recycle Bin]{Style.RESET_ALL} {dup.name}")
                    else:
                        raise Exception("Win32 API Error")
                        
                elif action_choice == '3':
                    # PERMANENT DELETE
                    dup.unlink()
                    print(f"  {Fore.RED}[Terhapus]{Style.RESET_ALL} {dup.name}")
                    
                total_processed += 1
                total_bytes_saved += file_size
                
            except Exception as e:
                print(f"  {Fore.RED}[Gagal]{Style.RESET_ALL} {dup.name}: {e}")
                
    elapsed = time.perf_counter() - start_time
    mb_saved = total_bytes_saved / (1024 * 1024)
    
    print("\n" + "="*SEP_LEN)
    print(f"[{'DUPLICATE SUMMARY' if lang == 'en' else 'RINGKASAN DUPLIKAT'}]")
    print("="*SEP_LEN)
    
    if action_choice == '1':
        lbl_moved = "Total Diisolasi" if lang == "id" else "Total Isolated"
    elif action_choice == '2':
        lbl_moved = "Total di Recycle Bin" if lang == "id" else "Total Recycled"
    else:
        lbl_moved = "Total Dihapus" if lang == "id" else "Total Deleted"
        
    lbl_space = "Potensi Ruang Hemat" if lang == "id" else "Potential Space Saved"
    lbl_time  = "Waktu Proses" if lang == "id" else "Process Time"
    
    print(f"{lbl_moved:<22}: {Fore.CYAN}{total_processed} file{Style.RESET_ALL}")
    print(f"{lbl_space:<22}: {Fore.GREEN}{mb_saved:.2f} MB{Style.RESET_ALL}")
    print(f"{lbl_time:<22}: {elapsed:.2f} detik")
    print("-" * SEP_LEN)
    
    if action_choice == '1':
        if lang == "id":
            print(f"File duplikat berhasil dipindahkan ke folder '{quarantine_folder_name}'.")
            print("Anda dapat memeriksa dan menghapusnya secara manual jika sudah yakin.")
        else:
            print(f"Duplicate files successfully moved to '{quarantine_folder_name}' folder.")
            print("You can review and delete them manually when you are sure.")
    elif action_choice == '2':
        if lang == "id":
            print("File duplikat berhasil dipindahkan ke Recycle Bin.")
        else:
            print("Duplicate files successfully moved to the Recycle Bin.")
    elif action_choice == '3':
        if lang == "id":
            print(f"{Fore.RED}File duplikat telah dihapus secara permanen.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Duplicate files have been permanently deleted.{Style.RESET_ALL}")
            
    _safe_input("\nTekan Enter untuk kembali..." if lang == "id" else "\nPress Enter to return...")
