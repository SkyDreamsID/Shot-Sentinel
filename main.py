#!/usr/bin/env python3
import sys
import os
import re
import json
import datetime
import subprocess
from pathlib import Path
import exifread # buat read metadata
from colorama import init, Fore, Style

LOG_FILE = Path(__file__).resolve().parent / "process_log.txt"
CONFIG_FILE = Path(__file__).resolve().parent / "config.json"
DEFAULT_CONFIG = {
    "filename_format": "[{camera}]{date}_{time}_{index}",
    "use_phone_model": True,
    "unknown_camera_name": "CAM",
    "max_camera_length": 10,
    
    "supported_image_extensions": [
        ".jpg",".jpeg",".png",".nef",".cr2",".cr3",".arw",".raf",".orf",".rw2",".dng",
    ],
    
    "supported_video_extensions": [
        ".mp4",".mov",".avi",".mts",".m2ts",".mxf",
    ],
    
    "brand_keywords": [
        "NIKON","SONY","CANON","OLYMPUS","FUJIFILM","PANASONIC","LEICA","PENTAX","HASSELBLAD",
    ],
    
    "camera_aliases": {
        "NIKOND3300": "D3300",
        "NIKOND3100": "D3100",
    }
}
init(autoreset=True)

### Warna Log/Status
## --- Shortcut Warna ---
Hijau   = Fore.GREEN
Kuning  = Fore.YELLOW
Merah   = Fore.RED
Cyan    = Fore.CYAN
BiruTua = Fore.BLUE
Abu     = Style.DIM

## --- Shortcut Nama Status (S = Status) ---
S_Sukses    = "[Berhasil]"    # 
S_Gagal     = "[Gagal]"       
S_Skip      = "[SKIP]"        
S_Error     = "[ERROR]"       # Eror path dll
S_Done      = "[SELESAI]"
S_Skipped   = "[SKIPPED]"     # Skip (udah rename / udah nama asli)

# Rename
S_Renamed   = "[RENAMED]"     # Sukses Rename

# Restore
S_Restored  = "[RESTORED]"   # Sukses Restore
S_Failed    = "[FAILED]"       # Gagal Restore

## --- Global Theme Mapping ---
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

def log(prefix: str, message: str):
    color = LOG_COLORS.get(prefix, "")
    print(f"{color}{prefix}{Style.RESET_ALL} {message}")
    
    # Mencatat entri timestamp ke dalam log file
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"{timestamp} {prefix} {message}\n")
    except Exception:
        pass

def load_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            json.dumps(
                DEFAULT_CONFIG,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )
        return DEFAULT_CONFIG
    try:
        return json.loads(
            CONFIG_FILE.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        log(
            "[ERROR]"
            "config.json rusak, pakai default"
        )
        return DEFAULT_CONFIG

CONFIG = load_config()

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
IMAGE_EXTS = {
    x.lower()
    for x in
CONFIG["supported_image_extensions"]
}
VIDEO_EXTS = {
    x.lower()
    for x in
CONFIG["supported_video_extensions"]
}
SUPPORTED_EXTS = IMAGE_EXTS.union(VIDEO_EXTS)
BRAND_KEYWORDS = set(
    CONFIG["brand_keywords"]
)
TARGET_REGEX = re.compile(r"^\[.+?\]\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_\d+")

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------

def get_master_history_path() -> Path:
    """ Mencari path untuk file master_history.txt didalam root script.
    Jika tidak ditemukan akan otomatis membuat file master_history.txt
    """
    script_dir = Path(os.path.dirname(os.path.realpath(__file__))).resolve()
    master_file = script_dir / "master_history.txt"
    if not master_file.is_file():
        master_file.touch(exist_ok=True)
    return master_file

def log_rename(new_path: Path, old_path: Path, history_file: Path, session_ts: str) -> None:
    """(Append) Menambahkan log rename kedalam file master history
    Format (pipe-delimited): timestamp|new_name|old_name|status
    Status awal selalu "ACTIVE". Kolom status ini yang dipakai restore
    untuk tahu entry mana yang masih valid di-restore, biar gak restore
    dobel
    """
    line = f"{session_ts}|{new_path.name}|{old_path.name}|ACTIVE\n"
    with history_file.open("a", encoding="utf-8") as f:
        f.write(line)

def log_session_entry(session_log: Path, new_path: Path, old_path: Path) -> None:
    """Menambah/update isi log (append).
    Format (no timestamp, only filenames): "NewName -> OldName".
    """
    line = f"{new_path.name} -> {old_path.name}\n"
    with session_log.open("a", encoding="utf-8") as f:
        f.write(line)

def update_history_status(new_name: str, history_file: Path, new_status: str) -> None:
    if not history_file.is_file():
        return
    lines = history_file.read_text(encoding="utf-8").splitlines()
    out_lines = []
    for ln in lines:
        if not ln.strip():
            continue
        if "|" in ln:
            parts = ln.split("|")
            if len(parts) == 4 and parts[1] == new_name:
                parts[3] = new_status
                out_lines.append("|".join(parts))
            else:
                out_lines.append(ln)
        else:
            # Format lama, migrasi ke format baru
            try:
                ts_part, rest = ln.split('] ', 1)
                ts = ts_part.lstrip('[')
                old_new_name, old_old_name = [s.strip() for s in rest.split(' -> ', 1)]
                status = new_status if old_new_name == new_name else "ACTIVE"
                out_lines.append(f"{ts}|{old_new_name}|{old_old_name}|{status}")
            except Exception:
                out_lines.append(ln)
    history_file.write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")

def remove_session_entry(new_name: str, session_log: Path) -> None:
    if not session_log.is_file():
        return
    lines = session_log.read_text(encoding="utf-8").splitlines()
    filtered = []
    for ln in lines:
        try:
            left_part = ln.split(" -> ")[0].strip()
        except Exception:
            filtered.append(ln)
            continue
        if left_part != new_name:
            filtered.append(ln)
    session_log.write_text("\n".join(filtered) + "\n", encoding="utf-8")

def get_target_paths() -> list[Path]:
    args = [a for a in sys.argv[1:] if a.strip()]
    if not args:
        base_dir = Path(os.path.dirname(os.path.realpath(__file__))).resolve()
        return [p for p in base_dir.iterdir() if is_supported(p)]
    if len(args) == 1 and Path(args[0]).expanduser().resolve().is_dir():
        folder = Path(args[0]).expanduser().resolve()
        return [p for p in folder.iterdir() if is_supported(p)]
    files = []
    for a in args:
        p = Path(a).expanduser().resolve()
        if p.is_file() and is_supported(p):
            files.append(p)
    return files

def is_supported(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in SUPPORTED_EXTS

def clean_camera_model(raw: str) -> str:
    """Meringkas nama Model Kamera sehingga jadi <10 huruf, misal "NIKON D3300" -> [D3300]
    Jika Merk & Model Kamera tidak terdeteksi maka akan menghasilkan "CAM"
    """
    model = raw.upper()
    for brand in BRAND_KEYWORDS:
        model = model.replace(brand, "")
    model = model.replace(" ", "")
    
    aliases = CONFIG["camera_aliases"]
    
    if model in aliases:
        model = aliases[model]
        
    if not model:
        return CONFIG["unknown_camera_name"]
    
    return model[:CONFIG["max_camera_length"]]

def extract_exif(p: Path) -> tuple[str, str, str]:
    tags = {}
    try:
        with p.open("rb") as f:
            tags = exifread.process_file(f, details=False)
    except Exception:
        tags = {}

    # Model
    model_tag = tags.get("Image Model")
    model = clean_camera_model(str(model_tag)) if model_tag else "CAM"

    # Date & time
    datetime_tag = tags.get("EXIF DateTimeOriginal")
    if datetime_tag:
        try:
            # Format: "YYYY:MM:DD HH:MM:SS" [Tahun:Bulan:Hari Jam:menit:Detik]
            raw = str(datetime_tag)
            date_part, time_part = raw.split(' ')
            y, m, d = date_part.split(":")
            date_str = f"{y}-{m}-{d}"
            time_str = time_part.replace(":", "-")
        except Exception:
            datetime_tag = None
    if not datetime_tag:
        ts = p.stat().st_mtime
        dt = datetime.datetime.fromtimestamp(ts)
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H-%M-%S")
    return model, date_str, time_str

def already_formatted(p: Path) -> bool:
    """Cek apakah nama file sudah sesuai dengan standar format yang ditentukan"""
    return bool(TARGET_REGEX.match(p.name))

def extract_index_from_name(name: str) -> str | None:
    """Ngambil 4 digit terakhir dari index nama file asli, misal "DSC_1234" -> "1234" atau "2024-06-29_10-15-17_Foto12345" -> "2345" """
    stem = Path(name).stem
    matches = re.findall(r"(\d+)", stem)
    if not matches:
        return None
    num_seq = matches[-1]
    if len(num_seq) > 4:
        num_seq = num_seq[-4:]
    return num_seq.zfill(4)

def create_session_log() -> Path:
    """ Membuat file log baru dengan timestamp di dalam folder 'log'
    Format file : DD-MM-YYYY_HHMMSS.txt
    Isi log     : per baris "NewName -> OldName"
    Return path kedalam file yang dibuat
    """
    script_dir = Path(os.path.dirname(os.path.realpath(__file__))).resolve()
    log_dir = script_dir / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H%M%S")
    session_file = log_dir / f"{timestamp}.txt"
    session_file.touch(exist_ok=True)
    return session_file

def find_latest_history_file() -> Path:
    """Mencari file log (.txt) terbaru berdasarkan timestamp di folder 'log'
    Jika tidak terdeteksi maka raises FileNotFoundError. 
    """
    script_dir = Path(os.path.dirname(os.path.realpath(__file__))).resolve()
    log_dir = script_dir / "log"
    if not log_dir.is_dir():
        raise FileNotFoundError("Tidak ada data 'log' yang ditemukan")
    txt_files = []
    for f in log_dir.iterdir():
        if f.is_file() and f.suffix == ".txt":
            name = f.stem
            if len(name) == 15 and name[2] == "-" and name[5] == "-" and name[8] == "_":
                txt_files.append(f)
    if not txt_files:
        raise FileNotFoundError("No history .txt file found in 'log' directory.")
    latest = sorted(txt_files, key=lambda p: p.name, reverse=True)[0]
    return latest

def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog="Shot Sentinel",
    
    formatter_class=argparse.RawTextHelpFormatter, description="""
v0.7a (sementara Windows only) - Anti-Overwrite media
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

    # Target dari select explorer
    files = []
    if args.files:
        files = [Path(p).resolve() for p in args.files if is_supported(Path(p))]
    else:
        # Target dari fungsi helper
        files = get_target_paths()

        if not files:
            log(S_Skip, "Tidak ada file yang terdeteksi, Program dihentikan")
            return

    os.system('cls')

    ## Daftar Fitur (tampilan)
    if args.mode:
        choice = "1" if args.mode == "rename" else "2"
    else:
        header1 = (f"=== Shot-Sentinel 0.7a (Anti Ketimpa Foto Anyar :v) ===")
        border1 = (len(header1))
        print(f"{border1*'='}")
        print(header1)
        print(f"{border1*'='}")
        print(f"Terdeteksi {len(files)} file")
        print("\nPengen Ngapain?")
        print("[1] Auto Rename (y)")
        print("[2] Restore ke nama asli (r)")
        print("[3] Batal (Enter)")
        try:
            choice = input("\nPilih: ").strip().lower()
        except EOFError:
            choice = "1"

    if choice in ('1', 'y'):
        # ----- Rename Flow -----
        master_history = get_master_history_path()
        session_log = create_session_log()
        session_ts = datetime.datetime.now().strftime("%d-%m-%Y_%H%M%S")
        auto_index = 1
        renamed_count = 0
        unprocessed_count = 0 # total skip dan eror
        total_files = len(files)
        idx_width = len(str(total_files))
        max_name_len = max((len(f.name) for f in files), default=0)
        for idx_file, file_path in enumerate(files, start=1):
            try:
                # Format Waktu & Merek Kamera
                if already_formatted(file_path):
                    # Log progress (already changed)
                    log(S_Skipped, f"Proses {idx_file:>{idx_width}}/{total_files} {file_path.name.ljust(max_name_len)} {Abu}[already changed]{Style.RESET_ALL}")
                    unprocessed_count += 1
                    continue
                if file_path.suffix.lower() in IMAGE_EXTS:
                    model, date_str, time_str = extract_exif(file_path)
                else:
                    ts = file_path.stat().st_mtime
                    dt = datetime.datetime.fromtimestamp(ts)
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H-%M-%S")
                    model = "CAM"
                # Ngambil Index Foto
                idx = extract_index_from_name(file_path.name)
                if idx is None:
                    idx = str(auto_index).zfill(4)
                    auto_index += 1

                # Merubah nama file menjadi dengan waktu dan index dari exif
                fmt = CONFIG["filename_format"]
                
                if not model:
                    fmt = fmt.replace("[{camera}]", "")
                    fmt = fmt.replace("{camera}_", "")
                    fmt = fmt.replace("{camera}", "")
                    
                new_name = (
                    fmt.format(
                        camera=model,
                        date=date_str,
                        time=time_str,
                        index=idx
                    )
                    + file_path.suffix
                )
                
                new_path = file_path.with_name(new_name)
                if new_path.exists():
                    # Mengatasi collision dengan appending 
                    base_stem = new_path.stem
                    suffix = new_path.suffix
                    counter = 1
                    while True:
                        candidate_name = f"{base_stem}_{counter:03d}{suffix}"
                        candidate_path = file_path.with_name(candidate_name)
                        if not candidate_path.exists():
                            new_path = candidate_path
                            break
                        counter += 1

                file_path.rename(new_path)
                # Log success ke process log
                log(S_Renamed, f"Proses {idx_file:>{idx_width}}/{total_files} {file_path.name.ljust(max_name_len)} {Abu}=>{Style.RESET_ALL} {new_path.name}")
                # Log ke master history (dengan timestamp) dan session log (plain)
                log_rename(new_path, file_path, master_history, session_ts)
                log_session_entry(session_log, new_path, file_path)
                renamed_count += 1
            except Exception as e:
                log(S_Error, f"Proses {idx_file:>{idx_width}}/{total_files} {file_path.name.ljust(max_name_len)} {Abu}=>{Style.RESET_ALL} ERROR [{e}]")
                unprocessed_count += 1

        if renamed_count > 0:
            log(S_Done, f"Berhasil rename {renamed_count}/{total_files} file | Skip/Gagal: {unprocessed_count} | History tersimpan di {master_history}")
        else:
            log(S_Done, f"Tidak ada file yang diproses ({unprocessed_count}/{total_files} file sudah sesuai format)")
            
        try:
            input("\nTekan Enter untuk keluar...")
            sys.exit(0)
        except EOFError:
            pass
        return

    elif choice in ('2', 'r'):
        # ----- Restore Flow -----
        master_history = get_master_history_path()
        
        total_files = len(files)
        idx_width = len(str(total_files))
        max_name_len = max((len(f.name) for f in files), default=0)
        restored_count = 0
        skipped_count = 0   # Udah nama asli, gak perlu di-restore
        failed_count = 0    # Gagal rename / histori gak ketemu
        
        # Entry yang statusnya udah RESTORED gak dimasukkan -> ini guard
        history_map: dict[str, str] = {}
        for line in master_history.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            if "|" in line:
                # Format baru: timestamp|new_name|old_name|status
                parts = line.split("|")
                if len(parts) != 4:
                    continue
                _, new_name, old_name, status = parts
                if status != "ACTIVE":
                    continue
                history_map[new_name] = old_name
            elif '] ' in line and ' -> ' in line:
                try:
                    _, rest = line.split('] ', 1)
                    new_name, old_name = [part.strip() for part in rest.split(' -> ', 1)]
                    history_map[new_name] = old_name
                except Exception:
                    continue

        for idx_file, file_path in enumerate(files, start=1):
            if file_path.name in history_map:
                old_name = history_map[file_path.name]
                old_path = file_path.parent / old_name
                try:
                    file_path.rename(old_path)
                    update_history_status(file_path.name, master_history, "RESTORED")
                    restored_count += 1
                    log(S_Restored, f"Proses {idx_file:>{idx_width}}/{total_files} {file_path.name.ljust(max_name_len)} {Abu}=>{Style.RESET_ALL} {old_name}")
                except Exception as e:
                    log(S_Failed, f"Proses {idx_file:>{idx_width}}/{total_files} {file_path.name.ljust(max_name_len)} {Abu}=>{Style.RESET_ALL} ERROR [{e}]")
                    failed_count += 1
            elif not already_formatted(file_path):
                #Jika Nama gak match pola hasil rename -> kemungkinan udah nama asli
                log(S_Skipped, f"Proses {idx_file:>{idx_width}}/{total_files} {file_path.name.ljust(max_name_len)} {Abu}[sudah nama asli]{Style.RESET_ALL}")
                skipped_count += 1
            else:
                log(S_Failed, f"Proses {idx_file:>{idx_width}}/{total_files} {file_path.name.ljust(max_name_len)} {Abu}=>{Style.RESET_ALL} No History")
                failed_count += 1
        unprocessed_count = skipped_count + failed_count
        if restored_count > 0:
            log(S_Done, f"Berhasil Restore {restored_count}/{total_files} file | Skip/Gagal: {unprocessed_count} | Update history ke {master_history}")
        elif skipped_count == total_files:
            # Semua file nama asli, gak ada yang perlu di-restore
            log(S_Done, f"Tidak ada file yang diproses ({skipped_count}/{total_files} file sudah nama asli)")
        elif failed_count == total_files:
            # History beneran gak ketemu/relevan buat semua file yang dipilih
            log(S_Gagal, "Catatan history tidak ditemukan, nama file gagal di restore :(")
        else:
            # Campuran: sebagian udah nama asli, sebagian gagal/no-history
            log(S_Gagal, f"Tidak ada file yang di-restore | Sudah nama asli: {skipped_count}, Gagal: {failed_count}")
        try:
            input("\nTekan Enter untuk keluar...")
            sys.exit(0)
        except EOFError:
            pass
        return
    else:
        print("[Cancel] Proses dibatalkan oleh pengguna")
        return

if __name__ == "__main__":
    main()