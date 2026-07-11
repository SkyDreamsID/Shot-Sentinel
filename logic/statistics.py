"""
logic/statistics.py
--------------------
Penghitung statistik berdasarkan data di master_history.json.
Didesain untuk beroperasi murni dengan data statis tanpa database eksternal.
"""
from pathlib import Path
import os
from collections import defaultdict
from logic.log_history import _load_history, get_master_history_path

def calculate_protection_rank(total_renamed: int) -> dict:
    ranks_asc = [
        (0, "UNRANKED"),
        (100, "MILESTONE"),
        (500, "BRONZE"),
        (1000, "SILVER"),
        (5000, "GOLD"),
        (10000, "PLATINUM"),
        (50000, "MASTER"),
        (100000, "LEGENDARY"),
        (250000, "GUARDIAN"),
        (500000, "SENTINEL"),
        (1000000, "IMMORTAL")
    ]
    
    current_idx = 0
    for i, (threshold, name) in enumerate(ranks_asc):
        if total_renamed >= threshold:
            current_idx = i
        else:
            break
            
    current_rank = ranks_asc[current_idx][1]
    
    if current_idx < len(ranks_asc) - 1:
        next_threshold = ranks_asc[current_idx+1][0]
        next_rank = ranks_asc[current_idx+1][1]
        prev_threshold = ranks_asc[current_idx][0]
        
        remaining = next_threshold - total_renamed
        progress = ((total_renamed - prev_threshold) / (next_threshold - prev_threshold)) * 100
        progress = min(max(progress, 0), 100)
    else:
        next_threshold = total_renamed
        next_rank = "MAX RANK"
        remaining = 0
        progress = 100.0
        
    return {
        "current_rank": current_rank,
        "next_rank": next_rank,
        "next_threshold": next_threshold,
        "remaining": remaining,
        "progress_percent": round(progress, 1)
    }

def get_statistics() -> dict:
    """
    Membaca master_history.json dan menghitung statistik.
    
    Returns:
        dict berisi berbagai metrik statistik.
    """
    history_path = get_master_history_path()
    data = _load_history(history_path)
    entries = data.get("history", [])
    
    stats = {
        "total_rename": 0,
        "total_restore": 0,
        "camera_usage": defaultdict(int),
        "file_type_stats": defaultdict(int),
        "timeline": defaultdict(int),
        "session_counts": defaultdict(int),
        "largest_session": ("None", 0),
        "most_used_camera": ("None", 0)
    }
    
    for entry in entries:
        # Total Rename & Restore
        if entry.get("operation") == "rename":
            stats["total_rename"] += 1
        if entry.get("status") == "RESTORED":
            stats["total_restore"] += 1
            
        # Camera Usage
        camera = entry.get("camera", "Unknown")
        if camera:
            stats["camera_usage"][camera] += 1
            
        # File Types
        current_name = entry.get("current_name", "")
        if current_name:
            ext = os.path.splitext(current_name)[1].lower()
            if ext:
                stats["file_type_stats"][ext] += 1
                
        # Timeline & Sessions
        timestamp = entry.get("timestamp", "")
        if timestamp:
            date_only = timestamp.split("T")[0]
            stats["timeline"][date_only] += 1
            stats["session_counts"][timestamp] += 1

    # Find Most Used Camera
    if stats["camera_usage"]:
        best_cam = max(stats["camera_usage"].items(), key=lambda x: x[1])
        stats["most_used_camera"] = best_cam
        
    # Find Largest Session
    if stats["session_counts"]:
        best_session = max(stats["session_counts"].items(), key=lambda x: x[1])
        stats["largest_session"] = best_session
        
    # Convert defaultdict to dict for cleaner output
    stats["camera_usage"] = dict(stats["camera_usage"])
    stats["file_type_stats"] = dict(stats["file_type_stats"])
    stats["timeline"] = dict(stats["timeline"])
    del stats["session_counts"]
    
    stats["protection_rank"] = calculate_protection_rank(stats["total_rename"])
    
    return stats
