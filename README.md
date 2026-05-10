# FL Backup Cleaner
A small desktop app built with PySide6. It:
1. Scans a chosen root folder for project folders that contain a child named Backup, then files containing "overwritten" in the name.
    (shows user analysis of storage distribution and storage size taken up)
2. Can remove the contents of those Backup folders safely by sending items to the system recycle bin.

## Quick start (while I tweak the app, figure out how to attach a logo, and make it an executable)
1. Create and activate a virtual environment
2. pip install -r requirements.txt
3. python -m flcleaner.app

The app shows a window with a folder picker, a preview table, and a button to run the cleanup.