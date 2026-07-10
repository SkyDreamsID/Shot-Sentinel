import re
from pathlib import Path

# Case-insensitive patterns for classification
RE_SCR = re.compile(r"(?i)screenshot|screen_shot|screen-shot|^scr_|^ss_|capture")
RE_REC = re.compile(r"(?i)screenrecording|screen\s?recording|screencast|screen_recording|screen-recording|^rec_|video_capture|recording")
RE_DL = re.compile(r"(?i)download|^dl_|whatsapp|telegram|instagram|snapchat|facebook|^fb_|^wa_|^tg_|^ig_|discord")

def detect_source(p: Path, config: dict = None, has_exif: bool = None, image_exts: set = None, video_exts: set = None) -> str:
    if config is None:
        from .metadata import load_config_file
        config = load_config_file()
        
    stem = p.stem
    ext = p.suffix.lower()
    
    if image_exts is None:
        image_exts = {x.lower() for x in config.get("supported_image_extensions", [])}
    if video_exts is None:
        video_exts = {x.lower() for x in config.get("supported_video_extensions", [])}
    
    # Check DL folder first
    in_download_dir = False
    for parent in p.parents:
        if parent.name.lower() == "downloads":
            in_download_dir = True
            break
            
    if in_download_dir or RE_DL.search(stem):
        return "DL"
        
    if ext in video_exts:
        if RE_REC.search(stem):
            return "REC"
        if stem.startswith(("VID_", "MVI_", "GOPR", "GP", "DSC_")):
            return "CAM"
    elif ext in image_exts:
        if RE_SCR.search(stem):
            return "SCR"
        if has_exif is not None:
            if has_exif:
                return "CAM"
        else:
            from .metadata import has_exif_camera
            if has_exif_camera(p):
                return "CAM"
        if stem.startswith(("DSC_", "IMG_", "PANO_", "MVIMG_", "CIMG_", "DCIM", "IMG-")):
            return "CAM"
            
    return "UNK"

def get_source_alias(source_type: str, config: dict = None) -> str:
    if config is None:
        from .metadata import load_config_file
        config = load_config_file()
    aliases = config.get("source_aliases", {})
    return aliases.get(source_type, source_type)
