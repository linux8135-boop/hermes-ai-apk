"""Hermes AI — protocol and config loader."""
import json
from pathlib import Path

CONFIG_DIR = str(Path.home() / ".hermes")
CONFIG_PATH = CONFIG_DIR + "/config.json"


def ensure():
    Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)


def load():
    try:
        p = Path(CONFIG_PATH)
        if p.exists():
            return json.loads(p.read_text())
    except:
        pass
    return {}


def save(data):
    ensure()
    Path(CONFIG_PATH).write_text(json.dumps(data, indent=2))
