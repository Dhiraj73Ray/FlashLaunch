
import webbrowser
from urllib.parse import quote

from PySide6.QtCore import Qt, QEvent, QTimer, QPoint
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit,
    QFrame, QListWidget, QListWidgetItem, QApplication
)

from services.suggestion_service import SuggestionService
from system.position_manager import PositionManager


class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.position_manager = PositionManager()
        self.dragging = False
        self.drag_offset = QPoint()

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

        # --------- Suggestion service ---------
        self.suggestion_service = SuggestionService()
        self.suggestion_service.suggestions_ready.connect(self.display_suggestions)

        # Debounce timer
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fetch_google_suggestions)

        self.search.textChanged.connect(self.update_suggestions)

        self.center_on_screen()

    # ---------- Window ----------

    def center_on_screen(self):
        pos = self.position_manager.get_position()

        if (
            self.position_manager.should_save_position()
            and pos["x"] is not None
            and pos["y"] is not None
        ):
            self.move(pos["x"], pos["y"])
            return

        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() // 4
        self.move(x, y)

    def show_launcher(self):
        self.search.clear()
        self.list.clear()
        self.list.hide()
        self.setFixedHeight(self.collapsed_height)
        self.show()
        self.activateWindow()
        self.raise_()
        self.search.setFocus()

    def dismiss(self):
        self.hide()
        self.search.clear()
        self.list.clear()
        self.list.hide()
        self.setFixedHeight(self.collapsed_height)
        self.search.setFocus()

    # ---------- Suggestions ----------

    def update_suggestions(self, text):
        if not text.strip():
            self.list.clear()
            self.list.hide()
            self.setFixedHeight(self.collapsed_height)
            return

        self.timer.start(150)

    def fetch_google_suggestions(self):
        query = self.search.text().strip()
        self.suggestion_service.fetch(query)

    def display_suggestions(self, suggestions):
        self.list.clear()

        if not suggestions:
            self.list.hide()
            self.setFixedHeight(self.collapsed_height)
            return

        for s in suggestions:
            self.list.addItem(QListWidgetItem(s))

        self.list.setCurrentRow(0)
        self.list.show()
        self.setFixedHeight(self.expanded_height)

    # ---------- Keyboard ----------

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

    # ---------- Mouse Dragging ----------

    def mousePressEvent(self, event):
        # Only allow dragging from the top 8px strip
        if (
            event.button() == Qt.LeftButton
            and event.position().y() <= 20
        ):
            self.dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
    
        super().mousePressEvent(event)
    
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()
            return
    
        super().mouseMoveEvent(event)
    
    
    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            self.position_manager.set_position(self.x(), self.y())
            event.accept()
            return
    
        super().mouseReleaseEvent(event)
    