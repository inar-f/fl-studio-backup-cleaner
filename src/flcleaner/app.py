import sys
from PySide6 import QtWidgets
from PySide6.QtGui import QIcon
from importlib.resources import files

from . import resources_rc
from .widgets.main_window import MainWindow
from .utils.logging_setup import setup_logger

def main():
    app = QtWidgets.QApplication(sys.argv)

    # Tooltip bg change
    app.setStyleSheet("""QToolTip {
        background-color: #E4E4E4;
        color: black;
        border: 3px outset #2b2b2b;
        padding: 6px;
        }
    """)
    
    icon_path = files("flcleaner").joinpath("ui/icons/app.ico")
    app.setWindowIcon(QIcon(":/ui/icons/app.svg"))

    logger = setup_logger()
    win = MainWindow(logger)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
