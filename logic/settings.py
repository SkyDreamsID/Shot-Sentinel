"""
logic/settings.py
-----------------
Settings menu untuk Shot Sentinel v1.0 Final.
Berisi fungsi-fungsi untuk mengelola pengaturan yang dapat diubah user
langsung dari program tanpa edit config/ manual.
"""
import os
import json
from pathlib import Path
from colorama import Fore, Style

from .metadata import FILENAME_PRESETS, CONFIG_FILE, DEFAULT_CONFIG, load_alias_file, save_alias_file
from .worker import generate_preset_preview
from .version import HEADER_TEXT, SEP_LEN

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ---------------------------------------------------------------------------
# String UI Bilingual
# ---------------------------------------------------------------------------

_UI = {
    "id": {
        "settings_header"     : "PENGATURAN",
        "settings_prompt"     : "Pilih",
        "opt_language"        : "[1] Bahasa",
        "opt_preset"          : "[2] Preset Nama File",
        "opt_alias"           : "[3] Camera Alias",
        "opt_username"        : "[4] Username",
        "opt_cam_name"        : "[5] Unknown Camera Alias",
        "opt_csv"             : "[6] Export CSV",
        "opt_reset"           : "[7] Reset ke Default",
        "opt_back"            : "[E] Kembali",
        "invalid"             : "[!] Pilihan tidak valid, coba lagi.",
        "saved"               : "[OK] Pengaturan disimpan.",
        "cancelled"           : "[Batal] Tidak ada perubahan.",
        # Language menu
        "lang_header"         : "BAHASA",
        "lang_current"        : "Bahasa saat ini",
        "lang_opt1"           : "[1] Bahasa Indonesia",
        "lang_opt2"           : "[2] Bahasa Inggris",
        "lang_back"           : "[E] Kembali",
        "lang_changed"        : "[OK] Bahasa diubah ke",
        # Preset menu
        "preset_header"       : "PRESET NAMA FILE",
        "preset_current"      : "Preset saat ini",
        "preset_preview_file" : "Preview File",
        "preset_no_preview"   : "(No preview available)",
        "preset_custom_note"  : "Preset lanjutan untuk pengguna yang ingin membuat format\n     nama file sendiri melalui config.json.",
        "preset_back"         : "[E] Kembali",
        "preset_changed"      : "[OK] Preset diubah ke",
        "preset_custom_set"   : "[OK] Mode custom aktif (menggunakan filename_format).",
        # CSV menu
        "csv_header"          : "EXPORT CSV",
        "csv_current"         : "Status saat ini",
        "csv_active"          : "Aktif",
        "csv_inactive"        : "Tidak aktif",
        "csv_opt1"            : "[1] Nyalakan",
        "csv_opt2"            : "[2] Matikan",
        "csv_back"            : "[E] Kembali",
        "csv_changed"         : "[OK] Export CSV diubah ke",
        # Unknown camera menu
        "cam_header"          : "UNKNOWN CAMERA ALIAS",
        "cam_current"         : "Alias saat ini",
        "cam_options"         : "Pilihan alias:",
        "cam_prompt"          : "Masukkan alias baru (maks 10 karakter)",
        "cam_empty"           : "[!] Nama tidak boleh kosong.",
        "cam_changed"         : "[OK] Unknown Camera Alias diubah ke",
        "cam_register"        : "[R] Tambah alias baru",
        "cam_delete"          : "[D] Hapus alias",
        "cam_back"            : "[E] Kembali",
        "cam_limit"           : "[!] Batas tercapai! Maksimal 10 alias diperbolehkan.",
        "cam_invalid_char"    : "[!] Nama tidak valid. Hanya huruf dan angka.",
        "cam_already_exists"  : "Sudah ada di daftar. Dipilih sebagai alias aktif.",
        "cam_registered"      : "[OK] Terdaftar dan dipilih:",
        "cam_protected"       : "[!] Protected: tidak bisa dihapus.",
        "cam_delete_title"    : "Pilih nomor yang ingin dihapus:",
        "cam_delete_confirm"  : "Yakin hapus '{name}'? (y/n): ",
        "cam_delete_ok"       : "[OK] Berhasil dihapus.",
        "cam_delete_cancel"   : "Penghapusan dibatalkan.",
        # Reset menu
        "reset_header"        : "RESET PENGATURAN",
        "reset_warning"       : "[!] Pengaturan akan dikembalikan ke nilai awal.",
        "reset_confirm"       : "Yakin? (y/n)",
        "reset_done"          : "[OK] Pengaturan berhasil direset.",
        "reset_cancelled"     : "[Batal] Reset dibatalkan.",
        # Alias menu
        "alias_header"        : "CAMERA ALIAS",
        "alias_count"         : "Camera Alias",
        "alias_no_entry"      : "(Tidak ada alias tersimpan)",
        "alias_col_no"        : "No",
        "alias_col_brand"     : "Brand",
        "alias_col_model"     : "Camera Model",
        "alias_col_alias"     : "Alias",
        "alias_opt_add"       : "[1] Tambah Alias",
        "alias_opt_edit"      : "[2] Edit Alias",
        "alias_opt_del"       : "[3] Hapus Alias",
        "alias_opt_back"      : "[E] Kembali",
        "alias_prompt_model"  : "Masukkan nama model kamera\n(contoh: NIKOND3300, CANONEOSRP, SONYA7III)\n>> ",
        "alias_suggest"       : "Saran Alias",
        "alias_prompt_alias"  : "Masukkan Alias\n(Disarankan {suggest})\n>> ",
        "alias_prompt_no"     : "Masukkan nomor",
        "alias_prompt_edit"   : "Masukkan Alias Baru [{old}]: ",
        "alias_err_empty"     : "[!] Input tidak boleh kosong.",
        "alias_err_duplicate" : "[!] Alias untuk Camera Model tersebut sudah ada.",
        "alias_err_invalid_char": "[!] Alias hanya boleh berisi huruf, angka, dan spasi.",
        "alias_err_not_found" : "[!] Nomor tidak valid.",
        "alias_added"         : "[OK] berhasil ditambahkan.",
        "alias_edited"        : "[OK] berhasil diperbarui.",
        "alias_deleted"       : "[OK] berhasil dihapus.",
        # Username menu
        "username_header"     : "EDIT USERNAME",
        "username_current"    : "Username saat ini",
        "username_rules"      : "Aturan:",
        "username_rule1"      : "- 3-16 karakter",
        "username_rule2"      : "- Huruf, angka, & underscore (_)",
        "username_rule3"      : "- Tanpa spasi & karakter khusus",
        "username_prompt"     : "Masukkan Username baru: ",
        "username_empty"      : "[!] Input tidak boleh kosong.",
        "username_len"        : "[!] Username harus berukuran 3-16 karakter.",
        "username_invalid"    : "[!] Username hanya boleh berisi huruf, angka, dan underscore (_).",
        "username_ok"         : "[OK] Username berhasil diubah ke: ",
        # Preview settings
        "settings_preview"      : "Konfigurasi Saat Ini",
        "settings_language"     : "Bahasa",
        "settings_preset_label" : "Preset",
        "settings_csv_label"    : "Export CSV",
        "settings_unknown"      : "Unknown Camera",
        "settings_custom"       : "Custom",
        "settings_on"           : "Aktif",
        "settings_off"          : "Tidak aktif",
        "settings_format"       : "Format",
        # Press enter
        "press_continue"      : "\nTekan Enter untuk melanjutkan...",
    },
    "en": {
        "settings_header"     : "SETTINGS",
        "settings_prompt"     : "Select",
        "opt_language"        : "[1] Language",
        "opt_preset"          : "[2] Filename Preset",
        "opt_alias"           : "[3] Camera Alias",
        "opt_username"        : "[4] Username",
        "opt_cam_name"        : "[5] Unknown Camera Alias",
        "opt_csv"             : "[6] CSV Export",
        "opt_reset"           : "[7] Reset to Default",
        "opt_back"            : "[E] Back",
        "invalid"             : "[!] Invalid choice, try again.",
        "saved"               : "[OK] Settings saved.",
        "cancelled"           : "[Cancel] No changes made.",
        # Language menu
        "lang_header"         : "LANGUAGE",
        "lang_current"        : "Current language",
        "lang_opt1"           : "[1] Bahasa Indonesia",
        "lang_opt2"           : "[2] English",
        "lang_back"           : "[E] Back",
        "lang_changed"        : "[OK] Language changed to",
        # Preset menu
        "preset_header"       : "FILENAME PRESET",
        "preset_current"      : "Current preset",
        "preset_preview_file" : "Preview File",
        "preset_no_preview"   : "(No preview available)",
        "preset_custom_note"  : "Advanced preset for users who want to define\n     their own filename format via config.json.",
        "preset_back"         : "[E] Back",
        "preset_changed"      : "[OK] Preset changed to",
        "preset_custom_set"   : "[OK] Custom mode active (using filename_format).",
        # CSV menu
        "csv_header"          : "CSV EXPORT",
        "csv_current"         : "Current status",
        "csv_active"          : "Enabled",
        "csv_inactive"        : "Disabled",
        "csv_opt1"            : "[1] Enable",
        "csv_opt2"            : "[2] Disable",
        "csv_back"            : "[E] Back",
        "csv_changed"         : "[OK] CSV export changed to",
        # Unknown camera menu
        "cam_header"          : "UNKNOWN CAMERA ALIAS",
        "cam_current"         : "Current alias",
        "cam_options"         : "Alias options:",
        "cam_prompt"          : "Enter new alias (max 10 chars)",
        "cam_empty"           : "[!] Name cannot be empty.",
        "cam_changed"         : "[OK] Unknown Camera Alias changed to",
        "cam_register"        : "[R] Register new alias",
        "cam_delete"          : "[D] Delete alias",
        "cam_back"            : "[E] Back",
        "cam_limit"           : "[!] Limit reached! Maximum 10 entries allowed.",
        "cam_invalid_char"    : "[!] Invalid name. Only letters and numbers are allowed.",
        "cam_already_exists"  : "Already in list. Selected as current alias.",
        "cam_registered"      : "[OK] Registered and selected:",
        "cam_protected"       : "[!] Protected: cannot be deleted.",
        "cam_delete_title"    : "Select entry number to delete:",
        "cam_delete_confirm"  : "Are you sure you want to delete '{name}'? (y/n): ",
        "cam_delete_ok"       : "[OK] Deleted successfully.",
        "cam_delete_cancel"   : "Deletion cancelled.",
        # Reset menu
        "reset_header"        : "RESET SETTINGS",
        "reset_warning"       : "[!] All settings will be restored to default values.",
        "reset_confirm"       : "Are you sure? (y/n)",
        "reset_done"          : "[OK] Settings have been reset.",
        "reset_cancelled"     : "[Cancel] Reset cancelled.",
        # Alias menu
        "alias_header"        : "CAMERA ALIAS",
        "alias_count"         : "Camera Alias",
        "alias_no_entry"      : "(No aliases stored)",
        "alias_col_no"        : "No",
        "alias_col_brand"     : "Brand",
        "alias_col_model"     : "Camera Model",
        "alias_col_alias"     : "Alias",
        "alias_opt_add"       : "[1] Add Alias",
        "alias_opt_edit"      : "[2] Edit Alias",
        "alias_opt_del"       : "[3] Delete Alias",
        "alias_opt_back"      : "[E] Back",
        "alias_prompt_model"  : "Enter camera model name\n(example: NIKOND3300, CANONEOSRP, SONYA7III)\n>> ",
        "alias_suggest"       : "Suggested Alias",
        "alias_prompt_alias"  : "Enter Alias\n(Suggested {suggest})\n>> ",
        "alias_prompt_no"     : "Enter number",
        "alias_prompt_edit"   : "Enter New Alias [{old}]: ",
        "alias_err_empty"     : "[!] Input cannot be empty.",
        "alias_err_duplicate" : "[!] Alias for this Camera Model already exists.",
        "alias_err_invalid_char": "[!] Alias can only contain letters, numbers, and spaces.",
        "alias_err_not_found" : "[!] Invalid number.",
        "alias_added"         : "[OK] successfully added.",
        "alias_edited"        : "[OK] successfully updated.",
        "alias_deleted"       : "[OK] successfully deleted.",
        # Username menu
        "username_header"     : "EDIT USERNAME",
        "username_current"    : "Current username",
        "username_rules"      : "Rules:",
        "username_rule1"      : "- 3-16 characters",
        "username_rule2"      : "- Letters, numbers, & underscore (_)",
        "username_rule3"      : "- No spaces & special characters",
        "username_prompt"     : "Enter new Username: ",
        "username_empty"      : "[!] Input cannot be empty.",
        "username_len"        : "[!] Username must be 3-16 characters.",
        "username_invalid"    : "[!] Username can only contain letters, numbers, and underscore (_).",
        "username_ok"         : "[OK] Username changed to: ",
        # Preview settings
        "settings_preview"      : "Current Configuration",
        "settings_language"     : "Language",
        "settings_preset_label" : "Preset",
        "settings_csv_label"    : "CSV Export",
        "settings_unknown"      : "Unknown Camera",
        "settings_custom"       : "Custom",
        "settings_on"           : "Enabled",
        "settings_off"          : "Disabled",
        "settings_format"       : "Format",
        # Press enter
        "press_continue"      : "\nPress Enter to continue...",
    },
}

# Urutan preset yang ditampilkan di menu
_PRESET_KEYS = ["default", "datetime_only", "camera_datetime", "date_index", "alias_index", "username_index"]

# Brand detection untuk tampilan tabel alias (display-only)
_BRAND_DISPLAY = [
    ("NIKON",     "Nikon"),
    ("CANON",     "Canon"),
    ("SONY",      "Sony"),
    ("FUJIFILM",  "Fujifilm"),
    ("PANASONIC", "Panasonic"),
    ("OLYMPUS",   "Olympus"),
    ("LEICA",     "Leica"),
    ("PENTAX",    "Pentax"),
    ("SIGMA",     "Sigma"),
]

def _detect_brand(model_key: str) -> str:
    """Deteksi brand dari nama model kamera untuk tampilan tabel. Display-only."""
    key = model_key.upper()
    for prefix, name in _BRAND_DISPLAY:
        if key.startswith(prefix):
            return name
    return "Unknown"

# Regex untuk validasi alias: hanya huruf, angka, spasi. Tidak boleh kosong.
import re
_ALIAS_RE = re.compile(r"^[A-Za-z0-9 ]+$")

# Prefix brand untuk saran alias
_SUGGEST_PREFIXES = ["NIKON", "CANON", "SONY", "FUJIFILM", "PANASONIC", "OLYMPUS", "LEICA", "PENTAX", "SIGMA"]

def _generate_alias_suggestion(model_key: str) -> str:
    """Hapus prefix brand dari model kamera untuk saran alias."""
    key_upper = model_key.upper()
    for prefix in _SUGGEST_PREFIXES:
        if key_upper.startswith(prefix):
            suggestion = model_key[len(prefix):]
            if suggestion:
                return suggestion
    return model_key

# ---------------------------------------------------------------------------
# Config I/O
# ---------------------------------------------------------------------------

def save_config(config: dict) -> bool:
    """
    Tulis ulang config/config.json dari dict config yang diberikan.
    Mengembalikan True jika berhasil, False jika gagal.
    """
    try:
        CONFIG_FILE.parent.mkdir(exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(config, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Gagal menyimpan config: {e}{Style.RESET_ALL}")
        return False

# ---------------------------------------------------------------------------
# Helper kecil
# ---------------------------------------------------------------------------

def _t(lang: str, key: str) -> str:
    """Ambil string UI sesuai bahasa. Fallback ke 'id' kalau key tidak ada."""
    return _UI.get(lang, _UI["id"]).get(key, _UI["id"].get(key, key))

def _header(title: str, color: str = Fore.BLUE):
    clear_screen()
    header = f"{HEADER_TEXT}"
    border = "=" * len(header)
    print(f"\n{border}")
    print(f"{header}")
    print(f"{border}")
    print(f"\n{color}{Style.BRIGHT}[{title}]{Style.RESET_ALL}")

def _safe_input(prompt: str) -> str:
    """Input yang aman dari EOFError."""
    try:
        return input(prompt).strip()
    except EOFError:
        return ""

def _is_back(choice: str) -> bool:
    """Cek apakah input adalah perintah kembali/batal (e, E, atau Enter)."""
    return choice.lower() == "e" or choice == ""

# ---------------------------------------------------------------------------
# Submenu: Bahasa / Language
# ---------------------------------------------------------------------------

def language_menu(config: dict, lang: str) -> dict:
    _header(_t(lang, "lang_header"))
    current_name = "Bahasa Indonesia" if config.get("language", "id") == "id" else "English"
    print(f"{_t(lang, 'lang_current')}: {Fore.YELLOW}{current_name}{Style.RESET_ALL}\n")
    print(_t(lang, "lang_opt1"))
    print(_t(lang, "lang_opt2"))
    print(f"\n{Fore.YELLOW}{_t(lang, 'lang_back')}{Style.RESET_ALL}")

    choice = _safe_input(f"\n{_t(lang, 'settings_prompt')}: ")
    if choice == "1":
        config["language"] = "id"
        save_config(config)
        print(f"{_t(lang, 'lang_changed')} Bahasa Indonesia")
    elif choice == "2":
        config["language"] = "en"
        save_config(config)
        print(f"{_t(lang, 'lang_changed')} English")
    elif _is_back(choice):
        pass
    else:
        print(f"{_t(lang, 'invalid')}")
    return config

# ---------------------------------------------------------------------------
# Submenu: Preset Nama File (dengan dynamic preview)
# ---------------------------------------------------------------------------

def filename_preset_menu(config: dict, lang: str, preview_file=None) -> dict:
    _header(_t(lang, "preset_header"))

    current = config.get("filename_preset")
    current_display = current if current is not None else _t(lang, "settings_custom")

    # Tampilkan info file preview
    if preview_file is not None:
        print(f"{_t(lang, 'preset_preview_file')} : {Fore.CYAN}{preview_file.name}{Style.RESET_ALL}")
    else:
        print(f"{_t(lang, 'preset_preview_file')} : {Style.DIM}{_t(lang, 'preset_no_preview')}{Style.RESET_ALL}")

    print(f"{_t(lang, 'preset_current')} : {Fore.YELLOW}{current_display}{Style.RESET_ALL}\n")

    # Tampilkan setiap preset dengan contoh dinamis
    for i, preset_key in enumerate(_PRESET_KEYS, start=1):
        marker = f"{Fore.GREEN}*{Style.RESET_ALL} " if preset_key == current else "  "
        print(f"{marker}[{i}] {preset_key}")
        if preview_file is not None:
            example = generate_preset_preview(preview_file, preset_key, config)
        else:
            example = FILENAME_PRESETS.get(preset_key, "")
        print(f"     {Fore.CYAN}{example}{Style.RESET_ALL}")
        print()

    # Custom mode (pilihan [7])
    custom_num = len(_PRESET_KEYS) + 1  # 7
    custom_marker = f"{Fore.GREEN}*{Style.RESET_ALL} " if current is None else "  "
    print(f"{custom_marker}[{custom_num}] Custom (config.json)")
    print(f"     {Style.DIM}{_t(lang, 'preset_custom_note')}{Style.RESET_ALL}")
    print(f"\n  {Fore.YELLOW}{_t(lang, 'preset_back')}{Style.RESET_ALL}")

    choice = _safe_input(f"\n{_t(lang, 'settings_prompt')}: ")

    valid_preset_choices = {str(i+1): key for i, key in enumerate(_PRESET_KEYS)}

    if choice in valid_preset_choices:
        selected_key = valid_preset_choices[choice]
        config["filename_preset"] = selected_key
        save_config(config)
        print(f"{_t(lang, 'preset_changed')} {selected_key}")

    elif choice == str(custom_num):
        config.pop("filename_preset", None)
        save_config(config)
        print(f"{_t(lang, 'preset_custom_set')}")

    elif _is_back(choice):
        pass

    else:
        print(f"{_t(lang, 'invalid')}")

    return config

# ---------------------------------------------------------------------------
# Submenu: CSV Export
# ---------------------------------------------------------------------------

def csv_menu(config: dict, lang: str) -> dict:
    _header(_t(lang, "csv_header"))
    active = config.get("export_csv", False)
    status_str = _t(lang, "csv_active") if active else _t(lang, "csv_inactive")
    status_color = Fore.GREEN if active else Fore.RED
    print(f"{_t(lang, 'csv_current')}: {status_color}{status_str}{Style.RESET_ALL}\n")
    print(f"{Fore.GREEN}{_t(lang, 'csv_opt1')}{Style.RESET_ALL}")
    print(f"{Fore.RED}{_t(lang, 'csv_opt2')}{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}{_t(lang, 'csv_back')}{Style.RESET_ALL}")

    choice = _safe_input(f"\n{_t(lang, 'settings_prompt')}: ")
    if choice == "1":
        config["export_csv"] = True
        save_config(config)
        print(f"{Fore.GREEN}{_t(lang, 'csv_changed')} {_t(lang, 'csv_active')}{Style.RESET_ALL}")
    elif choice == "2":
        config["export_csv"] = False
        save_config(config)
        print(f"{Fore.YELLOW}{_t(lang, 'csv_changed')} {_t(lang, 'csv_inactive')}{Style.RESET_ALL}")
    elif _is_back(choice):
        pass
    else:
        print(f"{Fore.YELLOW}{_t(lang, 'invalid')}{Style.RESET_ALL}")
    return config

# ---------------------------------------------------------------------------
# Submenu: Nama Kamera Tidak Dikenal
# ---------------------------------------------------------------------------

def unknown_camera_menu(config: dict, lang: str) -> dict:
    import time
    while True:
        _header(_t(lang, "cam_header"))

        # Load the list of aliases from config, fallback to default
        cam_list = config.get("unknown_camera_list")
        if not cam_list or not isinstance(cam_list, list):
            cam_list = ["CAM", "UNKNOWN", "NOEXIF", "MISC"]
            config["unknown_camera_list"] = cam_list
            save_config(config)

        current = config.get("unknown_camera_name", "CAM")

        print(f"{_t(lang, 'cam_current')}: {Fore.YELLOW}{current}{Style.RESET_ALL}\n")
        print(f"{_t(lang, 'cam_options')}")

        # Display selection options
        for i, name in enumerate(cam_list, start=1):
            marker = f"{Fore.GREEN}*{Style.RESET_ALL} " if name == current else "  "
            perm_text = f" {Style.DIM}(Protected){Style.RESET_ALL}" if name in ("CAM", "NOEXIF") else ""
            print(f"{marker}[{i}] {name}{perm_text}")

        print()
        print(f"  {Fore.CYAN}{_t(lang, 'cam_register')}{Style.RESET_ALL}")
        print(f"  {Fore.RED}{_t(lang, 'cam_delete')}{Style.RESET_ALL}")
        print(f"\n  {Fore.YELLOW}{_t(lang, 'cam_back')}{Style.RESET_ALL}")

        choice = _safe_input(f"\n{_t(lang, 'settings_prompt')}: ").strip()
        choice_lower = choice.lower()

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(cam_list):
                selected = cam_list[idx]
                config["unknown_camera_name"] = selected
                save_config(config)
                print(f"{Fore.GREEN}{_t(lang, 'cam_changed')} {selected}{Style.RESET_ALL}")
                time.sleep(1)
            else:
                print(f"{Fore.RED}{_t(lang, 'invalid')}{Style.RESET_ALL}")
                time.sleep(1)

        elif choice_lower == "r":
            # Check maximum limit of 10 entries total
            if len(cam_list) >= 10:
                print(f"{Fore.RED}{_t(lang, 'cam_limit')}{Style.RESET_ALL}")
                time.sleep(2)
                continue

            prompt = _t(lang, "cam_prompt") + ": "
            raw = _safe_input(prompt).strip().upper()
            if not raw:
                print(f"{Fore.RED}{_t(lang, 'cam_empty')}{Style.RESET_ALL}")
                time.sleep(1)
                continue

            # Validate: alphanumeric only, up to 10 chars
            import re as _re
            clean_name = _re.sub(r'[^A-Z0-9]', '', raw)[:10]
            if not clean_name:
                print(f"{Fore.RED}{_t(lang, 'cam_invalid_char')}{Style.RESET_ALL}")
                time.sleep(1)
                continue

            if clean_name in cam_list:
                config["unknown_camera_name"] = clean_name
                save_config(config)
                print(f"{Fore.GREEN}{clean_name} — {_t(lang, 'cam_already_exists')}{Style.RESET_ALL}")
            else:
                cam_list.append(clean_name)
                config["unknown_camera_list"] = cam_list
                config["unknown_camera_name"] = clean_name
                save_config(config)
                print(f"{Fore.GREEN}{_t(lang, 'cam_registered')} {clean_name}{Style.RESET_ALL}")

            time.sleep(1.5)

        elif choice_lower == "d":
            print(f"\n{_t(lang, 'cam_delete_title')}")
            for i, name in enumerate(cam_list, start=1):
                is_perm = name in ("CAM", "NOEXIF")
                suffix = f" {Style.DIM}(Protected){Style.RESET_ALL}" if is_perm else ""
                print(f"  [{i}] {name}{suffix}")

            del_choice = _safe_input(f"\n{_t(lang, 'settings_prompt')}: ").strip()
            if del_choice.isdigit():
                del_idx = int(del_choice) - 1
                if 0 <= del_idx < len(cam_list):
                    del_name = cam_list[del_idx]
                    if del_name in ("CAM", "NOEXIF"):
                        print(f"{Fore.RED}{_t(lang, 'cam_protected')} '{del_name}'{Style.RESET_ALL}")
                        time.sleep(2)
                    else:
                        confirm_prompt = _t(lang, "cam_delete_confirm").format(name=del_name)
                        confirm = _safe_input(confirm_prompt).strip().lower()
                        if confirm in ("y", "yes"):
                            cam_list.pop(del_idx)
                            config["unknown_camera_list"] = cam_list
                            if config.get("unknown_camera_name") == del_name:
                                config["unknown_camera_name"] = "CAM"
                            save_config(config)
                            print(f"{Fore.GREEN}{_t(lang, 'cam_delete_ok')}{Style.RESET_ALL}")
                            time.sleep(1)
                        else:
                            print(f"{Fore.YELLOW}{_t(lang, 'cam_delete_cancel')}{Style.RESET_ALL}")
                            time.sleep(1)
                else:
                    print(f"{Fore.RED}{_t(lang, 'invalid')}{Style.RESET_ALL}")
                    time.sleep(1)
            else:
                print(f"{Fore.RED}{_t(lang, 'invalid')}{Style.RESET_ALL}")
                time.sleep(1)

        elif _is_back(choice):
            break
        else:
            print(f"{Fore.RED}{_t(lang, 'invalid')}{Style.RESET_ALL}")
            time.sleep(1)

    return config

# ---------------------------------------------------------------------------
# Submenu: Reset ke Default
# ---------------------------------------------------------------------------

_RESET_DEFAULTS = {
    "language"            : "id",
    "filename_format"     : "[{camera}]{date}_{time}_{index}",
    "filename_preset"     : "default",
    "export_csv"          : False,
    "unknown_camera_name" : "CAM",
    "use_phone_model"     : True,
    "max_camera_length"   : 10,
    "username"            : "Your Name",
    "unknown_camera_list" : ["CAM", "UNKNOWN", "NOEXIF", "MISC"],
}

def reset_config(config: dict, lang: str) -> dict:
    _header(_t(lang, "reset_header"))
    print(f"{Fore.YELLOW}{_t(lang, 'reset_warning')}{Style.RESET_ALL}")
    print()
    for k, v in _RESET_DEFAULTS.items():
        print(f"  {k}: {v}")
    print()

    confirm = _safe_input(f"{_t(lang, 'reset_confirm')}: ").lower()
    if confirm in ("y", "yes"):
        config.update(_RESET_DEFAULTS)
        save_config(config)
        print(f"{Fore.GREEN}{_t(lang, 'reset_done')}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{_t(lang, 'reset_cancelled')}{Style.RESET_ALL}")
    return config

# ---------------------------------------------------------------------------
# Submenu: Camera Alias Manager
# ---------------------------------------------------------------------------

def _print_alias_table(aliases: dict, lang: str):
    """Cetak tabel alias yang otomatis diurutkan alfabet berdasarkan Brand kemudian Camera Model."""
    items = []
    for model_key, alias_val in aliases.items():
        brand = _detect_brand(model_key)
        items.append((brand, model_key, alias_val))

    # otomatis diurutkan alfabet berdasarkan Brand kemudian Camera Model
    items.sort(key=lambda x: (x[0].lower(), x[1].lower()))

    col_no    = _t(lang, "alias_col_no")
    col_brand = _t(lang, "alias_col_brand")
    col_model = _t(lang, "alias_col_model")
    col_alias = _t(lang, "alias_col_alias")

    header_line = f"{col_no:<5}{col_brand:<12}{col_model:<22}{col_alias}"
    print(f"{Style.BRIGHT}{header_line}{Style.RESET_ALL}")
    print("-" * SEP_LEN)

    for i, (brand, model_key, alias_val) in enumerate(items, start=1):
        row = f"{i:<5}{brand:<12}{model_key:<22}{alias_val}"
        if i % 2 == 0:
            print(f"{Style.DIM}{row}{Style.RESET_ALL}")
        else:
            print(row)

def _pause(lang: str):
    _safe_input(_t(lang, "press_continue"))

def alias_menu(config: dict, lang: str) -> dict:
    """CRUD menu untuk config/camera_alias.json."""
    import time
    status_msg = None
    status_color = Fore.GREEN

    while True:
        aliases = load_alias_file()

        # Urutkan items berdasarkan Brand lalu Camera Model untuk memetakan nomor pilihan user
        items = []
        for model_key, alias_val in aliases.items():
            brand = _detect_brand(model_key)
            items.append((brand, model_key, alias_val))
        items.sort(key=lambda x: (x[0].lower(), x[1].lower()))
        sorted_items = [(model_key, alias_val) for brand, model_key, alias_val in items]

        _header(_t(lang, "alias_header"))

        # Cetak status pesan di atas jika ada
        if status_msg:
            print(f"{status_color}{status_msg}{Style.RESET_ALL}\n")
            status_msg = None
            status_color = Fore.GREEN

        count = len(aliases)
        print(f"{_t(lang, 'alias_count')} ({count})\n")

        if not aliases:
            print(f"  {Style.DIM}{_t(lang, 'alias_no_entry')}{Style.RESET_ALL}\n")
        else:
            _print_alias_table(aliases, lang)
            print()

        print(_t(lang, "alias_opt_add"))
        print(_t(lang, "alias_opt_edit"))
        print(_t(lang, "alias_opt_del"))
        print(f"\n{Fore.YELLOW}{_t(lang, 'alias_opt_back')}{Style.RESET_ALL}")

        choice = _safe_input(f"\n{_t(lang, 'settings_prompt')}: ")

        if choice == "1":
            # --- Add ---
            model_key = _safe_input(f"\n{_t(lang, 'alias_prompt_model')}").upper().replace(" ", "")
            if not model_key:
                print(f"{Fore.RED}{_t(lang, 'alias_err_empty')}{Style.RESET_ALL}")
                time.sleep(3)
                continue
            if model_key in aliases:
                print(f"{Fore.RED}{_t(lang, 'alias_err_duplicate')}{Style.RESET_ALL}")
                time.sleep(3)
                continue

            # Generate saran alias
            suggest = _generate_alias_suggestion(model_key)
            alias_prompt = _t(lang, "alias_prompt_alias").format(suggest=suggest)
            alias_val = _safe_input(f"\n{alias_prompt}").strip()

            if not alias_val:
                print(f"{Fore.RED}{_t(lang, 'alias_err_empty')}{Style.RESET_ALL}")
                time.sleep(3)
                continue

            if not _ALIAS_RE.match(alias_val):
                print(f"{Fore.RED}{_t(lang, 'alias_err_invalid_char')}{Style.RESET_ALL}")
                time.sleep(3)
                continue

            max_len = config.get("max_camera_length", 10)
            aliases[model_key] = alias_val[:max_len]
            save_alias_file(aliases)
            print(f"{Fore.GREEN}{alias_val} {_t(lang, 'alias_added')}{Style.RESET_ALL}")
            time.sleep(3)

        elif choice == "2":
            # --- Edit ---
            if not sorted_items:
                print(f"{Fore.YELLOW}{_t(lang, 'alias_err_not_found')}{Style.RESET_ALL}")
                time.sleep(3)
                continue
            no_str = _safe_input(f"\n{_t(lang, 'alias_prompt_no')}: ")
            if not no_str.isdigit() or not (1 <= int(no_str) <= len(sorted_items)):
                print(f"{Fore.RED}{_t(lang, 'alias_err_not_found')}{Style.RESET_ALL}")
                time.sleep(3)
                continue
            model_key, old_alias = sorted_items[int(no_str) - 1]

            edit_prompt = _t(lang, "alias_prompt_edit").format(old=old_alias)
            alias_val = _safe_input(edit_prompt).strip()

            if not alias_val:
                print(f"{Fore.RED}{_t(lang, 'alias_err_empty')}{Style.RESET_ALL}")
                time.sleep(3)
                continue

            if not _ALIAS_RE.match(alias_val):
                print(f"{Fore.RED}{_t(lang, 'alias_err_invalid_char')}{Style.RESET_ALL}")
                time.sleep(3)
                continue

            max_len = config.get("max_camera_length", 10)
            aliases[model_key] = alias_val[:max_len]
            save_alias_file(aliases)
            print(f"{Fore.GREEN}{alias_val} {_t(lang, 'alias_edited')}{Style.RESET_ALL}")
            time.sleep(3)

        elif choice == "3":
            # --- Delete ---
            if not sorted_items:
                print(f"{Fore.YELLOW}{_t(lang, 'alias_err_not_found')}{Style.RESET_ALL}")
                time.sleep(3)
                continue
            no_str = _safe_input(f"\n{_t(lang, 'alias_prompt_no')}: ")
            if not no_str.isdigit() or not (1 <= int(no_str) <= len(sorted_items)):
                print(f"{Fore.RED}{_t(lang, 'alias_err_not_found')}{Style.RESET_ALL}")
                time.sleep(3)
                continue
            model_key, alias_val = sorted_items[int(no_str) - 1]
            del aliases[model_key]
            save_alias_file(aliases)
            print(f"{Fore.GREEN}{alias_val} {_t(lang, 'alias_deleted')}{Style.RESET_ALL}")
            time.sleep(3)

        elif _is_back(choice):
            break

        else:
            print(f"{Fore.YELLOW}{_t(lang, 'invalid')}{Style.RESET_ALL}")
            time.sleep(3)

    return config

def username_menu(config: dict, lang: str) -> dict:
    _header(_t(lang, "username_header"))

    current = config.get("username", "Your Name").strip()
    if not current:
        current = "Your Name"

    print(f"{_t(lang, 'username_current')}: {Fore.YELLOW}{current}{Style.RESET_ALL}\n")
    print(_t(lang, "username_rules"))
    print(_t(lang, "username_rule1"))
    print(_t(lang, "username_rule2"))
    print(_t(lang, "username_rule3"))
    print()

    new_username = _safe_input(_t(lang, "username_prompt")).strip()

    if not new_username:
        print(f"\n{Fore.RED}{_t(lang, 'username_empty')}{Style.RESET_ALL}")
        import time
        time.sleep(1.5)
        return config

    import re
    if not (3 <= len(new_username) <= 16):
        print(f"\n{Fore.RED}{_t(lang, 'username_len')}{Style.RESET_ALL}")
        import time
        time.sleep(1.5)
        return config

    if not re.match(r'^[a-zA-Z0-9_]+$', new_username):
        print(f"\n{Fore.RED}{_t(lang, 'username_invalid')}{Style.RESET_ALL}")
        import time
        time.sleep(2)
        return config

    config["username"] = new_username
    save_config(config)
    print(f"\n{Fore.GREEN}{_t(lang, 'username_ok')}{new_username}{Style.RESET_ALL}")
    import time
    time.sleep(1.5)
    return config

# ---------------------------------------------------------------------------
# Settings Menu Utama
# ---------------------------------------------------------------------------

def settings_menu(config: dict, preview_file=None) -> dict:
    """
    Menampilkan menu pengaturan dan mengelola submenunya.
    preview_file: Path | None — file pertama dari session, untuk preview preset dinamis.
    Mengembalikan config terbaru setelah user keluar dari menu.
    """
    while True:
        lang = config.get("language", "id")
        _header(_t(lang, "settings_header"))

        # Preview konfigurasi saat ini
        lang_name   = "Bahasa Indonesia" if config.get("language", "id") == "id" else "English"
        preset_name = config.get("filename_preset", _t(lang, "settings_custom"))
        csv_color   = Fore.GREEN if config.get("export_csv", False) else Fore.RED
        csv_text    = _t(lang, "settings_on") if config.get("export_csv") else _t(lang, "settings_off")
        unknown_cam = config.get("unknown_camera_name", "CAM")
        uname       = config.get("username", "Your Name").strip()
        if not uname:
            uname = "Your Name"

        print(f"{_t(lang, 'settings_preview')}")
        print("-" * 36)
        print(f"{'Username':16} : {Fore.YELLOW}{uname}{Style.RESET_ALL}")
        print(f"{_t(lang, 'settings_language'):16} : {Fore.YELLOW}{lang_name}{Style.RESET_ALL}")
        print(f"{_t(lang, 'settings_preset_label'):16} : {Fore.YELLOW}{preset_name}{Style.RESET_ALL}")
        if config.get("filename_preset") is None:
            print(f"{_t(lang, 'settings_format'):16} : {Fore.YELLOW}{config.get('filename_format', '')}{Style.RESET_ALL}")
        print(f"{_t(lang, 'settings_csv_label'):16} : {csv_color}{csv_text}{Style.RESET_ALL}")
        print(f"{_t(lang, 'settings_unknown'):16} : {Fore.YELLOW}{unknown_cam}{Style.RESET_ALL}")
        print("-" * 36)
        print()

        print(_t(lang, "opt_language"))
        print(_t(lang, "opt_preset"))
        print(_t(lang, "opt_alias"))
        print(_t(lang, "opt_username"))
        print(_t(lang, "opt_cam_name"))
        print(_t(lang, "opt_csv"))
        print(f"{Fore.RED}{_t(lang, 'opt_reset')}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}{_t(lang, 'opt_back')}{Style.RESET_ALL}")

        choice = _safe_input(f"\n{_t(lang, 'settings_prompt')}: ")

        if choice == "1":
            config = language_menu(config, lang)
        elif choice == "2":
            config = filename_preset_menu(config, lang, preview_file=preview_file)
        elif choice == "3":
            config = alias_menu(config, lang)
        elif choice == "4":
            config = username_menu(config, lang)
        elif choice == "5":
            config = unknown_camera_menu(config, lang)
        elif choice == "6":
            config = csv_menu(config, lang)
        elif choice == "7":
            config = reset_config(config, lang)
        elif _is_back(choice):
            break
        else:
            print(f"{Fore.YELLOW}{_t(lang, 'invalid')}{Style.RESET_ALL}")

    return config


# End of logic/settings.py
