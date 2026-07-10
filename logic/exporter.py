import csv
import json
from pathlib import Path

def export_session_history(session_log_path: Path, output_format: str = "csv") -> Path:
    """Membaca isi berkas log sesi dan mengekspornya ke format CSV atau JSON.
    Menghasilkan berkas baru di direktori yang sama dengan ekstensi yang disesuaikan.
    """
    if not session_log_path.is_file():
        raise FileNotFoundError(f"File log sesi tidak ditemukan: {session_log_path}")
        
    records = []
    lines = session_log_path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if " -> " in line:
            parts = line.split(" -> ")
            if len(parts) == 2:
                records.append({
                    "new_name": parts[0].strip(),
                    "original_name": parts[1].strip()
                })
                
    output_format = output_format.lower().strip()
    if output_format == "csv":
        out_path = session_log_path.with_suffix(".csv")
        with out_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["new_name", "original_name"])
            for rec in records:
                writer.writerow([rec["new_name"], rec["original_name"]])
        return out_path
    elif output_format == "json":
        out_path = session_log_path.with_suffix(".json")
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(records, f, indent=4, ensure_ascii=False)
        return out_path
    else:
        raise ValueError(f"Format ekspor tidak didukung: {output_format}")
