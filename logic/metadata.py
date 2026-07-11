import datetime
import json
import re
from pathlib import Path
import exifread

ROOT_DIR    = Path(__file__).resolve().parent.parent
CONFIG_DIR  = ROOT_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"
ALIAS_FILE  = CONFIG_DIR / "camera_alias.json"

# Preset format nama file bawaan
# Format string menggunakan placeholder yang sama dengan filename_format:
# {camera}, {date}, {time}, {year}, {month}, {day}, {hour}, {minute}, {second}, {index}
# Catatan: alias_index dan username_index memiliki format resolver khusus di worker.py
FILENAME_PRESETS = {
    "default"         : "[{camera}]{date}_{time}_{index}",
    "datetime_only"   : "{date}_{time}",
    "date_index"      : "{date}_{index}",
    "camera_index"    : "[{camera}]_{index}",
    "camera_datetime" : "[{camera}]{date}_{time}",
    "alias_index"     : "{camera}_{index}",
    "username_index"  : "{camera}_{index}",  # {camera} diisi dengan username dari config
}

# Case-insensitive patterns for classification
RE_SCR = re.compile(r"(?i)screenshot|screen_shot|screen-shot|^scr_|^ss_|capture")
RE_REC = re.compile(r"(?i)screenrecording|screen\s?recording|screencast|screen_recording|screen-recording|^rec_|video_capture|recording")
RE_DL = re.compile(r"(?i)download|^dl_|whatsapp|telegram|instagram|snapchat|facebook|^fb_|^wa_|^tg_|^ig_|discord")

def detect_source(p: Path, config: dict = None, has_exif: bool = None, image_exts: set = None, video_exts: set = None) -> str:
    if config is None:
        config = load_config_file()
        
    stem = p.stem
    ext = p.suffix.lower()
    
    if image_exts is None:
        image_exts = {x.lower() for x in config.get("supported_image_extensions", [])}
    if video_exts is None:
        video_exts = {x.lower() for x in config.get("supported_video_extensions", [])}
    
    # Check DL folder first
    in_download_dir = False
    for parent in p.parents:
        if parent.name.lower() == "downloads":
            in_download_dir = True
            break
            
    if in_download_dir or RE_DL.search(stem):
        return "DL"
        
    if ext in video_exts:
        if RE_REC.search(stem):
            return "REC"
        if stem.startswith(("VID_", "MVI_", "GOPR", "GP", "DSC_")):
            return "CAM"
    elif ext in image_exts:
        if RE_SCR.search(stem):
            return "SCR"
        if has_exif is not None:
            if has_exif:
                return "CAM"
        else:
            if has_exif_camera(p):
                return "CAM"
        if stem.startswith(("DSC_", "IMG_", "PANO_", "MVIMG_", "CIMG_", "DCIM", "IMG-")):
            return "CAM"
            
    return "UNK"

def get_source_alias(source_type: str, config: dict = None) -> str:
    if config is None:
        config = load_config_file()
    aliases = config.get("source_aliases", {})
    return aliases.get(source_type, source_type)

# ---------------------------------------------------------------------------
# Detection regex — dibangun dinamis berdasarkan preset aktif
# ---------------------------------------------------------------------------

# Blok pattern reusable
_DATE   = r"\d{4}-\d{2}-\d{2}"        # 2026-07-07
_TIME   = r"\d{2}-\d{2}-\d{2}"        # 10-30-00
_IDX    = r"\d+"                       # 0001
_IDX4   = r"\d{4}"                     # 0001 — index selalu 4 digit (zfill(4))
_IDX5   = r"\d{5}"                     # 00001 — index selalu 5 digit (zfill(5))
_CAM    = r".+?"                       # nama kamera apa saja
_ALIAS  = r"[a-zA-Z0-9_]{1,16}"            # alias/username: huruf besar, kecil, angka, dan underscore, maks 16 char

# Negative lookahead untuk alias_index/username_index:
# Menolak prefix nama file kamera/HP asli yang strukturnya mirip output Shot Sentinel.
# Shot Sentinel tidak pernah menghasilkan nama berawalan IMG_, VID_, DSC, PXL_, dll.
_ALIAS_NEG = r"(?!IMG_|VID_|PXL_|DSC|MVI_|GOPR|GP\d|MOV_|PANO_|MVIMG_|CIMG|DCIM)"

# Mapping preset -> pattern regex
_PRESET_PATTERNS = {
    "default"        : rf"^\[{_CAM}\]{_DATE}_{_TIME}_{_IDX}",     # [D3300]2026-07-07_10-30-00_0001
    "camera_datetime": rf"^\[{_CAM}\]{_DATE}_{_TIME}",            # [D3300]2026-07-07_10-30-00
    "datetime_only"  : rf"^{_DATE}_{_TIME}",                       # 2026-07-07_10-30-00
    "date_index"     : rf"^{_DATE}_{_IDX}",                        # 2026-07-07_0001
    "camera_index"   : rf"^\[{_CAM}\]_{_IDX}",                    # [D3300]_0001
    # alias_index: ALIAS_00001 — 5 digit index, bukan prefix kamera asli
    "alias_index"    : rf"^{_ALIAS_NEG}{_ALIAS}_{_IDX5}(?=\.)",   # D3300_00001, CAM_00042
    # username_index: USERNAME_00001 — 5 digit index
    "username_index" : rf"^{_ALIAS_NEG}{_ALIAS}_{_IDX5}(?=\.)",   # SkyDreamsID_00001, rifkiekap07_00001
}


def build_detection_regex(config: dict) -> re.Pattern:
    """
    Buat regex deteksi 'already renamed' berdasarkan preset aktif di config.

    Cara kerja:
    - Jika config menggunakan filename_preset yang dikenal → pakai pattern spesifik preset.
    - Jika custom (filename_format) → parse token dalam format string dan buat pattern.
    - Jika tidak ada yang cocok → fallback ke pattern default.

    Tidak ada hardcode di luar fungsi ini.
    """
    preset_key = config.get("filename_preset")

    # 1. Preset yang dikenal — pattern sudah terdefinisi di _PRESET_PATTERNS
    if preset_key and preset_key in _PRESET_PATTERNS:
        return re.compile(_PRESET_PATTERNS[preset_key])

    # 2. Custom filename_format — parse token secara generik
    fmt = config.get("filename_format", "[{camera}]{date}_{time}_{index}")
    pattern = _fmt_to_regex(fmt)
    return re.compile(pattern)


def _fmt_to_regex(fmt: str) -> str:
    """
    Ubah format string (misal '[{camera}]{date}_{time}_{index}') menjadi
    anchored regex pattern yang mendeteksi output format tersebut.
    Dipakai untuk custom filename_format.
    """
    import re as _re
    # Escape literal chars dulu, lalu ganti placeholder
    # Pisahkan token menggunakan split pada placeholder
    # Contoh: '[{camera}]{date}_{time}_{index}'
    #   → '^\\[.+?\\]\\d{4}-\\d{2}-\\d{2}_\\d{2}-\\d{2}-\\d{2}_\\d+'
    _TOKEN_MAP = {
        "{camera}"  : r".+?",
        "{date}"    : r"\d{4}-\d{2}-\d{2}",
        "{time}"    : r"\d{2}-\d{2}-\d{2}",
        "{year}"    : r"\d{4}",
        "{month}"   : r"\d{2}",
        "{day}"     : r"\d{2}",
        "{hour}"    : r"\d{2}",
        "{minute}"  : r"\d{2}",
        "{second}"  : r"\d{2}",
        "{index}"   : r"\d+",
    }
    # Split berdasarkan placeholder, pertahankan separator
    parts = _re.split(r"(\{[^}]+\})", fmt)
    result = "^"
    for part in parts:
        if part in _TOKEN_MAP:
            result += _TOKEN_MAP[part]
        else:
            # Escape literal chars (brackets, dots, dll)
            result += _re.escape(part)
    return result


# Default alias kamera — digunakan saat camera_alias.json belum ada
_DEFAULT_ALIASES = {
    "NIKOND3300": "D3300",
    "NIKOND3100": "D3100",
}

DEFAULT_CONFIG = {
    "language"            : "id",
    "filename_format"     : "[{camera}]{date}_{time}_{index}",
    "filename_preset"     : "default",
    "use_phone_model"     : True,
    "unknown_camera_name" : "CAM",
    "max_camera_length"   : 10,
    "username"            : "Your Name",
    "unknown_camera_list" : ["CAM", "UNKNOWN", "NOEXIF", "MISC"],
    "supported_image_extensions": [
        ".jpg",".jpeg",".png",".nef",".cr2",".cr3",".arw",".raf",".orf",".rw2",".dng",
    ],
    "supported_video_extensions": [
        ".mp4",".mov",".avi",".mts",".m2ts",".mxf",
    ],
    "brand_keywords": [
        "NIKON","SONY","CANON","OLYMPUS","FUJIFILM","PANASONIC","LEICA","PENTAX","HASSELBLAD",
    ],
    "source_aliases": {
        "CAM": "CAM",
        "SCR": "SCR",
        "REC": "REC",
        "DL" : "DL",
        "UNK": "UNK"
    },
    "enable_easter_eggs": True
}

# ---------------------------------------------------------------------------
# Alias file helpers
# ---------------------------------------------------------------------------

def load_alias_file() -> dict:
    """Load config/camera_alias.json. Return {} jika tidak ada atau corrupt."""
    if not ALIAS_FILE.exists():
        return {}
    try:
        return json.loads(ALIAS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_alias_file(aliases: dict) -> bool:
    """Simpan aliases ke config/camera_alias.json."""
    try:
        CONFIG_DIR.mkdir(exist_ok=True)
        # Urutkan keys secara alfabetis saat disimpan
        sorted_aliases = dict(sorted(aliases.items()))
        ALIAS_FILE.write_text(
            json.dumps(sorted_aliases, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False

def ensure_alias_file() -> None:
    """Buat config/camera_alias.json dengan default jika belum ada. Dipanggil saat startup."""
    CONFIG_DIR.mkdir(exist_ok=True)
    if not ALIAS_FILE.exists():
        save_alias_file(_DEFAULT_ALIASES)

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def resolve_filename_format(config: dict) -> str:
    """
    Menentukan format nama file berdasarkan config.
    Priority: filename_preset > filename_format > fallback default.
    Jika filename_preset tidak dikenal, fallback ke '[{camera}]{date}_{time}_{index}'.
    Jika filename_preset tidak ada di config, gunakan filename_format (backward compatible).
    """
    _DEFAULT_FMT = "[{camera}]{date}_{time}_{index}"
    preset_key = config.get("filename_preset")
    if preset_key is not None:
        resolved = FILENAME_PRESETS.get(preset_key)
        if resolved is None:
            valid = ", ".join(FILENAME_PRESETS.keys())
            print(f"[WARNING] filename_preset '{preset_key}' tidak dikenal. Fallback ke format default.")
            print(f"          Preset yang tersedia: {valid}")
            return _DEFAULT_FMT
        return resolved
    return config.get("filename_format", _DEFAULT_FMT)

def load_config_file() -> dict:
    CONFIG_DIR.mkdir(exist_ok=True)
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    try:
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        merged = DEFAULT_CONFIG.copy()
        merged.update(cfg)
        return merged
    except Exception:
        return DEFAULT_CONFIG.copy()

# ---------------------------------------------------------------------------
# EXIF helpers
# ---------------------------------------------------------------------------

def clean_camera_model(raw: str, config: dict = None) -> str:
    if config is None:
        config = load_config_file()
    
    # 1. Bersihkan untuk lookup alias (uppercase, no space)
    model_key = raw.upper().replace(" ", "")
    
    # Lookup alias dari camera_alias.json (satu-satunya sumber alias)
    aliases = load_alias_file()
    if model_key in aliases:
        model = aliases[model_key]
    else:
        # 2. Fallback: pembersihan brand keyword bawaan jika tidak ada alias
        model = raw.upper()
        brand_keywords = set(config.get("brand_keywords", DEFAULT_CONFIG["brand_keywords"]))
        for brand in brand_keywords:
            model = model.replace(brand, "")
        model = model.replace(" ", "")
        
        import re
        model = re.sub(r'[\\/:*?"<>|]', '', model)

    if not model:
        return config.get("unknown_camera_name", DEFAULT_CONFIG["unknown_camera_name"])

    max_len = config.get("max_camera_length", DEFAULT_CONFIG["max_camera_length"])
    return model[:max_len]

def has_exif_camera(p: Path) -> bool:
    try:
        with p.open("rb") as f:
            tags = exifread.process_file(f, details=False)
            return "Image Model" in tags
    except Exception:
        return False

def extract_exif(p: Path, config: dict = None) -> tuple[str, str, str, bool]:
    if config is None:
        config = load_config_file()

    tags = {}
    try:
        with p.open("rb") as f:
            tags = exifread.process_file(f, details=False)
    except Exception:
        tags = {}

    # Model
    model_tag = tags.get("Image Model")
    model = clean_camera_model(str(model_tag), config) if model_tag else config.get("unknown_camera_name", "CAM")

    # Date & time
    datetime_tag = tags.get("EXIF DateTimeOriginal")
    if datetime_tag:
        try:
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
    
    has_exif = bool(model_tag or datetime_tag)
    return model, date_str, time_str, has_exif
