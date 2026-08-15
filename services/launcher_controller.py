from PySide6.QtCore import QObject, QEvent, QTimer
from PySide6.QtWidgets import QApplication


class LauncherController(QObject):
    def __init__(self, launcher):
        super().__init__()

        self.launcher = launcher
        self.visible = False

        # Listen to all application events
        QApplication.instance().installEventFilter(self)

    def show(self):
        if self.visible:
            return

        self.launcher.show_launcher()
        self.visible = True

    def hide(self):
        if not self.visible:
            return

        self.launcher.dismiss()
        self.visible = False

    def toggle(self):
        QTimer.singleShot(0, self._toggle)
    
    def _toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    # def eventFilter(self, obj, event):
    #     if not self.visible:
    #         return False

    #     # Outside click dismissal
    #     if event.type() == QEvent.MouseButtonPress:
    #         widget = QApplication.widgetAt(event.globalPosition().toPoint())

    #         if widget is None:
    #             self.hide()
    #             return False

    #         if widget is self.launcher or self.launcher.isAncestorOf(widget):
    #             return False

    #         self.hide()

    #     return False

    def eventFilter(self, obj, event):
        return False