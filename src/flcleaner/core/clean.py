from pathlib import Path
from send2trash import send2trash
import os
from typing import Iterable

def clean_backup_folder(backup_folder: Path) -> dict:
    """
    Remove all contents of the given Backup folder by sending items to the recycle bin.
    Makes sure the Backup folder itself is kept.
    """
    backup_folder = Path(backup_folder)
    removed = 0
    errors = 0
    for entry in iter_children(backup_folder):
        if not is_backup_file(entry):
            continue
        try:
            send2trash(str(entry))
            removed += 1
        except Exception:
            errors += 1
    return {"removed": removed, "errors": errors}

def iter_children(folder: Path) -> Iterable[Path]:
    for name in os.listdir(folder):
        yield folder / name

def is_backup_file(file: Path) -> bool:
    filename = str(file)
    if "overwritten" in filename and ".flp" in filename:
        return True
    return False
