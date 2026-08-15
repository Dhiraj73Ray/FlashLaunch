import json
from pathlib import Path


class PositionManager:
    def __init__(self):
        self.settings_path = Path(__file__).parent.parent / "data" / "settings.json"

        self.default_position = {
            "x": None,
            "y": None
        }

        self.settings = {
            "save_position": False,
            "position": self.default_position.copy()
        }

        self.load()

    def load(self):
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    self.settings.update(json.load(f))
            except Exception:
                pass

    def save(self):
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)

    def should_save_position(self):
        return self.settings.get("save_position", False)

    def get_position(self):
        return self.settings.get("position", self.default_position)

    def set_position(self, x, y):
        self.settings["position"] = {
            "x": x,
            "y": y
        }

        if self.should_save_position():
            self.save()

    def set_save_position(self, enabled: bool):
        self.settings["save_position"] = enabled
        self.save()