"""
logic/organizer.py
--------------------
Engine Media Organizer untuk Shot Sentinel v1.0.
Memindahkan file ke folder tujuan terstruktur berdasarkan template dan metadata.
"""
import os
import shutil
import re
import time
from pathlib import Path
from colorama import Fore, Style
from logic.metadata import extract_exif, load_config_file
from logic.settings import save_config, _safe_input, clear_screen, _header

# Colors
Hijau = Fore.GREEN
Kuning = Fore.YELLOW
Merah = Fore.RED
Cyan = Fore.CYAN
Abu = Style.DIM
Reset = Style.RESET_ALL

def get_camera_no_alias(raw: str, config: dict) -> str:
    """Membersihkan model kamera tanpa lookup alias."""
    model = raw.upper()
    brand_keywords = set(config.get("brand_keywords", []))
    for brand in brand_keywords:
        model = model.replace(brand, "")
    model = model.replace(" ", "")
    model = re.sub(r'[\/\\\:\*\?\"\<\>\|]', '', model)
    model = model.strip()
    
    max_len = config.get("max_camera_length", 10)
    if len(model) > max_len:
        model = model[:max_len].strip()
        
    return model if model else config.get("unknown_camera_name", "CAM")

def pick_folder() -> str | None:
    """
    Membuka native folder picker (Windows diutamakan).
    Return string absolute path jika sukses, atau None jika gagal/dibatalkan.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()  # Sembunyikan window utama Tkinter
        
        # mustexist=False mengizinkan pengguna untuk membuat folder baru dari dalam dialog
        selected_path = filedialog.askdirectory(mustexist=False, title="Pilih Folder Tujuan")
        
        root.destroy()
        
        if selected_path:
            return selected_path
        return None
    except Exception as e:
        print(f"\n[!] Gagal memuat native folder picker: {e}")
        return None

def resolve_target_path(file_path: Path, config: dict, org_config: dict) -> Path:
    """Menghitung path tujuan absolut untuk file tertentu berdasarkan template."""
    dest_mode = org_config.get("destination_mode", "custom")
    dest_path = org_config.get("destination_path", "")
    
    if dest_mode == "custom":
        base_dir = Path(dest_path)
    elif dest_mode == "pictures":
        base_dir = Path(os.path.expandvars("%USERPROFILE%/Pictures"))
    else:  # same_folder
        base_dir = file_path.parent
        
    model_alias, date_str, time_str, has_exif = extract_exif(file_path, config)
    
    # Ambil raw model dari file
    import exifread
    raw_model = ""
    try:
        with file_path.open("rb") as f:
            tags = exifread.process_file(f, details=False)
            model_tag = tags.get("Image Model")
            if model_tag:
                raw_model = str(model_tag)
    except Exception:
        pass
        
    model_no_alias = get_camera_no_alias(raw_model, config) if raw_model else config.get("unknown_camera_name", "CAM")
    
    # Date parsing (YYYY-MM-DD)
    parts = date_str.split('-')
    year = parts[0] if len(parts) >= 1 else "Unknown"
    month = parts[1] if len(parts) >= 2 else "Unknown"
    day = parts[2] if len(parts) >= 3 else "Unknown"
    
    # File Type & Extension
    ext = file_path.suffix.lower()
    is_video = ext in config.get("supported_video_extensions", [])
    file_type = "Videos" if is_video else "Images"
    
    template = org_config.get("folder_template", "{Year}/{Month}/{CameraAlias}")
    
    rel_path = template.replace("{Year}", year)\
                       .replace("{Month}", month)\
                       .replace("{Day}", day)\
                       .replace("{Camera}", model_no_alias)\
                       .replace("{CameraAlias}", model_alias)\
                       .replace("{FileType}", file_type)\
                       .replace("{Extension}", ext.upper().strip('.'))
                       
    # Sanitasi struktur folder
    rel_parts = rel_path.replace('\\', '/').split('/')
    safe_parts = []
    for part in rel_parts:
        part = re.sub(r'[\\/:*?"<>|]', '', part)
        if part:
            safe_parts.append(part)
            
    return base_dir.joinpath(*safe_parts) / file_path.name

def resolve_conflict_rename(target_path: Path) -> Path:
    """Menyelesaikan konflik nama dengan menambahkan index numerik (contoh: foto_1.jpg)."""
    base = target_path.stem
    ext = target_path.suffix
    parent = target_path.parent
    counter = 1
    while True:
        new_path = parent / f"{base}_{counter}{ext}"
        if not new_path.exists():
            return new_path
        counter += 1

def validate_template(template: str) -> tuple[bool, str]:
    if not template.strip():
        return False, "Template cannot be empty."
        
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in invalid_chars:
        if char in template:
            return False, f"Invalid Windows path character:\n\n{char}"
            
    placeholders = re.findall(r'\{([^}]+)\}', template)
    valid_placeholders = {'Year', 'Month', 'Day', 'Camera', 'CameraAlias', 'FileType', 'Extension'}
    for p in placeholders:
        if p not in valid_placeholders:
            return False, f"Unknown placeholder:\n\n{{{p}}}"
            
    return True, ""

def render_relative_preview(template: str, metadata_map: dict) -> str:
    rel_path = template
    for placeholder, val in metadata_map.items():
        rel_path = rel_path.replace(placeholder, val)
        
    rel_parts = rel_path.replace('\\', '/').split('/')
    safe_parts = []
    for part in rel_parts:
        part = re.sub(r'[\\/:*?"<>|]', '', part)
        if part:
            safe_parts.append(part)
            
    return "/".join(safe_parts)

def render_template_preview(base_dir: Path, template: str, metadata_map: dict) -> str:
    rel_path = template
    for placeholder, val in metadata_map.items():
        rel_path = rel_path.replace(placeholder, val)
        
    rel_parts = rel_path.replace('\\', '/').split('/')
    safe_parts = []
    for part in rel_parts:
        part = re.sub(r'[\\/:*?"<>|]', '', part)
        if part:
            safe_parts.append(part)
            
    out = [f"{base_dir}\\"]
    indent = ""
    for part in safe_parts:
        out.append(f"{indent}└── {part}\\")
        indent += "    "
    return "\n".join(out)

def run_organizer_flow(files: list[Path], config: dict) -> None:
    """Flow interaktif untuk mengonfigurasi, mereview, dan mengeksekusi Media Organizer."""
    lang = config.get("language", "id")
    
    if not files:
        print(f"{Merah}[!] Tidak ada file untuk di-organize.{Reset}")
        return
        
    # Pre-flight check: Prevent Recursive Media Organization
    current_dir = files[0].parent
    sentinel_found = False
    
    while True:
        if (current_dir / ".shotsentinel").exists():
            sentinel_found = True
            break
        parent_dir = current_dir.parent
        if parent_dir == current_dir:
            break
        current_dir = parent_dir
        
    if sentinel_found:
        clear_screen()
        _header("WARNING", Fore.YELLOW)
        print("The selected folder appears to already belong to a Media Organizer destination.")
        print("Running the organizer again may create nested folder structures.\n")
        print(f"{Cyan}[1]{Reset} Cancel (Recommended)")
        print(f"{Cyan}[2]{Reset} Choose Another Folder")
        print(f"{Merah}[3]{Reset} Continue Anyway")
        
        while True:
            warn_choice = _safe_input("\nPilih [1-3]: ").strip()
            if warn_choice == "1" or not warn_choice:
                print("Operation cancelled.")
                _safe_input("\nTekan Enter untuk kembali...")
                return
            elif warn_choice == "2":
                print("Please restart the application with a different folder.")
                _safe_input("\nTekan Enter untuk keluar...")
                import sys
                sys.exit(0)
            elif warn_choice == "3":
                break
            else:
                print(f"{Merah}Pilihan tidak valid.{Reset}")

    org_config = config.get("organizer", {
        "enabled": False,
        "destination_mode": "custom",
        "destination_path": "",
        "folder_template": "{Year}/{Month}/{CameraAlias}"
    })
    
    # 1. Konfigurasi Destination Strategy jika kosong / diset custom tapi kosong
    dest_mode = org_config.get("destination_mode", "custom")
    dest_path = org_config.get("destination_path", "")
    
    while True:
        clear_screen()
        _header("MEDIA ORGANIZER CONFIG")
        
        print("Pilih Mode Lokasi Tujuan:")
        print(f"{Cyan}[1]{Reset} Custom Folder (Recommended)")
        print(f"{Cyan}[2]{Reset} Same Folder (Subfolder di lokasi asal file)")
        print(f"{Cyan}[3]{Reset} Windows Pictures Folder (%USERPROFILE%\\Pictures)")
        print(f"{Kuning}\n[E] Cancel{Reset}")
        
        mode_choice = _safe_input("\nPilih [1-3]: ").strip().upper()
        
        if not mode_choice or mode_choice == "E":
            return
            
        if mode_choice not in ["1", "2", "3"]:
            print(f"{Merah}[!] Pilihan tidak valid.{Reset}")
            continue
            
        if mode_choice == "2":
            org_config["destination_mode"] = "same"
            org_config["destination_path"] = ""
            break
        elif mode_choice == "3":
            org_config["destination_mode"] = "pictures"
            org_config["destination_path"] = ""
            break
        elif mode_choice == "1":
            org_config["destination_mode"] = "custom"
            
            custom_choice_handled = False
            while True:
                clear_screen()
                _header("CUSTOM DESTINATION")
                print("Destination Mode\n")
                print(f"{Cyan}[1]{Reset} Browse Folder (Recommended)")
                print(f"{Cyan}[2]{Reset} Manual Path")
                print(f"{Cyan}[3]{Reset} Recent Locations")
                print(f"{Kuning}\n[E] Back{Reset}\n")
                
                custom_choice = _safe_input("Select > ").strip().upper()
                
                if not custom_choice:
                    print(f"\n{Merah}Invalid selection.\nPlease choose one of the available options.{Reset}")
                    _safe_input("\nPress Enter to continue...")
                    continue
                    
                if custom_choice == "E":
                    break
                    
                recent_list = org_config.get("recent_custom_destinations", [])
                
                # Filter paths that no longer exist and remove duplicates
                valid_recent = []
                seen_lower = set()
                for rp in recent_list:
                    rp_str = str(rp).strip()
                    if not rp_str: continue
                    try:
                        rp_path = Path(rp_str)
                        if rp_path.exists():
                            rp_res = str(rp_path.resolve())
                            rp_lower = rp_res.lower()
                            if rp_lower not in seen_lower:
                                valid_recent.append(rp_res)
                                seen_lower.add(rp_lower)
                    except Exception:
                        pass
                
                org_config["recent_custom_destinations"] = valid_recent[:5]
                recent_list = org_config["recent_custom_destinations"]
                
                if custom_choice == "1":
                    print("\nMembuka Folder Picker...")
                    selected = pick_folder()
                    if selected:
                        p = Path(selected)
                        if p.is_absolute() and p.exists() and os.access(str(p), os.W_OK):
                            selected_path = str(p.resolve())
                            recent_list.insert(0, selected_path)
                            
                            # Dedup
                            final_recent = []
                            seen_l = set()
                            for r in recent_list:
                                r_l = r.lower()
                                if r_l not in seen_l:
                                    final_recent.append(r)
                                    seen_l.add(r_l)
                            org_config["recent_custom_destinations"] = final_recent[:5]
                            org_config["destination_path"] = selected_path
                            custom_choice_handled = True
                            break
                        else:
                            print(f"\n{Merah}Folder yang dipilih tidak valid atau tidak dapat ditulisi.{Reset}")
                            _safe_input("\nPress Enter to continue...")
                    else:
                        print(f"\n{Kuning}Pemilihan folder dibatalkan atau gagal.{Reset}")
                        _safe_input("\nPress Enter to continue...")
                    continue
                    
                if custom_choice == "2":
                    print(f"\nEnter absolute destination path")
                    print(f"Example:\nF:\\GALERI\\Photos\n")
                    new_path_input = _safe_input("> ").strip()
                    if not new_path_input:
                        print(f"\n{Merah}Invalid selection.\nPlease choose one of the available options.{Reset}")
                        _safe_input("\nPress Enter to continue...")
                        continue
                        
                    try:
                        p = Path(new_path_input)
                        if p.is_absolute() and p.exists() and os.access(str(p), os.W_OK):
                            selected_path = str(p.resolve())
                            recent_list.insert(0, selected_path)
                            # Dedup
                            final_recent = []
                            seen_l = set()
                            for r in recent_list:
                                r_l = r.lower()
                                if r_l not in seen_l:
                                    final_recent.append(r)
                                    seen_l.add(r_l)
                            org_config["recent_custom_destinations"] = final_recent[:5]
                            org_config["destination_path"] = selected_path
                            custom_choice_handled = True
                            break
                        else:
                            print(f"\n{Merah}Invalid path. Pastikan path absolut, ada, dan dapat ditulisi.{Reset}")
                            _safe_input("\nPress Enter to continue...")
                            continue
                    except Exception as e:
                        print(f"\n{Merah}Error: {e}{Reset}")
                        _safe_input("\nPress Enter to continue...")
                        continue
                        
                if custom_choice == "3":
                    while True:
                        clear_screen()
                        _header("RECENT LOCATIONS")
                        
                        if recent_list:
                            for idx, rp in enumerate(recent_list, 1):
                                print(f"[{idx}] {rp}")
                        else:
                            print("No recent custom destination found.")
                            
                        print(f"\n[E] Back\n")
                        
                        r_choice = _safe_input("Select > ").strip().upper()
                        
                        if not r_choice:
                            print(f"\n{Merah}Invalid selection.\nPlease choose one of the available options.{Reset}")
                            _safe_input("\nPress Enter to continue...")
                            continue
                            
                        if r_choice == "E":
                            break
                            
                        if r_choice.isdigit():
                            idx = int(r_choice)
                            if 1 <= idx <= len(recent_list):
                                selected_path = recent_list[idx-1]
                                recent_list.pop(idx-1)
                                recent_list.insert(0, selected_path)
                                org_config["recent_custom_destinations"] = recent_list
                                org_config["destination_path"] = selected_path
                                custom_choice_handled = True
                                break
                            else:
                                print(f"\n{Merah}Invalid selection.\nPlease choose one of the available options.{Reset}")
                                _safe_input("\nPress Enter to continue...")
                                continue
                                
                        print(f"\n{Merah}Invalid input.\nPlease enter a valid option.{Reset}")
                        _safe_input("\nPress Enter to continue...")
                    
                    if custom_choice_handled:
                        break
                    else:
                        continue
                
                print(f"\n{Merah}Invalid input.\nPlease enter a valid option.{Reset}")
                _safe_input("\nPress Enter to continue...")
                
            if not custom_choice_handled:
                # User typed E
                continue
            else:
                break

    # Ambil base_dir untuk preview
    first_file = files[0]
    if org_config["destination_mode"] == "custom":
        base_dir = Path(org_config["destination_path"])
    elif org_config["destination_mode"] == "pictures":
        base_dir = Path(os.path.expandvars("%USERPROFILE%/Pictures"))
    else:  # same
        base_dir = first_file.parent

    # Extract metadata dari file pertama untuk dynamic preview
    model_alias, date_str, time_str, has_exif = extract_exif(first_file, config)
    
    import exifread
    raw_model = ""
    try:
        with first_file.open("rb") as f:
            tags = exifread.process_file(f, details=False)
            model_tag = tags.get("Image Model")
            if model_tag:
                raw_model = str(model_tag)
    except Exception:
        pass
    model_no_alias = get_camera_no_alias(raw_model, config) if raw_model else config.get("unknown_camera_name", "CAM")
    
    parts = date_str.split('-')
    year = parts[0] if len(parts) >= 1 else "Unknown"
    month = parts[1] if len(parts) >= 2 else "Unknown"
    day = parts[2] if len(parts) >= 3 else "Unknown"
    
    ext = first_file.suffix.lower()
    is_video = ext in config.get("supported_video_extensions", [])
    file_type = "Videos" if is_video else "Images"
    extension_name = ext.upper().strip('.')
    
    metadata_map = {
        "{Year}": year,
        "{Month}": month,
        "{Day}": day,
        "{Camera}": model_no_alias,
        "{CameraAlias}": model_alias,
        "{FileType}": file_type,
        "{Extension}": extension_name
    }
                    
    # 2. Konfigurasi Template Struktur Folder dengan Dynamic Preview
    while True:
        clear_screen()
        _header("MEDIA ORGANIZER", Fore.BLUE)
        
        print("Destination")
        print(f"{Hijau}{base_dir}{Reset}\n")
        
        print("Templates\n")
        
        t1 = render_relative_preview("{Year}/{Month}/{CameraAlias}", metadata_map)
        print(f"{Cyan}[1]{Reset} Year / Month / Camera")
        print(f"    {t1}\n")
        
        t2 = render_relative_preview("{Year}/{Month}", metadata_map)
        print(f"{Cyan}[2]{Reset} Year / Month")
        print(f"    {t2}\n")
        
        t3 = render_relative_preview("{CameraAlias}/{Year}", metadata_map)
        print(f"{Cyan}[3]{Reset} Camera / Year")
        print(f"    {t3}\n")
        
        t4 = render_relative_preview("{Extension}/{Year}", metadata_map)
        print(f"{Cyan}[4]{Reset} File Type / Year")
        print(f"    {t4}\n")
        
        print(f"{Cyan}[5]{Reset} Custom Template\n")
        
        print(f"{Kuning}[E] Back{Reset}\n")
        
        temp_choice = _safe_input("Pilih [1-5]: ").strip().upper()
        
        if temp_choice == "E":
            return
            
        if not temp_choice or temp_choice not in ["1", "2", "3", "4", "5"]:
            print(f"\n{Merah}Invalid selection.\nPlease choose one of the available options.{Reset}")
            time.sleep(2)
            continue
            
        if temp_choice == "1":
            org_config["folder_template"] = "{Year}/{Month}/{CameraAlias}"
            break
        elif temp_choice == "2":
            org_config["folder_template"] = "{Year}/{Month}"
            break
        elif temp_choice == "3":
            org_config["folder_template"] = "{CameraAlias}/{Year}"
            break
        elif temp_choice == "4":
            org_config["folder_template"] = "{Extension}/{Year}"
            break
        elif temp_choice == "5":
            print(f"\nAvailable Variables\n")
            print("{Year}\n{Month}\n{Day}\n{Camera}\n{CameraAlias}\n{FileType}\n{Extension}")
            while True:
                print("\nTemplate")
                custom_temp = _safe_input("> ").strip()
                valid, err = validate_template(custom_temp)
                if valid:
                    org_config["folder_template"] = custom_temp
                    break
                else:
                    print(f"\n{Merah}{err}{Reset}")
            break

    # Tampilkan full folder tree setelah memilih template
    clear_screen()
    _header("MEDIA ORGANIZER", Fore.BLUE)
    print("Selected Template Preview\n")
    print(render_template_preview(base_dir, org_config["folder_template"], metadata_map))
    _safe_input("\nTekan Enter untuk melanjutkan...")
        
    # Simpan perubahan konfigurasi ke config.json
    config["organizer"] = org_config
    save_config(config)
    print(f"\n{Hijau}[OK] Konfigurasi organizer disimpan ke config.json{Reset}\n")
    
    # 3. Hitung Preview & Keamanan
    clear_screen()
    _header("MEDIA ORGANIZER PREVIEW")
    
    preview_moves = [] # list of (old_path, new_path)
    new_folders = set()
    conflicts_detected = [] # list of (old_path, target_path)
    already_organized = []
    skipped_duplicates = []
    
    print("Menganalisa struktur tujuan...")
    for f in files:
        if not f.is_file():
            continue
            
        target = resolve_target_path(f, config, org_config)
        
        # Normalize paths for comparison
        norm_source = os.path.normcase(os.path.normpath(str(f.resolve())))
        norm_target = os.path.normcase(os.path.normpath(str(target.resolve())))
        
        # 1. Identity Check (Already Organized)
        if norm_source == norm_target:
            already_organized.append(f)
            continue
            
        # 2. Prevent Nested Structures in same_folder mode
        is_nested = False
        if org_config.get("destination_mode") == "same":
            template_parts = target.parent.relative_to(f.parent).parts
            if len(template_parts) > 0 and len(f.parent.parts) >= len(template_parts):
                parent_tail = [p.lower() for p in f.parent.parts[-len(template_parts):]]
                temp_tail = [p.lower() for p in template_parts]
                if parent_tail == temp_tail:
                    already_organized.append(f)
                    is_nested = True
                    
        if is_nested:
            continue
            
        # 3. Duplicate Prevention (Identical file exists at target)
        if target.exists():
            try:
                if f.stat().st_size == target.stat().st_size:
                    skipped_duplicates.append(f)
                    continue
                else:
                    conflicts_detected.append((f, target))
            except Exception:
                conflicts_detected.append((f, target))
        else:
            new_folders.add(target.parent)
            
        preview_moves.append((f, target))
            
    # Tentukan berapa folder baru yang harus dibuat
    new_folders_to_create = [folder for folder in new_folders if not folder.exists()]
    
    # Tampilkan summary preview
    print(f"\nTotal diproses       : {Fore.CYAN}{len(files)}{Reset}")
    print(f"Sudah terorganisir   : {Hijau}{len(already_organized)}{Reset}")
    print(f"Lewati (Duplikat)    : {Kuning}{len(skipped_duplicates)}{Reset}")
    print(f"Akan dipindah        : {Fore.CYAN}{len(preview_moves)}{Reset}")
    print(f"Folder baru dibuat   : {Fore.CYAN}{len(new_folders_to_create)}{Reset}")
    print(f"Konflik nama file    : {Merah if conflicts_detected else Hijau}{len(conflicts_detected)} file{Reset}")
    
    # Preview folder list
    if new_folders_to_create:
        print("\nStruktur folder baru yang akan dibuat:")
        for folder in sorted(list(new_folders_to_create))[:5]:
            print(f"  - {folder}")
        if len(new_folders_to_create) > 5:
            print(f"  ... dan {len(new_folders_to_create) - 5} folder lainnya.")
            
    # Preview file move list
    print("\nPreview perpindahan (5 file pertama):")
    for old, new in preview_moves[:5]:
        print(f"  {old.name} -> {Hijau}{new}{Reset}")
    if len(preview_moves) > 5:
        print(f"  ... dan {len(preview_moves) - 5} file lainnya.")
        
    # 4. Konflik Penanganan
    conflict_mode = "s" # Default skip
    if conflicts_detected:
        print(f"\n{Kuning}[KONFLIK DETEKSI] Ada {len(conflicts_detected)} nama file bentrok.{Reset}")
        print("Pilih opsi penanganan konflik:")
        print("1. Skip (Lewati file bentrok)")
        print("2. Rename otomatis (Tambah angka indeks)")
        print("3. Overwrite (Timpa file lama - butuh konfirmasi tambahan)")
        
        c_choice = _safe_input("\nPilih [1-3]: ").strip()
        if c_choice == "2":
            conflict_mode = "r"
        elif c_choice == "3":
            confirm_over = _safe_input(f"{Merah}PERINGATAN: File lama akan terhapus selamanya! Yakin ingin timpa? (y/n): {Reset}").strip().lower()
            if confirm_over in ("y", "yes"):
                conflict_mode = "o"
            else:
                print("Fallback ke mode Skip.")
                conflict_mode = "s"
        else:
            conflict_mode = "s"
            
    # 5. Minta Konfirmasi Akhir
    confirm_run = _safe_input(f"\nLanjutkan proses pemindahan file? (y/n): ").strip().lower()
    if confirm_run not in ("y", "yes"):
        print(f"\n{Kuning}[BATAL] Proses pemindahan file dibatalkan oleh pengguna.{Reset}")
        _safe_input("\nTekan Enter untuk kembali...")
        return
        
    # 6. Eksekusi Pemindahan
    print(f"\nMemulai pemindahan...")
    moved_count = 0
    skipped_count = len(skipped_duplicates)
    already_organized_count = len(already_organized)
    error_count = 0
    error_details = []
    
    for old_path, target_path in preview_moves:
        try:
            target_dir = target_path.parent
            target_dir.mkdir(parents=True, exist_ok=True)
            
            final_target = target_path
            if target_path.exists():
                if conflict_mode == "s":
                    skipped_count += 1
                    continue
                elif conflict_mode == "r":
                    final_target = resolve_conflict_rename(target_path)
                elif conflict_mode == "o":
                    pass # Overwrite
                    
            # Pindahkan file
            shutil.move(str(old_path), str(final_target))
            moved_count += 1
        except Exception as e:
            error_count += 1
            error_details.append((old_path.name, str(e)))
            
    if moved_count > 0:
        import json
        import ctypes
        roots_to_mark = set()
        
        dest_mode = org_config.get("destination_mode", "custom")
        dest_path = org_config.get("destination_path", "")
        
        for old_path, target_path in preview_moves:
            if dest_mode == "custom":
                roots_to_mark.add(Path(dest_path))
            elif dest_mode == "pictures":
                roots_to_mark.add(Path(os.path.expandvars("%USERPROFILE%/Pictures")))
            else:
                roots_to_mark.add(old_path.parent)
                
        sentinel_data = {
            "app": "Shot Sentinel",
            "version": "v1.0 Final",
            "template": org_config.get("folder_template", "")
        }
        
        for root in roots_to_mark:
            sentinel_path = root / ".shotsentinel"
            if not sentinel_path.exists():
                sentinel_data["root_path"] = str(root)
                try:
                    with open(sentinel_path, "w", encoding="utf-8") as f:
                        json.dump(sentinel_data, f, indent=4)
                    if os.name == 'nt':
                        FILE_ATTRIBUTE_HIDDEN = 0x02
                        ctypes.windll.kernel32.SetFileAttributesW(str(sentinel_path), FILE_ATTRIBUTE_HIDDEN)
                except Exception:
                    pass
            
    # Tampilkan Ringkasan
    print(f"\n{Hijau}--- MEDIA ORGANIZER SUMMARY ---{Reset}")
    print(f"Processed          : {len(files)} file")
    print(f"Moved              : {moved_count} file")
    print(f"Already Organized  : {already_organized_count} file")
    print(f"Skipped            : {skipped_count} file")
    print(f"Failed             : {error_count} file")
    
    if error_details:
        print(f"\nDetail Kegagalan:")
        for name, err in error_details:
            print(f"  - {name} : {err}")
            
    _safe_input("\nTekan Enter untuk keluar...")
    import sys
    sys.exit(0)
