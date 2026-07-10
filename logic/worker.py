import re
import datetime
from pathlib import Path
from .metadata import extract_exif, resolve_filename_format, build_detection_regex, FILENAME_PRESETS
from .source_detector import detect_source, get_source_alias
from .collision import resolve_collision
from .log_history import (
    batch_log_renames,
    log_rename,
    log_session_entry,
    build_restore_map,
    batch_update_history_status,
    update_history_status,
)

# Regex fallback (format default) — hanya dipakai bila config tidak tersedia.
# Jangan gunakan langsung; pakai already_formatted(p, config) untuk akurasi penuh.
_FALLBACK_REGEX = re.compile(r"^\[.+?\]\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_\d+")

def already_formatted(p: Path, config: dict = None, regex: re.Pattern = None) -> bool:
    """
    Cek apakah nama file sudah sesuai dengan standar format yang ditentukan.
    Gunakan config untuk memilih regex yang sesuai dengan preset aktif.
    Jika config=None, fallback ke pattern default agar backward compatible.
    """
    if regex is not None:
        return bool(regex.match(p.name))
    if config is not None:
        regex = build_detection_regex(config)
    else:
        regex = _FALLBACK_REGEX
    return bool(regex.match(p.name))

def extract_index_from_name(name: str, length: int = 4) -> str | None:
    """Mengambil digit terakhir dari indeks nama file asli."""
    stem = Path(name).stem
    matches = re.findall(r"(\d+)", stem)
    if not matches:
        return None
    num_seq = matches[-1]
    if len(num_seq) > length:
        num_seq = num_seq[-length:]
    return num_seq.zfill(length)

def compute_target_path(
    p: Path,
    config: dict,
    existing_set: set[Path] = None,
    auto_index_state: dict = None,
    image_exts: set[str] = None,
    video_exts: set[str] = None
) -> Path:
    """Menghitung path target baru berdasarkan deteksi sumber dan metadata."""
    if auto_index_state is None:
        auto_index_state = {"val": 1}
        
    if image_exts is None:
        image_exts = {x.lower() for x in config.get("supported_image_extensions", [])}
    if video_exts is None:
        video_exts = {x.lower() for x in config.get("supported_video_extensions", [])}
        
    # 1. Ekstrak exif/mtime first (hanya open file 1 kali!)
    ext = p.suffix.lower()
    has_exif = False
    if ext in image_exts:
        exif_model, date_str, time_str, has_exif = extract_exif(p, config)
    else:
        ts = p.stat().st_mtime
        dt = datetime.datetime.fromtimestamp(ts)
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H-%M-%S")
        exif_model = "CAM"
        
    # 2. Deteksi tipe sumber (pass has_exif, image_exts, video_exts agar cepat)
    source_type = detect_source(p, config, has_exif=has_exif, image_exts=image_exts, video_exts=video_exts)
    
    # 3. Tentukan model/alias kamera yang dipakai
    preset_key = config.get("filename_preset")
    unknown_name = config.get("unknown_camera_name", "CAM")
    
    if preset_key == "username_index":
        # username_index: selalu gunakan username dari config, bukan alias kamera
        raw_username = config.get("username", "Your Name").strip()
        if not raw_username:
            raw_username = "Your Name"
        # Batasi maks 16 karakter, hanya huruf, angka, dan underscore (_)
        import re as _re
        raw_username = _re.sub(r'[^a-zA-Z0-9_]', '', raw_username)[:16] or "USER"
        model_or_alias = raw_username
    elif preset_key == "alias_index":
        # alias_index: gunakan alias kamera terdaftar (known camera) atau Unknown Camera Alias (unknown camera)
        if source_type == "CAM":
            from .metadata import load_alias_file
            aliases = load_alias_file()
            has_known_alias = False
            if exif_model and exif_model != unknown_name:
                # Cek apakah exif_model adalah alias terdaftar (salah satu value di camera_alias.json)
                if exif_model in aliases.values():
                    model_or_alias = exif_model
                    has_known_alias = True
            if not has_known_alias:
                model_or_alias = unknown_name
        else:
            model_or_alias = get_source_alias(source_type, config)
    elif source_type == "CAM":
        if exif_model and exif_model != unknown_name:
            model_or_alias = exif_model
        else:
            model_or_alias = unknown_name
    else:
        model_or_alias = get_source_alias(source_type, config)
        
    # 4. Ambil index
    idx_len = 5 if preset_key in ("alias_index", "username_index") else 4
    idx = extract_index_from_name(p.name, idx_len)
    if idx is None:
        idx = str(auto_index_state["val"]).zfill(idx_len)
        auto_index_state["val"] += 1
        
    # 5. Format nama file — gunakan preset atau filename_format dari config
    fmt = resolve_filename_format(config)
    if not model_or_alias:
        fmt = fmt.replace("[{camera}]", "")
        fmt = fmt.replace("{camera}_", "")
        fmt = fmt.replace("{camera}", "")
        
    try:
        y, m, d = date_str.split("-")
        hh, mm, ss = time_str.split("-")
    except Exception:
        y, m, d = "1970", "01", "01"
        hh, mm, ss = "00", "00", "00"
        
    new_name = fmt.format(
        camera=model_or_alias,
        date=date_str,
        time=time_str,
        year=y,
        month=m,
        day=d,
        hour=hh,
        minute=mm,
        second=ss,
        index=idx
    ) + p.suffix
    
    new_path = p.with_name(new_name)
    
    # 6. Atasi tabrakan nama (collision)
    new_path = resolve_collision(new_path, existing_set)
    return new_path

def generate_rename_preview(files: list[Path], config: dict) -> list[tuple[Path, Path]]:
    """Menghasilkan pasangan (path_lama, path_baru) untuk 5 file pertama secara simulasi."""
    preview_list = []
    simulated_existing = set()
    detect_regex = build_detection_regex(config)
    image_exts = {x.lower() for x in config.get("supported_image_extensions", [])}
    video_exts = {x.lower() for x in config.get("supported_video_extensions", [])}
    
    for p in files[:5]:
        if already_formatted(p, config, regex=detect_regex):
            preview_list.append((p, p))
            continue
            
        try:
            new_path = compute_target_path(p, config, simulated_existing, None, image_exts, video_exts)
            preview_list.append((p, new_path))
            simulated_existing.add(new_path)
        except Exception:
            preview_list.append((p, p))
            
    return preview_list

def generate_preset_preview(file_path: Path, preset_key: str | None, config: dict) -> str:
    """
    Generate contoh nama file hasil rename untuk preset tertentu.
    Tidak melakukan rename sungguhan — hanya simulasi dengan tmp config.
    Return string nama file, atau '(preview unavailable)' jika error.
    """
    import copy
    tmp_config = copy.copy(config)
    if preset_key is None:
        tmp_config.pop("filename_preset", None)
    else:
        tmp_config["filename_preset"] = preset_key
    try:
        new_path = compute_target_path(file_path, tmp_config)
        return new_path.name
    except Exception:
        return "(preview unavailable)"

def execute_rename(files: list[Path], config: dict, session_log: Path, master_history: Path, session_ts: str):
    """Menjalankan rename secara iteratif dan mengembalikan progress generator.
    Master history ditulis sekali di akhir (batch) untuk efisiensi disk I/O.
    """
    auto_index_state = {"val": 1}
    session_targets = set()
    rename_pairs = []   # kumpulkan (new_path, old_path) untuk batch write
    
    detect_regex = build_detection_regex(config)
    image_exts = {x.lower() for x in config.get("supported_image_extensions", [])}
    video_exts = {x.lower() for x in config.get("supported_video_extensions", [])}

    try:
        for file_path in files:
            try:
                if already_formatted(file_path, config, regex=detect_regex):
                    yield ("skipped", file_path, "already changed")
                    continue

                new_path = compute_target_path(file_path, config, session_targets, auto_index_state, image_exts, video_exts)
                session_targets.add(new_path)

                # Ganti nama file fisik
                file_path.rename(new_path)

                # Catat session TXT log (per file, ringan)
                log_session_entry(session_log, new_path, file_path)

                rename_pairs.append((new_path, file_path))
                yield ("renamed", file_path, new_path)
            except Exception as e:
                yield ("error", file_path, str(e))
    finally:
        # Tulis master history JSON sekali di akhir (setelah generator exhausted)
        if rename_pairs:
            batch_log_renames(rename_pairs, master_history, session_ts, config)

def execute_restore(files: list[Path], config: dict, master_history: Path):
    """Menjalankan restore secara iteratif dan mengembalikan progress generator.
    Master history dibaca sekali dan diupdate batch di akhir.
    """
    # Baca history JSON sekali — {current_name: original_name} untuk entry ACTIVE
    history_map = build_restore_map(master_history)
    detect_regex = build_detection_regex(config)

    restored_names = []   # kumpulkan nama yang berhasil di-restore

    try:
        for file_path in files:
            if file_path.name in history_map:
                old_name = history_map[file_path.name]
                old_path = file_path.parent / old_name
                try:
                    if old_path.exists():
                        yield ("error", file_path, "File aslinya sudah tertimpa atau ada file lain dengan nama yang sama")
                        continue
                    file_path.rename(old_path)
                    restored_names.append(file_path.name)
                    yield ("restored", file_path, old_path)
                except Exception as e:
                    yield ("error", file_path, str(e))
            elif not already_formatted(file_path, config, regex=detect_regex):
                yield ("skipped_original", file_path, "sudah nama asli")
            else:
                yield ("failed_no_history", file_path, "No History")
    finally:
        # Update status JSON sekali di akhir
        if restored_names:
            batch_update_history_status(restored_names, master_history, "RESTORED")
