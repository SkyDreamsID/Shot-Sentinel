# 🛡️ Shot Sentinel Development Blueprint & Roadmap

> **From v0.7a → v1.0 Final**

---

## Filosofi Proyek (Ngapain Bikin Ginian?)

Shot Sentinel ini bukan sekadar aplikasi *rename* foto biasa. Idenya adalah membuat *tools* CLI yang enteng, cepat, dan aman buat siapa aja (mau fotografer pro atau kasual). Tujuannya simpel: **biar kita gak kehilangan foto berharga** cuma gara-gara nama file bawaan kamera yang suka *reset* dan menimpa file lain pas dipindahin ke laptop.

---

## Kenapa Pakai "SendTo"? Kok Gak Langsung Klik Kanan (Registry)?

Sebenarnya ada alasan teknis kenapa saya lebih memilih menempatkan aplikasinya ke dalam folder **SendTo** Windows (`shell:sendto`) daripada pakai *Registry Windows* buat menu klik kanan biasa:

1. **Bug Multi-Terminal di Registry:**
   Dulu pas awal-awal dites pake Registry, saya sempat memilih banyak file sekaligus terus klik kanan buat di-*rename*, Windows malah ngebuka banyak terminal `main.py` barengan (satu terminal buat satu file). Asli, bikin Laptop ngelag. Saya udah ngulik daleman registry macem-macem, tapi tetep aja gak solve dengan bersih.
2. **Terinspirasi dari KDE Connect:**
   Ide *Send To* ini terinspirasi dari cara kerja **KDE Connect** saat mentransfer file. Dengan metode ini, Windows otomatis mengelompokkan semua file yang dipilih menjadi satu untuk dikirim ke *satu* terminal aja. Hasilnya? Eksekusi *batch* jalan mulus di satu terminal.
3. **Lebih Aman & Gampang Diatur:**
   Pake cara ini tidak perlu akses Administrator (UAC), tidak mengotori *registry* sistem, dan mudah sekali saat di instal atau di uninstall (karena cuma membuat *shortcut* `.lnk` saja). Sangat portabel!

---

## Project Information

| Item | Value |
|------|-------|
| Project | Shot Sentinel |
| Author | Rifki Eka Putra (SkyDreamsID) |
| Language | Python 3 |
| UI | CLI (Terminal) |
| Status | Production Release |
| Current Version | v1.0 Final |
| Target Final | v1.0 Final |

---

## Progress

```
v0.7a Foundation        ██████████ 100%
v0.8 Beta               ██████████ 100%
v1.0 Final              ██████████ 100%

Overall Project        ██████████ 100%
```

---

## Timeline Development

```
v0.7a (Foundation)
     ↓
v0.8 Beta (Past Release)
│
└──> v1.0 Final (Production Release - Current)

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
- ✅ Master History (Versi .txt)
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

## v0.8 Beta (Past Release)

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
=== Shot Sentinel v1.0 Final (Protect Your Media) ===========
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

## v1.0 Final — Production Release (CURRENT)

Versi Final. Seluruh target fitur untuk v1.0 telah diselesaikan.

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

### Standalone Duplicate Checker
- RAM-efficient Two-Pass Algorithm (Size -> MD5 Hash)
- Intelligent Original File Detection (Shortest Name + Oldest Creation Time)
- Safe Isolate to quarantine folder
- Native Windows Recycle Bin Integration (via ctypes)
- Captcha protection for Permanent Deletion

### Media Organizer
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
- Dynamic UI Synchronization (Flexible line length based on header)
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

## Project Structure (v1.0 Final)

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
│   ├── dev_present.py
│   ├── html_report.py
│   ├── integrity.py
│   ├── log_history.py
│   ├── metadata.py
│   ├── organizer.py
│   ├── settings.py
│   ├── statistics.py
│   ├── version.py
│   └── worker.py
│
├── assets/                   (Eksternalisasi aset non-logika)
│   ├── ascii/                (istri dev ada disini :v)
│   ├── html/                 (Template HTML & CSS)
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

Gak ada rencana buat nambahin fitur gede-gedean lagi. Fokusnya murni cuma buat *maintenance* atau nambal *bug* kalau ketemu.

---

## Visi Jangka Panjang

Shot Sentinel bakal tetep dipertahanin jadi aplikasi CLI yang simpel dan ringan. Fokusnya tetep satu: ngamanin penamaan file foto lu biar gak ketimpa. Proyek ini **gak akan pernah** berubah jadi *file manager* raksasa atau maksa pakai GUI yang berat. Setiap fitur baru yang masuk harus tetep patuh sama prinsip awal: **simpel, ngebut, hemat RAM, dan bisa diandelin.**


