# Changelog

All notable changes to **Shot Sentinel** will be documented in this file.

## [v1.0 Final] - 2026-07-11
### Added
- **Native Folder Picker**: Added a native Windows folder selection dialog to browse for custom destination paths.
- **Offline HTML Report**: Complete refactor to a professional, offline-capable HTML report (no external CDN dependencies).
- **CSS Flexbox Charts**: Implemented pure CSS charting for File Type Distribution and Camera Usage statistics.
- **Protection Rank System**: Implemented gamified progress tracking with ASCII progress bars via CLI and HTML report.
- **Standalone Duplicate Checker**: A dedicated tool to find and manage duplicate files using a fast, memory-efficient two-pass algorithm (Size & MD5 hash). Includes safe options to Isolate, move to Recycle Bin (via native Win32 API), or Permanently Delete (with Captcha protection).
- **Idempotent Media Organizer**: The Media Organizer is now fully idempotent. Re-running it safely skips already organized files and prevents nested folder creation.
- **Recursive Protection System**: Engineered a `.shotsentinel` hidden metadata marker to detect and warn users if they attempt to organize a folder that is already a child of a previously organized destination.
- **Native Linux Support**: Ported the application to Linux (tested on Mint, Ubuntu, and Debian). Added bash wrappers, a GIO-based native Recycle Bin integration, and automated installer scripts for Nemo, Nautilus, and Caja file managers.

### Changed
- **Global UI Synchronization**: All CLI separators and borders now dynamically scale their lengths based on the main header width, ensuring perfectly aligned and symmetrical UI outputs across all modules.
- **Terminology**: Unified "File Organizer" to "Media Organizer" across the main menu and internal logic.
- **Refactoring**: Decoupled HTML, CSS, and JS assets into the `assets/html/` directory for cleaner architecture.
- **User Display**: The generated report now correctly extracts `username` from `config.json` instead of defaulting to system OS user.

### Fixed
- **Template Menu**: Fixed an issue where submitting empty input immediately aborted the menu instead of allowing a retry.

---

## [v0.8 Beta] - 2026-07-10

### Added
- **Developer Corner**: Added a developer-oriented menu featuring Kaomoji animations, DEV Waifu's (featuring Sunao Nako ASCII art), developer notes, and Nako-styled logic quotes.
- **Camera Alias Manager**: Integrated a full CRUD CLI manager for camera model aliases (`config/camera_alias.json`) supporting table views, brand detection, and automatic suggestions.
- **Dynamic Preset Preview**: Added real-time previews for file-renaming presets using the first target file instead of static placeholders.
- **Username Alias**: Added a configuration parameter to set a custom username alias in filename templates.
- **Unknown Camera Alias**: Added customizable fallback aliases directly configurable from the CLI for media without EXIF.
- **Statistics Placeholder**: Added a menu option for upcoming project-wide statistics.
- **CSV Export Module**: Added support for exporting session logs in CSV format.
- **Duplicate Checking System**: Implemented double-pass duplicate/overwrite checks during rename operations.
- **JSON History**: Migrated master history tracking from plain text to a structured JSON-based `master_history.json`.

### Changed
- **CLI Architecture**: Refactored main scripts into a modular structure under the `logic/` directory for cleaner maintainability.
- **Folder Structure**: Centralized configuration JSONs into the `config/` directory.
- **UI & UX Polish**: Updated the application header, simplified menu flows, and overhauled rename/restore summary reports.
- **Documentation**: Fully synchronized `README.md`, `BLUEPRINT.md`, and `ABOUT.md` with version 0.8 specifications.

### Fixed
- Fixed an issue where terminating the script (Ctrl+C) mid-process could corrupt the master history by gracefully catching `KeyboardInterrupt`.
- Resolved an `EOFError` exception handling logic bug when piping input or closing the terminal unexpectedly.
- Fixed a bug where files could be silently overwritten during a `restore` operation if a naming collision occurred.
- Improved cross-platform input capturing (using `msvcrt` on Windows and `select` on Linux) to prevent animation blocking.

## [v0.7a] - 2026-07-03

### Added
- Initial core renaming and restore functionality based on EXIF/Last Modified metadata.
- Basic interactive CLI.
- Batch installation scripts for Windows contextual "SendTo" menu integration.
- `process_log.txt` integration.
- Camera Alias mapping via `config.json`.
