import sys
from PySide6.QtWidgets import QApplication

from ui.launcher_window import LauncherWindow
from services.launcher_controller import LauncherController
from services.hotkey_service import HotkeyService

app = QApplication(sys.argv)

launcher = LauncherWindow()
controller = LauncherController(launcher)

launcher.deactivated.connect(controller.hide)

hotkeys = HotkeyService()
hotkeys.hotkey_pressed.connect(controller.toggle)
hotkeys.register("ctrl+space")

sys.exit(app.exec())