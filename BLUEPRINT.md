# 🛡️ Shot Sentinel Development Blueprint & Roadmap

> **From v0.7a → v1.0 Final**

---

## Project Philosophy

Shot Sentinel bukan sekadar aplikasi rename foto. Tujuannya adalah menjadi utilitas CLI ringan, cepat, aman, dan profesional untuk fotografer maupun pengguna umum agar tidak kehilangan file akibat penamaan bawaan kamera yang sering bertabrakan saat dipindahkan ke komputer.

---

## Design Decisions: Mengapa Menggunakan "SendTo" Bukan Registry?

Ada alasan teknis dan pengalaman praktis yang melatarbelakangi keputusan untuk tidak mengintegrasikan aplikasi langsung ke *Registry Windows* (Context Menu klik kanan biasa), melainkan lewat folder **SendTo** (`shell:sendto`):

1. **Masalah Multi-Proses pada Registry (Bug Multi-Terminal):**
   Pada uji coba awal menggunakan Registry, ketika pengguna memilih banyak file sekaligus lalu klik kanan untuk di-rename, Windows akan membuka instansi terminal `main.py` yang baru **untuk setiap file yang dipilih**. Memilih 50 file akan memicu 50 jendela terminal terbuka bersamaan. Mencoba mengutak-atik argumen registry tetap tidak berhasil menyelesaikan masalah ini secara bersih.
2. **KDE Connect Inspirasi:**
   Inspirasi menggunakan *Send To* lahir dari cara kerja **KDE Connect** (aplikasi transfer file antar perangkat). Dengan memanfaatkannya, Windows secara otomatis mengelompokkan semua file yang dipilih dan meneruskannya ke satu jendela aplikasi Shot Sentinel yang sama sebagai argumen list, sehingga eksekusi *batch* berjalan stabil di satu jendela.
3. **Keamanan & Kemudahan:**
   Metode ini tidak memerlukan hak akses Administrator (UAC), tidak merusak registri sistem, mudah diinstal/diuninstal (hanya berupa *shortcut* `.lnk`), dan sangat portabel.

---

## Project Information

| Item | Value |
|------|-------|
| Project | Shot Sentinel |
| Author | Rifki Eka Putra (SkyDreamsID) |
| Language | Python 3 |
| UI | CLI (Terminal) |
| Status | Beta Development |
| Current Version | v0.8 Beta |
| Target Final | v1.0 |

---

## Progress

```
v0.7a Foundation        ██████████ 100%
v0.8 Beta              ██████████ 100%
v1.0 Final             ░░░░░░░░░░   0%

Overall Project        ██████░░░░  65%
```

---

## Timeline Development

```
v0.7a (Foundation)
     ↓
v0.8 Beta (Final Feature Release - Current)
     ↓
v1.0 Final (Production Release)
     ↓
v1.0.1 → v1.0.2 → v1.0.3+
(Maintenance Only)
```

---

## v0.7a — Foundation Release

> Membuktikan bahwa engine rename bekerja stabil.

Versi ini adalah pondasi seluruh proyek. Fokus utama adalah memastikan engine rename benar-benar stabil sebelum fitur lain ditambahkan.

### Core Engine
- ✅ Rename berdasarkan EXIF
- ✅ Rename berdasarkan Last Modified
- ✅ Preview Rename
- ✅ Restore Filename
- ✅ History
- ✅ Master History (Versi Teks)
- ✅ Collision Detection
- ✅ Progress Bar

### Metadata
- ✅ EXIF Reader
- ✅ Fallback Last Modified
- ✅ Camera Detection

### Logging
- ✅ Session Log
- ✅ Master History

### Configuration
- ✅ config.json
- ✅ Filename Preset

---

## v0.8 Beta — Final Feature Release (CURRENT)

Versi ini adalah implementasi fitur lengkap yang sudah stabil. Tidak ada lagi perombakan arsitektur besar.

### ARCHITECTURE MODULARITY
- ✅ **Modular Refactoring**: Memecah berkas tunggal monolith `main.py` dari v0.7a menjadi modul-modul terpisah di dalam direktori `logic/` (`worker.py`, `metadata.py`, `settings.py`, `log_history.py`, `collision.py`, etc.) demi keterbacaan dan pemeliharaan kode jangka panjang.
- ✅ **Eksternalisasi Aset**: Memindahkan teks statis, gambar ASCII, catatan developer, dan quotes ke dalam folder `assets/`.
- ✅ **Pemisahan Konfigurasi**: Memisahkan data dinamis `camera_alias.json` agar terisolasi dari setelan utama `config.json`.

### CORE
- ✅ Auto Rename (Aman dari duplicate & overwrite)
- ✅ Restore Filename (Aman dari silent overwrite)
- ✅ Preview Rename Dinamis
- ✅ Progress Bar Interaktif
- ✅ Master History (Migrasi ke JSON)
- ✅ Session Log (Teks & CSV Export)

### SETTINGS
- ✅ Language (ID / EN) terintegrasi di config.json
- ✅ Filename Preset (Default, Date Only, dsb.)
- ✅ Camera Alias
- ✅ Unknown Camera Name / Fallback
- ✅ Username Alias
- ✅ Reset Settings
- ✅ Dynamic Configuration

### Dynamic Preset Preview

Menampilkan contoh nama file berdasarkan file pertama yang ditemukan. Tidak menggunakan contoh statis lagi.

```
Preset saat ini : default
[D3300]2026-07-05_18-20-31_1234.JPG
```

### Camera Alias Manager

Menu baru. Semua alias disimpan pada `config/camera_alias.json`, bukan lagi di config utama.

```
Camera Alias
[1] View Alias
[2] Add Alias
[3] Edit Alias
[4] Delete Alias
[0] Back
```

**Tampilan Table:**
```
Camera Alias (4)

No  Brand   Camera Model        Alias
------------------------------------------
1   Canon   CANONEOS80D         80D
2   Nikon   NIKOND3100          D3100
3   Nikon   NIKOND3300          D3300
4   Sony    SONYILCE6400        A6400
```

**Group View:**
```
Nikon (2)
 ├── D3100
 └── D3300

Canon (1)
 └── 80D

Sony (1)
 └── A6400
```

### Smart Alias Suggestion

| Input | Saran Otomatis |
|-------|---------------|
| CANON600D | 600D |
| NIKOND3300 | D3300 |
| SONYA7III | A7III |

### JSON Folder Structure

Semua konfigurasi dipindahkan ke `config/`:
```
config/
├── config.json
└── camera_alias.json
```

### UI Polish

**Header baru:**
```
============================================================
=== Shot Sentinel v0.8 Beta (Protect Your Media) ===========
============================================================
```

**Rename Summary:**
```
============================================================
[RENAME SUMMARY]
============================================================

Processed              : xx file
Successfully Renamed   : xx file
Already Renamed        : xx file
Failed                 : xx file

------------------------------------------------------------
Completed successfully.

Press Enter to exit...
```

**Restore Summary:**
```
============================================================
[RESTORE SUMMARY]
============================================================

Processed               : xx file
Successfully Restored   : xx file
Already Original        : xx file
Failed                  : xx file

------------------------------------------------------------
Completed successfully.

Press Enter to exit...
```

**Failed Files display:**
```
Failed Files
• IMG_0001.JPG
  Reason : Permission denied

• DSC_1234.JPG
  Reason : Target filename already exists
```

### Additional Features Menu

```
Additional Features
[1] Statistics
[2] About
[3] Developer Corner
[0] Back
```

**About screen:**
```
Shot Sentinel — Protect Your Media

Developer   : Rifki Eka Putra (SkyDreamsID)
Language    : Python
Libraries   : Colorama, EXIFRead, tqdm, csv, json, pathlib
Repository  : GitHub

Fun Fact    : Project ini dibuat karena developer frustasi
              kehilangan banyak foto akibat filename kamera
              yang tertimpa di Windows Explorer.

Press Enter to return...
```

### Bug Fix Priority

**Critical:**
- Race Condition Rename
- Crash Dynamic Preview
- Crash Camera Alias
- Config Migration
- Summary Baru

**Important:**
- History Validation
- Camera Alias Validation
- Duplicate Detection
- Collision Detection

**Minor:**
- UI Alignment, Padding, Color, Header, Wording

### Testing Checklist

**Rename:**
- [ ] Folder kosong
- [ ] 1 file
- [ ] 10 file
- [ ] 100 file
- [ ] 1000 file
- [ ] 10000 file

**Restore:**
- [ ] Semua file original
- [ ] Semua file renamed
- [ ] Sebagian renamed

**Metadata:**
- [ ] EXIF ada
- [ ] EXIF kosong
- [ ] PNG
- [ ] MP4
- [ ] RAW

**Error:**
- [ ] Read Only
- [ ] Permission Denied
- [ ] Duplicate Filename
- [ ] Config rusak
- [ ] History rusak

### Performance Target

| Metric | Target |
|--------|--------|
| Rename 10.000 file | < 1 menit |
| RAM usage | < 100 MB |
| Memory Leak | Tidak ada |

---

## v1.0 Final — Production Release

Versi Final. Pengembangan hanya akan difokuskan untuk menyempurnakan fitur-fitur yang sudah ada dan perbaikan bug di v0.8 Beta.

### Statistics Dashboard
- Total Files Renamed
- Total Files Restored
- Camera Usage
- File Type Statistics
- Timeline Statistics
- Largest Session
- Most Used Camera

### HTML Report
- Dashboard
- Before / After
- Rename History
- Statistics
- Responsive Layout

### File Organizer
- Organize by Year
- Organize by Month
- Organize by Camera
- Organize by File Type
- Custom Folder Structure

### Integrity Check
- Duplicate Filename
- Missing EXIF
- Invalid Date
- Rename Conflict

### Better Logging
- JSON Log
- Improved Session Summary
- CSV Enhancement

### Final Polish
- Konsistensi seluruh menu
- Alignment seluruh output CLI
- Warna konsisten
- Wording profesional
- UX lebih sederhana

### Dokumentasi Lengkap
- Blueprint final
- README GitHub
- Screenshot CLI
- Panduan penggunaan
- Changelog v1.0

---

## Project Structure (v0.8 Beta)

```
Shot Sentinel/
│
├── config/
│   ├── config.json           (Setelan bahasa, preset, ext, dll)
│   └── camera_alias.json     (Data alias khusus kamera)
│
├── history/
│   ├── master_history.json   (Riwayat absolut seluruh file)
│   ├── process_log.txt       (Log operasional)
│   └── sessions/             (Log per sesi dalam TXT & CSV)
│
├── logic/                    (Core Engine & System)
│   ├── additional_features.py
│   ├── collision.py
│   ├── dev_present.py
│   ├── exporter.py
│   ├── log_history.py
│   ├── metadata.py
│   ├── settings.py
│   ├── source_detector.py
│   ├── version.py
│   └── worker.py
│
├── assets/                   (Eksternalisasi aset non-logika)
│   ├── ascii/                (istri dev ada disini :v)
│   ├── notes/
│   └── quotes/
│
├── Sample/
├── Step by step/
│
├── [ID] PENTING!!.txt
├── ABOUT.md
├── BLUEPRINT.md
├── CHANGELOG.md
├── Install-Program.bat
├── main.py                   (Entry point)
├── program.bat
├── Readme.md
├── requirements.txt
└── Uninstall-Program.bat
```

---

## Compatibility

| Platform | Status |
|----------|--------|
| Windows | ✅ |
| Linux | ✅ (Posix compliance) |
| Python 3.10+ | ✅ |

---

## Setelah v1.0

Tidak ada roadmap fitur mayor. Hanya maintenance.

---

## Visi Jangka Panjang

Shot Sentinel akan tetap menjadi aplikasi CLI ringan dengan fokus pada satu tugas: mengelola nama file media secara aman dan konsisten. Proyek ini tidak akan berkembang menjadi file manager atau aplikasi GUI penuh. Setiap fitur baru harus tetap sejalan dengan tujuan utama: **sederhana, cepat, hemat sumber daya, dan dapat diandalkan.**


