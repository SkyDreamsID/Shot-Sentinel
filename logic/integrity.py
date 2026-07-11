"""
logic/integrity.py
--------------------
Modul khusus untuk melakukan validasi file dan sistem secara manual.
"""
from pathlib import Path
from collections import Counter
import json

from logic.metadata import extract_exif, load_config_file
from logic.log_history import get_master_history_path, _load_history
from logic.settings import CONFIG_FILE

def run_integrity_check(files: list[Path]) -> dict:
    """
    Menjalankan berbagai pengecekan integritas pada list file yang diberikan dan sistem.
    
    Returns:
        dict berisi hasil pengecekan.
    """
    config = load_config_file()
    
    results = {
        "duplicate_filenames": [],
        "rename_conflict": [],
        "missing_exif": [],
        "invalid_date": [],
        "broken_history": 0,
        "invalid_config": False,
        "total_scanned": len(files)
    }
    
    # 1. Check Configuration
    if not CONFIG_FILE.exists():
        results["invalid_config"] = True
    else:
        try:
            json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            results["invalid_config"] = True
            
    # 2. Check Broken History
    history_path = get_master_history_path()
    active_names = set()
    try:
        h_data = _load_history(history_path)
        entries = h_data.get("history", [])
        for e in entries:
            if not e.get("id") or not e.get("original_name"):
                results["broken_history"] += 1
            if e.get("status") == "ACTIVE":
                active_names.add(e.get("current_name"))
    except Exception:
        results["broken_history"] = -1 # Corrupted
        
    # 3. File Level Checks
    filenames = [f.name for f in files]
    counts = Counter(filenames)
    results["duplicate_filenames"] = [name for name, count in counts.items() if count > 1]
    
    for f in files:
        if not f.is_file(): continue
        
        if f.name in active_names:
            results["rename_conflict"].append(f.name)
        
        try:
            model, date_str, time_str, has_exif = extract_exif(f, config)
            if not has_exif:
                results["missing_exif"].append(f.name)
            
            # Check Invalid Date (1970 is Unix epoch start, often means missing real date)
            if "1970" in date_str or "1969" in date_str or "Unknown" in date_str:
                results["invalid_date"].append(f.name)
        except Exception:
            results["missing_exif"].append(f.name)
            
    return results
