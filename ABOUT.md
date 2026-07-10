# About Shot Sentinel

**Version:** v0.8 Beta
**Developer:** Rifki Eka Putra (SkyDreamsID)
**License:** Non-Commercial License

## The Problem
Shot Sentinel exists because I lost some valuable photos. My camera reset its file numbering, created duplicate names like `DSC_0001.JPG`, and overwrote my older files when I pasted them into the same folder. Since that happened, I realized there should be a simple tool to handle this exact problem.

## The Solution
Every feature and decision in this project is based on real experience managing photos from different cameras. It's not meant to replace professional Digital Asset Management (DAM) software like Lightroom or Capture One. Shot Sentinel only does one thing: **prevent files from being overwritten because of duplicate camera filenames**.

It renames media files by leveraging EXIF metadata to ensure each file is named uniquely based on the exact moment it was taken and the camera model that took it. 

### Why not just sort them into folders?
Because I am lazy and often forget to create new folders for every single session. It's much safer to have globally unique filenames that can safely coexist in a single massive dump folder.

## Key Technical Decisions
- **SendTo Integration**: We chose the Windows "SendTo" folder over direct Windows Registry menu entries because the Windows registry triggers a new CLI process per selected file, whereas the SendTo system correctly groups all selected items to be passed to a single process. This design was inspired by how KDE Connect manages sharing files.
- **Python**: Chosen for its wide library support (like `exifread`) and ease of maintenance.
- **Cross-Platform Readiness**: While currently built as a Windows CLI (with batch file installers and SendTo integration), the Python logic is fully path-agnostic and uses `pathlib` heavily, making a future Linux/macOS port straightforward.
- **History Logs**: We maintain a `master_history.json` and a session log for every single batch operation to ensure we can *always* safely restore files to their original names if the user makes a mistake.
- **No Dependencies on System APIs**: The rename logic avoids Windows-specific APIs in favor of pure Python `os` and `shutil` operations, avoiding edge cases across different file systems.

## Acknowledgements
- `exifread`: For robust metadata extraction.
- `colorama`: For making the CLI look nice and organized.
- My past self for losing those photos so that this tool could be born.
