import json
from urllib.parse import quote

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest


class SuggestionService(QObject):
    suggestions_ready = Signal(list)

    def __init__(self):
        super().__init__()
        self.network = QNetworkAccessManager()
        self.network.finished.connect(self._handle_reply)

    def fetch(self, query: str):
        query = query.strip()
        if not query:
            self.suggestions_ready.emit([])
            return

        url = QUrl(
            f"https://suggestqueries.google.com/complete/search?client=firefox&q={quote(query)}"
        )
        request = QNetworkRequest(url)
        self.network.get(request)

    def _handle_reply(self, reply):
        try:
            data = bytes(reply.readAll())
            result = json.loads(data.decode("utf-8"))
            suggestions = result[1]
        except Exception:
            suggestions = []

        self.suggestions_ready.emit(suggestions[:6])