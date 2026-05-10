from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QIcon
from importlib.resources import files

from ..core.scan import scan_for_backups, format_bytes
from ..core.clean import clean_backup_folder

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, logger, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.setWindowTitle("FLBU Cleaner")
        
        icon_path = files("flcleaner").joinpath("ui/icons/app.ico")
        self.setWindowIcon(QIcon(str(icon_path)))
        
        self.resize(900, 550)
        self._build_ui()

    def _build_ui(self):
        central = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(central)

        # Top controls
        path_row = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText("Choose the folder that contains your FL Studio project folders")
        browse_btn = QtWidgets.QPushButton("Browse")
        scan_btn = QtWidgets.QPushButton("Scan")
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(browse_btn)
        path_row.addWidget(scan_btn)

        # Table
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Backup folder", "Files", "Size"])
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        # Bottom controls
        bottom_row = QtWidgets.QHBoxLayout()
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setMinimumWidth(200)
        bottom_row.addWidget(self.status_label, 1)
        self.run_btn = QtWidgets.QPushButton("Run cleanup")
        self.run_btn.setEnabled(False)
        bottom_row.addWidget(self.run_btn)

        layout.addLayout(path_row)
        layout.addWidget(self.table, 1)
        layout.addLayout(bottom_row)

        self.setCentralWidget(central)

        # signals
        browse_btn.clicked.connect(self.on_browse)
        scan_btn.clicked.connect(self.on_scan)
        self.run_btn.clicked.connect(self.on_run)

    def on_browse(self):
        dlg = QtWidgets.QFileDialog(self, "Choose root folder")
        dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        dlg.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        if dlg.exec():
            sel = dlg.selectedFiles()
            if sel:
                self.path_edit.setText(sel[0])

    def on_scan(self):
        root = Path(self.path_edit.text().strip()).expanduser()
        if not root.exists():
            QtWidgets.QMessageBox.warning(self, "Invalid path", "Folder does not exist")
            return
        self.logger.info("scan start: %s", root)
        data = scan_for_backups(root)
        self.populate_table(data)
        total_files = sum(d["file_count"] for d in data)
        total_bytes = sum(d["byte_size"] for d in data)
        self.status_label.setText(f"Found {len(data)} backup folders, {total_files} files, {format_bytes(total_bytes)} total")
        self.run_btn.setEnabled(len(data) > 0)

    def populate_table(self, rows):
        self.table.setRowCount(0)
        for row in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(row["backup_path"]))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(row["file_count"]))
            )
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(format_bytes(row["byte_size"])))
        self.table.sortItems(0, QtCore.Qt.AscendingOrder)

    def on_run(self):
        count = self.table.rowCount()
        if count == 0:
            return
        ans = QtWidgets.QMessageBox.question(
            self,
            "Confirm",
            "Send all files inside every listed Backup folder to the recycle bin now"
        )
        if ans != QtWidgets.QMessageBox.Yes:
            return

        removed = 0
        errors = 0
        for i in range(count):
            backup_path = self.table.item(i, 0).text()
            res = clean_backup_folder(Path(backup_path))
            removed += res["removed"]
            errors += res["errors"]
            self.logger.info("cleaned %s removed=%s errors=%s", backup_path, res["removed"], res["errors"])
        msg = f"Done. Removed items {removed}. Errors {errors}."
        self.status_label.setText(msg)
        QtWidgets.QMessageBox.information(self, "Cleanup complete", msg)
