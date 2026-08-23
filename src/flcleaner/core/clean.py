from pathlib import Path
from send2trash import send2trash
import os
from typing import Iterable

def clean_backup_folder(
        backup_folder: Path,
        include_overwritten: bool,
        include_autosaved: bool
    ) -> dict:
    """
    Remove selected FL Studio backup types from the given Backup folder.
    Keeps the Backup folder itself.
    """
    backup_folder = Path(backup_folder)
    removed = 0
    errors = 0

    for entry in iter_children(backup_folder):
        if not is_backup_file(entry, include_overwritten,include_autosaved):
            continue

        try:
            send2trash(str(entry))
            removed += 1
        except Exception:
            errors += 1

    return {
        "removed": removed,
        "errors": errors
    }

def iter_children(folder: Path) -> Iterable[Path]:
    for name in os.listdir(folder):
        yield folder / name

def is_backup_file(file: Path, include_overwritten: bool, include_autosaved: bool) -> bool:
    bad_file_check = (not file.is_file()) or (file.suffix.lower() != ".flp")
    if bad_file_check:
        return False

    filename = file.name.lower()

    if include_overwritten and "overwritten" in filename:
        return True

    if include_autosaved and "autosaved" in filename:
        return True

    return False
