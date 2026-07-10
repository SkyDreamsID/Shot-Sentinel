from pathlib import Path

def resolve_collision(new_path: Path, existing_set: set[Path] = None) -> Path:
    """Mengatasi collision dengan menambahkan counter akhiran (suffix counter), misal _001, _002.
    Jika existing_set diberikan, penyelesaian konflik juga akan mengecek apakah path target
    sudah direncanakan untuk digunakan oleh file lain dalam sesi ini.
    """
    if existing_set is None:
        existing_set = set()
        
    if not new_path.exists() and new_path not in existing_set:
        return new_path
        
    base_stem = new_path.stem
    suffix = new_path.suffix
    counter = 1
    
    while True:
        candidate_name = f"{base_stem}_{counter:03d}{suffix}"
        candidate_path = new_path.with_name(candidate_name)
        if not candidate_path.exists() and candidate_path not in existing_set:
            return candidate_path
        counter += 1
