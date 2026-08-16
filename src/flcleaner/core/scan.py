from pathlib import Path
from typing import List, Dict
from datetime import datetime
import os

def is_backup_name(name: str) -> bool:
    return name.lower() == "backup"

def scan_for_backups(root: Path) -> List[Dict]:
    results: List[Dict] = []
    root = Path(root).expanduser().resolve()
    if not root.exists():
        return results

    for dirpath, dirnames, _ in os.walk(root):
        # find child named Backup in this folder
        child_names = {d for d in dirnames}
        target = None
        for d in child_names:
            if is_backup_name(d):
                target = d
                break
        if target is None:
            continue

        # Table scan display details
        backup_path = Path(dirpath) / target
        if not any(backup_path.iterdir()): continue

        display_path = backup_path.relative_to(root.parent)
        file_count, byte_size = count_files_and_size(backup_path)
        modified_time = datetime.fromtimestamp(backup_path.stat().st_mtime)

        results.append({
            "backup_path": str(backup_path),
            "display_path": str(display_path),
            "modified_time": modified_time,
            "file_count": file_count,
            "byte_size": byte_size,
        })
    return results

def count_files_and_size(folder: Path) -> tuple[int, int]:
    count = 0
    total = 0
    for dirpath, _, filenames in os.walk(folder):
        for name in filenames:
            count += 1
            try:
                total += (Path(dirpath) / name).stat().st_size
            except Exception:
                pass
    return count, total

def format_bytes(n: int) -> str:
    step = 1024.0
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    val = float(n)
    while val >= step and i < len(units) - 1:
        val /= step
        i += 1
    return f"{val:.2f} {units[i]}"
