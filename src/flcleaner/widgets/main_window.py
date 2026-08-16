from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtCore import Qt, QUrl
from importlib.resources import files

from ..core.scan import scan_for_backups, format_bytes
from ..core.clean import clean_backup_folder

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, logger, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.setWindowTitle("FLBU Cleaner")
        
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
        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Clean", "Backup folder", "Date", "Files", "Size"])
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

        # Bottom controls
        bottom_row = QtWidgets.QHBoxLayout()

        self.donate_btn = QtWidgets.QPushButton("Donate")
        bottom_row.addWidget(self.donate_btn)

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
        self.donate_btn.clicked.connect(self.on_donate)

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
            modified_text = row["modified_time"].strftime("%d %b %Y, %H:%M")

            # Checkbox
            check_item = QtWidgets.QTableWidgetItem()
            check_item.setFlags(
                Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
            )
            check_item.setCheckState(Qt.Checked)

            i = self.table.rowCount()
            self.table.insertRow(i)

            # seperate relative diplay path and absolute path
            path_item = QtWidgets.QTableWidgetItem(row["display_path"])
            path_item.setData(Qt.UserRole, row["backup_path"])


            self.table.setItem(i, 0, check_item)
            self.table.setItem(i, 1, path_item)
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(modified_text))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(row["file_count"])))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(format_bytes(row["byte_size"])))
        self.table.sortItems(0, QtCore.Qt.AscendingOrder)

    def refresh_table(self):
        root = Path(self.path_edit.text().strip()).expanduser()

        data = scan_for_backups(root)
        self.populate_table(data)

        total_files = sum(d["file_count"] for d in data)
        total_bytes = sum(d["byte_size"] for d in data)

        self.status_label.setText(
            f"Found {len(data)} backup folders, "
            f"{total_files} files, "
            f"{format_bytes(total_bytes)} total"
        )

        self.run_btn.setEnabled(len(data) > 0)

    def on_run(self):
        count = self.table.rowCount()
        if count == 0:
            return

        # Check selected folders
        selected_count = 0

        for i in range(count):
            if self.table.item(i, 0).checkState() == Qt.Checked:
                selected_count += 1

        if selected_count == 0:
            QtWidgets.QMessageBox.information(
                self,
                "Nothing selected",
                "No backup folders are selected for cleanup."
            )
            return

        
        ans = QtWidgets.QMessageBox.question(
            self,
            "Confirm cleanup",
            f"Send the contents of {selected_count} selected backup folder(s) to the recycle bin?"
        )
        if ans != QtWidgets.QMessageBox.Yes:
            return

        removed = 0
        errors = 0
        for i in range(count):
            check_item = self.table.item(i, 0)
            if check_item.checkState() != Qt.Checked: continue

            # backup_path = self.table.item(i, 1).text()
            backup_path = self.table.item(i, 1).data(Qt.UserRole)
            res = clean_backup_folder(Path(backup_path))

            removed += res["removed"]
            errors += res["errors"]

            self.logger.info("cleaned %s removed=%s errors=%s", backup_path, res["removed"], res["errors"])

        msg = f"Done. Removed items {removed}. Errors {errors}."
        self.status_label.setText(msg)
        QtWidgets.QMessageBox.information(self, "Cleanup complete", msg)

    def on_donate(self):
        kofi_link = "https://ko-fi.com/rainyyrays"
        msg1 = "I hope this app has been helpful! If you'd like, you can support me keep making free stuff through Ko-fi :)"
        msg2 = msg1 + "\n\n" + "Would you like to open my Ko-fi page in your browser?"

        ans = QtWidgets.QMessageBox.question(
                self,
                "Open Ko-fi",
                msg2,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

        if ans != QtWidgets.QMessageBox.Yes:
            return

        QDesktopServices.openUrl(QUrl(kofi_link))