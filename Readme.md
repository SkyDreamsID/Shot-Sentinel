# 🛡️ Shot Sentinel

> Never lose your memories because your camera decided to start from DSC_0001 again.

![Version](https://img.shields.io/badge/version-v0.7a--alpha-orange)
![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)
![License](https://img.shields.io/badge/license-MIT-green)

### 📥 Installation & Setup

### Requirements

- Windows 10/11
- Python 3.10 or newer (with pip)
- Internet connection (first run only)

### Install Python

Download Python from:
https://www.python.org/downloads/

⚠️ During installation, make sure to enable:

☑ Add Python.exe to PATH

### First Run

On the first launch, Shot Sentinel will automatically install the required dependencies:

- exifread
- colorama

## Cara Pakai | How to use

| Bahasa Indonesia | English |
|---|---|
| **1. Extract file Zip yang telah didownload** | **1. Extract the downloaded Zip file** |
| **2. Buka folder Shot Sentinel** | **2. Open the Shot Sentinel folder** |
| **3. Jalankan Install-Program.bat** | **3. Run Install-Program.bat** |
| **4. Setelah sukses terinstall, pilih file yang akan diproses** | **4. After successful installation, select files to process** |
| **5. Klik kanan → SendTo/Bagikan ke → Shot Sentinel** | **5. Right-click → SendTo → Shot Sentinel** |
| **6. Pilih fitur menggunakan keyboard** | **6. Select feature using keyboard input** |
| **7. Program berhasil dijalankan** | **7. Program successfully executed** |

## 🗑️ Uninstall

| Bahasa Indonesia | English |
|---|---|
| **1. Jalankan Uninstall-Program.bat** | **1. Run Uninstall-Program.bat** |
| **2. Selesai** | **2. Done** |

<details>
<summary><h3>📷 Visual Guide (Screenshot Step by Step)</h3></summary>

**1. Extract file Zip yang telah didownload**
![CRtF9XS.png](https://iili.io/CRtF9XS.png)

**2. Buka folder dan Jalankan Install-Program.bat**
![CRt3yI2.png](https://iili.io/CRt3yI2.png) ![CRt3be4.png](https://iili.io/CRt3be4.png)

**3. Setelah sukses terinstall, pilih file yang akan diproses**
![CRtF21e.png](https://iili.io/CRtF21e.png)

**4. Klik kanan → SendTo/Bagikan ke → Shot Sentinel**
![CRtFf7j.png](https://iili.io/CRtFf7j.png)

**5. Pilih fitur menggunakan keyboard**
![CRtFxLP.png](https://iili.io/CRtFxLP.png)

**6. Program berhasil dijalankan**
1) Rename
![CRtFohB.png](https://iili.io/CRtFohB.png)
2) Restore
![CRtFTEF.png](https://iili.io/CRtFTEF.png)

----
## Uninstall guide
**1. Jalankan Uninstall-Program.bat lalu akan muncul tampilan seperti ini**
![CRtFIB1.png](https://iili.io/CRtFIB1.png)

**2. Uninstall berhasil dan selesai**
![CRtF7kv.png](https://iili.io/CRtF7kv.png)

</details>

---

<details open>
<summary><h2>ID Bahasa Indonesia</h2></summary>

Utility sederhana untuk mencegah foto dan video tertimpa akibat penamaan bawaan kamera yang berulang, seperti:

```text
DSC_1234.JPG
DSC_1235.JPG
DSC_1236.JPG
```

Beberapa kamera akan mereset nomor file setelah mencapai batas tertentu atau setelah mengganti kartu memori. Hal ini dapat menyebabkan foto lama tertimpa tanpa disadari.

Shot Sentinel dibuat untuk mengatasi masalah tersebut dengan merubah nama file menjadi unik berdasarkan metadata.

### ✨ Fitur

- 📸 Rename otomatis berdasarkan EXIF
- 🎥 Mendukung foto dan video
- 🛡️ Mencegah file tertimpa (overwrite)
- 🔄 Restore ke nama file asli
- 📝 Session log
- 📋 Process log
- ⚙️ Bisa dikonfigurasi lewat `config.json`

### 📷 Format Penamaan

Default:

```text
[CameraModel]YYYY-MM-DD_HH-MM-SS_Index.ext
```

Contoh:

```text
[D3300]2026-06-28_12-34-56_1234.JPG
```

### 📸 Sebelum & Sesudah

**Sebelum:**

```text
DSC_1234.JPG
DSC_1235.JPG
DSC_1236.JPG
```

**Sesudah:**

```text
[D3300]2026-06-28_12-34-56_1234.JPG
[D3300]2026-06-28_12-35-11_1235.JPG
[D3300]2026-06-28_12-35-45_1236.JPG
```

### 🗂️ Struktur Project

```text
Shot-Sentinel/
├── log/
├── Sample/
├── Step by step/
├── [ID] Read this!!.txt
├── config.json
├── Install-Program.bat
├── main.py
├── master_history.txt
├── process_log.txt
├── program.bat
├── Readme.md
├── requirements.txt
└── Uninstall-Program.bat
```

### ⚙️ Konfigurasi

#### Config File

`config.json`

```json
{
    "filename_format": "[{camera}]{date}_{time}_{index}",
    "use_phone_model": false,
    "unknown_camera_name": "CAM",
    "max_camera_length": 10
}
```

#### Preset Format Penamaan

Ubah value `filename_format` di `config.json` sesuai keinginanmu:

**Default (Recommended)**
```json
"filename_format": "[{camera}]{date}_{time}_{index}"
```
Hasil: `[D3300]2026-06-28_23-23-07_1234.JPG`

**Datetime Only**
```json
"filename_format": "{date}_{time}"
```
Hasil: `2026-06-28_23-23-07.JPG`

**Dengan Tahun Terpisah**
```json
"filename_format": "{year}-{month}-{day}_{time}_{index}"
```
Hasil: `2026-06-28_23-23-07_1234.JPG`

**Camera + Index Only**
```json
"filename_format": "[{camera}]_{index}"
```
Hasil: `[D3300]_1234.JPG`

**Custom Sendiri**
Campur-campur variabel di bawah sesuai preferensimu.

#### Variable Reference

| Variable | Keterangan | Contoh |
|---|---|---|
| `{camera}` | Nama model kamera dari EXIF | `D3300`, `A6400`, `80D` |
| `{date}` | Tanggal lengkap | `2026-06-28` |
| `{time}` | Waktu lengkap | `23-23-07` |
| `{year}` | Tahun | `2026` |
| `{month}` | Bulan (2 digit) | `06` |
| `{day}` | Hari (2 digit) | `28` |
| `{hour}` | Jam (2 digit) | `23` |
| `{minute}` | Menit (2 digit) | `23` |
| `{second}` | Detik (2 digit) | `07` |
| `{index}` | Nomor file asli dari kamera | `1234` |

**Catatan:** Jika EXIF tidak tersedia, gunakan nilai default dari `unknown_camera_name` (default: `CAM`)

#### Custom Format File

Kamu bisa menambah atau menghapus ekstensi file dari array `supported_image_extensions` dan `supported_video_extensions` di `config.json`:

```json
"supported_image_extensions": [
    ".jpg",
    ".jpeg",
    ".png",
    ".nef",
    ".webp"
],
"supported_video_extensions": [
    ".mp4",
    ".mov",
    ".mkv"
]
```

Ini berguna jika kamu ingin memproses format spesifik atau tambah format yang belum terdaftar.

### 📋 File History

Format: `timestamp    new_name    old_name    status`

Contoh:

```text
20260628_103012  [D3300]2026-06-28_12-34-56_1234.JPG  DSC_1234.JPG  ACTIVE
```

Status:

- `ACTIVE`
- `RESTORED`

### 🛣️ Roadmap

**v0.7b**
- Dukungan Linux
- Pengorganisasian folder
- Pengecekan duplikat
- Export CSV
- Peningkatan performa

### ❓ Alasan Bikin Ini

Saya pernah kehilangan beberapa foto berharga di HDD saat memindahkan file dari kamera ke laptop. Ternyata kamera saya reset urutan penomoran file, jadi beberapa foto lama ketimpa tanpa saya sadari. (tools ini useless jika anda tidak menaruh semua foto di satu folder)

### ❤️ Tentang Project Ini

Shot Sentinel ada karena saya pernah kehilangan beberapa foto berharga. Kamera saya reset nomor file, jadinya nama file sama dan yang lama tertimpa. Sejak pengalaman itu, saya mulai mikir perlu ada tool sederhana untuk handle masalah ini.

Setiap fitur dan keputusan di project ini didasarkan pada pengalaman nyata mengelola foto dari berbagai kamera. Bukan dimaksudkan sebagai pengganti software DAM profesional seperti Lightroom atau Capture One. Shot Sentinel hanya fokus pada satu hal: mencegah file tertimpa karena nama kamera yang sama.

### 🤖 Kredit Pengembangan

**Penulis dan Developer**

Rifki Eka Putra

**Kontribusi Saya**

Konsep, problem definition, design fitur, naming convention, edge case testing, algoritma, dan arah project semuanya ditangani oleh saya.

**AI Assistants**

ChatGPT (OpenAI), Claude (Anthropic), Gemini (Google), Antigravity

Digunakan untuk membantu code generation, debugging, dokumentasi, dan refactoring suggestions. Semua keputusan dan arah project tetap ditentukan oleh saya.

</details>

<details>
<summary><h2>EN English</h2></summary>

A simple utility to prevent photos and videos from being overwritten due to repeating camera default filenames, such as:

```text
DSC_1234.JPG
DSC_1235.JPG
DSC_1236.JPG
```

Some cameras reset their file numbering after reaching a certain limit or after a memory card swap. This can cause old photos to be overwritten without you noticing.

Shot Sentinel was built to solve this by renaming files into unique filenames based on their metadata.

### ✨ Features

- 📸 Automatic renaming based on EXIF data
- 🎥 Supports both photos and videos
- 🛡️ Prevents file overwrites
- 🔄 Restore to original filename
- 📝 Session log
- 📋 Process log
- ⚙️ Configurable via `config.json`

### 📷 Naming Format

Default:

```text
[CameraModel]YYYY-MM-DD_HH-MM-SS_Index.ext
```

Example:

```text
[D3300]2026-06-28_12-34-56_1234.JPG
```

### 📸 Before & After

**Before:**

```text
DSC_1234.JPG
DSC_1235.JPG
DSC_1236.JPG
```

**After:**

```text
[D3300]2026-06-28_12-34-56_1234.JPG
[D3300]2026-06-28_12-35-11_1235.JPG
[D3300]2026-06-28_12-35-45_1236.JPG
```

### 🗂️ Project Structure

```text
Shot-Sentinel/
├── log/
├── Sample/
├── Step by step/
├── [ID] Read this!!.txt
├── config.json
├── Install-Program.bat
├── main.py
├── master_history.txt
├── process_log.txt
├── program.bat
├── Readme.md
├── requirements.txt
└── Uninstall-Program.bat
```

### ⚙️ Configuration

#### Config File

`config.json`

```json
{
    "filename_format": "[{camera}]{date}_{time}_{index}",
    "use_phone_model": false,
    "unknown_camera_name": "CAM",
    "max_camera_length": 10
}
```

#### Naming Format Presets

Modify the `filename_format` value in `config.json` to customize your naming:

**Default (Recommended)**
```json
"filename_format": "[{camera}]{date}_{time}_{index}"
```
Output: `[D3300]2026-06-28_23-23-07_1234.JPG`

**Datetime Only**
```json
"filename_format": "{date}_{time}"
```
Output: `2026-06-28_23-23-07.JPG`

**With Separate Year**
```json
"filename_format": "{year}-{month}-{day}_{time}_{index}"
```
Output: `2026-06-28_23-23-07_1234.JPG`

**Camera + Index Only**
```json
"filename_format": "[{camera}]_{index}"
```
Output: `[D3300]_1234.JPG`

**Custom Combination**
Mix and match any variables below to suit your preference.

#### Variable Reference

| Variable | Description | Example |
|---|---|---|
| `{camera}` | Camera model from EXIF metadata | `D3300`, `A6400`, `80D` |
| `{date}` | Full date | `2026-06-28` |
| `{time}` | Full time | `23-23-07` |
| `{year}` | Year (4 digits) | `2026` |
| `{month}` | Month (2 digits) | `06` |
| `{day}` | Day (2 digits) | `28` |
| `{hour}` | Hour (2 digits) | `23` |
| `{minute}` | Minute (2 digits) | `23` |
| `{second}` | Second (2 digits) | `07` |
| `{index}` | Original file number from camera | `1234` |

**Note:** If EXIF data is unavailable, the fallback value `unknown_camera_name` (default: `CAM`) will be used.

#### Custom File Extensions

You can add or remove file extensions from the `supported_image_extensions` and `supported_video_extensions` arrays in `config.json`:

```json
"supported_image_extensions": [
    ".jpg",
    ".jpeg",
    ".png",
    ".nef",
    ".webp"
],
"supported_video_extensions": [
    ".mp4",
    ".mov",
    ".mkv"
]
```

This is useful if you want to process specific formats or add file types that aren't pre-registered.

### 📋 History File

Format: `timestamp    new_name    old_name    status`

Example:

```text
20260628_103012  [D3300]2026-06-28_12-34-56_1234.JPG  DSC_1234.JPG  ACTIVE
```

Status:

- `ACTIVE`
- `RESTORED`

### 🛣️ Roadmap

**v0.7b**
- Linux support
- Folder organization
- Duplicate checker
- CSV export
- Performance improvements

### ❓ Why I Made This

I lost several photos because my camera restarted its numbering sequence after a memory card swap. Some files were overwritten without me realizing, frustration prompted me to create this solution.

### ❤️ About This Project

Shot Sentinel exists because I lost some valuable photos. My camera reset its file numbering, created duplicate names, and overwritten my older files. Since that happened, I thought there should be a simple tool to handle this problem.

Every feature and decision in this project is based on real experience managing photos from different cameras. It's not meant to replace professional DAM software like Lightroom or Capture One. Shot Sentinel only does one thing: prevent files from being overwritten because of duplicate camera filenames.

### 🤖 Development Credits

**Author and Developer**

Rifki Eka Putra

**My Contributions**

Concept, problem definition, feature design, naming convention, edge case testing, algorithm decisions, and project direction were all handled by me.

**AI Assistants**

ChatGPT (OpenAI), Claude (Anthropic), Gemini (Google), Antigravity

Used to help with code generation, debugging, documentation, and refactoring suggestions. All decisions and project direction remain mine.

</details>

---

# Made with ❤️ and Python by **Rifki Eka Putra (rifkiekap07)**

© June 2026 Rifki Eka Putra
