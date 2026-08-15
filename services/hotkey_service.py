import keyboard
from PySide6.QtCore import QObject, Signal


class HotkeyService(QObject):
    hotkey_pressed = Signal()

    def __init__(self):
        super().__init__()
        self.hotkey = None

    def register(self, key_combination="ctrl+space"):
        self.unregister()

        self.hotkey = keyboard.add_hotkey(
            key_combination,
            self.hotkey_pressed.emit
        )

    def unregister(self):
        if self.hotkey is not None:
            keyboard.remove_hotkey(self.hotkey)
            self.hotkey = None