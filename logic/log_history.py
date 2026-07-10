"""
logic/log_history.py
--------------------
Master History system untuk Shot Sentinel.

Master History  : master_history.json  (JSON — internal database)
Session Log     : log/session_*.txt    (TXT — human-readable, tidak berubah)

Migrasi otomatis dari master_history.txt lama dilakukan sekali saat startup.
"""
import json
import uuid
import datetime
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HISTORY_DIR               = ROOT_DIR / "history"
SESSIONS_DIR              = HISTORY_DIR / "sessions"
MASTER_HISTORY_JSON       = HISTORY_DIR / "master_history.json"
MASTER_HISTORY_TXT_LEGACY = ROOT_DIR / "master_history.txt"   # path lama, untuk migrasi
_LEGACY_JSON_ROOT         = ROOT_DIR / "master_history.json"

# ---------------------------------------------------------------------------
# JSON internal helpers
# ---------------------------------------------------------------------------

def _load_history(path: Path) -> dict:
    """Load master_history.json. Return struktur kosong jika tidak ada atau corrupt."""
    if not path.is_file():
        return {"version": "1.0", "history": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data.get("history"), list):
            data["history"] = []
        return data
    except Exception:
        return {"version": "1.0", "history": []}

def _save_history(data: dict, path: Path) -> None:
    """Tulis master_history.json ke disk."""
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

def _make_entry(new_path: Path, old_path: Path, session_ts: str, config: dict = None) -> dict:
    """Buat satu entry history baru."""
    cam_match = re.match(r'^\[(.+?)\]', new_path.name)
    camera = cam_match.group(1) if cam_match else ""

    preset = ""
    if config:
        preset = config.get("filename_preset") or "custom"

    return {
        "id"            : uuid.uuid4().hex,
        "original_name" : old_path.name,
        "current_name"  : new_path.name,
        "status"        : "ACTIVE",
        "operation"     : "rename",
        "preset"        : preset,
        "camera"        : camera,
        "timestamp"     : _to_iso_ts(session_ts),
    }

def _to_iso_ts(ts_str: str) -> str:
    """Konversi session_ts lama 'DD-MM-YYYY_HHMMSS' atau 'YYYY-MM-DD_HH-MM-SS' ke ISO 8601."""
    try:
        date_part, time_part = ts_str.split('_', 1)
        parts = date_part.split('-')
        if len(parts[0]) == 4:
            # Format baru YYYY-MM-DD
            y, m, d = parts
        else:
            # Format lama DD-MM-YYYY
            d, m, y = parts
        t = time_part.replace('-', '')
        h, mi, s = t[:2], t[2:4], t[4:6]
        return f"{y}-{m}-{d}T{h}:{mi}:{s}"
    except Exception:
        return ts_str

# ---------------------------------------------------------------------------
# Public API — Master History (JSON)
# ---------------------------------------------------------------------------

def get_master_history_path() -> Path:
    """
    Return path ke history/master_history.json.
    Jika belum ada, auto-migrasi dari TXT lama / JSON root lama atau buat file baru kosong.
    """
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    if not MASTER_HISTORY_JSON.is_file():
        if _LEGACY_JSON_ROOT.is_file():
            import shutil
            try:
                shutil.move(str(_LEGACY_JSON_ROOT), str(MASTER_HISTORY_JSON))
                print(f"[OK] master_history.json dipindahkan ke history/")
            except Exception as e:
                print(f"[WARNING] Gagal memindahkan master_history.json ke history/: {e}")
        elif MASTER_HISTORY_TXT_LEGACY.is_file():
            _migrate_txt_to_json(MASTER_HISTORY_TXT_LEGACY, MASTER_HISTORY_JSON)
        else:
            _save_history({"version": "1.0", "history": []}, MASTER_HISTORY_JSON)
    return MASTER_HISTORY_JSON

def log_rename(new_path: Path, old_path: Path, history_file: Path, session_ts: str, config: dict = None) -> None:
    """
    Append satu entry rename ke master history JSON.
    Untuk banyak file sekaligus, pakai batch_log_renames() agar lebih efisien.
    """
    data = _load_history(history_file)
    data["history"].append(_make_entry(new_path, old_path, session_ts, config))
    _save_history(data, history_file)

def batch_log_renames(pairs: list, history_file: Path, session_ts: str, config: dict = None) -> None:
    """
    Append banyak entry rename dalam satu siklus baca-tulis.
    pairs: list of (new_path: Path, old_path: Path)
    """
    if not pairs:
        return
    data = _load_history(history_file)
    for new_path, old_path in pairs:
        data["history"].append(_make_entry(new_path, old_path, session_ts, config))
    _save_history(data, history_file)

def build_restore_map(history_file: Path) -> dict:
    """
    Return dict {current_name: original_name} untuk semua entry ACTIVE.
    Dipakai oleh execute_restore() di worker.py.
    """
    data = _load_history(history_file)
    result = {}
    for entry in data.get("history", []):
        if entry.get("status") == "ACTIVE":
            result[entry["current_name"]] = entry["original_name"]
    return result

def update_history_status(new_name: str, history_file: Path, new_status: str) -> None:
    """
    Update status entry ACTIVE paling baru yang cocok dengan new_name.
    Untuk update banyak sekaligus, pakai batch_update_history_status().
    """
    data = _load_history(history_file)
    for entry in reversed(data["history"]):
        if entry.get("current_name") == new_name and entry.get("status") == "ACTIVE":
            entry["status"] = new_status
            break
    _save_history(data, history_file)

def batch_update_history_status(names: list, history_file: Path, new_status: str) -> None:
    """
    Update status banyak entry dalam satu siklus baca-tulis.
    Setiap nama hanya mengupdate satu entry ACTIVE paling baru yang cocok.
    """
    if not names:
        return
    data = _load_history(history_file)
    names_set = set(names)
    updated = set()
    for entry in reversed(data["history"]):
        name = entry.get("current_name")
        if name in names_set and name not in updated and entry.get("status") == "ACTIVE":
            entry["status"] = new_status
            updated.add(name)
            if updated == names_set:
                break
    _save_history(data, history_file)

def get_rename_count(history_file: Path) -> int:
    """Hitung total entry di master_history.json (untuk Easter Egg milestone)."""
    data = _load_history(history_file)
    return len(data.get("history", []))

# ---------------------------------------------------------------------------
# Public API — Session Log (TXT, tidak berubah)
# ---------------------------------------------------------------------------

def log_session_entry(session_log: Path, new_path: Path, old_path: Path) -> None:
    """Append satu baris ke session TXT log. Format: 'new_name -> old_name'."""
    line = f"{new_path.name} -> {old_path.name}\n"
    with session_log.open("a", encoding="utf-8") as f:
        f.write(line)

def remove_session_entry(new_name: str, session_log: Path) -> None:
    """Hapus baris dari session TXT log berdasarkan new_name."""
    if not session_log.is_file():
        return
    lines = session_log.read_text(encoding="utf-8").splitlines()
    filtered = [ln for ln in lines if not ln.startswith(new_name + " -> ")]
    session_log.write_text("\n".join(filtered) + "\n", encoding="utf-8")

def create_session_log(op_type: str = "rename") -> Path:
    """Buat file session TXT log baru di folder history/sessions/.
    op_type: "rename" atau "restore"
    """
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_file = SESSIONS_DIR / f"{op_type}_{timestamp}.txt"
    session_file.touch(exist_ok=True)
    return session_file

def find_latest_history_file() -> Path:
    """
    Cari file session TXT terbaru di folder history/sessions/ (dan fallback ke log/).
    Mendukung:
      - rename_YYYYMMDD_HHMMSS.txt / restore_YYYYMMDD_HHMMSS.txt
      - session_YYYY-MM-DD_HH-MM-SS.txt
      - DD-MM-YYYY_HHMMSS.txt
    """
    search_dirs = []
    if SESSIONS_DIR.is_dir():
        search_dirs.append(SESSIONS_DIR)
    legacy_log = ROOT_DIR / "log"
    if legacy_log.is_dir():
        search_dirs.append(legacy_log)

    if not search_dirs:
        raise FileNotFoundError("Tidak ada folder riwayat log yang ditemukan")

    re_op = re.compile(r"^(?:rename|restore)_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})$")
    re_session = re.compile(r"^session_(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})$")
    re_old = re.compile(r"^(\d{2})-(\d{2})-(\d{4})_(\d{2})(\d{2})(\d{2})$")

    candidate_files = []
    for directory in search_dirs:
        for f in directory.iterdir():
            if f.is_file() and f.suffix == ".txt":
                stem = f.stem

                m_op = re_op.match(stem)
                if m_op:
                    try:
                        y, m, d, hh, mm, ss = map(int, m_op.groups())
                        dt = datetime.datetime(y, m, d, hh, mm, ss)
                        candidate_files.append((dt, f))
                    except ValueError:
                        pass
                    continue

                m_session = re_session.match(stem)
                if m_session:
                    try:
                        y, m, d, hh, mm, ss = map(int, m_session.groups())
                        dt = datetime.datetime(y, m, d, hh, mm, ss)
                        candidate_files.append((dt, f))
                    except ValueError:
                        pass
                    continue

                m_old = re_old.match(stem)
                if m_old:
                    try:
                        d, m, y, hh, mm, ss = map(int, m_old.groups())
                        dt = datetime.datetime(y, m, d, hh, mm, ss)
                        candidate_files.append((dt, f))
                    except ValueError:
                        pass
                    continue

    if not candidate_files:
        raise FileNotFoundError("Tidak ada file riwayat log .txt yang ditemukan.")

    return sorted(candidate_files, key=lambda x: x[0], reverse=True)[0][1]

# ---------------------------------------------------------------------------
# Migration: TXT -> JSON (otomatis, sekali jalan)
# ---------------------------------------------------------------------------

def _migrate_txt_to_json(txt_path: Path, json_path: Path) -> None:
    """
    Konversi master_history.txt lama ke master_history.json.

    Format TXT lama (pipe-delimited):
        DD-MM-YYYY_HHMMSS|new_name|old_name|STATUS

    Format TXT jadul (bracket):
        [DD-MM-YYYY HH:MM:SS] new_name -> old_name

    Setelah sukses: TXT lama di-rename ke master_history_backup.txt (tidak dihapus).
    Jika migrasi gagal: partial JSON dihapus, TXT tetap utuh.
    """
    entries = []
    try:
        lines = txt_path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "|" in line:
                # Format pipe-delimited (format utama)
                parts = line.split("|")
                if len(parts) == 4:
                    ts, new_name, old_name, status = parts
                    cam_match = re.match(r'^\[(.+?)\]', new_name.strip())
                    entries.append({
                        "id"            : uuid.uuid4().hex,
                        "original_name" : old_name.strip(),
                        "current_name"  : new_name.strip(),
                        "status"        : status.strip(),
                        "operation"     : "rename",
                        "preset"        : "",
                        "camera"        : cam_match.group(1) if cam_match else "",
                        "timestamp"     : _to_iso_ts(ts.strip()),
                    })

            elif '] ' in line and ' -> ' in line:
                # Format bracket jadul
                try:
                    ts_part, rest = line.split('] ', 1)
                    ts = ts_part.lstrip('[')
                    new_name, old_name = [s.strip() for s in rest.split(' -> ', 1)]
                    cam_match = re.match(r'^\[(.+?)\]', new_name)
                    entries.append({
                        "id"            : uuid.uuid4().hex,
                        "original_name" : old_name,
                        "current_name"  : new_name,
                        "status"        : "ACTIVE",
                        "operation"     : "rename",
                        "preset"        : "",
                        "camera"        : cam_match.group(1) if cam_match else "",
                        "timestamp"     : ts,
                    })
                except Exception:
                    continue

        data = {"version": "1.0", "history": entries}
        _save_history(data, json_path)

        # Backup TXT lama — jangan dihapus
        backup_path = txt_path.parent / "master_history_backup.txt"
        if backup_path.exists():
            backup_path.unlink()
        txt_path.rename(backup_path)

        print(f"[OK] Migrasi master history selesai: {len(entries)} entri.")
        print(f"     Backup: {backup_path.name}")

    except Exception as e:
        print(f"[WARNING] Migrasi master history gagal: {e}")
        if json_path.is_file():
            try:
                json_path.unlink()
            except Exception:
                pass
