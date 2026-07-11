"""
logic/html_report.py
--------------------
Generator laporan HTML statis dan interaktif secara offline.
Menghasilkan dashboard berisi grafik, tabel history, dan statistik.
"""
from pathlib import Path
import datetime
import os
import getpass
from logic.statistics import get_statistics
from logic.log_history import _load_history, get_master_history_path
from logic.version import PROGRAM_VERSION, PROGRAM_NAME
from logic.metadata import load_config_file

ROOT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT_DIR / "history" / "reports"

def _load_asset(filename: str) -> str:
    """Load text content from the assets/html directory."""
    asset_path = ROOT_DIR / "assets" / "html" / filename
    if not asset_path.exists():
        return ""
    return asset_path.read_text(encoding="utf-8")

def _generate_bars(data_dict: dict, limit: int = 8) -> str:
    """Generate HTML snippet for CSS bar charts."""
    if not data_dict:
        return "<div style='font-size: 13px; color: var(--text-muted);'>No data available.</div>"
    
    sorted_items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)[:limit]
    max_val = max(data_dict.values())
    
    html = ""
    for label, count in sorted_items:
        pct = (count / max_val) * 100 if max_val > 0 else 0
        html += f'''
        <div class="bar-row">
            <div class="bar-label" title="{label}">{label}</div>
            <div class="bar-track">
                <div class="bar-fill" style="width: {pct}%;"></div>
            </div>
            <div class="bar-value">{count:,}</div>
        </div>
        '''
    return html

def generate_html_report() -> str:
    """
    Men-generate HTML report ke folder history/reports.
    Return path absolute ke file HTML yang dibuat.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stats = get_statistics()
    history_data = _load_history(get_master_history_path()).get("history", [])
    
    # Ambil 100 history terakhir, sort reverse
    recent = sorted(history_data, key=lambda x: x.get("timestamp", ""), reverse=True)[:100]
    
    rows_html = ""
    for r in recent:
        status = r.get("status", "")
        status_cls = "status-active" if status == "ACTIVE" else "status-restored"
        orig_name = r.get("original_name", "")
        cur_name = r.get("current_name", "")
        
        before_after = f"{orig_name} <span class='arrow'>&#9654;</span> {cur_name}"
        if status == "RESTORED":
            before_after = f"<span style='text-decoration: line-through; color: var(--text-muted)'>{cur_name}</span> <span class='arrow'>&#9654;</span> {orig_name}"
            
        rows_html += f"<tr>"
        rows_html += f"<td>{r.get('timestamp', '').replace('T', ' ')}</td>"
        rows_html += f"<td>{r.get('camera', 'Unknown')}</td>"
        rows_html += f"<td>{before_after}</td>"
        rows_html += f"<td class='col-status {status_cls}'>{status}</td>"
        rows_html += f"</tr>\n"
        
    ts_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    config = load_config_file()
    sys_user = config.get("username", "Unknown")
    
    muc = stats.get("most_used_camera", ("None", 0))[0]
    ls_date = stats.get("largest_session", ("None", 0))[0]
    ls_count = stats.get("largest_session", ("None", 0))[1]
    
    pr = stats.get("protection_rank", {})
    
    html_template = _load_asset("report.html")
    css_content = _load_asset("report.css")
    js_content = _load_asset("report.js")
    
    if not html_template:
        raise FileNotFoundError("report.html template not found in assets/html/")
        
    final_html = html_template.format(
        injected_css=css_content,
        injected_js=js_content,
        program_name=PROGRAM_NAME,
        program_version=PROGRAM_VERSION,
        timestamp=ts_now,
        system_user=sys_user,
        
        total_rename=f"{stats.get('total_rename', 0):,}",
        total_restore=f"{stats.get('total_restore', 0):,}",
        most_used_camera=muc,
        largest_session_date=ls_date.split("T")[0] if ls_date != "None" else "None",
        largest_session_count=f"{ls_count:,}",
        
        rank_name=pr.get("current_rank", "UNRANKED"),
        next_rank=pr.get("next_rank", "NONE"),
        rank_remaining=f"{pr.get('remaining', 0):,}",
        rank_pct=pr.get("progress_percent", 0.0),
        rank_target=f"{pr.get('next_threshold', 0):,}",
        
        camera_bars=_generate_bars(stats.get("camera_usage", {})),
        ext_bars=_generate_bars(stats.get("file_type_stats", {})),
        
        table_rows=rows_html
    )
    
    filename = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    out_path = REPORTS_DIR / filename
    out_path.write_text(final_html, encoding="utf-8")
    
    return str(out_path.resolve())
