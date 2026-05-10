import sys
from PySide6 import QtWidgets
from PySide6.QtGui import QIcon
from importlib.resources import files

from .widgets.main_window import MainWindow
from .utils.logging_setup import setup_logger

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    icon_path = files("flcleaner").joinpath("ui/icons/app.ico")
    app.setWindowIcon(QIcon(str(icon_path)))
    
    logger = setup_logger()
    win = MainWindow(logger)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
