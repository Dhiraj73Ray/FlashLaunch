import sys
from PySide6.QtWidgets import QApplication
from ui.launcher_window import LauncherWindow
from services.launcher_controller import LauncherController


app = QApplication(sys.argv)

launcher = LauncherWindow()
controller = LauncherController(launcher)
# launcher.show_launcher()
controller.show()
launcher.deactivated.connect(controller.hide)
sys.exit(app.exec())