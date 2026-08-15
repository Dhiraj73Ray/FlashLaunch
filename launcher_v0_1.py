import sys
import json
import webbrowser
from urllib.parse import quote

from PySide6.QtCore import Qt, QEvent, QTimer, QUrl
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit,
    QFrame, QListWidget, QListWidgetItem
)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest

class Launcher(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.collapsed_height = 90
        self.expanded_height = 300
        self.setFixedSize(760, self.collapsed_height)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QFrame()
        container.setObjectName("container")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search the web instantly...")
        self.search.setMinimumHeight(42)
        self.search.installEventFilter(self)

        self.list = QListWidget()
        self.list.hide()
        self.list.installEventFilter(self)

        layout.addWidget(self.search)
        layout.addWidget(self.list)
        outer.addWidget(container)

        self.setStyleSheet("""
            #container {
                background-color: #1b1b1d;
                border: 1px solid #34343a;
                border-radius: 24px;
            }

            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 20px;
                selection-background-color: #3b82f6;
            }

            QListWidget {
                background: transparent;
                border: none;
                color: white;
                font-size: 16px;
                outline: none;
            }

            QListWidget::item {
                padding: 10px;
                border-radius: 10px;
            }

            QListWidget::item:selected {
                background: #2d4b7c;
            }
        """)

        self.search.textChanged.connect(self.update_suggestions)

        self.network = QNetworkAccessManager()
        self.network.finished.connect(self.handle_suggestions)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fetch_google_suggestions)

        self.center_on_screen()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() // 4
        self.move(x, y)

    def show_launcher(self):
        self.search.clear()
        self.list.hide()
        self.setFixedHeight(self.collapsed_height)
        self.show()
        self.activateWindow()
        self.raise_()
        self.search.setFocus()

    def dismiss(self):
        self.hide()
        self.search.clear()
        self.list.hide()
        self.setFixedHeight(self.collapsed_height)
        self.search.setFocus()

    def update_suggestions(self, text):
        # self.list.clear()

        if not text.strip():
            self.list.clear()
            self.list.hide()
            self.setFixedHeight(self.collapsed_height)
            return

        self.timer.start(150)

        # suggestions = [
        #     text,
        #     f"{text} tutorial",
        #     f"{text} download",
        #     f"{text} github",
        #     f"{text} 2026"
        # ]

        # for s in suggestions:
        #     self.list.addItem(QListWidgetItem(s))

        # self.list.setCurrentRow(0)
        # self.list.show()
        # self.setFixedHeight(self.expanded_height)

    def fetch_google_suggestions(self):
        query = self.search.text().strip()
        if not query:
            return

        url = QUrl(
            f"https://suggestqueries.google.com/complete/search?client=firefox&q={quote(query)}"
        )
        request = QNetworkRequest(url)
        self.network.get(request)


    def handle_suggestions(self, reply):
        data = bytes(reply.readAll())

        try:
            result = json.loads(data.decode("utf-8"))
            suggestions = result[1]
        except Exception:
            suggestions = []

        self.list.clear()

        if not suggestions:
            self.list.hide()
            self.setFixedHeight(self.collapsed_height)
            return

        for s in suggestions[:6]:
            self.list.addItem(QListWidgetItem(s))

        self.list.setCurrentRow(0)
        self.list.show()
        self.setFixedHeight(self.expanded_height)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:

            # Esc works everywhere
            if event.key() == Qt.Key_Escape:
                self.dismiss()
                return True

            # Ctrl+Q quits the application
            if event.key() == Qt.Key_Q and event.modifiers() & Qt.ControlModifier:
                QApplication.quit()
                return True

            if obj == self.search:
                if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    query = self.search.text().strip()
                    if query:
                        webbrowser.open(
                            f"https://www.google.com/search?q={quote(query)}"
                        )
                        self.dismiss()
                    return True

            elif obj == self.list:
                if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    item = self.list.currentItem()
                    if item:
                        webbrowser.open(
                            f"https://www.google.com/search?q={quote(item.text())}"
                        )
                        self.dismiss()
                    return True

        return super().eventFilter(obj, event)


app = QApplication(sys.argv)

launcher = Launcher()
launcher.show_launcher()

sys.exit(app.exec())