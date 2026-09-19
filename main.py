# This is the entry point of the app: it creates the Qt application
# and the main window, then hands control over to Qt's event loop.
import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from gui.main_window import MainWindow


def _app_base_dir() -> str:
    """Folder the app's data (expenses.json, budgets.json, settings.json)
    should live in. When packaged as a single .exe (PyInstaller
    --onefile), sys.executable points at the .exe itself; in normal
    development it's this file's own folder. Without this, a Desktop
    shortcut to the .exe would write its data files into whatever
    random folder Windows happens to use as the current directory."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def main():
    # Make sure expenses.json / budgets.json / settings.json always end
    # up next to the app itself, no matter where it's launched from
    # (double-clicking a Desktop shortcut, Start Menu, etc.).
    os.chdir(_app_base_dir())

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # app.exec() blocks here and keeps the app running until the
    # window is closed; sys.exit() makes sure the exit code is passed
    # back to Windows correctly.
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

