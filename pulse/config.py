import json
import os
import sys
from copy import deepcopy
from pathlib import Path

from .constants import APP_ID, APP_NAME

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULTS = {
    "client_id": "",
    "sources": {"ytmusic": True, "youtube": True},
    "mode": "auto",  # auto | custom
    "idle_fallback": False,
    "custom": {
        "type": "PLAYING",
        "details": "",
        "state": "",
        "large_image": "",
        "large_text": "",
        "button_label": "",
        "button_url": "",
        "timer": True,
    },
    "autostart": False,
    "start_minimized": False,
    "close_to_tray": True,
}


def _config_dir() -> Path:
    root = os.environ.get("APPDATA")
    base = Path(root) if root else Path.home() / ".config"
    folder = base / APP_NAME
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _merge(base: dict, override: dict) -> dict:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge(base[key], value)
        elif key in base:
            base[key] = value
    return base


class Config:
    def __init__(self):
        self.path = _config_dir() / "config.json"
        self.data = deepcopy(DEFAULTS)
        self.load()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                _merge(self.data, json.load(fh))
        except (OSError, ValueError):
            pass

    def save(self):
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def effective_client_id(self) -> str:
        return (self.data["client_id"] or "").strip() or APP_ID
