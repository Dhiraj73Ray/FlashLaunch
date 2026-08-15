import sys
from PySide6.QtWidgets import QApplication
from ui.launcher_window import LauncherWindow

app = QApplication(sys.argv)

launcher = LauncherWindow()
launcher.show_launcher()

sys.exit(app.exec())